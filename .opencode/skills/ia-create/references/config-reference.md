# ia-config.yml Reference

The `ia-config.yml` file lives at the repository root and provides workspace identity,
customer governance rules, and project-specific defaults for intelligence artifact
generation. The skill operates fine without it — all settings have built-in defaults.

The file has **five sections**, each described below.

---

## Section 1: `workspace` — Workspace Identity

Identifies the customer engagement this workspace serves. Used in auto-generated tags,
PR descriptions, issue bodies, and companion document headers.

| Field | Type | Default | Description |
|---|---|---|---|
| `customer` | string | `""` | Customer or account name. Auto-converted to kebab-case and merged into `defaults.tags` if not already present. |
| `engagement` | string | `""` | Optional engagement or project label (e.g., `"CX FY26 Q3"`). Appears in PR descriptions. |
| `repository` | string | `""` | Canonical repo URL. Used by `ia-publish` for PR workflow. Falls back to `git remote get-url origin` if empty. |
| `description` | string | `""` | Human-readable workspace purpose. Appears in generated docs and PR summaries. |
| `cisco_support_api_scope` | string | `""` | Cisco Support API scope string (e.g., `"bug,case,eox,psirt,all"`). Informational — actual auth is in VS Code MCP config. |

**Example:**

```yaml
workspace:
  customer: "Acme Corp"
  engagement: "CX FY26 Q3"
  repository: "https://github.com/org/ia-workspace-acme"
  description: "Fault intelligence artifacts for Acme Corp IOS-XR deployment"
```

---

## Section 2: `defaults` — Global Defaults

Applied to every artifact type as baseline metadata. Overridden by user-specified values
in the current prompt.

| Field | Type | Default | Description |
|---|---|---|---|
| `author` | string | `"CX Intelligence Team"` | Default `metadata.created_by` / `metadata.author` |
| `severity` | string | `"WARNING"` | Default severity when not specified by user |
| `platforms` | list | `[]` | Product IDs added to every artifact's `product_ids` |
| `os_types` | list | `["IOS-XR"]` | OS types added to every artifact's `os_types` |
| `tags` | list | `[]` | Tags merged into every artifact's `tags` array |
| `product_scope` | list | `[]` | Human-readable product/platform names this workspace covers (e.g., `"Cisco 8000"`, `"ASR 9000"`). Used by `ia-research` and `ia-create` to scope product documentation lookups. **Distinct from `platforms`** — `platforms` sets artifact metadata; `product_scope` narrows which documentation is fetched. Populated by `ia-start` config interview. |

> **Auto-tag:** If `workspace.customer` is set, its kebab-case form is automatically
> merged into `defaults.tags` unless already present.

---

## Section 3: `rules` — Global Governance Rules

Constraints applied across **all** artifact types. Narrows the set of valid field values
to those relevant to this customer or deployment context.

### `rules.allowed_values`

Defines allow-lists for specific metadata fields. An **empty list `[]`** (or an omitted
key) means **no restriction** — all schema-valid values are accepted.

| Key | Restricts | Schema-valid values |
|---|---|---|
| `severity` | `metadata.severity` | `CRITICAL`, `MAJOR`, `WARNING`, `MINOR`, `UNKNOWN` |
| `platforms` | `metadata.product_ids` | Any hardware product ID string |
| `component` | `metadata.component` | `FAN`, `PSU`, `CHASSIS`, `OPTICS`, `CPU`, `MEMORY`, `LINECARD`, `FABRIC`, `ROUTE_PROCESSOR`, `CONTROLLER`, `INTERFACE`, `TEMPERATURE`, `VOLTAGE`, `NP`, `ASIC`, `BGP`, `UNKNOWN` |
| `os_types` | `metadata.os_types` | `IOS-XR`, `IOS-XE`, `NX-OS`, etc. |

**Merge semantics:** When `artifact_rules.<type>.allowed_values` is also set, the
effective allow-list for that type is the **intersection** of the global list and the
type-level list. A type-level entry **cannot add** values absent from the global list.

### `rules.required_fields`

Additional field names that must be populated on every artifact, beyond the schema
minimum. Example: `["cisco_defect_ids"]`.

### `rules.naming_prefix`

Prefix string prepended to every artifact `metadata.name`. Example: `"ACME_"` →
artifact name becomes `ACME_FAN_TRAY_THERMAL_FAULT`.

---

## Section 4: `artifact_rules` — Per-Artifact-Type Rules

