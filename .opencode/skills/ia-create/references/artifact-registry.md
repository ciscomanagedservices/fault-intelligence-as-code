# Intelligence Artifact Registry

Central reference for all six intelligence artifact types plus the
**Alert Definition (AD)** grouping concept. Three artifact types are active
(full generation support); three are stub-ready (schemas defined, generation
coming).

## Alert Definition (AD)

An **Alert Definition** is the top-level grouping concept that bundles a
matched Fault Signature, its Remediation Guide, and its Repair Action Workflow
into one alertable unit. It maps 1:1 to an alert definition in a fault
management system.

- **ID format:** `AD######` (6-digit zero-padded, e.g. `AD000004`)
- **Storage:** folder convention only — `intelligence-artifacts/AD######-<slug>/`
- **No standalone manifest file.** The folder name and its contained FS / RAW / RG
  files are the entire definition.
- **Wire field:** `alert_def_id` (snake_case), `--alert-def-id` (CLI flag),
  `"Alert Definition"` (user-facing label).

## AD Folder Layout (standard)

Every published Alert Definition folder follows this layout. Artifact files
(`FS|RG|RAW######-*.{yml,md}`) belong **only** at the AD root. All companion
documentation lives under `docs/`. RAW test bundles live under `tests/`.

```
intelligence-artifacts/AD######-<slug>/
├── FS######-<slug>.yml          ← Fault Signature (root, required)
├── RG######-<slug>.md           ← Remediation Guide (root, required)
├── RAW######-<slug>.yml         ← Repair Action Workflow (root, required)
├── tests/                       ← RAW test bundles (optional but recommended)
│   └── RAW######-<slug>.tests.yml
└── docs/                        ← Companion analysis + any other docs (optional)
    ├── FS######.analysis.md
    ├── RG######.analysis.md
    └── RAW######.analysis.md
```

**Convention rules:**
- Exactly one of each: `FS######-*.yml`, `RG######-*.md`, `RAW######-*.yml` at the AD root.
- All four IDs (`AD`, `FS`, `RAW`, `RG`) share the **same 6-digit suffix**.
- Test bundles use the canonical filename `RAW######-<slug>.tests.yml` and live under `tests/`.
- Companion analysis files (`<TYPE>######.analysis.md`) and any other non-artifact, non-test files live under `docs/`.
- `ia-publish` emits a **WARN** (not a hard fail this round) for any non-artifact file at the AD root.

Each AD###### folder contains:
- exactly one `FS######-<slug>.yml` (Fault Signature) at root
- exactly one `RAW######-<slug>.yml` (Repair Action Workflow) at root
- exactly one `RG######-<slug>.md` (Remediation Guide) at root
- optional `docs/` (companion analysis + any other docs)
- optional `tests/` (RAW test bundles)

All four IDs (`AD`, `FS`, `RAW`, `RG`) share the **same 6-digit suffix**.

## Artifact Types

| # | Type | ID Format | Name Pattern | Status | Pipeline |
|---|---|---|---|---|---|
| 1 | **Fault Signature** (FS) | `FS######` (e.g., `FS000004`) | `UPPERCASE_SNAKE_CASE` | **Active** | Fault Intelligence |
| 2 | Diagnostic Data Collection List (CL) | `CL######` (e.g., `CL000001`) | `UPPERCASE_SNAKE_CASE` | Stub | Health Intelligence |
| 3 | Diagnostic Data Parser (PARSE) | `PARSE######` (e.g., `PARSE000001`) | `PARSE_` prefix | Stub | Health Intelligence |
| 4 | Health Check Rule (HCR) | `HCR######` (e.g., `HCR000001`) | `UPPERCASE_SNAKE_CASE` | Stub | Health Intelligence |
| 5 | **Remediation Guide** (RG) | `RG######` (e.g., `RG000004`) | `..._GUIDE` suffix | **Active** | Fault Intelligence |
| 6 | **Repair Action Workflow** (RAW) | `RAW######` (e.g., `RAW000004`) | `..._REPAIR` suffix | **Active** | Fault Intelligence |

> All artifact IDs are **6-digit zero-padded strings**. The numeric suffix
> aligns with the parent Alert Definition (`AD######`) for FI-pipeline artifacts.

