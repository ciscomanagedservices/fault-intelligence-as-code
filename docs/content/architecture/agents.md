# Agent Architecture

OpenCode agents are part of the repository and live under `.opencode/agents/`. The runtime is split into read-only live troubleshooting agents and write-capable curator agents.

For general repository setup, file edits, local configuration, service startup, and troubleshooting, use OpenCode's default **Builder** agent. Use the specialized project agents only when the task matches their workflow.

## Which Agent Should I Use?

| Task | Agent |
|------|-------|
| Install/check local setup, edit `.env`, customize docs, or run utility commands | Builder |
| Run a live fault workflow or RAW test bundle | `network-troubleshooter` |
| Create, research, optimize, test, or publish FS/RAW/RG artifacts | `ia-curator` |
| Query, ingest, save, or lint KB vault content | `kb-curator` |
| Read existing intelligence artifacts without changing them | `ia-reader` |
| Read KB context without changing it | `kb-reader` |

The most important boundary is simple: live fault sessions use `network-troubleshooter`; authoring and maintenance use curator agents. `network-troubleshooter` must not write repository content or call curator agents.

## Runtime Agents

| Agent | Mode | Live fault role | Write access | Skills |
|-------|------|-----------------|--------------|--------|
| `network-troubleshooter` | primary | Orchestrates diagnosis and remediation against live devices. | No | `fault-remediation`, `webex-notify` |
| `ia-reader` | primary / sub-agent | Finds and returns FS, RAW, and RG artifacts from `intelligence-artifacts/`. | No | None |
| `kb-reader` | primary / sub-agent | Queries the KB wiki vault at `kb/wiki/`. | No | `wiki-query` |

`network-troubleshooter` is the only agent selected by the relay for live sessions. It delegates artifact loading to `ia-reader`, KB retrieval to `kb-reader`, RAW execution to `fault-remediation`, and Webex rendering/sending to `webex-notify`.

## Curator Agents

| Agent | Purpose | Write scope | Skills |
|-------|---------|-------------|--------|
| `ia-curator` | Create, research, optimize, and publish fault intelligence artifacts. | `ia-drafts/`, `intelligence-artifacts/` | `ia-start`, `ia-research`, `ia-create`, `ia-optimize`, `ia-publish`, `ia-explorer` |
| `kb-curator` | Add sources, lint, save, and maintain the KB wiki vault. | `kb/` | `wiki-query`, `wiki-ingest`, `wiki-lint`, `save`, `wiki`, `obsidian-markdown` |

Curator agents are human-initiated authoring tools. They are deliberately excluded from the live fault path.

## Defence in Depth

Agent separation is enforced in two places:

| Layer | What it controls |
|-------|------------------|
| `opencode.json` | Top-level tool allow-lists by agent name. For example, `network-troubleshooter` allows `radkit_*`, while reader and curator agents deny it. |
| Agent frontmatter | Per-agent permissions for skills, tasks, file edits, web access, shell access, and MCP tools. |

The important hard rule is that `network-troubleshooter` cannot invoke `kb-curator` or `ia-curator`. There is no path from a live remediation session to a repository write.

## Network Troubleshooter Responsibilities

During a live alert, `network-troubleshooter` does the surrounding orchestration that the RAW interpreter should not own:

1. Receives the normalized alert payload.
2. Creates a Markdown session log in `logs/troubleshooting/<UTC>-<alert_def_id>-<device>.md`.
3. Calls `ia-reader` to load the FS/RAW/RG artifact block.
4. Calls `kb-reader` to retrieve business rules and fault context.
5. Invokes `webex-notify` for fault receipt and progress notifications.
6. Invokes `fault-remediation` to execute the RAW.
7. Requests Webex approval before `config_cli` actions.
8. Resumes the workflow when the relay forwards an operator decision.
9. Sends final resolution, escalation, failure, or denial notifications.

The agent is explicitly forbidden from using an interactive ask-questions pause during a workflow. Missing information is treated as an escalation condition.

## Reader Agent Contracts

`ia-reader` returns a structured YAML block with artifact paths and full FS/RAW content for the matched alert definition. It can match by `alert_def_id` or by regex-matching supplied event text against Fault Signature patterns.

`kb-reader` returns a structured YAML block containing operational context such as severity level, response SLA, approval requirements, escalation path, known-issue matches, incident matches, pages read, and the query mode used.

These structured returns keep the parent agent grounded without granting it write privileges.