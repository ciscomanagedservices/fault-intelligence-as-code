# Troubleshooting

Use this checklist when the local demo, relay, OpenCode, RADKit MCP, Webex, or Splunk integration does not behave as expected.

Use Opencode **Builder** agent for setup and service diagnostics. Use `network-troubleshooter` for a direct fault run or RAW test-bundle run. Use `ia-curator` for artifact/test authoring issues and `kb-curator` for KB vault issues.

Primary prompt for Builder:

```text
Troubleshoot my local setup
```

## Fast Triage

| Symptom | First check | Likely fix |
|---------|-------------|------------|
| Simulator prints a prompt but agent cannot find artifacts | `alert_def_id` in prompt | Use a published artifact group under `intelligence-artifacts/`. |
| Relay returns 401 | `WEBHOOK_SECRET` and `Authorization` header | Send `Authorization: Bearer <secret>` or unset `WEBHOOK_SECRET` for local testing. |
| Relay cannot create OpenCode session | `OPENCODE_URL` and OpenCode auth | Start `opencode serve` and match `OPENCODE_SERVER_PASSWORD`. |
| `/health/deep` reports RADKit unreachable | `RADKIT_MCP_URL` | Set it to a URL reachable from the relay network namespace. |
| Agent cannot call RADKit tools | `opencode.json` MCP config | Update `mcp.radkit.url` and verify OpenCode can reach it. |
| No Webex messages | `WEBEX_BOT_TOKEN`, `WEBEX_ROOM_ID` | Add the bot to the room, set env vars, restart relay. |
| Webex approval does not reach agent | Relay logs and `/sessions` | Confirm the active incident exists and the websocket bot started. |
| Splunk webhook does nothing | Splunk alert action URL | Point it at `http://<relay-host>:8080/fault-alert`. |
| Splunk proxy returns 503 | `SPLUNK_UPSTREAM_URL` | Set the upstream Splunk management URL when CI or remote operators need `/splunk/` writes through the relay; otherwise avoid `/splunk/` routes. |

## OpenCode Checks

Start headed mode first when possible:

```bash
opencode
python scripts/simulate_alert.py --direct --mode strict
```

For headless mode, verify the server:

```bash
curl -s -u opencode:$OPENCODE_SERVER_PASSWORD http://localhost:4096/global/health
```

If this fails:

1. Confirm `opencode serve --port 4096` is running.
2. Confirm the username and password match the relay environment.
3. Confirm the host and port match `OPENCODE_URL`.
4. Try headed mode to separate OpenCode/provider auth from relay issues.

## Relay Checks

Start the relay directly while troubleshooting so logs are visible:

Primary prompt for Builder:

```text
Start the relay and check health
```

Manual fallback:

```bash
python -m app.alert_pipeline
```

Basic health:

```bash
curl -s http://localhost:8080/health
```

Dependency health:

```bash
curl -s http://localhost:8080/health/deep
```

`/health/deep` checks OpenCode, an optional RADKit MCP URL, and whether Webex credentials are present. It does not prove that OpenCode is using the same RADKit endpoint; OpenCode reads that from `opencode.json`.

## RADKit MCP Checks

When the agent cannot execute device commands:

1. Confirm the `radkit` MCP server is enabled in `opencode.json`.
2. Confirm the URL is reachable from the OpenCode host.
3. Confirm the target device hostname in the alert matches RADKit inventory.
4. Confirm credentials permit the requested `exec_cli` or approved `config_cli` action.
5. Review the OpenCode session for MCP tool errors.

## Webex Checks

The relay uses an outbound Webex websocket bot for approval-card callbacks.

Check these items:

| Check | Expected |
|-------|----------|
| `WEBEX_BOT_TOKEN` | Set to the bot token in the relay environment. |
| `WEBEX_ROOM_ID` | Set to the room where cards should appear. |
| Bot membership | Bot is a member of the room. |
| Relay logs | Websocket bot starts without auth errors. |
| `/sessions` | Active incident appears after a fault alert. |

If Webex is unset, approval requests are skipped and auto-approved with a warning. That is acceptable for local demos only.

## Splunk Checks

The relay expects Splunk-shaped JSON with a top-level `result` object.

Primary prompt for Builder:

```text
Validate Splunk alert integration
```

Minimal test:

```bash
python scripts/simulate_alert.py --api http://localhost:8080 --mode strict
```

If Splunk is used directly:

1. Confirm the alert action URL is `http://<relay-host>:8080/fault-alert`.
2. Confirm the saved search emits `alert_def_id`, `system`, and scenario variables.
3. Confirm network access from Splunk to the relay.
4. If `WEBHOOK_SECRET` is set, configure the matching `Authorization` header.

## Docker Checks

Docker Compose runs only the relay. OpenCode must be reachable separately.

Primary prompt for Builder:

```text
Troubleshoot Docker relay setup
```

Common Docker values:

```bash
OPENCODE_URL=http://host.docker.internal:4096
RADKIT_MCP_URL=http://host.docker.internal:8000/mcp
```

Validate Compose configuration:

```bash
docker compose config
```

Check container health:

```bash
docker compose ps
curl -s http://localhost:8080/health
```

## Logs

| Source | Location |
|--------|----------|
| Relay process | Terminal output or container logs. |
| OpenCode session | OpenCode TUI or server session view. |
| Agent session log | `logs/troubleshooting/<UTC>-<alert_def_id>-<device>.md`. |
| RAW test output | `out/results.xml` and `out/summary.md` when requested. |

Session logs are runtime artifacts and should not be committed.
