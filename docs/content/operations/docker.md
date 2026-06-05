# Docker Deployment

The Docker container runs only the FastAPI webhook relay. OpenCode still runs on the host machine or another service, because it owns the model runtime, agents, skills, and MCP connections.

Use **Builder** to help prepare `.env`, validate Docker Compose, and start the relay. The commands below are fallback/reference.

## Compose Service

`docker-compose.yml` defines one service:

| Service | Container | Purpose |
|---------|-----------|---------|
| `relay` | `alert-pipeline` | Runs `python -m app.alert_pipeline` and publishes port 8080. |

Start it from the repository root:

Primary prompt for Builder:

```text
Run the relay with Docker Compose
```

Manual fallback:

```bash
docker compose up --build
```

The compose file maps `8080:8080`, loads `.env`, and sets `OPENCODE_URL` to `http://host.docker.internal:4096` by default so the container can reach an OpenCode server running on the host.

## Example `.env`

Primary prompt for Builder:

```text
Configure the Docker .env file
```

Reference values:

```bash
OPENCODE_URL=http://host.docker.internal:4096
OPENCODE_SERVER_USERNAME=opencode
OPENCODE_SERVER_PASSWORD=<YOUR_SECURE_PASSWORD>
REMEDIATION_MODE=strict
WEBHOOK_SECRET=
WEBEX_BOT_TOKEN=
WEBEX_ROOM_ID=
SPLUNK_UPSTREAM_URL=
SPLUNK_VERIFY_TLS=false
RADKIT_MCP_URL=http://host.docker.internal:8000/mcp
```

Leave `SPLUNK_UPSTREAM_URL` empty unless public GitHub Actions runners or remote operators need to write Splunk saved searches through the relay to a lab Splunk management endpoint.

Add Webex values when you want notification and approval-card integration.

## Host OpenCode Server

Start OpenCode on the host before sending alerts to the relay:

```bash
export OPENCODE_SERVER_USERNAME="opencode"
export OPENCODE_SERVER_PASSWORD="<YOUR_SECURE_PASSWORD>"
opencode serve --port 4096
```

Then start the container:

```bash
docker compose up --build
```

Check the relay from the host:

```bash
curl -s http://localhost:8080/health
curl -s http://localhost:8080/health/deep
```

## What Is in the Image

The `Dockerfile` uses `python:3.12-slim`, installs `curl`, installs the project from `pyproject.toml`, copies `app/`, and sets:

```text
ENTRYPOINT ["python", "-m"]
CMD ["app.alert_pipeline"]
```

It does not copy or run OpenCode. The relay talks to OpenCode over HTTP.