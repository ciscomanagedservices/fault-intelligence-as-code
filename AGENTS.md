# AGENTS.md — DEVNET-3171: Fault Intelligence as Code

AI Agents, RAG, and MCP for Network Ops — Cisco Live US 2026 breakout session.
This is the **live demo repository** — it contains the working system demonstrated on stage.

---

## Repository Structure

```
app/                        # Webhook relay (FastAPI alert pipeline)
  alert_pipeline.py         # Receives Splunk webhooks, creates OpenCode sessions
.opencode/agents/           # OpenCode agent definitions
  network-troubleshooter.md # Primary: orchestrates fault diagnosis (RADKit MCP + Webex + KB)
  kb-reader.md              # Primary + subagent: read-only KB wiki reader
  kb-curator.md             # Primary: manual KB vault maintenance (ingest/lint/save)
.opencode/skills/           # OpenCode agent skills
  fault-remediation/        # RAW interpreter (invoked by network-troubleshooter)
  webex-notify/             # Webex notification renderer + sender (templates)
  wiki-query/               # Runtime KB reader (Quick/Standard/Deep)
  wiki-ingest/              # Author-time: add sources to the vault
  wiki-lint/                # Author-time: vault health check
  save/                     # Author-time: file a chat insight as a page
  wiki/                     # Vault scaffolding
  issue-report/             # Issue report skill
  obsidian-markdown/        # Obsidian markdown skill
intelligence-artifacts/     # Published FS YAML, RAW YAML, and RG Markdown artifacts grouped by fault ID
kb/                         # Knowledge base vault (wiki, raw sources, KB articles)
  wiki/                     # Wiki content (business-rules, runbooks, incidents, etc.)
  .raw/                     # Raw source documents (immutable)
docs/                       # Documentation (MkDocs with Material theme)
  content/                  # MkDocs source content
  site/                     # Generated MkDocs output
  project-docs/             # Internal investigation notes
  research/                 # Research notes
scripts/                    # Utility scripts (alert simulation, etc.)
tmp/                        # One-off debug or fix scripts (not promoted to main source)
BACKLOG.md                  # Task tracker — keep this up to date
```

---

## Architecture

- The **webhook relay** (`app/alert_pipeline.py`) runs inside Docker via `docker-compose.yml`.
- The **LLM agent** runs in OpenCode (on the host or as a separate service), configured via `opencode.json`.
- Device access is via **RADKit MCP** (configured as a remote MCP server in `opencode.json`).
- Use YAML for any configuration.

---

## Build and Run Commands

```bash
# Start the webhook relay in Docker
docker compose up --build

# Simulate a fault alert (headless mode — sends to relay)
python scripts/simulate_alert.py --api http://localhost:8080 --mode hybrid-reasoning

# Simulate a fault alert (headed mode — prints prompt for TUI paste)
python scripts/simulate_alert.py --direct --mode hybrid-reasoning
```

---

## Domain Vocabulary

| Term | Meaning |
|------|---------|
| **Fault Intelligence** | Machine-readable detection logic, diagnostic steps, and repair workflows derived from incidents and vendor knowledge |
| **TSG** | Troubleshooting Guide — codified as YAML with triggers, conditions, and remediation actions |
| **RAG** | Retrieval-Augmented Generation — LLM retrieves relevant docs from a knowledge base before generating |
| **MCP** | Model Context Protocol — open standard for AI agents to call external tools/data sources |
| **RALP loop** | Retrieve → Act → Log → Prompt — the troubleshooting agent's reasoning cycle |
| **Fault signature** | A syslog pattern + conditions that uniquely identify a known fault |
| **MTTR** | Mean Time to Repair/Resolve |

---

## Agent Architecture

The OpenCode runtime is split across focused agents and skills. See
`docs/project-docs/plans/2026-05-18-agent-architecture-refactor.md` for the full
design rationale.

| Agent | Mode | Purpose | Allow-list |
|-------|------|---------|------------|
| `network-troubleshooter` | primary | Orchestrates fault diagnosis end-to-end | Skills: `fault-remediation`, `webex-notify`. MCP: `radkit_*`. Subagent: `kb-reader`. |
| `kb-reader` | primary (also callable as subagent) | Read-only wiki vault queries | Skill: `wiki-query`. No MCP. No subagents. No writes. |
| `kb-curator` | primary | Manual vault maintenance (ingest/lint/save) | Skills: `wiki-query`, `wiki-ingest`, `wiki-lint`, `save`, `wiki`. No MCP. No subagents. |