## File Locations

| Type | Schema Reference | JSON Schema | Example |
|---|---|---|---|
| FS | `references/fault-signature-schema.md` | `assets/fault-signature.schema.json` | `references/examples/fault-signature-example.yaml` |
| CL | `references/collection-list-schema.md` | `assets/collection-list.schema.json` | — |
| Parser | `references/parser-schema.md` | `assets/parser.schema.json` | — |
| HCR | `references/health-check-rule-schema.md` | `assets/health-check-rule.schema.json` | — |
| RG | `references/remediation-guide-template.md` | — (Markdown, no JSON Schema) | `references/examples/remediation-guide-example.md` |
| RAW | `references/repair-action-workflow-schema.md` | `assets/repair-action-workflow.schema.json` | `references/examples/repair-action-workflow-example.yaml` |

## Cross-Reference Relationships

### Fault Intelligence Pipeline

```
Alert Definition (AD000004)
└── folder: intelligence-artifacts/AD000004-<slug>/
  ├── Remediation Guide (RG000004) ──▶ Fault Signature (FS000004)
    │   (source document)              │   repair_action_workflow_ref ─▶ RAW.metadata.name
    │                                  │
    │                                  └─▶ Repair Action Workflow (RAW000004)
    │                                        (derived from RG)
```

- FS `metadata.alert_def_id` → parent folder `AD######` (e.g. `AD000004`)
- RAW `metadata.alert_def_id` → parent folder `AD######`
- FS `repair_action_workflow_ref` → RAW `metadata.name`
- RG `fault_signature_ref` → FS `metadata.name` (optional navigational back-link)
- RAW `inputs[].source` → FS `evaluation.parameters[].name` (via `{{ alert_vars.X }}`)

### Health Intelligence Pipeline

```
Collection List ──────────────▶ Parser ──────────────▶ Health Check Rule
  cli.parser_ref ────────────▶ Parser.name             requires.collection_lists ──▶ CL.name
                                                        requires.parsers ──────────▶ Parser.name
                                                        actions[].remediate.workflow_ref ──▶ RAW.name
```

- CL `collections[].cli.parser_ref` → Parser `name`
- HCR `requires.collection_lists[]` → CL `name`
- HCR `requires.parsers[]` → Parser `name`
- HCR `actions[].remediate.workflow_ref` → RAW `name` (cross-pipeline link)

## Linked-Set ID Alignment

When generating a linked set under an Alert Definition, all four IDs share the
same 6-digit suffix:

| Artifact | ID Example |
|---|---|
| Alert Definition (folder) | `AD000010` |
| Fault Signature | `FS000010` |
| Remediation Guide | `RG000010` |
| Repair Action Workflow | `RAW000010` |

IDs are **assigned at publish time** by `ia-publish`. Sequential integers are
allocated by scanning `intelligence-artifacts/index.json` for the maximum existing
suffix, then incrementing. Pad to 6 digits with leading zeros.

## Draft vs Published ID Convention

| State | ID Value | Signal |
|---|---|---|
| **Draft** (in `ia-drafts/`) | `FS000000`, `RG000000`, `RAW000000`, `AD000000` | The `000000` suffix means "not yet published — ID pending" |
| **Published** (in `intelligence-artifacts/`) | `FS000004`+, `RG000004`+, etc. | Real sequential ID assigned by `ia-publish` |

### Rules

- **`000000` is a reserved placeholder suffix** — it MUST NOT appear in
  `intelligence-artifacts/`. Only `ia-drafts/` artifacts carry this suffix.
- Draft folders use the convention `AD000000-<slug>/` to match the published
  folder structure. At publish time, `ia-publish` renames them to
  `AD######-<slug>/` with the allocated suffix.
- Draft filenames follow the same pattern: `FS000000-<slug>.yml`,
  `RG000000-<slug>.md`, `RAW000000-<slug>.yml`.
- All placeholder IDs pass JSON Schema validation (`^<PREFIX>\d{6}$`).
- The `ia-create` skill NEVER assigns real sequential IDs — only placeholders.
- Cross-references within a draft set (e.g., `alert_def_id: AD000000` in a
  RAW file) are consistently rewritten to the allocated suffix at publish time.
