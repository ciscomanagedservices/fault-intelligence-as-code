---
name: ia-create
description: >-
  Create Intelligence Artifacts — Fault Signatures (FS), Remediation Guides
  (RG), Repair Action Workflows (RAW), and future Health Intelligence types — as
  validated YAML + companion Markdown files. Accepts research output, raw syslogs,
  troubleshooting procedures, or pasted text; auto-detects applicable artifact
  types; generates linked sets with placeholder IDs (real IDs assigned at publish
  time); and validates against JSON schemas.
  Use this skill whenever the user wants to create, draft,
  generate, or produce intelligence artifacts — including requests like
  "ia-create", "create fault signatures", "generate a remediation guide", "draft a
  RAW", "create artifacts from my research", "turn this syslog into a signature",
  "build a repair workflow", "generate FS + RG + RAW for this fault", "create intelligence
  artifacts", or any request to go from source data to structured YAML intelligence
  artifacts. Also trigger when the user mentions creating collection lists, parsers,
  or health check rules — these are stub types with full schemas ready for future
  generation support.
---

# Intelligence Artifact Generator

Generate Intelligence Artifacts — YAML for Fault Signatures and Repair Action
Workflows, Markdown for Remediation Guides. Six artifact types form two pipelines:

```
Fault Intelligence:   Remediation Guide ──▶ Fault Signature
                                         ──▶ Repair Action Workflow
Health Intelligence:  Collection List ──▶ Parser ──▶ Health Check Rule
```

**Active types** (full generation support): Fault Signatures, Remediation Guides,
Repair Action Workflows. **Stub types** (schemas ready, generation coming): Diagnostic
Data Collection Lists, Diagnostic Data Parsers, Health Check Rules.

## Artifact Routing Table

| User Intent | Type | Schema Reference | JSON Schema | ID Format |
|---|---|---|---|---|
| Detect faults, match syslog/alarms | **Fault Signature** | `references/fault-signature-schema.md` | `assets/fault-signature.schema.json` | `FS######` (e.g., `FS000004`) |
| Collection List (stub) | Collection List | `references/collection-list-schema.md` | `assets/collection-list.schema.json` | `CL######` (e.g., `CL000001`) |
| Data parser (stub) | Parser | `references/parser-schema.md` | `assets/parser.schema.json` | `PARSE######` (e.g., `PARSE000001`) |
| Health check rule (stub) | Health Check Rule | `references/health-check-rule-schema.md` | `assets/health-check-rule.schema.json` | `HCR######` (e.g., `HCR000001`) |
| Troubleshooting / remediation guide | **Remediation Guide** | `references/remediation-guide-template.md` | — (Markdown, no JSON Schema) | `RG######` (e.g., `RG000004`) |
| Automated repair workflow | **Repair Action Workflow** | `references/repair-action-workflow-schema.md` | `assets/repair-action-workflow.schema.json` | `RAW######` (e.g., `RAW000004`) |

See `references/artifact-registry.md` for the full registry with cross-references.

## Workflow

### Stage 0: Source Data Assessment

> **🛑 HARD STOP — INTERACTIVE GATE**
>
> This stage is **mandatory** and **fully interactive**. Before generating ANY
> artifact, you MUST complete Step A (research gate) AND Step B (source inventory)
> using the `question` tool. Skipping Stage 0 is a skill-contract violation.
>
> **Escape hatch (skip Stage 0 only when):** the user's CURRENT message explicitly
> says "skip questions", "I already answered", supplies all inputs inline
> (e.g., "use `research/<name>/`, issue-name `<name>`, generate FS+RAW"), or
> resumes a session where Stage 0 was already completed and recorded. In that
> case, echo the parsed inputs back as a single confirmation `question` call
> and proceed only after the user confirms.
>
> **Anti-pattern (forbidden):** silently generating drafts because source data
> "looks complete." Even with a research folder present, ASK first.

#### Step A — Research gate

Use `question` to ask:

> **Would you like to run `ia-research` before creating artifacts?**
> Running research first gives you structured findings (syslog samples, bug data,
> existing signatures) that make artifact generation much more accurate.

Options (single-select, freeform allowed):

