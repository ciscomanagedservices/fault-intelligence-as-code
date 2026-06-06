"""
app/alert_pipeline.py — Webhook relay for the OpenCode SDK architecture.

Minimal FastAPI service that:
  1. Receives Splunk fault alert webhooks (POST /fault-alert)
  2. Creates an OpenCode session targeting the network-troubleshooter agent
     and sends a structured fault alert prompt
  3. Receives Webex approval webhook callbacks (POST /webex-callback)
     and forwards them to the appropriate OpenCode session
  4. Health check (GET /health)

No Redis, no in-memory run tracking, no artifact loading. The OpenCode
server handles all LLM interaction, RAW execution (via skill), and
RADKit MCP tool calls.

Run as:
    python -m app.alert_pipeline
or via Docker:
    docker compose up --build
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import threading
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import urlsplit, urlunsplit

import httpx
import uvicorn
from fastapi import FastAPI, Header, HTTPException, Request, Response, status
from pydantic import BaseModel

# Optional: webex-bot for outbound websocket card callback handling.
# Graceful degradation if not installed.
try:
    from webex_bot.models.command import Command as _WebexCommand  # type: ignore[import-untyped]
    from webex_bot.webex_bot import WebexBot  # type: ignore[import-untyped]

    _WEBEX_BOT_AVAILABLE = True
except ImportError:
    _WEBEX_BOT_AVAILABLE = False

logger = logging.getLogger(__name__)

# Configure root logger as soon as the module loads so logs are captured under
# any entrypoint (python -m, uvicorn, gunicorn, pytest, etc.). The original
# basicConfig was inside `if __name__ == "__main__":`, which meant nothing
# logged when imported by ASGI servers — silently masking bugs like the
# websocket bot crash loop.
if not logging.getLogger().handlers:
    logging.basicConfig(
        level=os.environ.get("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(levelname)s %(name)s -- %(message)s",
        stream=sys.stdout,
    )

# ---------------------------------------------------------------------------
# Configuration from environment variables
# ---------------------------------------------------------------------------

OPENCODE_URL = os.environ.get("OPENCODE_URL", "http://localhost:4096")
OPENCODE_USERNAME = os.environ.get("OPENCODE_SERVER_USERNAME", "opencode")
OPENCODE_PASSWORD = os.environ.get("OPENCODE_SERVER_PASSWORD", "")
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "")
REMEDIATION_MODE = os.environ.get("REMEDIATION_MODE", "strict")  # strict | hybrid-reasoning
LISTEN_PORT = int(os.environ.get("INGEST_PORT", "8080"))

# Target agent for fault remediation sessions. The OpenCode REST API uses this
# to route the session to the correct agent definition (.opencode/agents/<name>.md).
OPENCODE_AGENT = os.environ.get("OPENCODE_AGENT", "network-troubleshooter")

# Splunk REST API reverse-proxy upstream. The relay exposes /splunk/<path> and
# forwards to <SPLUNK_UPSTREAM_URL>/<path>. This lets public GitHub Actions
# runners write Splunk saved searches through the relay when lab Splunk is not
# directly reachable from the internet.
SPLUNK_UPSTREAM_URL = os.environ.get("SPLUNK_UPSTREAM_URL", "").rstrip("/")
SPLUNK_VERIFY_TLS = os.environ.get("SPLUNK_VERIFY_TLS", "false").lower() == "true"
SPLUNK_UI_HOST = os.environ.get("SPLUNK_UI_HOST", "localhost")
SPLUNK_UNRESOLVABLE_HOSTS = {"splunk-server1"}

# Webex bot token used to fetch Adaptive Card submit ("attachment action") details.
# Webex's attachmentActions:created webhook payload only contains the action id;
# the actual card input values must be retrieved via GET /v1/attachment/actions/{id}.
WEBEX_BOT_TOKEN = os.environ.get("WEBEX_BOT_TOKEN", "")
WEBEX_API_BASE = os.environ.get("WEBEX_API_BASE", "https://webexapis.com/v1").rstrip("/")
# Default room for acknowledgment messages when a callback's roomId is missing.
WEBEX_ROOM_ID = os.environ.get("WEBEX_ROOM_ID", "")

# Track active sessions: incident_id -> session metadata (for routing Webex callbacks).
# ``alert_def_id`` remains the fault-signature / alert-definition identifier; it is
# not unique per occurrence and must not be used as the approval routing key.
ACTIVE_SESSION_TTL_SECONDS = int(os.environ.get("ACTIVE_SESSION_TTL_SECONDS", "86400"))


@dataclass
class ActiveSession:
    incident_id: str
    alert_def_id: str
    session_id: str
    created_at: datetime
    last_updated_at: datetime


_active_sessions: dict[str, ActiveSession] = {}
_incident_id_lock = threading.Lock()
_last_incident_timestamp: datetime | None = None

# Event loop reference for the websocket bot thread to schedule coroutines.
_main_event_loop: asyncio.AbstractEventLoop | None = None

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Fault Intelligence -- Webhook Relay",
    version="0.2.0",
    description=(
        "Receives Splunk fault alert webhooks and Webex approval callbacks, "
        "relays them to an OpenCode server for LLM-driven remediation."
    ),
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _verify_secret(authorization: str | None) -> None:
    if not WEBHOOK_SECRET:
        return
    expected = f"Bearer {WEBHOOK_SECRET}"
    if authorization != expected:
        logger.warning("Webhook request rejected: invalid Authorization header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook secret",
        )


def _format_incident_id(ts: datetime) -> str:
    """Format a UTC timestamp as a timestamp-only Incident ID."""
    return f"INC-{ts.strftime('%Y%m%dT%H%M%SZ')}"


def _generate_incident_id() -> str:
    """Generate a unique timestamp-only Incident ID for this relay process.

    IDs are intentionally seconds-precision for readability. To keep them unique
    when multiple alerts arrive within one second, this allocator advances the
    logical timestamp by one second if the current second has already been used.
    """
    global _last_incident_timestamp
    with _incident_id_lock:
        now = datetime.now(timezone.utc).replace(microsecond=0)
        if _last_incident_timestamp is not None and now <= _last_incident_timestamp:
            now = _last_incident_timestamp + timedelta(seconds=1)
        _last_incident_timestamp = now
        return _format_incident_id(now)


def _normalize_splunk_results_link(value: Any) -> Any:
    """Replace lab-local Splunk hostnames with the routable Splunk UI IP."""
    if not isinstance(value, str) or not value:
        return value
    try:
        parsed = urlsplit(value)
    except ValueError:
        return value
    if parsed.hostname not in SPLUNK_UNRESOLVABLE_HOSTS:
        return value

    netloc = SPLUNK_UI_HOST
    if parsed.port:
        netloc = f"{netloc}:{parsed.port}"
    return urlunsplit((parsed.scheme, netloc, parsed.path, parsed.query, parsed.fragment))


def _cleanup_active_sessions(now: datetime | None = None) -> None:
    """Remove stale active-session registrations."""
    if ACTIVE_SESSION_TTL_SECONDS <= 0:
        return
    now = now or datetime.now(timezone.utc)
    cutoff = now - timedelta(seconds=ACTIVE_SESSION_TTL_SECONDS)
    stale = [
        incident_id
        for incident_id, session in _active_sessions.items()
        if session.last_updated_at < cutoff
    ]
    for incident_id in stale:
        session = _active_sessions.pop(incident_id, None)
        if session:
            logger.info(
                "Expired active session: incident_id=%s alert_def_id=%s session_id=%s",
                session.incident_id,
                session.alert_def_id,
                session.session_id,
            )


def _register_active_session(incident_id: str, alert_def_id: str, session_id: str) -> None:
    """Register an OpenCode session for later Webex approval routing."""
    _cleanup_active_sessions()
    now = datetime.now(timezone.utc)
    _active_sessions[incident_id] = ActiveSession(
        incident_id=incident_id,
        alert_def_id=alert_def_id,
        session_id=session_id,
        created_at=now,
        last_updated_at=now,
    )


def _normalize_fault_alert(payload: dict[str, Any]) -> dict[str, Any]:
    """Normalize the Splunk webhook payload into the agent's alert shape."""
    result = payload.get("result")
    if not isinstance(result, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported fault alert format: expected a top-level result object",
        )

    alert_def_id = str(result.get("alert_def_id", "")).strip()
    incident_id = str(
        result.get("incident_id") or payload.get("incident_id") or _generate_incident_id()
    ).strip()
    # Accept both legacy "system" field and the newer "device_name" field.
    device_hostname = str(result.get("device_name") or result.get("system", "")).strip()

    if not alert_def_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fault alert result is missing alert_def_id",
        )

    if not device_hostname:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fault alert result is missing device_name (or legacy system) field",
        )

    alert_vars = {
        key: value
        for key, value in result.items()
        if key not in {"incident_id", "alert_def_id", "device_name", "system", "mode"}
    }

    metadata_field_map = {
        "sid": "splunk_sid",
        "search_name": "splunk_search_name",
        "app": "splunk_app",
        "owner": "splunk_owner",
        "results_link": "splunk_results_link",
    }
    for source_field, target_field in metadata_field_map.items():
        value = payload.get(source_field)
        if value is not None:
            if target_field == "splunk_results_link":
                value = _normalize_splunk_results_link(value)
            alert_vars[target_field] = value

    normalized_alert: dict[str, Any] = {
        "incident_id": incident_id,
        "alert_def_id": alert_def_id,
        "device_hostname": device_hostname,
        "mode": result.get("mode") or payload.get("mode"),  # caller-supplied override
        "alert_vars": alert_vars,
        "raw_message": payload.get("raw_message"),
    }
    if payload.get("kb_query_mode"):
        normalized_alert["kb_query_mode"] = payload["kb_query_mode"]
    return normalized_alert


