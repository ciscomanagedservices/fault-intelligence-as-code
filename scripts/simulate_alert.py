#!/usr/bin/env python3
"""
simulate_alert.py — Send a fake Splunk fault alert to the webhook relay.

Simulates an AD000002 BGP Neighbor Admin Shutdown alert (IOS XR).

Two modes of operation:

  1. **Via relay** (default): POST to the alert_pipeline.py relay, which
     creates an OpenCode session and sends the prompt. Use this to test
     the full headless pipeline (Splunk -> relay -> OpenCode -> RADKit).

  2. **Direct prompt** (--direct): Print the structured prompt to stdout
     so you can paste it into the OpenCode TUI for headed-mode testing.

Usage:
    # Via relay (headless mode)
    python scripts/simulate_alert.py [--api http://localhost:8080]

    # Direct prompt for TUI (headed mode)
    python scripts/simulate_alert.py --direct

    # Override specific fields
    python scripts/simulate_alert.py --direct --neighbor-ip 10.0.0.5 --neighbor-as 65001
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlsplit, urlunsplit

import requests

# ---------------------------------------------------------------------------
# Defaults -- AD000002 BGP Neighbor Admin Shutdown (IOS XR)
# ---------------------------------------------------------------------------

DEFAULT_API = "http://localhost:8080"
DEFAULT_ALERT_DEF_ID = "AD000002"
DEFAULT_SYSTEM = "xr-43"
DEFAULT_DEVICE_IP = "192.0.2.43"
DEFAULT_NEIGHBOR_IP = "172.20.20.18"
DEFAULT_VRF_NAME = "default"
DEFAULT_NEIGHBOR_AS = "3334"
DEFAULT_TIME = "1779776665"
DEFAULT_RAW_EVENT = (
    "May 26 06:24:25 192.0.2.43 792: xr-43 RP/0/RP0/CPU0:May 26 06:23:42.115 UTC: "
    "bgp[1090]: %ROUTING-BGP-5-ADJCHANGE : neighbor 172.20.20.18 Down - Admin. shutdown "
    "(CEASE notification sent - administrative shutdown) (VRF: default) (AS: 3334) "
)
DEFAULT_SEARCH_NAME = "ad000002_bgp_neighbor_admin_shutdown_v2"
DEFAULT_APP = "search"
DEFAULT_OWNER = "admin"
DEFAULT_SID = "scheduler__admin__search__RMD52d223463d946b4dd_at_1779776700_53"
DEFAULT_RESULTS_LINK = (
    "http://192.0.2.51:8000/app/search/search?q=%7Cloadjob%20"
    "scheduler__admin__search__RMD52d223463d946b4dd_at_1779776700_53"
    "%20%7C%20head%201%20%7C%20tail%201&earliest=0&latest=now"
)
DEFAULT_MODE = "strict"
SPLUNK_UI_HOST = "192.0.2.51"
SPLUNK_UNRESOLVABLE_HOSTS = {"splunk-server1"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _build_alert_payload(
    alert_def_id: str,
    system: str,
    device_ip: str,
    neighbor_ip: str,
    vrf_name: str,
    neighbor_as: str,
    time: str,
    raw_event: str,
    search_name: str,
    app: str,
    owner: str,
    sid: str,
    results_link: str,
    mode: str | None = None,
    kb_query_mode: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "sid": sid,
        "search_name": search_name,
        "app": app,
        "owner": owner,
        "results_link": results_link,
        "result": {
            "_time": time,
            "alert_def_id": alert_def_id,
            "system": system,
            "device_ip": device_ip,
            "neighbor_ip": neighbor_ip,
            "vrf_name": vrf_name,
            "neighbor_as": neighbor_as,
            "_raw": raw_event,
        },
    }
    if mode:
        payload["result"]["mode"] = mode
    if kb_query_mode:
        payload["kb_query_mode"] = kb_query_mode
    return payload


def _generate_incident_id() -> str:
    """Generate a timestamp-only Incident ID for direct/headed demo mode."""
    return f"INC-{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}"


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


def _normalize_alert_for_prompt(payload: dict[str, Any], mode: str) -> dict[str, Any]:
    """Mirror the relay's normalization so direct mode matches headless mode."""
    result = payload["result"]
    alert_vars = {
        key: value
        for key, value in result.items()
        if key not in {"incident_id", "alert_def_id", "device_name", "system", "mode"}
    }
    alert_vars.update(
        {
            "splunk_sid": payload["sid"],
            "splunk_search_name": payload["search_name"],
            "splunk_app": payload["app"],
            "splunk_owner": payload["owner"],
            "splunk_results_link": _normalize_splunk_results_link(payload["results_link"]),
        }
    )

    alert: dict[str, Any] = {
        "incident_id": result.get("incident_id") or payload.get("incident_id") or _generate_incident_id(),
        "alert_def_id": result["alert_def_id"],
        "device_hostname": result["system"],
        "mode": mode,
        "alert_vars": alert_vars,
        "raw_message": None,
    }
    if payload.get("kb_query_mode"):
        alert["kb_query_mode"] = payload["kb_query_mode"]
    return alert