**Defence in depth.** Each agent's allow-list is enforced both in
`opencode.json` (`permission.skill`, `permission.task`, `tools`) and in the
agent's own frontmatter. Skills declare what they need but cannot escape what
the calling agent allows.

**Hard rule.** `network-troubleshooter` MUST NOT be able to invoke
`kb-curator`. There is no path from a live fault session to a vault write.
`kb-curator` is a human-initiated agent only.

**Session logs.** `network-troubleshooter` writes a Markdown log per session
to `logs/troubleshooting/<UTC>-<alert_def_id>-<device>.md`. This is the canonical
record for post-hoc review; OpenCode's own session storage is a backup.

**Webex.** All Webex output goes through the `webex-notify` skill, which owns
templates under `.opencode/skills/webex-notify/references/`. When
`WEBEX_BOT_TOKEN`/`WEBEX_ROOM_ID` are unset, the skill returns `status:
skipped` and the agent auto-approves any pending `exec_cli` or `config_cli` with an explicit
`AUTO_APPROVE_WARNING` log entry.

---

## Skill Composition and the Vendored KB Wiki

The agent is composed from independent, reusable skills — not a single
monolith. The fault-remediation skill (`.opencode/skills/fault-remediation/`)
owns fault remediation logic only. For reading the knowledge base, it
delegates to the vendored `wiki-query` skill.

### Skill layout

```
.opencode/skills/fault-remediation/SKILL.md   # this project's primary skill
.opencode/skills/                              # wiki skills (vendored from kb-wiki upstream)
    wiki/SKILL.md                              # vault scaffolding (not used at runtime)
    wiki-query/SKILL.md                        # **runtime KB reader (Quick/Standard/Deep)**
    wiki-ingest/SKILL.md                       # author-time: add sources to the vault
    wiki-lint/SKILL.md                         # author-time: vault health check
    save/SKILL.md                              # author-time: file a chat insight as a page
kb/                                            # the vault root for this project
    AGENTS.md                                  # vault-local conventions (read by wiki-* skills)
    .raw/                                      # raw source documents (immutable)
    wiki/                                      # wiki content
        hot.md, index.md, overview.md, log.md  # standard wiki entry points
        business-rules/, known-issues/, incidents/, runbooks/, concepts/, entities/, sources/, ...
```

### Upstream provenance

The five wiki skills under `.opencode/skills/` are vendored as **full copies**.
We copy rather than submodule so customers cloning this public repo see everything in one place.
The skills are otherwise unmodified except for a clearly-marked
**"Vault location for this project"** override block at the top of each
runtime-relevant skill (`wiki-query`, `wiki-ingest`, `wiki-lint`, `save`).
That block pins the vault root to `kb/` because OpenCode
runs from the project root, not from the vault folder.

### How fault-remediation uses wiki-query

The fault-remediation skill's Step 0b **does not contain wiki-reading logic**.
It invokes the `wiki-query` skill with a fault-specific question and a query
mode (`quick` | `standard` | `deep`), then captures the returned business
rules into its variable store. This keeps each skill focused and makes mode
behavior consistent with any other use of the wiki.

### When to update the vendored skills

The vendored skills are forks. We do not expect the upstream repo to change
often, and customers will not have access to it. If a meaningful upstream
improvement lands, manually copy it over and re-apply the vault-path override
block. Do not silently diverge — record any non-override edits in
`docs/project-docs/`.

---

## Fault Intelligence Standards Reference

This project implements the data models from the IETF draft proposal
`draft-shoemaker-nmop-network-fault-yang`.
The draft defines two complementary YANG models: **Fault Signature (FS)** and
**Repair Action Workflow (RAW)**. All schemas, Pydantic models, and agent code
in this repo MUST conform to these structures.

### Fault Signature (FS)

A Fault Signature is a structured, machine-consumable specification that defines
the conditions under which a fault is detected. It is authored once (typically by
a vendor), versioned, and consumed by a Fault Management System (FMS) to derive
alert definitions.

**Top-level structure:**

```
schema_version   # Schema revision used to encode this instance
metadata         # Identity, applicability, classification
conditions       # Detection logic: events + boolean expression
```

**Metadata fields:**