def _build_prompt(payload: dict[str, Any]) -> str:
    """Build the structured prompt that triggers the network-troubleshooter agent."""
    alert: dict[str, Any] = {
        "incident_id": payload["incident_id"],
        "alert_def_id": payload["alert_def_id"],
        "device_hostname": payload["device_hostname"],
        "mode": payload.get("mode") or REMEDIATION_MODE,
        "alert_vars": payload.get("alert_vars", {}),
        "raw_message": payload.get("raw_message"),
    }
    # Optional override for the KB wiki query depth (quick | standard | deep).
    # Skill default is "standard". Forward only if the caller set it explicitly.
    if payload.get("kb_query_mode"):
        alert["kb_query_mode"] = payload["kb_query_mode"]
    alert_json = json.dumps(alert, indent=2)
    return (
        f"A fault alert has been received. Diagnose and remediate this fault:\n\n"
        f"```json\n{alert_json}\n```"
    )


def _opencode_auth() -> httpx.BasicAuth | None:
    """Build basic auth for the OpenCode server, if credentials are configured."""
    if OPENCODE_PASSWORD:
        return httpx.BasicAuth(username=OPENCODE_USERNAME, password=OPENCODE_PASSWORD)
    return None


async def _create_opencode_session() -> str:
    """Create a new OpenCode session.

    The agent is specified per-message (not per-session) via the prompt_async
    body. Session creation only accepts { parentID?, title? }.
    """
    async with httpx.AsyncClient(timeout=30, auth=_opencode_auth()) as http:
        resp = await http.post(
            f"{OPENCODE_URL}/session",
            json={},
        )
        resp.raise_for_status()
        data: dict[str, Any] = resp.json()
        session_id: str = data["id"]
        logger.info(
            "Created OpenCode session: %s (agent=%s)", session_id, OPENCODE_AGENT
        )
        return session_id