| Label | Description |
|---|---|
| Yes, research first | Invoke the `ia-research` skill now, then return here when done |
| No, I already have source data | Skip research — I have syslogs, docs, or existing files ready |

If the user selects **"Yes, research first"**: invoke the `ia-research` skill, then
re-enter Stage 0 Step B when research is complete.

If the user selects **"No, I already have source data"** or provides a freeform answer
indicating they have data: proceed to Step B.

#### Step B — Source inventory

Use `question` to present a multi-select checklist of available source types.
Ask the user to check every type they have available:

> **What source data do you have? Select all that apply:**

Options (multi-select, freeform allowed):

| Label | Description |
|---|---|
| Research folder (`research/<name>/`) | Output from a previous `ia-research` run |
| Syslog / alarm samples | Raw syslog lines, SNMP trap text, alarm strings |
| CLI show output | Device show command output (show logging, show interfaces, etc.) |
| Troubleshooting document or runbook | Existing troubleshooting guide, SOC runbook, or step-by-step procedure |
| Existing Remediation Guide (`.md` (RG)) | A previously drafted or edited `.md` (RG) file |
| Existing YAML artifacts | Fault Signature, RAW, or other `.yml` artifacts to extend or link |
| Defect / bug reference (CSCxx…) | A Cisco bug ID to pull context from |
| Free-form description | I'll describe the fault or issue in text |

After the user selects their sources, use `question` again to collect the
**specifics for each selected source** — one question per source type checked:

- **Research folder** → Scan the `research/` directory for all subdirectories. Present
  them as a **multi-select checklist** via `question` with each subfolder as
  an option (e.g., `research/bgp-mtu-pmtud-xe/`, `research/fan-tray-thermal-8000/`).
  Include an "Other (specify path)" freeform option for research not in the standard
  location. Allow the user to select one or more research folders.
- **Syslog / alarm samples** → "Please paste the syslog lines or alarm text."
- **CLI show output** → "Please paste the CLI output, or provide the file path."
- **Troubleshooting document** → "What is the file path, or paste the procedure text."
- **Existing `.md` (RG)** → Scan the `ia-drafts/` directory recursively for all `RG######-*.md`
  files. Present them as a **selectable list** via `question` (e.g.,
  `ia-drafts/AD000000-bgp-hold-timer-expired-ncs5500-8000/RG000000-bgp-hold-timer-expired.md`).
  Include an "Other (specify path)" freeform option for files not in `ia-drafts/`.
- **Existing YAML** → "What is the file path (or paths) to the YAML artifact(s)?"
- **Defect / bug reference** → "What is the bug ID (e.g., `CSCwr07525`)?"
- **Free-form description** → "Describe the fault, event, or issue you want to capture."

#### Step C — Special-case routing

After collecting all source specifics:

- If the **sole source** is an existing `.md` (RG) file: skip to Stage 2 and pre-select
  Fault Signature + Repair Action Workflow (the RG already exists). Use the AI derivation
  mapping tables in `references/remediation-guide-template.md` (Part 1) to parse the RG
  sections into FS events and RAW steps.
- If no usable source data was provided despite Step B: re-present the research gate
  (Step A) with a note that source data is required to proceed.

#### Step D — Derive issue name

Derive `<issue-name>` in kebab-case from the primary syslog mnemonic + platform +
defect reference (e.g., `fan-tray-thermal-8000-cscab12345`). This names the output
directory: `ia-drafts/AD000000-<issue-name>/`. The `AD000000-` prefix signals that
this is a draft group awaiting ID allocation at publish time. Confirm the derived
`<issue-name>` with the user via the `question` tool before creating any output
directory.

### Stage 1: Config Loading

Check for `ia-config.yml` at the repository root. See `references/config-reference.md`
for the full format specification. The config has five sections; load each as follows:

**Section 1 — `workspace`**
- Store `workspace.customer`, `workspace.engagement`, `workspace.repository`,
  `workspace.description` for use in generated docs, companion files, and downstream
  publish workflows.
- If `workspace.customer` is non-empty, convert it to kebab-case and auto-merge it
  into `defaults.tags` (unless an identical tag is already present). Example:
  `"Acme Corp"` → tag `acme-corp`.