| Field | Description |
|-------|-------------|
| `name` | Unique human-readable identifier |
| `id` | Unique numeric ID for programmatic reference |
| `version` | Semantic version (`MAJOR.MINOR.PATCH`) |
| `severity` | OpenConfig alarm severity: `CRITICAL`, `MAJOR`, `MINOR`, `WARNING`, `UNKNOWN` |
| `priority` | Numeric priority; lower = higher priority; default `5` |
| `symptom` | OpenConfig alarm symptom enum value |
| `description` | Multi-line human-readable fault explanation |
| `product_ids` | Hardware product identifiers (regex allowed) |
| `os_versions` | Software versions where signature is validated (regex allowed) |
| `component` | Primary affected component (e.g., `FAN`, `PSU`, `CHASSIS`) |
| `tags` | List of classification/filtering tags |

**Conditions block:**

```yaml
conditions:
  logic: "1 OR 2"          # Boolean expression over event IDs; AND/OR/NOT + parens
  logic_lookback_time: 120  # Seconds; all events must occur within this window
  events:
    - event:
        id: 1               # Referenced in `logic`
        type: syslog        # Event source type (syslog, alarm, state/counter, metric)
        path: "syslog"
        evaluation:
          type: regex
          value: "<pattern>"
          parameters:       # Optional: extract regex groups into named variables
            - type: extract_to_variable
              name: <var_name>
              source: "match.group(1)"
        match_count: 1      # Matches required within match_period
        match_period: 0     # Seconds (0 = instant)
        clear_event:        # Optional: auto-clear when fault resolves
          pattern: "<clear-regex>"
          lookback_period: 1200
```

**Key design rules:**
- Separate **metadata** (identity/applicability) from **detection logic** (conditions/events).
- Use explicit boolean logic expressions — never implicit AND between events.
- Event types are extensible via `identityref`; evaluation types via `choice`/`case`.
- A matched FS provides context and extracted variables for selecting a paired RAW.

---

### Repair Action Workflow (RAW)

A RAW is a portable, ordered set of steps with guards, inputs/outputs, and
status reporting used to diagnose and repair a matched fault. It is derived from
a human-readable **Remediation Guide** and represents its machine-consumable encoding.

**Top-level structure:**

```
workflow:
  metadata       # name, description, version
  inputs         # Variables provided by FMS (often from FS extracted vars)
  action_groups  # Optional reusable sequences of repair actions
  steps          # Ordered execution steps
```

**Each step contains:**

1. **`validation`** — checks device state and produces output variables:
   - `eval_cli` — run CLI commands, match regex, extract groups
   - `eval_logs` — search log buffer over a time window
   - `eval_var` — compare/match a workflow variable
   - `and` / `or` — logical combinators over validation actions

2. **`action_select`** — selects a repair path based on validation outputs:
   - Each entry has conditions (boolean expressions over output variables)
   - Matched entry executes one or more **action groups**

**Repair actions (within action groups):**

| Action | Description |
|--------|-------------|
| `exec_cli` | Execute a CLI command in exec mode |
| `config_cli` | Apply persistent configuration changes |
| `wait` | Pause execution for a duration |
| `goto` | Jump to a specific `step_id` |
| `revalidate` | Restart workflow from the top (escalating repair pattern) |
| `custom_action` | Execute external script/Ansible role with input/output bindings |
| `escalate` | Escalate to human/external process (subtypes: `open_support_case`, `rma`) |
| `resolve` | Signal successful resolution and exit |
| `fail` | Exit with explicit failure status |

**Workflow completion states:** `SUCCESS`, `PARTIAL`, `FAILURE`, `ESCALATION`

**Key design rules:**
- Inputs are bound from FS-extracted variables (e.g., `{{ alert_vars.fan_tray_id }}`).
- Validation actions live exclusively in the `validation` block; never inside action groups.
- Multiple action groups on the same `action_select` entry implement **escalating repair**:
  first group runs on first pass; subsequent groups only after `revalidate` cycles.
- Every repair step SHOULD include verification that the action succeeded.
- Workflow variables use Jinja2-style `{{ var_name }}` interpolation in commands/messages.

---

### FS + RAW Relationship

```
Fault Signature  ──(match)──►  extracted variables
                                      │
                                      ▼
                              Repair Action Workflow
                              inputs bound from FS vars
                                      │
                              steps: validate → select → act
                                      │
                              resolve / escalate / fail
```

A single FS may be bound to one or more RAWs. The FMS selects the appropriate
RAW on alert, passing extracted FS variables as workflow inputs.