async def _send_message(session_id: str, content: str) -> dict[str, Any]:
    """Send a message to an OpenCode session (fire-and-forget via async endpoint).

    The agent is specified here in the message body, which is where the
    OpenCode REST API actually supports it (POST /session/:id/prompt_async
    body: { agent?, model?, parts, ... }).
    """
    async with httpx.AsyncClient(timeout=30, auth=_opencode_auth()) as http:
        resp = await http.post(
            f"{OPENCODE_URL}/session/{session_id}/prompt_async",
            json={
                "agent": OPENCODE_AGENT,
                "parts": [{"type": "text", "text": content}],
            },
        )
        resp.raise_for_status()
        # prompt_async returns 204 No Content
        return {"status": "sent"}


async def _webex_get_person_name(person_id: str) -> str:
    """Look up a Webex user's display name; fall back to the raw id on failure."""
    if not (person_id and WEBEX_BOT_TOKEN):
        return person_id or "unknown user"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{WEBEX_API_BASE}/people/{person_id}",
                headers={"Authorization": f"Bearer {WEBEX_BOT_TOKEN}"},
            )
            resp.raise_for_status()
            data: dict[str, Any] = resp.json()
            return str(data.get("displayName") or data.get("emails", [person_id])[0])
    except httpx.HTTPError as exc:
        logger.warning("Failed to fetch Webex person %s: %s", person_id, exc)
        return person_id


