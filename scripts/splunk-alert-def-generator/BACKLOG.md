# Backlog — Future Capabilities

Ideas for extending the splunk-docker platform, organized by theme.

---

## Alert Pipeline Enhancements

- [ ] **Multi-event correlation alerts** — Improve AND-logic SPL generation for fault signatures with complex multi-event correlation (currently best-effort)
- [ ] **Batch deployment** — Accept a directory of fault signatures and deploy all generated alerts in one pass
- [ ] **Alert update/sync mode** — Detect drift between local YAML and deployed Splunk alerts; offer diff + reconciliation
- [ ] **Remediation Guide → alert actions** — Auto-wire RG steps as Splunk alert action scripts or webhook payloads
- [ ] **RAW → Splunk SOAR playbook export** — Convert Repair Action Workflows to Splunk SOAR-compatible playbook JSON

---

## Data Ingestion & Simulation

- [ ] **Syslog data generator** — Produce synthetic syslog events matching fault signature patterns for testing alert triggers
- [ ] **Sample data loader** — Pre-populate the Splunk `syslog` index with representative data on container start
- [ ] **HEC (HTTP Event Collector) integration** — Send test events via HEC to validate alert firing end-to-end
- [ ] **Log replay tool** — Replay real syslog captures (anonymized) into Splunk for demo/lab scenarios

---

## Observability & Reporting

- [ ] **Alert health dashboard** — Auto-generate a Splunk XML dashboard showing all deployed alerts, fire counts, and gaps
- [ ] **Coverage report** — Given a set of fault signatures, report which have deployed alerts and which are unmonitored
- [ ] **Alert test results** — Automated validation that a deployed alert fires when expected data is injected

---

## MCP & AI Integration

- [ ] **MCP tool: deploy_alert** — Expose alert deployment as an MCP tool so AI agents can create alerts conversationally
- [ ] **MCP tool: list_alerts** — Let agents query deployed alert status without running Python scripts
- [ ] **MCP tool: run_spl** — Execute arbitrary SPL via MCP for interactive troubleshooting
- [ ] **Natural language → SPL** — Accept plain-English fault descriptions and generate SPL queries via LLM
- [ ] **Alert tuning assistant** — Analyze alert fire history and suggest threshold/schedule adjustments

---

## DevOps & CI

- [ ] **Docker Compose stack** — Add `docker-compose.yml` with Splunk + syslog-ng + data generator for one-command lab setup
- [ ] **CI pipeline** — GitHub Actions / ADO pipeline that builds the image, starts Splunk, runs `test_alert_deployment.py`
- [ ] **requirements.txt / pyproject.toml** — Formalize Python dependencies for reproducible environments
- [ ] **Pre-commit hooks** — Validate alert YAML schema before commit (e.g., required fields, valid cron expressions)

---

## Documentation & UX

- [ ] **Interactive wizard** — Guided CLI (`python create_alert.py`) that interviews the user and generates alert YAML
- [ ] **Alert catalog** — Auto-generated index of all alert configs in the repo with severity, schedule, and SPL summary
- [ ] **Splunk app packaging** — Bundle generated alerts as a Splunk app (.spl) for one-click install on any instance
- [ ] **Web UI for alert management** — Lightweight Flask/FastAPI dashboard for managing alerts outside Splunk

---

## Security

- [ ] **Credential management** — Move hardcoded password to environment variables or a secrets store
- [ ] **Token-based auth** — Use Splunk API tokens instead of username/password for SDK connections
- [ ] **TLS verification** — Support custom CA certs for non-dev deployments (currently `verify=False`)
