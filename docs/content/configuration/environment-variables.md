# Environment Variables

The relay and OpenCode runtime are configured through environment variables. Secrets should be provided through the shell, a local `.env` file consumed by Docker Compose, or the host runtime environment.

Use **Builder** to create or check environment configuration. Ask it to collect values without printing secrets back to chat, then keep manual tables on this page as reference.

Primary prompt for Builder:

```text
Configure environment variables for this repository
```

## OpenCode Server

| Variable | Required | Default | Used by | Description |
|----------|----------|---------|---------|-------------|
| `OPENCODE_SERVER_USERNAME` | No | `opencode` | Relay and OpenCode server | Basic-auth username for OpenCode serve. |
| `OPENCODE_SERVER_PASSWORD` | Yes for authenticated OpenCode serve | Empty | Relay and OpenCode server | Basic-auth password for OpenCode serve. If empty, the relay sends no auth. |
| `OPENCODE_URL` | No | `http://localhost:4096` | Relay | Base URL for OpenCode REST API. Docker Compose defaults this to `http://host.docker.internal:4096`. |
| `OPENCODE_AGENT` | No | `network-troubleshooter` | Relay | Agent name sent in `prompt_async` for fault sessions. |

## Relay Runtime

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `INGEST_PORT` | No | `8080` | Port used by `app.alert_pipeline` when run directly. |
| `REMEDIATION_MODE` | No | `strict` | Mode injected into alert prompts: `strict` or `hybrid-reasoning`. |
| `WEBHOOK_SECRET` | No | Empty | If set, `POST /fault-alert` requires `Authorization: Bearer <secret>`. |
| `LOG_LEVEL` | No | `INFO` | Root log level for the relay process. |

## Webex

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `WEBEX_BOT_TOKEN` | No | Empty | Bot token used by `webex-notify` and by the relay websocket bot. |
| `WEBEX_ROOM_ID` | No | Empty | Room used for notifications, approval cards, acknowledgement messages, and websocket room filtering. |
| `WEBEX_API_BASE` | No | `https://webexapis.com/v1` | Webex API base URL used by the relay for person lookup and acknowledgements. |

If Webex credentials are missing, progress messages are skipped and approval cards are treated as auto-approved with a warning in the session log.

## Splunk Proxy

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SPLUNK_UPSTREAM_URL` | No | Empty | Upstream Splunk REST API target for the relay's `/splunk/{path}` reverse proxy. Set this when public GitHub Actions runners need to deploy saved searches through the relay to a lab Splunk instance that is not directly reachable. |
| `SPLUNK_VERIFY_TLS` | No | `false` | Set to `true` to verify the upstream Splunk certificate. |

The proxy exists so CI can write Splunk configuration through the same public relay endpoint used for alerts, without exposing the Splunk management API directly to the internet.

## Health Checks

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `RADKIT_MCP_URL` | No | `http://localhost:8000/mcp` | URL probed by `/health/deep` from the relay network namespace. This is only a smoke test and does not change `opencode.json`. |

The actual RADKit MCP server used by OpenCode is configured in `opencode.json`.

## LLM Providers

The checked-in configuration uses GitHub Copilot. If you switch providers in `opencode.json`, configure the matching provider credential in the OpenCode environment.

| Variable | Provider | Description |
|----------|----------|-------------|
| `GITHUB_TOKEN` | GitHub Copilot | Usually handled by the Copilot/OpenCode authentication path. |
| `ANTHROPIC_API_KEY` | Anthropic | Required only if using an Anthropic model directly. |
| `OPENAI_API_KEY` | OpenAI | Required only if using an OpenAI model. |
| `GOOGLE_API_KEY` | Google | Required only if using a Gemini model. |

## Minimal Headless Example

Primary prompt for Builder:

```text
Start a minimal headless setup
```

Manual fallback:

Terminal 1 starts OpenCode on the host:

```bash
export OPENCODE_SERVER_USERNAME="opencode"
export OPENCODE_SERVER_PASSWORD="<YOUR_SECURE_PASSWORD>"
opencode serve --port 4096
```

Open `http://localhost:4096` for the OpenCode web UI. For local browser-only testing from the repository root, run `opencode web` and use the same localhost URL.

Terminal 2 starts the relay directly:

```bash
export OPENCODE_URL="http://localhost:4096"
export OPENCODE_SERVER_USERNAME="opencode"
export OPENCODE_SERVER_PASSWORD="<YOUR_SECURE_PASSWORD>"
export REMEDIATION_MODE="strict"
export INGEST_PORT="8080"
python -m app.alert_pipeline
```

For Docker Compose, put these values in `.env`; the compose file maps `OPENCODE_URL` to `http://host.docker.internal:4096` by default.