async def _webex_post_message(room_id: str, markdown: str) -> None:
    """Post a markdown message to a Webex room using the bot token."""
    if not (room_id and WEBEX_BOT_TOKEN):
        logger.warning(
            "Skipping Webex post -- room_id or WEBEX_BOT_TOKEN missing (room=%s)",
            room_id,
        )
        return
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{WEBEX_API_BASE}/messages",
                headers={"Authorization": f"Bearer {WEBEX_BOT_TOKEN}"},
                json={"roomId": room_id, "markdown": markdown},
            )
            resp.raise_for_status()
    except httpx.HTTPError as exc:
        logger.warning("Failed to post Webex acknowledgment to %s: %s", room_id, exc)


# ---------------------------------------------------------------------------
# Route: Splunk fault alert webhook
# ---------------------------------------------------------------------------


class FaultAlertResponse(BaseModel):
    """Response for POST /fault-alert."""

    status: str
    incident_id: str
    alert_def_id: str
    session_id: str


@app.post("/fault-alert", status_code=status.HTTP_202_ACCEPTED)
async def receive_fault_alert(
    request: Request,
    authorization: str | None = Header(default=None),
) -> FaultAlertResponse:
    """
    Accept a fault alert webhook from Splunk.

    Creates an OpenCode session and sends a structured prompt that triggers
    the fault-remediation skill. Returns 202 immediately.

    Example:
        curl -s -X POST http://localhost:8080/fault-alert \\
          -H 'Content-Type: application/json' \\
          -d '{
                        "sid": "scheduler__admin_test_app__demo_sid",
                        "search_name": "ad000002_bgp_neighbor_admin_shutdown_v2",
                        "app": "test_app",
                        "owner": "admin",
                        "results_link": "http://splunk-server1:8000/app/test_app/@go?sid=demo_sid",
                        "result": {
                                                        "_time": "1779776665",
                                                        "alert_def_id": "AD000002",
                                                        "system": "xr-43",
                                                        "device_ip": "192.0.2.43",
                                                        "neighbor_ip": "172.20.20.18",
                                                        "vrf_name": "default",
                                                        "neighbor_as": "3334"
            }
          }'
    """
    _verify_secret(authorization)
    body: dict[str, Any] = await request.json()
    logger.info("Received fault alert: %s", json.dumps(body))

    normalized_alert = _normalize_fault_alert(body)
    incident_id = str(normalized_alert["incident_id"])
    alert_def_id = str(normalized_alert["alert_def_id"])

    try:
        session_id = await _create_opencode_session()
    except httpx.HTTPError as exc:
        logger.error("Failed to create OpenCode session: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Could not reach OpenCode server at {OPENCODE_URL}: {exc}",
        ) from exc

    # Track the session for Webex callback routing. Route by incident_id because
    # alert_def_id can repeat across simultaneous occurrences of the same fault.
    _register_active_session(incident_id, alert_def_id, session_id)

    prompt = _build_prompt(normalized_alert)
    logger.info(
        "Sending prompt to session %s for incident_id=%s alert_def_id=%s",
        session_id,
        incident_id,
        alert_def_id,
    )

    try:
        await _send_message(session_id, prompt)
    except httpx.HTTPError as exc:
        logger.error("Failed to send message to session %s: %s", session_id, exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to send prompt to OpenCode session: {exc}",
        ) from exc

    return FaultAlertResponse(
        status="accepted",
        incident_id=incident_id,
        alert_def_id=alert_def_id,
        session_id=session_id,
    )


