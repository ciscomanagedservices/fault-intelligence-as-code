# Fault Signature Schema Reference

This document defines the complete schema for **Fault Signature** YAML artifacts.
Fault Signatures provide structured, machine-consumable detection logic that
identifies fault conditions based on events and telemetry observations.

## Document Structure

```yaml
schema_version: "0.0.1"          # Required — schema revision

metadata:                         # Required — identification and classification
  name: ...
  id: ...
  ...

conditions:                       # Required — detection logic
  logic: ...
  events: [...]
```

---

## Top-Level Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `schema_version` | string | Yes | Schema revision for validation (semver, e.g., `"0.0.1"`) |
| `metadata` | object | Yes | Identification, applicability, and classification |
| `conditions` | object | Yes | Logical evaluation framework for fault detection |

---

## `metadata` Object

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | Yes | Unique identifier. **UPPERCASE_SNAKE_CASE** (e.g., `FAN_TRAY_THERMAL_FAULT`). Pattern: `^[A-Z][A-Z0-9_]+$` |
| `id` | string | Yes | Unique string ID. Pattern: **`FS######`** (6-digit zero-padded, e.g., `"FS000004"`). Shares the 6-digit suffix with its Alert Definition, RG, and RAW |
| `alert_def_id` | string | Yes | ID of the parent Alert Definition. Pattern: **`AD######`** (e.g., `"AD000004"`). Must match the parent folder name `AD######-<slug>/` |
| `version` | string | Yes | Semantic version: `MAJOR.MINOR.PATCH` (e.g., `"1.0.0"`) |
| `description` | string | Yes | Multi-line explanation of the fault condition. Use YAML `\|` block scalar |
| `severity` | string | Yes | Fault severity. Enum: `CRITICAL`, `MAJOR`, `WARNING`, `MINOR`, `UNKNOWN` |
| `component` | string | Yes | Primary component category affected (e.g., `FAN`, `PSU`, `OPTICS`) |
| `product_ids` | array of strings | Yes | Hardware product IDs where this signature applies. Regex patterns allowed |
| `os_versions` | array of strings | Yes | Software versions where this signature is validated. Regex patterns allowed |
| `tags` | array of strings | Yes | Classification tags. Lowercase with hyphens only. Pattern: `^[a-z][a-z0-9-]*$` |
| `created_date` | string | Yes | ISO 8601 creation date (e.g., `"2026-04-22"`) |
| `modified_date` | string | Yes | ISO 8601 date of last modification |
| `author` | string | Yes | Author or team responsible for this artifact |
| `priority` | integer | No | Ordering within same severity/symptom. 1–10, lower = higher priority. Default: `5` |
| `symptom` | string | No | OpenConfig alarm symptom enumeration value |
| `repair_action_workflow_ref` | string | No | Name of the linked Repair Action Workflow |

---

## `conditions` Object

| Field | Type | Required | Description |
|---|---|---|---|
| `logic` | string | Yes | Boolean expression over event `id` values. Supports `AND`, `OR`, `NOT`, parentheses |
| `logic_lookback_time` | integer | No | Time window in seconds for correlating events. Default: `0` |
| `events` | array of event wrappers | Yes | Event definitions referenced by the logic expression. Min 1 item |

### Logic Expression Syntax

- **Event references**: Integer IDs matching `events[].event.id` values
- **Operators**: `AND`, `OR`, `NOT` (case-sensitive)
- **Parentheses**: For precedence in complex expressions
- **Examples**: `"E1"`, `"E1 AND E2"`, `"E1 OR E2"`, `"(E1 OR E2) AND E3"`, `"NOT E1"`
- **Time correlation**: All referenced events must occur within `logic_lookback_time` seconds

---

## Event Wrapper

Each item in `conditions.events[]` is an object with a single `event` key:

```yaml
events:
  - event:
      id: "E1"
      type: syslog
      ...
```

---

## Event Definition (`conditions.events[].event`)

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | string | Yes | Unique event ID within this signature. **`"E<n>"`** format (e.g., `"E1"`). Referenced by `logic` expression |
| `type` | string | Yes | Data source type. Enum: `syslog`, `alarm`, `telemetry-counter`, `telemetry-gauge`, `telemetry-state`, `snmp-trap`, `yang` |
| `path` | string | Yes | Data source path (e.g., `"syslog"`, a YANG path, or a metric name) |
| `evaluation` | object | Yes | Evaluation rule for matching the event |
| `match_count` | integer | Yes | Number of positive evaluations needed. Default: `1` |
| `match_period` | integer | Yes | Time window (seconds) for accumulating matches. `0` = instant |
| `message_type` | string | Conditional | **Required when `type: syslog`**. Syslog message type identifier |
| `message_sample` | string | Conditional | **Required when `type: syslog`**. Representative raw log line for reference and regex validation |
| `clear_event` | object | No | Auto-clear criteria for the fault state |

