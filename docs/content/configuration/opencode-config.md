# OpenCode Configuration

OpenCode configuration lives in `opencode.json` at the repository root. It selects the model provider, defines agent-level tool allow-lists, and connects the MCP servers used by the project. The checked-in file is safe to publish and uses placeholders for sensitive values; put real credentials in your environment, not in JSON.

Use **Builder** to inspect or adapt `opencode.json`. Ask it to keep credentials in environment variables and to preserve the agent safety boundaries described below.

Primary prompt for Builder:

```text
Review opencode.json for my lab
```

## Current Shape

The current repository configuration uses GitHub Copilot as the model provider and pins the primary model to Claude Sonnet through Copilot:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "github-copilot/claude-sonnet-4.6",
  "enabled_providers": ["github-copilot"],
  "agent": {
    "network-troubleshooter": {
      "tools": { "radkit_*": true }
    },
    "kb-reader": {
      "tools": { "radkit_*": false }
    },
    "kb-curator": {
      "tools": { "radkit_*": false }
    },
    "ia-reader": {
      "tools": { "radkit_*": false }
    },
    "ia-curator": {
      "tools": { "radkit_*": false }
    }
  },
  "mcp": {
    "radkit": {
      "type": "remote",
      "url": "http://localhost:8000/mcp",
      "enabled": true,
      "timeout": 30000
    },
    "cisco-support": {
      "type": "local",
      "command": ["npx", "-y", "mcp-cisco-support@latest"],
      "enabled": true
    }
  }
}
```

The RADKit URL is a placeholder. Change it to match your own RADKit MCP endpoint before live remediation.

## Model and Provider

| Field | Current value | Purpose |
|-------|---------------|---------|
| `model` | `github-copilot/claude-sonnet-4.6` | Default model used by OpenCode unless an agent overrides it. |
| `enabled_providers` | `github-copilot` | Restricts model use to the Copilot provider in this demo repo. |

The agent frontmatter also pins the model for each agent. For example, `network-troubleshooter`, `kb-reader`, `ia-reader`, `kb-curator`, and `ia-curator` all currently specify `github-copilot/claude-sonnet-4.6`.

## Agent Tool Allow-Lists

The `agent` block provides a second permission layer on top of each agent file's frontmatter.

| Agent | `radkit_*` access | Why |
|-------|-------------------|-----|
| `network-troubleshooter` | Allowed | This is the only live remediation agent that should execute device commands. |
| `kb-reader` | Denied | KB reading must not touch network devices. |
| `kb-curator` | Denied | KB maintenance is repository work, not live operations. |
| `ia-reader` | Denied | Artifact lookup is read-only repository work. |
| `ia-curator` | Denied | Artifact authoring does not require live device access. |

See the [Agent Architecture](../architecture/agents.md) page for the full role split and task permissions.

## MCP Servers

| Server | Type | Used by | Purpose |
|--------|------|---------|---------|
| `radkit` | Remote streamable HTTP | Live remediation | Provides CLI access to Cisco network devices through RADKit MCP tools. |
| `cisco-support` | Local command (`npx mcp-cisco-support@latest`) | Author-time artifact work | Provides Cisco support data to intelligence-artifact research and curator workflows. |

OpenCode exposes tools with the server name as a prefix. RADKit tools therefore appear to agents as `radkit_*` tools.

## Updating for Another Lab

For a different environment, the most common change is the RADKit endpoint:

Primary prompt for Builder:

```text
Update the RADKit MCP endpoint
```

Manual fallback:

```json
{
  "mcp": {
    "radkit": {
      "type": "remote",
      "url": "http://<radkit-host>:8000/mcp",
      "enabled": true,
      "timeout": 30000
    }
  }
}
```

Keep the timeout at 30000 ms or higher. CLI operations often take longer than OpenCode's short default request timeout.

## Running OpenCode

Headed mode starts the TUI:

```bash
opencode
```

Headless mode starts the REST server consumed by the relay:

```bash
export OPENCODE_SERVER_USERNAME="opencode"
export OPENCODE_SERVER_PASSWORD="<YOUR_SECURE_PASSWORD>"
opencode serve --port 4096
```

Open `http://localhost:4096` to use the OpenCode web UI for session inspection and prompt testing. If you only want the local browser UI from this repository, run `opencode web` from the repo root and open the localhost URL it prints.

The relay uses `OPENCODE_URL`, `OPENCODE_SERVER_USERNAME`, and `OPENCODE_SERVER_PASSWORD` to create sessions and send `prompt_async` messages.