# ---------------------------------------------------------------------------
# Webex approval handling
# ---------------------------------------------------------------------------
#
# Approvals come back via the Webex websocket bot (see "Webex Websocket Bot"
# section below). There is no public HTTP webhook for approvals — the bot
# maintains an outbound websocket connection to Webex Cloud, which means the
# relay does not need to be publicly reachable for approvals to work.
#
# A previous version of this file also exposed POST /webex-callback as an
# inbound webhook handler. It was removed because:
#   (a) it required public URL setup that we do not provide in the demo,
#   (b) if a Webex admin ever registered both the webhook AND the websocket
#       bot was running, every click would be delivered twice — once via
#       websocket and once via HTTP — causing the agent to see two
#       "Human operator response: APPROVED" messages in a row.
# If you need an HTTP fallback path in the future, add it back behind an
# explicit feature flag and disable the websocket bot when the flag is on.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Route: List active sessions (debugging)
# ---------------------------------------------------------------------------


@app.get("/sessions")
async def list_sessions() -> dict[str, dict[str, str]]:
    """Return active incident_id -> session metadata mappings."""
    _cleanup_active_sessions()
    return {
        incident_id: {
            "incident_id": session.incident_id,
            "alert_def_id": session.alert_def_id,
            "session_id": session.session_id,
            "created_at": session.created_at.isoformat(),
            "last_updated_at": session.last_updated_at.isoformat(),
        }
        for incident_id, session in _active_sessions.items()
    }


# ---------------------------------------------------------------------------
# Route: Health check
# ---------------------------------------------------------------------------


@app.get("/health")
async def health() -> dict[str, str]:
    """Simple liveness probe -- relay process is up."""
    return {"status": "ok", "opencode_url": OPENCODE_URL, "agent": OPENCODE_AGENT, "mode": REMEDIATION_MODE}


@app.get("/health/deep")
async def health_deep() -> dict[str, Any]:
    """
    Deep health check -- verifies that the relay can reach both the OpenCode
    server and the RADKit MCP endpoint.

    Use this before triggering a fault alert to catch wiring problems early.
    Returns 200 with per-component status; the overall ``status`` field is
    ``ok`` only when every dependency is reachable.
    """
    # The RADKit MCP endpoint is configured in opencode.json on the host where
    # `opencode serve` runs, not in this relay. This optional health-check URL
    # lets operators verify relay-to-MCP network reachability from the relay's
    # network namespace.
    radkit_url = os.environ.get("RADKIT_MCP_URL", "http://localhost:8000/mcp")

    components: dict[str, dict[str, Any]] = {}

    # --- OpenCode server ---------------------------------------------------
    try:
        async with httpx.AsyncClient(timeout=5, auth=_opencode_auth()) as http:
            resp = await http.get(f"{OPENCODE_URL}/global/health")
            resp.raise_for_status()
            components["opencode"] = {
                "status": "ok",
                "url": OPENCODE_URL,
                "detail": resp.json(),
            }
    except Exception as exc:  # noqa: BLE001 -- want any error surfaced
        logger.warning("OpenCode health check failed: %s", exc)
        components["opencode"] = {
            "status": "unreachable",
            "url": OPENCODE_URL,
            "error": str(exc),
        }

    # --- RADKit MCP endpoint ----------------------------------------------
    # MCP streamable-HTTP responds to GET with 405 / 406 / 400 depending on
    # transport state; we only care that the TCP+HTTP layer is alive, not the
    # specific status code.
    try:
        async with httpx.AsyncClient(timeout=5) as http:
            resp = await http.get(radkit_url)
            components["radkit_mcp"] = {
                "status": "ok",
                "url": radkit_url,
                "http_status": resp.status_code,
            }
    except Exception as exc:  # noqa: BLE001
        logger.warning("RADKit MCP health check failed: %s", exc)
        components["radkit_mcp"] = {
            "status": "unreachable",
            "url": radkit_url,
            "error": str(exc),
        }

    # --- Webex (credential presence only) ---------------------------------
    webex_token_present = bool(os.environ.get("WEBEX_BOT_TOKEN"))
    webex_room_present = bool(os.environ.get("WEBEX_ROOM_ID"))
    components["webex"] = {
        "status": "ok" if (webex_token_present and webex_room_present) else "not_configured",
        "bot_token_present": webex_token_present,
        "room_id_present": webex_room_present,
    }

    overall = "ok" if all(c.get("status") == "ok" for c in components.values()) else "degraded"
    return {
        "status": overall,
        "mode": REMEDIATION_MODE,
        "components": components,
    }