**Section 2 — `defaults`**
- Apply `author`, `severity`, `platforms`, `os_types`, `tags` as baseline metadata for
  every artifact generated in this session.

**Section 3 — `rules`**
- Load `rules.allowed_values` (keys: `severity`, `platforms`, `component`, `os_types`).
  These define the **global** field allow-lists. An empty list `[]` means no restriction.
- Store `rules.required_fields` (additional fields required on every artifact).
- Store `rules.naming_prefix` (prefix applied to all artifact names).

**Section 4 — `artifact_rules`**
- For each artifact type, load `required_fields`, `naming_prefix`.
  (`id_start` is deprecated — IDs are assigned at publish time by `ia-publish`.)
- Load `artifact_rules.<type>.allowed_values` (if set). Compute the **effective**
  allow-list for each field as the **intersection** of the global list and the
  type-level list. A type-level list cannot introduce values absent from the global list.
  If the global list is empty (no restriction), the type-level list is used as-is.
- Load `required_sections` (Remediation Guide only).

**Section 5 — `output`**
- Apply `default_format`, `companion_markdown`, `output_dir`.

**Config allow-list validation (post-generation)**
After generating each artifact, validate its field values against the effective
allow-lists computed above. For any field with a non-empty allow-list, check:
- `metadata.severity` is in `effective.severity`
- `metadata.product_ids` items are in `effective.platforms` (if `effective.platforms`
  is non-empty)
- `metadata.component` is in `effective.component` (if non-empty)
- `metadata.os_types` items are in `effective.os_types` (if non-empty)

If a value falls outside the allow-list, surface a **warning** (not a hard error):
> ⚠️ Config allow-list warning: `metadata.severity` value `MINOR` is not in the
> configured allow-list `[CRITICAL, MAJOR, WARNING]` for `fault_signature`.

List all warnings together at the end of Stage 4 output and prompt the user to confirm
or correct. Do not block generation — the warning is advisory.

If no `ia-config.yml` exists, use built-in defaults: author `"CX Intelligence Team"`,
severity `WARNING`, format `yaml`, `companion_markdown: true`, no allow-list restrictions.

### Stage 2: Source Analysis & Artifact Detection

Analyze all source data and auto-detect applicable artifact types:

| Signal in Source Data | Candidate Artifact Type |
|---|---|
| Syslog message patterns, alarm strings, event correlation | Fault Signature |
| Step-by-step troubleshooting procedures, diagnostic commands | Remediation Guide |
| Branching repair procedures, decision trees, automated steps | Repair Action Workflow |

Present a multi-pick list:

> **Detected artifact candidates from your source data:**
> - [x] Remediation Guide — troubleshooting steps found *(default — edit before creating FS + RAW)*
> - [ ] Fault Signature — syslog patterns found
> - [ ] Repair Action Workflow — repair procedures with branching found
>
> Select which to generate (or add/remove types):

For each selected type, read the corresponding artifact reference from `references/` using the
Artifact Routing Table above. For most YAML artifact types this is `references/<type>-schema.md`;
for Remediation Guide it is `references/remediation-guide-template.md`.

**Single-signature rule:** When research or source data contains multiple syslog events
or patterns related to the same fault, generate **one Fault Signature with multiple
events** in `evaluation.events[]` — NOT multiple separate `.fs.yml` files. Multiple
events under a single FS is the correct model when the events are symptoms of the same
underlying fault. Only create separate Fault Signature artifacts when the events
represent genuinely different faults (different root cause, different remediation path).

**Recommended workflow — RG first:** The Remediation Guide is pre-selected by default
because it is the human-authored source document from which Fault Signatures and Repair
Action Workflows are created. Generate the RG first, review and edit it, then re-invoke
the skill (or use option 5 in the post-generation menu) to create the FS and RAW from
the edited RG. Selecting all three at once is supported, but the FS and RAW will be
created from an unreviewed draft.

### Stage 3: Artifact Generation (Staged Pipeline)

#### Companion Analysis Files (all artifact types)

**Every generated artifact MUST have a companion analysis markdown file**, written
to the `docs/` subfolder of the draft AD group (see **AD Folder Layout** below):