---

## `evaluation` Object

| Field | Type | Required | Description |
|---|---|---|---|
| `type` | string | Yes | Evaluation rule type. Enum: `regex`, `threshold`, `exact-match`, `range`, `state-change` |
| `value` | string | Conditional | **Required when `type: regex`**. Regular expression pattern to match |
| `operator` | string | Conditional | **Required when `type: threshold`**. Enum: `gt`, `gte`, `lt`, `lte`, `eq`, `ne` |
| `threshold_value` | number | Conditional | **Required when `type: threshold`**. Numeric threshold value |
| `parameters` | array | No | Extraction parameters for regex matches |

### Evaluation Parameters (`evaluation.parameters[]`)

Used with `type: regex` to extract values from match groups into workflow variables.

| Field | Type | Required | Description |
|---|---|---|---|
| `type` | string | Yes | Must be `extract_to_variable` |
| `name` | string | Yes | Variable name for the extracted value (e.g., `fan_tray_id`) |
| `source` | string | Yes | Extraction source expression (e.g., `match.group(1)`) |
| `description` | string | No | Human-readable explanation of the extracted variable |

---

## `clear_event` Object

| Field | Type | Required | Description |
|---|---|---|---|
| `pattern` | string | Yes | Regex pattern matching the clear event |
| `lookback_period` | integer | Yes | Time window (seconds) to look back for clear events |
| `correlation_variables` | array of strings | No | Variable names that must match between the fault match and the clear event to scope the clear to a specific fault instance (e.g., `[fan_tray_id]`) |

---

## Output Format Options

- **YAML** (default): Standard `.yml` file validated against `assets/fault-signature.schema.json`
- **JSON**: Same structure serialized as `.json`
- **Markdown-only**: Human-readable summary without machine-parseable structure

When generating YAML or JSON, always also produce a companion **FS analysis document**
(`<NAME>.analysis.md`).

## Companion Analysis Document (FS)

The FS analysis document accompanies every generated Fault Signature. Structure:

```markdown
# <NAME> — Fault Signature Analysis

## Syslog-to-Regex Mapping

| # | Source Syslog / Event | Event ID | Regex Pattern | Splunk Regex | Notes |
|---|---|---|---|---|---|
| 1 | <original syslog line> | 1 | <regex value> | <splunk variant if needed> | <notes> |

## Condition Logic Rationale
<Why this logic expression was chosen. Explain AND/OR/NOT decisions.>

## Detection Coverage Assessment
- **Catches**: <What fault conditions this signature detects>
- **Misses**: <Known gaps or edge cases not covered>
- **False positive risk**: <Scenarios that might match incorrectly>

## Open Items for SME Review
1. <Question or uncertainty requiring expert input>
```

## Pitfalls & Anti-Patterns

1. **Overlapping regex patterns**: Regex that matches unrelated syslogs from the same
   facility/severity. Always anchor patterns to the specific mnemonic and relevant
   fields — don't use broad wildcards like `.*FAULT.*`.

2. **Missing platform-specific regex variants**: Different platforms may format the same
   syslog differently (field order, spacing, additional fields). Test regex against
   samples from each target platform.

3. **Overly broad conditions**: Using `logic: "1"` with a generic syslog match that
   fires on normal operational messages. Combine with severity-specific or component-
   specific anchors.

4. **Hardcoded device identifiers**: Using literal slot numbers or interface names in
   regex instead of capture groups. Always extract variable parts (slot, module, port)
   via `evaluation.parameters[].name` (with `type: extract_to_variable`).

5. **Missing severity-to-condition alignment**: A `CRITICAL` severity signature that
   only matches `MINOR` alarm events. Ensure the signature severity reflects the
   highest severity event it correlates.

---

## Complete Example

See `references/examples/fault-signature-example.yml` for a best-practice example
(FAN_TRAY_THERMAL_FAULT with 2 syslog events, regex extraction, and clear events).