### Reference Files

- Standards source: IETF draft proposal `draft-shoemaker-nmop-network-fault-yang`
- Local draft documents, if present, are kept outside the public release tree.
- Sample FS + RAW artifacts are published under `intelligence-artifacts/`.

---

## Agent Workflow

### Large tasks
Write progress to `.progress.md` as you go. If resuming an interrupted task,
read `.progress.md` first to understand prior state.

### Lessons learned / bugs
Write strategic improvements and lessons learned to `BUGS.md`. Consult it when
stuck on a recurring or complex issue.

### Documentation
Write troubleshooting analysis and internal investigation notes to `docs/project-docs/`.
Write user-facing documentation alongside the code as you build.

Files that don't belong in git (large binaries, slide templates, recordings, PDFs, customer-specific setup notes, and credential-bearing runbooks) should stay in approved private storage, not in this public release tree.

### Utility scripts
Save one-off debug or fix scripts to `./tmp/`. Do not promote them to main source
unless they serve a reusable purpose.

---

## Agentic Troubleshooting System — Architecture

This section documents the architecture for the agentic response component
(Steve's scope). It is the runtime system demonstrated in the session.

### Session Abstract

As networks scale, the knowledge required to detect, diagnose, and repair
incidents becomes scattered across support cases, vendor advisories, telemetry
analysis, and tribal expertise. This session shows how agentic AI can transform
that fragmented knowledge into actionable fault intelligence that your tools can
consume via simple data models and APIs. Agents, custom knowledge bases, and
context-engineering techniques translate historical incidents and vendor
recommendations into precise detection logic and automated repair action
workflows. RAG and MCP keep agents grounded and connected to tooling.

### Demo Environment (dCloud)

| Component | Role |
|-----------|------|
| 3x Cisco routers | Managed network devices — target of diagnostics and remediation |
| Linux box(es) | Agent runtime host — runs the troubleshooting agent in Docker |
| Splunk | Event detection — monitors syslogs, fires webhooks on fault signature match |
| RADKit server | Programmatic device access via MCP — primary connectivity to routers |

### End-to-End Flow

```
Splunk detects syslog match (fault signature)
        │
        ▼  HTTP webhook (FS alert payload + extracted vars)
Webhook relay  (app/alert_pipeline.py :8080)
        │
        ▼  Creates OpenCode session via REST API
OpenCode agent  (fault-remediation skill)
  1. Load Fault Signature (FS) by fault ID  ← from intelligence-artifacts/
  2. Load Repair Action Workflow (RAW) by fault ID  ← from intelligence-artifacts/
  3. Retrieve RAG context  ← customer KB in kb/wiki/
  4. Execute RAW interpreter loop:
       validate → action_select → repair action → [loop back if needed]
  5. For `exec_cli` or `config_cli` actions → Webex approval card → wait for human
  6. Execute approved action via RADKit MCP
  7. Resolve / escalate / fail → Webex notification
```

### Agent Architecture Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Agent runtime | OpenCode + REST API | LLM-model-independent; hooks to GitHub Copilot (Cisco EMU) |
| RAW execution | Skill-guided (fault-remediation skill) | Predictable, auditable, slide-friendly |
| Agent loop | RAW-guided with LLM escape hatches | Supports looping back with better intelligence; LLM handles ambiguous decision points |
| Fault ingest | HTTP webhook → OpenCode session | Decouples Splunk from agent; simple relay |
| FS/RAW store | YAML files in `intelligence-artifacts/` (repo) | Version-controlled; on-brand for "fault intelligence as code" |
| Device access | RADKit MCP (remote, configured in `opencode.json`) | RADKit preferred for demo |
| Customer KB / RAG | Wiki vault in `kb/` (repo) | Simple for demo and sandbox use |
| Human-in-the-loop | Webex cards — pause before `exec_cli` and `config_cli` actions | Safety gate for live device commands; compelling demo moment |
| Notifications | Webex — fault receipt, step progress, resolution/escalation | Webex room ID + bot token provided at integration time |

### Demo Fault Scenarios

- **BGP neighbor administrative shutdown** (`AD000002`) — primary scenario and simulator default
- **BGP maximum-prefix limit exceeded** (`AD000003`) — additional published scenario

The agent architecture is intentionally generic: it should handle any valid FS/RAW pair,
not just the demo scenarios. The demo scenarios are chosen for ease of live demonstration.
