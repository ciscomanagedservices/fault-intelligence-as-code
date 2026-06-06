# Lab Environment Quickstart

Use this quickstart after the local OpenCode agent test works. It shows the order for connecting the demo to your own OpenCode host, RADKit MCP endpoint, Splunk alerting, and optional Webex approvals.

For the full reference, see [Adapting to Your Lab](../operations/adapting-to-your-lab.md).

Use **Builder** for setup and file changes in this quickstart. Use `network-troubleshooter` only when you are ready to run a fault workflow.

## 1. Start from a Clean Local Run

Before connecting lab services, verify the local prompt path with [Local Agent Prompt Test](local-agent-test.md).

## 2. Configure OpenCode and RADKit MCP

OpenCode reads agent, skill, model, and MCP settings from `opencode.json` in the repository root. Update the RADKit MCP endpoint:

Primary prompt for Builder:

```text
Configure RADKit MCP for my lab
```

Manual fallback:

```json
"radkit": {
  "type": "remote",
  "url": "http://<radkit-mcp-host>:8000/mcp",
  "enabled": true,
  "timeout": 30000
}
```

Verify the OpenCode host can reach RADKit MCP and that RADKit inventory contains the device hostname sent in alert payloads.

## 3. Configure Runtime Environment

Copy the template and fill in local values:

Primary prompt for Builder:

```text
Configure .env for the relay
```

Manual fallback:

```bash
cp .env.example .env
```

Minimum relay settings:

```bash
OPENCODE_URL=http://localhost:4096
OPENCODE_SERVER_USERNAME=opencode
OPENCODE_SERVER_PASSWORD=<YOUR_SECURE_PASSWORD>
INGEST_PORT=8080
REMEDIATION_MODE=strict
RADKIT_MCP_URL=http://<radkit-mcp-host>:8000/mcp
```

`RADKIT_MCP_URL` is only used by the relay health check. The agent runtime uses the `mcp.radkit.url` value in `opencode.json`.

## 4. Start OpenCode and the Relay

Terminal 1:

```bash
export OPENCODE_SERVER_USERNAME="opencode"
export OPENCODE_SERVER_PASSWORD="<YOUR_SECURE_PASSWORD>"
opencode serve --port 4096
```

Open `http://localhost:4096` to inspect sessions in the web UI.

Terminal 2:

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
curl -s http://localhost:8080/health/deep
```

## 5. Connect Splunk

Configure Splunk alerts to send webhooks to:

Primary prompt for Builder:

```text
Connect Splunk to this demo
```

Manual fallback:

```text
http://<relay-host>:8080/fault-alert
```

Use the Splunk alert generator when you want to derive saved searches from FS YAML:

```bash
cd scripts/splunk-alert-def-generator
python fs_to_alert.py AD000002 --repo-root ../.. --webhook-url http://<relay-host>:8080/fault-alert --output ad000002.yml
python splunk_alerts.py --create --config ad000002.yml --password "$SPLUNK_PASSWORD"
```

If public GitHub Actions runners need to write saved searches into a lab Splunk instance that is not directly reachable, set `SPLUNK_UPSTREAM_URL` on the relay and point the Splunk helper at the public relay with `--base-path /splunk`.

## 6. Add Webex Approvals

Webex is optional but useful for a realistic approval flow.

1. Create a Webex bot.
2. Add the bot to the target room.
3. Set `WEBEX_BOT_TOKEN` and `WEBEX_ROOM_ID` in `.env` or the host environment.
4. Restart the relay.

When Webex is unset, notification events are skipped and approval requests are auto-approved with an explicit warning in the troubleshooting log.

## 7. Send a Lab Alert

Primary prompt for `network-troubleshooter` when you want a direct agent run:

```text
Diagnose fault AD000002 on <device-hostname> in strict mode using the lab configuration. Use RADKit MCP for device access and request approval before any config action.
```

Primary prompt for Builder when you want to use the relay/simulator path:

```text
Send a simulated AD000002 alert
```

Manual fallback:

Use the simulator against the relay first:

```bash
python scripts/simulate_alert.py --api http://localhost:8080 --mode strict
```

Then trigger the Splunk saved search and watch the OpenCode web UI, relay logs, optional Webex room, and `logs/troubleshooting/`.

## 8. Keep Lab-Specific Values Out of Git

Use documentation IP ranges in committed examples. Put real hostnames, addresses, passwords, tokens, room IDs, and tunnel URLs only in local `.env` files, private runbooks, or runtime secret stores.