Overrides and additions that apply to a specific artifact type only. Each type key is
optional; omit keys you don't need to customize.

### All types

| Field | Type | Default | Description |
|---|---|---|---|
| `id_start` | integer | `1` | **DEPRECATED.** Previously defined the first available 6-digit suffix. IDs are now assigned at publish time by `ia-publish` based on `intelligence-artifacts/index.json`. This field is retained for backward compatibility but is ignored during artifact creation. |
| `required_fields` | list | `[]` | Additional required fields for this type |
| `naming_prefix` | string | `""` | Prefix for this type's artifact names (overrides global `rules.naming_prefix`) |
| `allowed_values` | map | `{}` | Type-level field allow-lists (intersected with global; see merge semantics above) |

### `remediation_guide` only

| Field | Type | Default | Description |
|---|---|---|---|
| `required_sections` | list | `[]` | RG section keys that must be non-empty (e.g., `["escalation", "post_repair_verification"]`) |

**Type keys and default ID suffix:**

All artifact IDs are 6-digit zero-padded strings (e.g. `FS000004`). IDs are
assigned at publish time by `ia-publish` — the `id_start` field is deprecated
and ignored. For Fault-Intelligence-pipeline artifacts (FS, RG, RAW), the same
suffix is shared with the parent Alert Definition (`AD######`).

| Key | Artifact Type | Notes |
|---|---|---|
| `fault_signature` | Fault Signature | Draft ID: `FS000000` |
| `remediation_guide` | Remediation Guide | Draft ID: `RG000000` |
| `repair_action_workflow` | Repair Action Workflow | Draft ID: `RAW000000` |
| `collection_list` | Collection List | Draft ID: `CL000000` |
| `parser` | Parser | Draft ID: `PARSE000000` |
| `health_check_rule` | Health Check Rule | Draft ID: `HCR000000` |

---

## Section 5: `output` — Output Settings

| Field | Type | Default | Description |
|---|---|---|---|
| `default_format` | string | `"yaml"` | Output format: `yaml` or `json` |
| `companion_markdown` | boolean | `true` | Generate companion analysis `.md` for every YAML artifact |
| `output_dir` | string | `"ia-drafts"` | Output directory name (relative to repo root) |

---

## Precedence

1. User-specified values in the current prompt (highest priority)
2. `ia-config.yml` settings
3. Built-in defaults (lowest priority)

---

## Annotated Full Example

```yaml
# ia-config.yml — Intelligence Artifact Configuration

workspace:
  customer: "Acme Corp"
  engagement: "CX FY26 Q3"
  repository: "https://github.com/org/ia-workspace-acme"
  description: "Fault intelligence artifacts for Acme Corp IOS-XR deployment"
  cisco_support_api_scope: "bug,case,eox,psirt"  # Informational

defaults:
  author: "CX Intelligence Team"
  severity: WARNING
  platforms:
    - "NCS-55A1-36H-SE-S"
    - "8808-SYS"
  os_types:
    - "IOS-XR"
  tags:
    - acme-corp                        # Also auto-added from workspace.customer
  product_scope:                       # Human-readable names; scopes documentation lookups
    - "NCS 5500"
    - "Cisco 8000"

rules:
  allowed_values:
    severity:
      - CRITICAL
      - MAJOR
      - WARNING
    platforms: []                      # No platform restriction
    component:
      - FAN
      - PSU
      - OPTICS
      - LINECARD
    os_types:
      - "IOS-XR"
  required_fields: []
  naming_prefix: ""

artifact_rules:
  fault_signature:
    id_start: 100                      # DEPRECATED — ignored; IDs assigned at publish time
    required_fields:
      - clear_event                    # Require clear events on all FSes
    allowed_values:
      severity:                        # Narrows global: only CRITICAL + MAJOR for FSes
        - CRITICAL
        - MAJOR
    naming_prefix: ""
  remediation_guide:
    id_start: 100                      # DEPRECATED — ignored; IDs assigned at publish time
    required_sections:
      - escalation
      - post_repair_verification
  repair_action_workflow:
    id_start: 100                      # DEPRECATED — ignored; IDs assigned at publish time
  collection_list:
    id_start: 100                      # DEPRECATED — ignored; IDs assigned at publish time
  parser:
    id_start: 100                      # DEPRECATED — ignored; IDs assigned at publish time
  health_check_rule:
    id_start: 100                      # DEPRECATED — ignored; IDs assigned at publish time

output:
  default_format: yaml
  companion_markdown: true
  output_dir: ia-drafts
```