- Fault Signature → `docs/FS######.analysis.md`
- Remediation Guide → `docs/RG######.analysis.md`
- Repair Action Workflow → `docs/RAW######.analysis.md`

(IDs are placeholders during draft authoring: `FS000000`, `RG000000`, `RAW000000`.)

Each analysis file documents:
1. **Source-to-artifact mapping** — how each section/field was derived from source data
2. **Assumptions** — decisions made during generation when source data was ambiguous or incomplete
3. **Decision tracing** — links from research findings to specific artifact content
4. **Areas needing verification** — where information was inferred rather than explicitly provided

Generate the companion analysis file alongside every artifact in every code path below.
Do not skip analysis files for any artifact type or generation mode.

#### Loading context for each artifact type

For every artifact type being generated, load these resources from the Artifact Routing Table and
artifact registry:
1. **Artifact reference**: the `references/` file for that type. For YAML artifact types this is
  `references/<type>-schema.md`; for Remediation Guide it is
  `references/remediation-guide-template.md`.
2. **JSON Schema**: the `assets/*.schema.json` file for that type, if one exists.
3. **Example**: the corresponding example file listed in the artifact registry.
4. **Config overrides**: from `ia-config.yml` (if present)

For **Remediation Guide** specifically, also load:
5. **RG format specification**: read `references/remediation-guide-template.md` in full — Parts 1–3:
   the section-by-section format spec with AI derivation mapping tables (Part 1), the
   blank template (Part 2), and filled examples A and B (Part 3). This file is the
   authoritative specification for the `.md` (RG) output format.
6. **RG markdown example**: `references/examples/remediation-guide-example.md` — the
   canonical filled example showing the exact output format expected.

#### Identity field assignment

- **`metadata.name`**: `UPPERCASE_SNAKE_CASE`. RGs append `_GUIDE`, RAWs append `_REPAIR`
- **`metadata.id`**: Use a **placeholder** with the type prefix and six zeros:
  `FS000000`, `RG000000`, `RAW000000` (or `CL000000`, `PARSE000000`, `HCR000000`
  for stub types). Real IDs are assigned at publish time by `ia-publish`.
  Do NOT manually assign sequential IDs — the `000000` suffix is the draft signal.
- **`metadata.alert_def_id`** (FS and RAW): Use placeholder `AD000000`.
- **`metadata.version`**: `"1.0.0"` for new artifacts
- **`schema_version`**: `"0.0.1"` (current draft version)

> **Note:** All placeholder IDs (`FS000000`, `RG000000`, `RAW000000`, `AD000000`)
> pass schema validation as-is (they match `^<PREFIX>\d{6}$`). The literal `000000`
> suffix is a reserved value that is never used as a real published ID.

#### RG-only generation (default)

When only Remediation Guide is selected:
- Read `references/remediation-guide-template.md` (all parts) and
  `references/examples/remediation-guide-example.md`
- Generate the RG as a **markdown file** (`RG000000-<NAME>.md`) following the template
  structure exactly: Title & Overview → Applicability → Triggering Events (per-event
  subsections: type, message ID, example message, key values to extract; plus
  correlation logic and recovery indicator) → Symptoms → Diagnosis & Repair Steps
  (commands, sample output healthy, sample output fault confirmed, decision point;
  caution where relevant) → Escalation → Post-Repair Verification → References
- The markdown RG contains **no regex, no YAML syntax, no machine expressions** —
  pure human-readable prose that a network engineer can edit directly
- **No YAML RG is generated.** YAML is never produced for the Remediation Guide type.
- Auto-assign `<NAME>_GUIDE` naming; use placeholder ID `RG000000` (real ID assigned
  at publish time)
- Generate companion **RG analysis (`<NAME>.analysis.md`)**: source-to-section
  mapping table, assumptions, escalation completeness check, open items for SME review
- Output both files to `ia-drafts/AD000000-<issue-name>/`
- Present the `.md` (RG) file and prompt: *"Review and edit the Remediation Guide, then
  use option 5 (Create FS + RAW from edited RG) when ready."*

#### Linked-set generation (FS + RG + RAW selected together)

**Stage 3a: Remediation Guide**

