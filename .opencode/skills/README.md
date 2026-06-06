# OpenCode Skills

Skills are reusable instruction packages loaded by OpenCode agents.

| Skill group | Purpose |
|-------------|---------|
| `fault-remediation` | Runtime RAW interpretation and remediation flow. |
| `webex-notify` | Webex notification and approval-card rendering/sending. |
| `golden-rules` | Safety and execution rules shared by runtime agents. |
| `wiki`, `wiki-query`, `wiki-ingest`, `wiki-lint`, `save` | Vendored KB wiki skills. Runtime sessions use `wiki-query`; author-time agents use ingest/lint/save. |
| `ia-start`, `ia-research`, `ia-create`, `ia-optimize`, `ia-publish`, `ia-explorer`, `raw-test-author` | Author-time intelligence-artifact workflow helpers. |
| `issue-report`, `obsidian-markdown` | Documentation and repository-support helpers. |

Runtime troubleshooting should use only the skills allowed by the calling agent. Curator and authoring skills are for human-initiated maintenance, not live fault response.
