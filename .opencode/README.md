# OpenCode Agents

These files define the agents used by the demo/reference implementation.

For general repository setup, file edits, local configuration, service startup, and troubleshooting, use OpenCode's default **Builder** agent. Use the project-specific agents below when the task belongs to a specialized workflow.

## Task-to-Agent Map

| If you want to... | Use this agent | Example prompt |
|-------------------|----------------|----------------|
| Install/check local setup, edit `.env`, customize docs, or run utility commands | Builder | `Help me adapt this repository to my lab. Ask for values, keep secrets out of chat, and summarize each change.` |
| Run a live or simulated fault workflow | `network-troubleshooter` | `Run the RAW test bundle for AD000002 in test mode using the checked-in test bundle.` |
| Create, research, optimize, test, or publish FS/RAW/RG artifacts | `ia-curator` | `Create a new fault-intelligence scenario from this syslog and draft the RG first.` |
| Query, ingest, save, or lint KB vault content | `kb-curator` | `Ingest this source into the KB vault and update the hot cache and index.` |
| Read existing intelligence artifacts without changing them | `ia-reader` | `Find the artifact group for AD000002 and summarize the FS and RAW.` |
| Read KB context without changing it | `kb-reader` | `Query quick: what business rules apply to BGP remediation?` |

Do not use `network-troubleshooter` for repository edits, artifact authoring, or KB writes. It is intentionally read-only with respect to the repository.

| Agent | Use | Live device access |
|-------|-----|--------------------|
| `network-troubleshooter` | Primary live fault diagnosis and RAW-guided remediation. | Yes, via `radkit_*` tools. |
| `kb-reader` | Read-only knowledge-base lookup, callable as a subagent. | No. |
| `ia-reader` | Read-only intelligence-artifact lookup. | No. |
| `kb-curator` | Human-initiated KB vault maintenance. | No. |
| `ia-curator` | Human-initiated fault-intelligence artifact authoring. | No. |

`network-troubleshooter` must not call curator agents. Live fault sessions should be read-only with respect to the repository and should require approval before persistent device changes.