Generate the markdown RG first (same process as RG-only mode above):
- Generate `RG000000-<NAME>.md` + `<NAME>.analysis.md`
- Output to `ia-drafts/AD000000-<issue-name>/`
- Ask: *"Would you like to review the Remediation Guide before generating the FS
  and RAW?"*

**Stage 3b: Optional RG Review Gate**

If user accepts → pause and present the `.md` (RG) for review. User edits the file,
then signals to continue. If skipped → the Stage 3a RG draft is used as-is.

**Stage 3c: Fault Signature (created from RG)**

Generate FS from the RG's Triggering Events section:
- Map **ALL** Triggering Events from the RG into a **single** Fault Signature's
  `evaluation.events[]` array. Each syslog pattern becomes a separate event entry
  with its own `id`, `type`, `evaluation`, and `message_sample`. The
  `conditions.logic` field ties them together (e.g., `"1 OR 2 OR 3"` if any event
  indicates the fault). Do NOT create multiple `.fs.yml` files — one FS per fault.
- Use the AI derivation mapping tables in `references/remediation-guide-template.md`
  Part 1 (§ "Triggering Events" table) to map RG event descriptions → FS evaluation
  patterns and extraction parameters
- Auto-link: set `FS.corresponding_rg` to `<NAME>_GUIDE`
- Generate YAML + **FS analysis (`<NAME>.analysis.md`):** syslog-to-regex mapping
  table, condition logic rationale, detection coverage assessment, open items
- Run validation (Stage 4)

**Stage 3d: Repair Action Workflow (created from RG)**

Generate RAW using the RG's Diagnosis & Repair Steps section as primary source:
- Use the AI derivation mapping tables in `references/remediation-guide-template.md`
  Part 1 (§ "Diagnosis & Repair Steps" table) to formalize steps → encode decision
  points → parameterize variables → add verification steps → specify control flow
- Auto-link: use placeholder RAW ID (`RAW000000`), set `RAW.rg_ref` to `<NAME>_GUIDE`,
  populate `inputs` from FS extracted variables
- Generate YAML + **RAW analysis (`<NAME>.analysis.md`):** source-to-step mapping,
  conversion decisions, open items, and **Mermaid flowchart** (`flowchart TD`, green
  resolve nodes, amber escalate, red fail)
- Run validation

#### Non-linked generation (individual or partial selections)

Generate each selected type independently using the standard per-artifact flow. Same
loading, identity assignment, and validation — just without cross-linking.

#### Output format

- **Fault Signature, Repair Action Workflow**: YAML + companion Markdown analysis
  document. User can request JSON instead of YAML. File naming:
  `<ARTIFACT_NAME>.yml` + `<ARTIFACT_NAME>.analysis.md`
- **Remediation Guide**: Markdown file only (no YAML, never). File naming:
  `<ARTIFACT_NAME>.md` + `<ARTIFACT_NAME>.analysis.md`. The `.md` (RG) file
  follows the template structure from `references/remediation-guide-template.md`
  and is designed for human editing before FS + RAW are created from it.

#### OPEN DESIGN QUESTIONS block

Every generated YAML artifact MUST include a comment block at the top:

```yaml
# ──────────────────────────────────────────────────────────────────────────────
# OPEN DESIGN QUESTIONS
#
# 1. <Question or ambiguity from source data>
# 2. <Assumption made during generation>
# ──────────────────────────────────────────────────────────────────────────────
```

This documents ambiguities and items requiring SME review.

### Stage 4: Validation

Run the validation script on all generated YAML files:

```bash
python .opencode/skills/ia-create/scripts/validate_artifact.py ia-drafts/AD000000-<issue-name>/
```

The script:
- Auto-detects artifact type from ID range, name suffix, or structural keys
- Validates against JSON Schema (Draft 7)
- Runs semantic cross-reference checks per type
- Reports errors and warnings
- Supports `--strict`, `--quiet`, `--format json` flags

If validation fails, fix issues and re-validate. Simple issues (missing required
fields with sensible defaults) can be auto-fixed.

