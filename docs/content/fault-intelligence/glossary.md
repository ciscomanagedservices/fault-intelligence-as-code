# Glossary

| Term | Meaning |
|------|---------|
| Alert Definition (AD) | Folder-level grouping for one published fault-intelligence set. ID format: `AD######`. |
| Fault Signature (FS) | YAML artifact that detects a fault from events, telemetry, or alarms and extracts variables. ID format: `FS######`. |
| Remediation Guide (RG) | Markdown-only human-readable troubleshooting and remediation source document. ID format: `RG######`. |
| Repair Action Workflow (RAW) | YAML artifact that encodes validation, action selection, repair actions, and terminal outcomes. ID format: `RAW######`. |
| Linked set | An AD folder containing aligned FS, RG, and RAW artifacts with the same six-digit suffix. |
| Artifact group | Same as linked set: a folder under `intelligence-artifacts/` for one alert definition. |
| `alert_vars` | Variables passed from a matched FS or alert payload into the RAW. |
| `eval_cli` | RAW validation action that runs CLI and evaluates output with a pattern. |
| `config_cli` | RAW repair action that applies persistent configuration after approval. |
| `resolve` | RAW terminal action for successful repair. |
| `escalate` | RAW terminal action for permanent handoff to support, TAC, or RMA. |
| `fail` | RAW terminal action for workflow execution failure. |
| Collection List (CL) | Future Health Intelligence YAML artifact defining what diagnostic data to collect. |
| Parser (PARSE) | Future Health Intelligence YAML artifact defining how to parse collected data. |
| Health Check Rule (HCR) | Future Health Intelligence YAML artifact defining health evaluation logic. |
| IA | Intelligence Artifact. |
| FMS | Fault Management System. |
| MCP | Model Context Protocol. |
| Headed mode | Interactive OpenCode TUI run where the operator pastes an alert prompt directly. |
| Headless mode | OpenCode server plus FastAPI relay receiving alerts over HTTP. |
| Strict mode | Agent execution mode that follows the RAW as the controlling workflow. |
| Hybrid-reasoning mode | Agent execution mode that allows additional LLM judgment around ambiguous workflow choices. |
| Test bundle | YAML test file that exercises RAW behavior without LLM, RADKit, Webex, or Splunk. |
| Session log | Markdown record written under `logs/troubleshooting/` for post-run review. |

## Naming Conventions

| Item | Convention |
|------|------------|
| Artifact names | `UPPERCASE_SNAKE_CASE` |
| RG names | `..._GUIDE` suffix |
| RAW names | `..._REPAIR` suffix |
| Tags | lowercase kebab-case |
| Published folders | `intelligence-artifacts/AD######-<slug>/` |