# ---------------------------------------------------------------------------
# Splunk REST API reverse proxy
# ---------------------------------------------------------------------------
#
# Why this exists: public GitHub Actions runners may need to deploy generated
# Splunk saved searches (alert definitions) into a lab Splunk instance that is not directly
# reachable from the internet. Configure SPLUNK_UPSTREAM_URL and expose the
# relay publicly; callers can target /splunk/ and the relay forwards every
# method, header, query string, and body to the upstream Splunk REST API.
#
# TLS verification is disabled by default because lab Splunk uses a
# self-signed certificate. Set SPLUNK_VERIFY_TLS=true to opt in.

_HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
    "host",
    "content-length",
    # httpx auto-decompresses gzip/br/deflate bodies, so the upstream's
    # Content-Encoding header would lie about what we return. Strip it.
    "content-encoding",
}


@app.api_route(
    "/splunk/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"],
)
async def splunk_proxy(path: str, request: Request) -> Response:
    """Forward /splunk/<path> to the configured Splunk REST upstream.

    Streams the response body back unchanged. Hop-by-hop headers are
    stripped per RFC 7230 so httpx and Starlette can manage framing.
    """
    if not SPLUNK_UPSTREAM_URL:
        raise HTTPException(
            status_code=503,
            detail="Splunk proxy is not configured. Set SPLUNK_UPSTREAM_URL to enable /splunk routes.",
        )

    target_url = f"{SPLUNK_UPSTREAM_URL}/{path}"
    request_headers = {
        k: v for k, v in request.headers.items() if k.lower() not in _HOP_BY_HOP_HEADERS
    }
    body = await request.body()

    try:
        async with httpx.AsyncClient(verify=SPLUNK_VERIFY_TLS, timeout=30) as http:
            upstream = await http.request(
                method=request.method,
                url=target_url,
                headers=request_headers,
                params=request.query_params,
                content=body,
            )
    except httpx.RequestError as exc:
        logger.warning("Splunk proxy upstream error for %s %s: %s", request.method, path, exc)
        raise HTTPException(status_code=502, detail=f"Splunk upstream error: {exc}") from exc

    response_headers = {
        k: v for k, v in upstream.headers.items() if k.lower() not in _HOP_BY_HOP_HEADERS
    }
    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers=response_headers,
        media_type=upstream.headers.get("content-type"),
    )


# ---------------------------------------------------------------------------
# Webex Websocket Bot — outbound-only card callback handler
# ---------------------------------------------------------------------------
# Uses the `webex-bot` library to maintain a persistent outbound websocket
# connection to Webex cloud. Card submit actions with
# callback_keyword="fault_approval" are routed here, eliminating the need for
# a publicly-reachable inbound webhook endpoint.
#
# The existing POST /webex-callback route is preserved as a fallback.
# ---------------------------------------------------------------------------