**Test bundles:** Test bundles generated by `raw-test-author` (Stage 5 option 6)
are NOT validated by `validate_artifact.py`. They are validated separately by
the `raw-test-author` skill's packaged validator
(`assets/test-bundle.schema.json` + `scripts/validate_test_bundle.py`) at
authoring time. `ia-create` does not re-validate bundles in Stage 4; trust the
author skill's `validate-only` pass. The release-facing RAW test framework
reference lives at `docs/content/fault-intelligence/test-framework.md`.

### Stage 5: Post-Generation Actions

Present a summary of what was generated, validation status, and output paths. Then
offer a loop menu:

1. **Edit artifacts** — user describes changes, re-read and apply
2. **Regenerate** — regenerate specific artifacts with different parameters
3. **Validate again** — re-run validation
4. **Generate additional artifacts** — add more types from the same source data
5. **Create FS + RAW from edited RG** — *(shown only when `.md` (RG) exists but no
   FS/RAW have been generated)* reads the edited `.md` (RG), applies the derivation
   mapping from `references/remediation-guide-template.md` Part 1, and generates the
   Fault Signature and Repair Action Workflow YAML artifacts
6. **Generate RAW test bundle** — *(shown only when at least one `RAW######-*.yml`
   exists in the draft group)* invokes the `raw-test-author` skill in `author` mode
   for each draft RAW that lacks a matching `tests/<RAW>-<slug>.tests.yml`. The
   resulting bundle is validated via the `raw-test-author` skill's packaged
   validator before returning to this menu. Test bundles live at
   `ia-drafts/AD000000-<issue-name>/tests/RAW000000-<slug>.tests.yml`; `ia-publish`
   Step 1b rewrites their IDs at publish time.
7. **Done** — exit

## Cross-Cutting Concerns

### AD Folder Layout (standard)

Every Alert Definition draft and published folder MUST follow this layout:

```
AD######-<slug>/                              ← artifacts + tests at root
  FS######-<slug>.yml                         ← Fault Signature
  RAW######-<slug>.yml                        ← Repair Action Workflow
  RG######-<slug>.md                          ← Remediation Guide (Markdown)
  tests/                                      ← optional; RAW test bundles
    RAW######-<slug>.tests.yml
  docs/                                       ← all non-artifact, non-test files
    FS######.analysis.md
    RAW######.analysis.md
    RG######.analysis.md
    <any-other-documentation>.md
```

**Rules:**

- **At root:** only artifacts (`FS`, `RAW`, `RG`) and the `tests/` subfolder.
- **`docs/`:** all companion analysis files, design notes, references, screenshots,
  and any other non-artifact, non-test documentation. Anything that is NOT
  an FS/RAW/RG artifact and NOT a test bundle goes here.
- **`tests/`:** RAW test bundles only (one bundle per RAW). Owned by
  `raw-test-author`. ID and filename are rewritten by `ia-publish` Step 1b at
  publish time.
- Draft folders (`AD000000-<slug>/`) follow the same layout. `ia-publish` Step 2
  preserves both `tests/` and `docs/` subfolders verbatim when copying to
  `intelligence-artifacts/`.
- Convention enforced by documentation only at present — `validate_artifact.py`
  emits a WARN for non-artifact files at the root and for content placed
  outside `docs/` or `tests/`.

### Naming conventions

| Type | Pattern | Example |
|---|---|---|
| Fault Signature | `UPPERCASE_SNAKE_CASE` | `FAN_TRAY_THERMAL_FAULT` |
| Remediation Guide | `..._GUIDE` suffix | `FAN_TRAY_THERMAL_FAULT_GUIDE` |
| Repair Action Workflow | `..._REPAIR` suffix | `FAN_TRAY_THERMAL_FAULT_REPAIR` |
| Collection List | `UPPERCASE_SNAKE_CASE` | `OPTICS_TRANSCEIVER_DIAGNOSTICS` |
| Parser | `PARSE_` prefix | `PARSE_OPTICS_CONTROLLER` |
| Health Check Rule | `UPPERCASE_SNAKE_CASE` | `OPTICS_DOM_HEALTH_CHECK` |

### `custom_action` vs `escalate` semantics (RAW)

- **`custom_action`**: Invokes an external capability (physical intervention, human task,
  third-party integration) and the workflow **resumes afterward**. Use for "reseat the
  module", "swap the cable", "reconnect the fiber". Requires `handler` field, optional
  `inputs`/`outputs`.
