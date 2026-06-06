# Adapting to Your Lab

The checked-in configuration is customer-safe and intentionally generic. Use this page to replace demo placeholders with your own OpenCode, RADKit MCP, Splunk, Webex, and device values.

## Configuration Checklist

| Area | File or setting | Required for |
|------|-----------------|--------------|
| OpenCode model provider | `opencode.json` | All agent runs |
| RADKit MCP URL | `opencode.json` and optional `RADKIT_MCP_URL` | Live device diagnostics and remediation |
| OpenCode REST auth | `.env` or shell variables | Headless relay mode |
| Webex bot | `WEBEX_BOT_TOKEN`, `WEBEX_ROOM_ID` | Notifications and approval cards |
| Splunk webhook | Splunk alert action URL | Real alert ingestion |
| Splunk proxy | `SPLUNK_UPSTREAM_URL` | Optional reverse proxy through the relay |
| Device and BGP values | Simulator flags or Splunk result fields | Scenario-specific alerts |

## 1. Configure OpenCode

OpenCode loads agents, skills, model settings, and MCP servers from `opencode.json` at the repository root.

Update the RADKit endpoint:

```json
"radkit": {
  "type": "remote",
  "url": "http://<radkit-mcp-host>:8000/mcp",
  "enabled": true,
  "timeout": 30000
}
```

Keep API credentials as environment variables:

```bash
export CISCO_CLIENT_ID="<client-id>"
export CISCO_CLIENT_SECRET="<client-secret>"
export CISCO_DOCS_API_KEY="<api-key>"
```

If you do not use the optional Cisco support or Cisco docs MCP servers, disable them in `opencode.json`.

For browser-based testing from your workstation, run this from the repository root:

```bash
opencode web
```

Open `http://localhost:4096`. If OpenCode is running on a remote lab host with `opencode serve --port 4096`, open `http://<opencode-host>:4096` from a browser that can reach that host.

## 2. Configure RADKit MCP

RADKit MCP is the live-device access path. Before running a remediation workflow, verify:

Primary prompt for Builder:

```text
Verify my RADKit MCP setup
```

| Check | Why it matters |
|-------|----------------|
| MCP endpoint is reachable from the OpenCode host | OpenCode calls RADKit MCP directly. |
| Device inventory contains the alert hostname | The agent maps `device_hostname` to RADKit inventory. |
| Credentials are scoped to the test devices | The demo can execute `exec_cli` and approved `config_cli` actions. |
| Change controls are understood | The RAW may propose persistent config changes. |

`RADKIT_MCP_URL` in `.env` is only for `/health/deep` smoke checks from the relay. The actual runtime MCP endpoint is the `radkit.url` value in `opencode.json`.

## 3. Configure the Relay

Primary prompt for Builder:

```text
Configure the alert relay for my lab
```

Manual fallback:

For direct Python runs:

```bash
export OPENCODE_URL="http://localhost:4096"
export OPENCODE_SERVER_USERNAME="opencode"
export OPENCODE_SERVER_PASSWORD="<YOUR_SECURE_PASSWORD>"
export REMEDIATION_MODE="strict"
export INGEST_PORT="8080"
python -m app.alert_pipeline
```

For Docker Compose, copy `.env.example` to `.env`, edit it, then run:

```bash
docker compose up --build
```

When OpenCode runs on the Docker host, use:

```bash
OPENCODE_URL=http://host.docker.internal:4096
```

## 4. Configure Webex

Webex is optional for local testing and recommended for a realistic approval flow.

1. Create a Webex bot.
2. Add the bot to the target room.
3. Set `WEBEX_BOT_TOKEN` and `WEBEX_ROOM_ID` in `.env` or the host environment.
4. Restart the relay.

If Webex variables are unset, notification events are skipped and approval-card requests are auto-approved with an explicit warning in the troubleshooting log. That behavior is useful for quick demos; configure Webex when you want a visible human approval step.

## 5. Configure Splunk

Splunk should send a webhook to:

```text
http://<relay-host>:8080/fault-alert
```

The payload must include a top-level `result` object with at least:

| Field | Example | Purpose |
|-------|---------|---------|
| `alert_def_id` | `AD000002` | Selects the artifact group. |
| `system` | `xr-43` | Device hostname for the agent. |
| `device_ip` | `192.0.2.43` | Context carried into `alert_vars`. |
| `neighbor_ip` | `172.20.20.18` | Scenario variable used by the RAW. |
| `vrf_name` | `default` | Scenario variable used by the RAW. |
| `neighbor_as` | `3334` | Scenario variable used by the RAW. |
| `_raw` | syslog text | Evidence and extracted context. |

Use `scripts/splunk-alert-def-generator/` if you want to generate Splunk saved-search definitions from FS YAML.

If a public GitHub Actions runner needs to write saved searches into Splunk, but Splunk is only reachable from the lab network, set `SPLUNK_UPSTREAM_URL` on the relay to the Splunk management URL, for example `https://<splunk-host>:8089`. Then configure the Splunk helper to target the public relay with the `/splunk` base path. The relay forwards those CI writes to Splunk without exposing the Splunk management API directly.

## 6. Run Services Persistently on a Linux Lab Host

For a shared lab, run OpenCode and the relay as long-lived user services on the Linux services host. The examples below use placeholders; keep real passwords and tokens in an environment file that is readable only by the service account.

Primary prompt for Builder:

```text
Create Linux services for OpenCode and the relay
```

Manual fallback:

Create an environment file:

```bash
sudo install -d -m 0750 -o <service-user> -g <service-user> /etc/fault-intelligence-as-code
sudoedit /etc/fault-intelligence-as-code/relay.env
```

Example values:

```bash
OPENCODE_URL=http://127.0.0.1:4096
OPENCODE_SERVER_USERNAME=opencode
OPENCODE_SERVER_PASSWORD=<YOUR_SECURE_PASSWORD>
INGEST_PORT=8080
REMEDIATION_MODE=strict
WEBEX_BOT_TOKEN=<WEBEX_BOT_TOKEN>
WEBEX_ROOM_ID=<WEBEX_ROOM_ID>
SPLUNK_UPSTREAM_URL=https://<splunk-host>:8089
SPLUNK_VERIFY_TLS=false
RADKIT_MCP_URL=http://<radkit-mcp-host>:8000/mcp
```

Example OpenCode service:

```ini
[Unit]
Description=OpenCode fault intelligence server
After=network-online.target
Wants=network-online.target

[Service]
WorkingDirectory=/opt/fault-intelligence-as-code
EnvironmentFile=/etc/fault-intelligence-as-code/relay.env
ExecStart=/usr/local/bin/opencode serve --port 4096
Restart=on-failure
User=<service-user>
Group=<service-user>

[Install]
WantedBy=multi-user.target
```

Example relay service:

```ini
[Unit]
Description=Fault Intelligence alert relay
After=network-online.target opencode.service
Wants=network-online.target

[Service]
WorkingDirectory=/opt/fault-intelligence-as-code
EnvironmentFile=/etc/fault-intelligence-as-code/relay.env
ExecStart=/opt/fault-intelligence-as-code/.venv/bin/python -m app.alert_pipeline
Restart=on-failure
User=<service-user>
Group=<service-user>

[Install]
WantedBy=multi-user.target
```

Install and start the services after adjusting paths and users:

```bash
sudo cp opencode.service /etc/systemd/system/opencode.service
sudo cp fault-relay.service /etc/systemd/system/fault-relay.service
sudo systemctl daemon-reload
sudo systemctl enable --now opencode.service fault-relay.service
sudo systemctl status opencode.service fault-relay.service
```

## 7. Adapt Scenario Values

The simulator defaults to `AD000002`, BGP Neighbor Administrative Shutdown on IOS XR. Override values for your lab:

Primary prompt for Builder:

```text
Adapt AD000002 simulator values to my lab
```

Manual fallback:

```bash
python scripts/simulate_alert.py --direct \
  --system <device-hostname> \
  --device-ip <device-management-ip> \
  --neighbor-ip <bgp-neighbor-ip> \
  --vrf-name <vrf> \
  --neighbor-as <asn>
```

Use documentation IP ranges such as `192.0.2.0/24`, `198.51.100.0/24`, and `203.0.113.0/24` in docs and examples. Use real customer values only in local `.env` files, private Splunk saved searches, or lab-specific runbooks that are not committed.