async def _forward_approval(
    incident_id: str,
    decision_raw: str,
    actor_id: str,
    room_id: str,
    alert_def_id: str = "",
) -> None:
    """Forward a card approval/denial to the correct OpenCode session."""
    _cleanup_active_sessions()
    if decision_raw.upper() in ("APPROVE", "APPROVED"):
        action = "APPROVED"
    elif decision_raw.upper() in ("DENY", "DENIED", "REJECT", "REJECTED"):
        action = "DENIED"
    else:
        logger.warning("Unrecognized decision '%s'; defaulting to DENIED", decision_raw)
        action = "DENIED"

    session = _active_sessions.get(incident_id)
    if not session:
        # Fallback: pick the most-recently-registered session (single-fault demo mode).
        if _active_sessions:
            original_incident_id = incident_id
            incident_id = next(iter(reversed(_active_sessions)))
            session = _active_sessions[incident_id]
            logger.warning(
                "No session for incident_id=%s; falling back to most recent: %s",
                original_incident_id or "<missing>",
                incident_id,
            )
        else:
            logger.error(
                "No active sessions; cannot forward approval for incident_id=%s",
                incident_id or "<missing>",
            )
            return

    session.last_updated_at = datetime.now(timezone.utc)
    alert_def_id = alert_def_id or session.alert_def_id
    session_id = session.session_id

    # Post acknowledgment to Webex room.
    ack_room = room_id or WEBEX_ROOM_ID
    actor_name = await _webex_get_person_name(actor_id)
    decision_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    verb = "approved" if action == "APPROVED" else "denied"
    ack_markdown = (
        f"**Incident {incident_id}** (Alert Definition {alert_def_id}) - change request "
        f"**{verb}** by **{actor_name}** at {decision_time}."
    )
    await _webex_post_message(ack_room, ack_markdown)

    # Forward decision to the OpenCode session.
    message = f"Human operator response: **{action}**\n{ack_markdown}"
    try:
        await _send_message(session_id, message)
        logger.info(
            "Forwarded %s to session %s for incident_id=%s alert_def_id=%s",
            action,
            session_id,
            incident_id,
            alert_def_id,
        )
    except httpx.HTTPError as exc:
        logger.error("Failed to forward approval to session %s: %s", session_id, exc)
        return

    # Do not pop the mapping here: one incident can legitimately require more
    # than one approval card. TTL cleanup removes stale entries.