- **`escalate`**: Permanently hands off control. The workflow **does not resume**. Use only
  for TAC case, RMA, or engineering escalation when the workflow cannot continue.

RG steps like "reseat the module" MUST map to `custom_action`, NOT `escalate`.

### Variable syntax

Use `{{ variable }}` (double braces with spaces, Jinja2 convention) for all variable
substitution in CLI commands, messages, and conditions.

## Quick Reference: Enum Values

**Severity:** CRITICAL · MAJOR · WARNING · MINOR · UNKNOWN (FS/RG/RAW) | + INFO (HCR)

**Component:** FAN · PSU · CHASSIS · OPTICS · CPU · MEMORY · LINECARD · FABRIC ·
CONTROLLER · INTERFACE · ROUTING · SYSTEM

**Event Type (FS):** syslog · alarm · state_counter · metric

**Evaluation Type (FS):** regex · threshold

**Validation Actions (RAW):** eval_cli · eval_logs · eval_var · and · or

**Repair Actions (RAW):** exec_cli · config_cli · wait · goto · revalidate ·
custom_action · escalate · resolve · fail

**Eval Types (HCR):** threshold · range · pattern · trend · comparison · expression

**Action Types (HCR):** alert · collect_more · escalate · remediate

## Common Pitfalls

- **FS**: `conditions.logic` must reference only declared event IDs. If `logic: "1 OR 2"`,
  events `id: 1` and `id: 2` must both exist.
- **FS**: `evaluation.type` must match parameters — `regex` needs `value`, `threshold` needs
  `operator` + `threshold_value`.
- **FS**: Syslog events require `message_type`. Include `message_sample` for regex context.
- **RAW**: Every branch must terminate with `resolve`, `escalate`, `fail`, `goto`, or
  `revalidate`. Dangling branches are invalid.
- **RAW**: Never use `goto.step_id` referencing a nonexistent step.
- **RAW**: Use `custom_action` for physical/human interventions, not `escalate`.
- **RAW**: Don't create single-use named `action_groups` — inline them instead.
- **RAW**: Don't add explicit `goto` for sequential steps (sequential flow is implicit).
- **RAW**: `fail` is for workflow execution errors only; use `escalate` for unresolved faults.
- **RAW**: `exec_cli` is for state-changing exec-mode commands (`clear`, `reload`).
  Never for `show` commands — those belong in `eval_cli` or `escalate.data.commands[]`.
- **RAW**: `config_cli.commands[]` excludes mode-entry and commit bookends
  (`configure terminal`, `commit`, `end`, `write memory`). Include only the
  navigation context to scope the change plus the change itself.
- **RAW**: `escalate.data` is an object with `commands:` (show commands to collect)
  and `vars:` (workflow variables to include). Not a list of strings or mixed items.
- **RAW**: All regex extraction happens in `eval_cli.pattern` via capture
  groups, read out as `{{ result.groups[N] }}` (or `{{ result.matched }}` for
  booleans). NEVER call functions like `result.extract(...)` or
  `result.search(...)` inside `outputs[*].source` — the interpreter does not
  implement them. For multi-field extraction, use the `and` validation
  combinator with one focused `eval_cli` per field; keep each pattern simple
  and avoid compound lookahead regexes.
- **RG**: `fault_signature_ref` must be UPPER_SNAKE_CASE (the FS name, no suffix).
- **RG**: Must include an escalation path and a "verify resolution" final step.
- **RG**: Don't hardcode device names or IPs — use parameterized placeholders.
- **HCR**: Every condition needs both `result.healthy` and `result.unhealthy`.
- **HCR**: `eval.type` must match exactly one sub-block (threshold/range/pattern/etc.).
- **HCR**: `actions[].trigger` must reference a valid `conditions[].id`.

---

## Closing Message

When this skill completes (user selects "Done" from the Stage 5 menu) and the user is
about to proceed to another skill, append this tip to your final output:

> ---
> **💡 Tip:** Start a **new chat** (click the **+** button at the top of the Copilot
> Chat panel) before running the next skill. This resets the context window and gives
> the next skill a clean slate to work with.
> ---
