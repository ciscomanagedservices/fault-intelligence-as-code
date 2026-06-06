# Agent Instructions — splunk-alert-def-generator

## Project Overview

This project integrates **Fault Intelligence artifacts** (Fault Signatures, Remediation Guides, Repair Action Workflows) with Splunk. Given an Alert Definition ID (e.g. `AD000002`), it resolves the associated Fault Signature YAML from `intelligence-artifacts/`, converts it into a Splunk alert definition, and deploys it via the Python SDK. Sample integration scripts and an end-to-end test suite are included.

Built for **Cisco Live 2026** presentation demos.

## Architecture

```
Alert Def ID → fs_to_alert.py (resolves FS from intelligence-artifacts/) → alert_config.yml → splunk_alerts.py → Splunk
```

- **fs_to_alert.py** — Takes an AD ID, locates the FS YAML, generates `alert_config.yml` with multi-line SPL (regex + rex + eval + table)
- **splunk_alerts.py** — CRUD operations on Splunk saved searches/alerts via `splunk-sdk`
- **alert_config.yml** — Generated alert definition (maps 1:1 to `savedsearches.conf` fields)
- **Dockerfile** — Minimal wrapper around `splunk/splunk:latest` with license acceptance baked in

## Environment

- **Splunk instance**: ports 8000 (web UI) and 8089 (REST/SDK API)
- **Default target**: `localhost` for local Docker, or a customer-provided Splunk host
- **Credentials**: provide `--password` or `$SPLUNK_PASSWORD`; do not commit real credentials
- **Reverse proxy path**: use `--base-path /splunk` or `$SPLUNK_BASE_PATH=/splunk` when public GitHub Actions runners need to deploy new alert definitions to through the relay to lab Splunk via `SPLUNK_UPSTREAM_URL`
- **Python deps**: `splunk-sdk`, `pyyaml`, `requests`

### Docker Commands (local dev)

```powershell
docker build -t splunk-docker .
docker run -d -p 8000:8000 -p 8089:8089 -e "SPLUNK_PASSWORD=<YOUR_SPLUNK_PASSWORD>" --name splunk splunk-docker
docker start splunk   # restart existing container
docker stop splunk
```

## Key Commands

```powershell
# Generate alert config from an Alert Definition ID
python fs_to_alert.py AD000002
python fs_to_alert.py AD000002 --output alert.yml --index syslog --cron "*/5 * * * *"
python fs_to_alert.py AD000002 --sourcetype cisco:iosxr --webhook-url ""

# Deploy alert to Splunk (remote)
python splunk_alerts.py --host <splunk-host> --create --config alert.yml --password "$SPLUNK_PASSWORD"

# Deploy alert to Splunk through the relay reverse proxy
python splunk_alerts.py --create --config alert.yml --host <relay-hostname> --port 443 --scheme https --base-path /splunk --username admin --password "$SPLUNK_PASSWORD"

# List deployed alerts
python splunk_alerts.py --host <splunk-host> --password "$SPLUNK_PASSWORD"

# Delete an alert
python splunk_alerts.py --host <splunk-host> --delete --config alert.yml --password "$SPLUNK_PASSWORD"

# Generate a config, then create it through a public relay endpoint
python fs_to_alert.py AD000002 --output ad000002-relay.yml --webhook-url https://<relay-hostname>/fault-alert
python splunk_alerts.py --create --config ad000002-relay.yml --host <relay-hostname> --port 443 --scheme https --base-path /splunk --username admin --password "$SPLUNK_PASSWORD"

# End-to-end test (requires accessible Splunk instance)
python tests/test_alert_deployment.py
```

## Generated SPL Format

```spl
index=syslog sourcetype=cisco:ios "ROUTING-BGP-5-ADJCHANGE"
| regex _raw="%ROUTING-BGP-5-ADJCHANGE\\s*...doubled backslashes..."
| rex field=_raw "%ROUTING-BGP-5-ADJCHANGE\s*...(?<neighbor_ip>\S+)...named groups..."
| eval alert_def_id="AD000002"
| table _time host alert_def_id neighbor_ip vrf_name neighbor_as _raw
```

## Alert Defaults

| Setting | Value |
|---------|-------|
| Trigger | `number of events > 0` |
| Digest mode | Off (per-result) |
| Alert expiry | 7 days |
| Suppression | Per `host`, 1 hour |
| Webhook | `http://localhost:8080/fault-alert` |

## Conventions

- Alert configs use YAML with keys mapping directly to Splunk `savedsearches.conf` fields
- The `name` field is `<ad_id>_<fs_name>` lowercased (e.g. `ad000002_bgp_neighbor_admin_shutdown`)
- Only `syslog` event types from fault signatures are supported; others are skipped with a warning
- SPL uses `sourcetype=cisco:ios` (configurable via `--sourcetype`) and a quoted mnemonic phrase for filtering
- `| regex` uses doubled backslashes (Splunk eval-string escaping); `| rex` uses single backslashes with named groups
- Every SPL includes `| eval alert_def_id="<AD-ID>"` for downstream correlation
- Severity mapping: CRITICAL→5, MAJOR→4, WARNING→3, MINOR→2, UNKNOWN→1
- Webhook URL defaults to the fault-alert relay; disable with `--webhook-url ""`

## Reference Docs

- [docs/ALERT_PARAMETERS.md](docs/ALERT_PARAMETERS.md) — Full reference of Splunk alert/saved-search parameters
- [docs/SPLUNK_API.md](docs/SPLUNK_API.md) — Python SDK and REST API usage examples
- [docs/notes.md](docs/notes.md) — MCP server config and operational notes
- [examples/alert_config.yml](examples/alert_config.yml) — Example alert config (generated from AD000002)