def _start_webex_bot_thread() -> None:
    """Spawn a daemon thread running the WebexBot with exponential-backoff retry."""
    if not _WEBEX_BOT_AVAILABLE:
        logger.warning(
            "webex-bot package not installed; websocket card callbacks disabled"
        )
        return

    if not WEBEX_BOT_TOKEN:
        logger.warning(
            "WEBEX_BOT_TOKEN not set; websocket card callbacks disabled"
        )
        return

    class FaultApprovalCommand(_WebexCommand):  # type: ignore[misc]
        """Handle Adaptive Card submits with callback_keyword='fault_approval'."""

        def __init__(self) -> None:
            super().__init__(
                command_keyword="fault_approval",
                help_message="Handle fault approval card callbacks",
                card_callback_keyword="fault_approval",
            )

        def execute(self, message: Any, attachment_actions: Any, activity: Any) -> str:  # noqa: ARG002
            """Extract decision and forward to the OpenCode session."""
            inputs: dict[str, Any] = {}
            if attachment_actions and hasattr(attachment_actions, "inputs"):
                inputs = attachment_actions.inputs or {}

            incident_id = str(inputs.get("incident_id", ""))
            alert_def_id = str(inputs.get("alert_def_id", ""))
            decision = str(inputs.get("decision", ""))
            actor_id = ""
            room_id = ""

            # Prefer direct fields on AttachmentActions (webexpythonsdk exposes
            # personId and roomId as camelCase properties).
            if attachment_actions:
                actor_id = str(
                    getattr(attachment_actions, "personId", "")
                    or getattr(attachment_actions, "person_id", "")
                    or ""
                )
                room_id = str(
                    getattr(attachment_actions, "roomId", "")
                    or getattr(attachment_actions, "room_id", "")
                    or ""
                )

            # Fall back to activity object if the direct fields are empty.
            if not actor_id and activity:
                actor = getattr(activity, "actor", None)
                if isinstance(actor, dict):
                    actor_id = str(actor.get("id", ""))
                elif actor is not None:
                    actor_id = str(getattr(actor, "id", "") or "")
            if not room_id and activity:
                target = getattr(activity, "target", None)
                if isinstance(target, dict):
                    room_id = str(target.get("id", ""))
                elif target is not None:
                    room_id = str(getattr(target, "id", "") or "")

            if not incident_id and _active_sessions:
                incident_id = next(iter(reversed(_active_sessions)))
                logger.warning(
                    "No incident_id in card inputs; falling back to most recent: %s",
                    incident_id,
                )

            logger.info(
                "Websocket card callback: incident_id=%s alert_def_id=%s decision=%s actor=%s",
                incident_id,
                alert_def_id,
                decision,
                actor_id,
            )

            # Schedule the async forwarding on the main event loop.
            if _main_event_loop and not _main_event_loop.is_closed():
                asyncio.run_coroutine_threadsafe(
                    _forward_approval(incident_id, decision, actor_id, room_id, alert_def_id),
                    _main_event_loop,
                )
            else:
                logger.error("Main event loop not available; cannot forward approval")

            return ""

    def _run_bot() -> None:
        """Run the WebexBot with exponential-backoff retry.

        Notes on asyncio + threads (Python 3.12):

          * webex-bot's WebsocketClient.run() calls asyncio.get_event_loop()
            and run_until_complete() directly. Python 3.10+ does NOT
            auto-create an event loop in non-main threads, so we must
            asyncio.new_event_loop() and asyncio.set_event_loop() once for
            the bot thread.

          * Card events arrive on a separate executor worker thread
            (`asyncio_0`) spawned by loop.run_in_executor(). The library's
            _ack_message() in that worker calls asyncio.run(send(...)).
            Native asyncio.run() in a worker thread creates its own fresh
            loop, runs the coroutine, and tears it down — completely
            thread-local. Do NOT monkey-patch asyncio.run; a previous
            version of this file did, redirecting to asyncio.get_event_loop()
            (which raises in worker threads on 3.10+), which silently broke
            every card click. Removed.
        """
        backoff = 5.0
        max_backoff = 120.0

        while True:
            try:
                # Bot thread needs its own loop because the library calls
                # asyncio.get_event_loop().run_until_complete(...) directly.
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                approved_rooms = [WEBEX_ROOM_ID] if WEBEX_ROOM_ID else []
                if not approved_rooms:
                    logger.warning(
                        "WEBEX_ROOM_ID not set; bot will not filter rooms (security risk)"
                    )
                bot = WebexBot(
                    teams_bot_token=WEBEX_BOT_TOKEN,
                    approved_rooms=approved_rooms,
                )
                bot.add_command(FaultApprovalCommand())
                logger.info(
                    "Webex websocket bot starting (outbound connection, approved_rooms=%s)...",
                    approved_rooms or "ALL",
                )
                bot.run()
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "Webex websocket bot crashed (%s); retrying in %.0fs",
                    exc,
                    backoff,
                )
                import time

                time.sleep(backoff)
                backoff = min(backoff * 2, max_backoff)

    thread = threading.Thread(target=_run_bot, daemon=True, name="webex-bot")
    thread.start()
    logger.info("Webex websocket bot thread started (daemon)")


@app.on_event("startup")
async def _on_startup() -> None:
    """Capture the main event loop and start the websocket bot thread."""
    global _main_event_loop  # noqa: PLW0603
    _main_event_loop = asyncio.get_event_loop()
    _start_webex_bot_thread()


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    uvicorn.run(
        "app.alert_pipeline:app",
        host="0.0.0.0",
        port=LISTEN_PORT,
        reload=False,
    )