def _build_prompt(payload: dict[str, Any], mode: str) -> str:
    """Build the same prompt the relay would send to OpenCode."""
    alert = _normalize_alert_for_prompt(payload, mode)
    alert_out: dict[str, Any] = {
        "incident_id": alert["incident_id"],
        "alert_def_id": alert["alert_def_id"],
        "device_hostname": alert["device_hostname"],
        "mode": alert["mode"],
        "alert_vars": alert["alert_vars"],
        "raw_message": alert["raw_message"],
    }
    if alert.get("kb_query_mode"):
        alert_out["kb_query_mode"] = alert["kb_query_mode"]
    alert_json = json.dumps(alert_out, indent=2)
    return (
        f"A fault alert has been received. Diagnose and remediate this fault:\n\n"
        f"```json\n{alert_json}\n```"
    )


def _post_fault_alert(api_base: str, payload: dict[str, Any]) -> dict[str, Any]:
    """POST /fault-alert to the webhook relay."""
    url = f"{api_base.rstrip('/')}/fault-alert"
    print(f"  POST {url}")
    print(f"  Body: {json.dumps(payload, indent=2)}")
    resp = requests.post(url, json=payload, timeout=10)
    resp.raise_for_status()
    return resp.json()  # type: ignore[no-any-return]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Simulate an AD000002 BGP Neighbor Admin Shutdown alert"
    )
    parser.add_argument(
        "--api",
        default=DEFAULT_API,
        help=f"Base URL of the webhook relay (default: {DEFAULT_API})",
    )
    parser.add_argument(
        "--alert-def-id",
        default=DEFAULT_ALERT_DEF_ID,
        help=f"Alert Definition ID (default: {DEFAULT_ALERT_DEF_ID})",
    )
    parser.add_argument(
        "--system",
        default=DEFAULT_SYSTEM,
        help=f"Device hostname (default: {DEFAULT_SYSTEM})",
    )
    parser.add_argument(
        "--device-ip",
        default=DEFAULT_DEVICE_IP,
        help=f"Device management IP (default: {DEFAULT_DEVICE_IP})",
    )
    parser.add_argument(
        "--neighbor-ip",
        default=DEFAULT_NEIGHBOR_IP,
        help=f"BGP neighbor IP (default: {DEFAULT_NEIGHBOR_IP})",
    )
    parser.add_argument(
        "--vrf-name",
        default=DEFAULT_VRF_NAME,
        help=f"VRF name (default: {DEFAULT_VRF_NAME})",
    )
    parser.add_argument(
        "--neighbor-as",
        default=DEFAULT_NEIGHBOR_AS,
        help=f"Neighbor AS number (default: {DEFAULT_NEIGHBOR_AS})",
    )
    parser.add_argument(
        "--time",
        default=DEFAULT_TIME,
        help=f"Splunk _time epoch (default: {DEFAULT_TIME})",
    )
    parser.add_argument(
        "--raw-event",
        default=DEFAULT_RAW_EVENT,
        help="Original syslog line (_raw field)",
    )
    parser.add_argument(
        "--search-name",
        default=DEFAULT_SEARCH_NAME,
        help=f"Splunk saved search name (default: {DEFAULT_SEARCH_NAME})",
    )
    parser.add_argument(
        "--app",
        default=DEFAULT_APP,
        help=f"Splunk app name (default: {DEFAULT_APP})",
    )
    parser.add_argument(
        "--owner",
        default=DEFAULT_OWNER,
        help=f"Splunk search owner (default: {DEFAULT_OWNER})",
    )
    parser.add_argument(
        "--sid",
        default=DEFAULT_SID,
        help="Splunk search ID (default: demo SID)",
    )
    parser.add_argument(
        "--results-link",
        default=DEFAULT_RESULTS_LINK,
        help="Splunk results link URL",
    )
    parser.add_argument(
        "--mode",
        choices=["strict", "hybrid-reasoning"],
        default=DEFAULT_MODE,
        help=f"Remediation mode (default: {DEFAULT_MODE})",
    )
    parser.add_argument(
        "--kb-query-mode",
        choices=["quick", "standard", "deep"],
        default=None,
        help="Override the KB wiki query depth (skill default: standard)",
    )
    parser.add_argument(
        "--direct",
        action="store_true",
        help="Print the prompt for pasting into OpenCode TUI instead of sending to relay",
    )

    args = parser.parse_args()

    payload = _build_alert_payload(
        alert_def_id=args.alert_def_id,
        system=args.system,
        device_ip=args.device_ip,
        neighbor_ip=args.neighbor_ip,
        vrf_name=args.vrf_name,
        neighbor_as=args.neighbor_as,
        time=args.time,
        raw_event=args.raw_event,
        search_name=args.search_name,
        app=args.app,
        owner=args.owner,
        sid=args.sid,
        results_link=args.results_link,
        mode=args.mode,
        kb_query_mode=args.kb_query_mode,
    )

    if args.direct:
        payload["incident_id"] = _generate_incident_id()
        # Print the prompt for headed-mode testing
        print("=" * 60)
        print("  Paste the following into the OpenCode TUI:")
        print("=" * 60)
        print()
        print(_build_prompt(payload, args.mode))
        print()
        return

    # Send to the webhook relay
    print("=" * 60)
    print("  Fault Alert Simulator — AD000002 BGP Admin Shutdown")
    print("=" * 60)
    print(f"  Relay:      {args.api}")
    print(f"  Alert Def:  {args.alert_def_id}")
    print(f"  Device:     {args.system} ({args.device_ip})")
    print(f"  Neighbor:   {args.neighbor_ip} AS {args.neighbor_as} VRF {args.vrf_name}")
    print(f"  Mode:       {args.mode}")
    print(f"  KB query:   {args.kb_query_mode or 'standard (skill default)'}")
    print(f"  Search:     {args.search_name}")
    print()

    print("Submitting fault alert to relay ...")
    try:
        resp = _post_fault_alert(args.api, payload)
    except requests.RequestException as exc:
        print(f"\nERROR: Could not reach the relay at {args.api}: {exc}")
        print("Is the webhook relay running?")
        sys.exit(1)

    print()
    print("=" * 60)
    print("  ACCEPTED")
    print("=" * 60)
    print(f"  Alert Def:  {resp.get('alert_def_id')}")
    print(f"  Incident:   {resp.get('incident_id')}")
    print(f"  Session ID: {resp.get('session_id')}")
    print()
    print("The OpenCode session is now running the remediation workflow.")
    print("Monitor progress in the OpenCode TUI or Webex room.")
    print()


if __name__ == "__main__":
    main()
