# Fault Intelligence Artifacts + Splunk Integration

This project demonstrates how to take Fault Intelligence artifacts, such as Fault Signatures, and integrate them with Splunk as automated alert definitions. It includes scripts for the integration pipeline and an end-to-end test suite backed by a local Splunk Docker image.

Built for **Cisco Live 2026** presentation demos.

---

## Prerequisites

| Requirement | Notes |
|-------------|-------|
| **Docker** | Required to run Splunk locally. [Install Docker Desktop](https://www.docker.com/products/docker-desktop/) |
| **Python 3.9+** | Required to run `fs_to_alert.py` and `splunk_alerts.py` |
| **Python dependencies** | `pip install -r requirements.txt` — installs `splunk-sdk`, `pyyaml`, `requests` |
| **Node.js + npx** | Optional — only needed for the Splunk MCP server integration (see [MCP Setup](#optional-splunk-mcp-server)) |

---

## Architecture

```
Fault Signature YAML → fs_to_alert.py (by AD ID) → alert_config.yml → splunk_alerts.py → Splunk
```

---

## 1. Start Splunk

### Option A — Build and run the custom image (recommended)

```powershell
docker build -t splunk-docker .
docker run -d -p 8000:8000 -p 8089:8089 -e "SPLUNK_PASSWORD=<YOUR_SPLUNK_PASSWORD>" --name splunk splunk-docker
```

### Option B — Run the upstream image directly

```powershell
docker run -d -p 8000:8000 -p 8089:8089 `
  -e "SPLUNK_START_ARGS=--accept-license" `
  -e "SPLUNK_GENERAL_TERMS=--accept-sgt-current-at-splunk-com" `
  -e "SPLUNK_PASSWORD=<YOUR_SPLUNK_PASSWORD>" `
  --name splunk splunk/splunk:latest
```

### Restart / stop an existing container

```powershell
docker start splunk   # restart
docker stop splunk    # stop
```

Once running, the Splunk Web UI is at [http://localhost:8000](http://localhost:8000). Log in as `admin` with the password you supplied in `SPLUNK_PASSWORD`.

---

## 2. Install Python dependencies

```powershell
pip install -r requirements.txt
```

---

## 3. Convert a Fault Signature to a Splunk alert config

`fs_to_alert.py` takes an Alert Definition ID (e.g. `AD000002`), locates the
associated Fault Signature YAML under `intelligence-artifacts/`, and generates
an `alert_config.yml` consumable by `splunk_alerts.py`.

```powershell
# Basic — resolves FS from intelligence-artifacts/AD000002-*/FS*.yml
python fs_to_alert.py AD000002

# Specify output file, target index, and schedule
python fs_to_alert.py AD000002 `
  --output my_alert.yml `
  --index syslog `
  --cron "*/5 * * * *"

# Override sourcetype (default: cisco:ios)
python fs_to_alert.py AD000002 --sourcetype cisco:iosxr

# Override webhook URL (default: http://localhost:8080/fault-alert)
python fs_to_alert.py AD000002 --webhook-url http://myhost:8080/fault-alert

# Disable webhook action entirely
python fs_to_alert.py AD000002 --webhook-url ""

# Use a different repo root
python fs_to_alert.py AD000002 --repo-root /path/to/fault-mgmt-as-code
```

**Generated SPL format:**

The generated search uses the following multi-line format:

```spl
index=syslog sourcetype=cisco:ios "ROUTING-BGP-5-ADJCHANGE"
| regex _raw="%ROUTING-BGP-5-ADJCHANGE\\s*:\\s*neighbor\\s+(\\S+)..."
| rex field=_raw "%ROUTING-BGP-5-ADJCHANGE\s*:\s*neighbor\s+(?<neighbor_ip>\S+)..."
| eval alert_def_id="AD000002"
| table _time host alert_def_id neighbor_ip vrf_name neighbor_as _raw
```

- `| regex` guards extraction (backslashes doubled for Splunk eval-string parsing)
- `| rex` extracts named fields from the FS `evaluation.parameters`
- `| eval alert_def_id` tags every result with the source Alert Definition
- `| table` projects key fields for downstream consumption

**Alert defaults:**

| Setting | Default |
|---------|--------|
| Trigger | `number of events > 0` |
| Digest mode | Off (per-result) |
| Alert expiry | 7 days |
| Suppression | Per `host`, 1 hour |
| Webhook | `http://localhost:8080/fault-alert` |
| Severity | Mapped from FS metadata |

**Notes:**
- Only `syslog` event types are supported; other types are skipped with a warning.
- Severity mapping: `CRITICAL`→5, `MAJOR`→4, `WARNING`→3, `MINOR`→2, `UNKNOWN`→1.
- See [examples/alert_config.yml](examples/alert_config.yml) for the output format.

---

## 4. Deploy alerts to Splunk

`splunk_alerts.py` performs CRUD operations on Splunk saved searches/alerts via the Python SDK. It targets `localhost:8089` with username `admin` by default and requires a password through `--password` or `SPLUNK_PASSWORD`.

Connection settings can be overridden via CLI flags or environment variables:

| Flag | Env var | Default |
|------|---------|---------|
| `--host` | `SPLUNK_HOST` | `127.0.0.1` |
| `--port` | `SPLUNK_PORT` | `8089` |
| `--username` | `SPLUNK_USERNAME` | `admin` |
| `--password` | `SPLUNK_PASSWORD` | Required |
| `--scheme` | `SPLUNK_SCHEME` | `https` |
| `--base-path` | `SPLUNK_BASE_PATH` | `` |

### List all deployed alerts

```powershell
python splunk_alerts.py --password "$env:SPLUNK_PASSWORD"
```

### Create an alert from a config file

```powershell
# From the default examples/alert_config.yml
python splunk_alerts.py --create --password "$env:SPLUNK_PASSWORD"

# From a generated or custom config
python splunk_alerts.py --create --config my_alert.yml --password "$env:SPLUNK_PASSWORD"

# Against a remote Splunk instance
python splunk_alerts.py --host <splunk-host> --create --config my_alert.yml --password "$env:SPLUNK_PASSWORD"

# Against Splunk exposed through the relay reverse proxy
python splunk_alerts.py `
  --create `
  --config my_alert.yml `
  --host <relay-hostname> `
  --port 443 `
  --scheme https `
  --base-path /splunk `
  --username admin `
  --password "$env:SPLUNK_PASSWORD"
```

If the alert already exists it is skipped (idempotent).

Use `--base-path /splunk` when public GitHub Actions runners or remote operators need to write alert definitions through the FastAPI relay to a lab Splunk instance that is not directly reachable on port 8089.

### Generate an alert config, then create it through the public relay

This is the full workflow for generating the alert config and then issuing the create request through a public relay endpoint. The relay forwards `/splunk` requests to `SPLUNK_UPSTREAM_URL` inside the lab network.

```powershell
# 1. Generate the Splunk alert config from the published AD/FS artifacts
python fs_to_alert.py AD000002 `
  --output ad000002-relay.yml `
  --webhook-url https://<relay-hostname>/fault-alert

# 2. Create the saved search through the relay's /splunk reverse proxy
python splunk_alerts.py `
  --create `
  --config ad000002-relay.yml `
  --host <relay-hostname> `
  --port 443 `
  --scheme https `
  --base-path /splunk `
  --username admin `
  --password "$env:SPLUNK_PASSWORD"
```

To remove that alert later, reuse the same config file with `--delete`:

```powershell
python splunk_alerts.py `
  --delete `
  --config ad000002-relay.yml `
  --host <relay-hostname> `
  --port 443 `
  --scheme https `
  --base-path /splunk `
  --username admin `
  --password "$env:SPLUNK_PASSWORD"
```

### Delete an alert

```powershell
python splunk_alerts.py --delete --config my_alert.yml --password "$env:SPLUNK_PASSWORD"
```

---

## 5. Full end-to-end demo (single command)

The test suite in `tests/test_alert_deployment.py` runs the complete pipeline automatically:

1. Generates an alert config from alert definition AD000002
2. Deploys the alert to Splunk
3. Lists all alerts to confirm deployment
4. Cleans up by deleting the alert

```powershell
python tests/test_alert_deployment.py
```

> **Requires a running Splunk instance** on `localhost:8089` (or set `SPLUNK_HOST`) before running.

---

## Reference

| File | Purpose |
|------|---------|
| [fs_to_alert.py](fs_to_alert.py) | Convert Alert Definition (AD ID) → `alert_config.yml` |
| [splunk_alerts.py](splunk_alerts.py) | Create / list / delete Splunk alerts via SDK |
| [examples/alert_config.yml](examples/alert_config.yml) | Example alert config (generated from AD000002) |
| [docs/ALERT_PARAMETERS.md](docs/ALERT_PARAMETERS.md) | Full Splunk alert parameter reference |
| [docs/SPLUNK_API.md](docs/SPLUNK_API.md) | Python SDK and REST API usage examples |
| [tests/test_alert_deployment.py](tests/test_alert_deployment.py) | End-to-end integration test |

---

## Optional: Splunk MCP Server

The Splunk MCP server lets you query Splunk directly from a Copilot / agent session via the Model Context Protocol. It is **not required** for the alert integration scripts.

### Prerequisites

1. **Install the Splunk MCP Server app** on your Splunk instance:  
   ([docs](https://help.splunk.com/en/splunk-cloud-platform/mcp-server-for-splunk-platform/1.1/configure-the-splunk-mcp-server))

2. **Enable token authentication** in Splunk:  
   Settings → Tokens → Enable Token Auth  
   ([docs](https://help.splunk.com/en/splunk-cloud-platform/administer/manage-users-and-security/10.3.2512/authenticate-into-the-splunk-platform-with-tokens/enable-or-disable-token-authentication))

3. **Generate a token** for the `admin` user and copy it — you'll be prompted for it when the MCP server connects.

4. **Node.js** must be installed so `npx` is available.

### VS Code `mcp.json` configuration

Add to your MCP server list (e.g. `.vscode/mcp.json`):

```jsonc
{
  "servers": {
    "splunk-mcp-server": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://127.0.0.1:8089/services/mcp",
        "--header",
        "Authorization: Bearer ${input:splunk_token}"
      ],
      "type": "stdio",
      "env": {
        "NODE_TLS_REJECT_UNAUTHORIZED": "0"
      }
    }
  },
  "inputs": [
    {
      "id": "splunk_token",
      "type": "promptString",
      "description": "Splunk API Token",
      "password": true
    }
  ]
}
```

- Connects via `mcp-remote` to `https://127.0.0.1:8089/services/mcp`
- Authenticates with your Splunk API token (prompted at connect time)
- `NODE_TLS_REJECT_UNAUTHORIZED=0` bypasses the self-signed cert on the local container
