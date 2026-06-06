# Headless Mode (Daemon)

Headless mode runs OpenCode as an HTTP server and the FastAPI relay as the alert ingress service. This is the path used when Splunk or the simulator posts an alert to the system.

## Start OpenCode

From the repository root on the host machine:

```bash
export OPENCODE_SERVER_USERNAME="opencode"
export OPENCODE_SERVER_PASSWORD="<YOUR_SECURE_PASSWORD>"
opencode serve --port 4096
```

Verify OpenCode is healthy:

```bash
curl -s -u opencode:$OPENCODE_SERVER_PASSWORD http://localhost:4096/global/health
```

Open the OpenCode web UI at `http://localhost:4096` to inspect sessions and test prompts from a browser. If you are running OpenCode locally without the relay, `opencode web` starts the browser UI from the current repository and uses the same localhost port.

## Start the Relay Directly

Primary prompt for Builder:

```text
Start the alert relay
```

Manual fallback:

In a second terminal:

```bash
export OPENCODE_URL="http://localhost:4096"
export OPENCODE_SERVER_USERNAME="opencode"
export OPENCODE_SERVER_PASSWORD="<YOUR_SECURE_PASSWORD>"
export REMEDIATION_MODE="strict"
export INGEST_PORT="8080"
python -m app.alert_pipeline
```

Verify the relay:

```bash
curl -s http://localhost:8080/health
```

Expected shape:

```json
{
  "status": "ok",
  "opencode_url": "http://localhost:4096",
  "agent": "network-troubleshooter",
  "mode": "strict"
}
```

For dependency checks, use:

```bash
curl -s http://localhost:8080/health/deep
```

## Send an Alert with the Simulator

Primary prompt for Builder:

```text
Send a simulated AD000002 alert
```

Manual fallback:

```bash
python scripts/simulate_alert.py --api http://localhost:8080
```

The simulator posts a Splunk-style alert for `AD000002` and prints the returned OpenCode session ID.

## Send an Alert with Curl

Primary prompt for Builder:

```text
Send a minimal AD000002 curl alert
```

Manual fallback:

The relay expects a top-level `result` object:

```bash
curl -s -X POST http://localhost:8080/fault-alert \
  -H 'Content-Type: application/json' \
  -d '{
    "sid": "scheduler__admin__search__demo_sid",
    "search_name": "ad000002_bgp_neighbor_admin_shutdown_v2",
    "app": "search",
    "owner": "admin",
    "results_link": "http://splunk-server1:8000/app/search/search?q=demo",
    "result": {
      "_time": "1779776665",
      "alert_def_id": "AD000002",
      "system": "xr-43",
      "device_ip": "192.0.2.43",
      "neighbor_ip": "172.20.20.18",
      "vrf_name": "default",
      "neighbor_as": "3334",
      "_raw": "May 26 06:24:25 192.0.2.43 bgp[1090]: %ROUTING-BGP-5-ADJCHANGE : neighbor 172.20.20.18 Down - Admin. shutdown (VRF: default) (AS: 3334)"
    }
  }'
```

Response:

```json
{
  "status": "accepted",
  "incident_id": "INC-20260529T120102Z",
  "alert_def_id": "AD000002",
  "session_id": "ses_..."
}
```

## Webex Approvals

If `WEBEX_BOT_TOKEN` and `WEBEX_ROOM_ID` are set, the relay starts a Webex websocket bot on startup. Approval card clicks arrive over that outbound websocket connection, and the relay forwards the decision to the OpenCode session.

No public inbound Webex webhook endpoint is required. The current relay receives approval decisions through the outbound websocket bot.

## Relay API

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/fault-alert` | Accept a Splunk fault alert, create an OpenCode session, and send the troubleshooting prompt. |
| `GET` | `/sessions` | Return the in-memory `incident_id -> session metadata` map used for approval routing. |
| `GET` | `/health` | Basic process health check. |
| `GET` | `/health/deep` | Checks OpenCode reachability, RADKit MCP HTTP reachability, and Webex credential presence. |
| Any | `/splunk/{path}` | Reverse proxy to `SPLUNK_UPSTREAM_URL` so public GitHub Actions runners can write Splunk saved searches through the relay when lab Splunk is not directly internet-reachable. |

## Monitoring

Watch these places during a headless run:

| Source | What to look for |
|--------|------------------|
| Relay logs | Alert receipt, OpenCode session creation, websocket bot status, approval forwarding. |
| OpenCode session messages | Agent progress and RAW execution output. |
| Webex room | Fault receipt, step progress, approval card, acknowledgement, and final status. |
| `logs/troubleshooting/` | Markdown session log written by `network-troubleshooter`. |
