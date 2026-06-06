---
source: source-data/HEALTH-IC-PROPOSAL.md
created: 2026-02-21
purpose: >-
  Full schema definition and example for Health Check Rules
  (health-check-rule/v1.0.0). The most complex artifact type — defines
  conditions, evaluation logic, and automated actions. Referenced by the
  health-intelligence skill during YAML artifact generation.
---

# Health Check Rule Schema

> **Status: STUB** — This artifact type is fully documented and schema-validated.
> Generation support is coming in a future release. The schema below is the
> authoritative reference for the Health Check Rule data model.

**Schema**: `health-check-rule/v1.0.0`

Define expert-curated validation logic to assess device health based on collected
and parsed data. Rules specify thresholds, conditions, and recommended actions when
health issues are detected.

Health Check Rules sit at the top of the intelligence pipeline — they depend on
Collection Lists (for data gathering) and Parsers (for data normalization).

## Schema Definition

```yaml
# Schema: health-check-rule/v1.0.0

name: string                    # Unique rule identifier (UPPERCASE_SNAKE_CASE)
id: string                      # Unique string ID, pattern "HCR######" (6-digit zero-padded, e.g. "HCR000001")
version: string                 # Semantic version
description: string             # Human-readable description

# Classification
category: enum                  # hardware, software, interface, protocol, capacity, security
component: string               # Target component
severity: enum                  # CRITICAL, MAJOR, WARNING, MINOR, INFO

# Applicability
product_ids: list[string]       # Supported hardware PIDs
os_types: list[string]          # Supported OS types
os_versions: string             # Version constraint

# Data dependencies — REQUIRED
requires:
  collection_lists: list[string]  # Collection List names this rule depends on
  parsers: list[string]           # Parser names this rule depends on

# Health check conditions
conditions:
  - id: string                  # Condition identifier (lowercase_snake_case)
    name: string                # Human-readable condition name
    description: string         # What this condition checks

    # Evaluation logic
    eval:
      type: enum                # threshold, range, pattern, trend, comparison, expression

      # For threshold checks — compare a field against a single value
      threshold:
        field: string           # Field to evaluate (from parser output schema)
        operator: enum          # gt, gte, lt, lte, eq, ne
        value: number           # Threshold value
        unit: string            # Unit for display

      # For range checks — verify a field is within/outside a range
      range:
        field: string
        min: number
        max: number
        unit: string

      # For pattern matching — regex match/no-match on a string field
      pattern:
        field: string
        regex: string
        match: boolean          # true = should match, false = should not match

      # For trend analysis — detect changes over time
      trend:
        field: string
        window: string          # Time window (e.g., "1h", "24h", "7d")
        direction: enum         # increasing, decreasing, stable
        rate: number            # Change rate threshold

      # For comparison — compare two fields
      comparison:
        field_a: string
        operator: enum          # gt, gte, lt, lte, eq, ne
        field_b: string

      # For complex expressions — Python-like formula
      expression:
        formula: string         # Expression using field names as variables
        variables: list[string] # Fields used in the expression

    # Result classification — REQUIRED on every condition
    result:
      healthy: string           # Description when check passes
      unhealthy: string         # Description when check fails

# Actions on health check failure
actions:
  - trigger: string             # Condition ID that triggers this action
    type: enum                  # alert, collect_more, escalate, remediate
    priority: enum              # immediate, scheduled, advisory

    # Alert action — send notification
    alert:
      severity: enum            # CRITICAL, MAJOR, WARNING, MINOR, INFO
      message: string           # Alert message (supports {{ variable }} substitution)

    # Collect additional data — trigger another collection list
    collect_more:
      collection_list_ref: string  # Name of the Collection List to run

    # Escalation — create support case or RMA
    escalate:
      type: enum                # tac_case, rma, engineering
      message: string           # Escalation details

    # Remediation — trigger a repair workflow
    remediate:
      workflow_ref: string      # Name of the Repair Action Workflow to execute

# Metadata
tags: list[string]              # Classification tags (lowercase)
knowledge_refs: list[string]    # Links to KB articles, field notices, documentation
created_by: string              # Author/team
created_date: string            # ISO 8601 date (YYYY-MM-DD)
```

## Field Notes

- **`name`**: Use `UPPERCASE_SNAKE_CASE`. Suffix with `_HEALTH_CHECK` for clarity
  (e.g., `OPTICS_DOM_HEALTH_CHECK`, `CPU_UTILIZATION_HEALTH_CHECK`).
- **`id`**: String matching `^HCR\d{6}$` (6-digit zero-padded, e.g. `HCR000001`).
- **`severity`**: The overall severity of the rule. Individual conditions may trigger
  actions at different severity levels via `actions[].alert.severity`.
- **`requires`**: **CRITICAL** — every rule must include this block. List all Collection
  Lists and Parsers that this rule depends on, by their `name` field.
- **`conditions[].id`**: Use `lowercase_snake_case`. Must be unique within the rule.
  Actions reference conditions by this ID.
- **`conditions[].eval.type`**: Must match exactly one sub-block. If `type: threshold`,
  provide `threshold:` block only. Never mix eval types in a single condition.
- **`conditions[].result`**: Both `healthy` and `unhealthy` are required. These appear
  in health reports and dashboards.
- **`actions[].trigger`**: Must match a `conditions[].id` in the same rule. Multiple
  actions can share the same trigger (e.g., alert + escalate on the same condition).
- **`actions[].type`**: Determines which sub-block to include (`alert`, `collect_more`,
  `escalate`, or `remediate`). Only include the matching sub-block.
- **`actions[].alert.message`**: Supports `{{ variable }}` substitution using field
  names from the parser output schema.
- **`knowledge_refs`**: Link to Cisco documentation, field notices, or KB articles that
  provide context for the health check rules.

## Eval Type Guide

| Eval Type | When to Use | Required Fields |
|---|---|---|
| `threshold` | Compare a field against a fixed value | `field`, `operator`, `value`, `unit` |
| `range` | Check if a field is within/outside a numeric range | `field`, `min`, `max`, `unit` |
| `pattern` | Regex match on a string field | `field`, `regex`, `match` |
| `trend` | Detect changes in a field over time | `field`, `window`, `direction`, `rate` |
| `comparison` | Compare two fields against each other | `field_a`, `operator`, `field_b` |
| `expression` | Complex multi-field evaluation | `formula`, `variables` |

## Example: Optics DOM Health Check Rules

```yaml
name: OPTICS_DOM_HEALTH_CHECK
id: "HCR000001"
version: "1.3.0"
description: |
  Health check rules for optical transceiver DOM (Digital Optical Monitoring) values.
  Validates TX/RX power levels, temperature, voltage, and bias current against
  manufacturer thresholds and operational baselines.

category: hardware
component: OPTICS
severity: MAJOR

product_ids:
  - "8201-SYS"
  - "8202-SYS"
  - "8808-SYS"
  - "NCS-55A1-36H-SE-S"

os_types:
  - "IOS-XR"
os_versions: ">=7.5.0"

requires:
  collection_lists:
    - "OPTICS_TRANSCEIVER_DIAGNOSTICS"
  parsers:
    - "PARSE_OPTICS_CONTROLLER"

conditions:
  # RX Power Checks
  - id: "rx_power_low_critical"
    name: "RX Power Below Critical Threshold"
    description: |
      Checks if receive optical power has dropped below the manufacturer's
      low alarm threshold, indicating potential fiber issues, connector problems,
      or remote transmitter failure.
    eval:
      type: threshold
      threshold:
        field: "rx_power_dbm"
        operator: lt
        value: -25.0
        unit: "dBm"
    result:
      healthy: "RX power is within acceptable range"
      unhealthy: "RX power is critically low (< -25.0 dBm)"

  - id: "rx_power_low_warning"
    name: "RX Power Below Warning Threshold"
    description: |
      Checks if receive optical power is approaching the low alarm threshold.
      Early warning for degrading optical path.
    eval:
      type: range
      range:
        field: "rx_power_dbm"
        min: -25.0
        max: -20.0
        unit: "dBm"
    result:
      healthy: "RX power is above warning threshold"
      unhealthy: "RX power is in warning range (-25.0 to -20.0 dBm)"

  - id: "rx_power_high_critical"
    name: "RX Power Above Critical Threshold"
    description: |
      Checks if receive optical power exceeds the high alarm threshold.
      Over-power condition may damage receiver components.
    eval:
      type: threshold
      threshold:
        field: "rx_power_dbm"
        operator: gt
        value: 3.0
        unit: "dBm"
    result:
      healthy: "RX power is not over-threshold"
      unhealthy: "RX power is critically high (> 3.0 dBm) - receiver damage risk"

  # TX Power Checks
  - id: "tx_power_low_critical"
    name: "TX Power Below Critical Threshold"
    description: |
      Checks if transmit optical power has dropped below acceptable levels.
      May indicate laser degradation or power supply issues.
    eval:
      type: threshold
      threshold:
        field: "tx_power_dbm"
        operator: lt
        value: -10.0
        unit: "dBm"
    result:
      healthy: "TX power is within acceptable range"
      unhealthy: "TX power is critically low (< -10.0 dBm)"

  - id: "tx_power_using_dom_threshold"
    name: "TX Power vs DOM Threshold"
    description: |
      Compares current TX power against the transceiver's reported alarm thresholds.
    eval:
      type: expression
      expression:
        formula: "tx_power_dbm < tx_power_low_alarm"
        variables:
          - "tx_power_dbm"
          - "tx_power_low_alarm"
    result:
      healthy: "TX power is above DOM low alarm threshold"
      unhealthy: "TX power has crossed the transceiver's low alarm threshold"

  # Laser State Check
  - id: "laser_state_off"
    name: "Laser State Unexpected Off"
    description: |
      Verifies the laser is in expected state. Unexpected 'Off' state
      on an active interface indicates a fault condition.
    eval:
      type: pattern
      pattern:
        field: "laser_state"
        regex: "^Off$"
        match: false
    result:
      healthy: "Laser is in 'On' state"
      unhealthy: "Laser is unexpectedly 'Off' on active interface"

  # Temperature Checks
  - id: "temperature_high_critical"
    name: "Module Temperature Critical"
    description: |
      Checks if transceiver module temperature exceeds safe operating range.
      High temperature accelerates component degradation.
    eval:
      type: threshold
      threshold:
        field: "temperature_c"
        operator: gt
        value: 75.0
        unit: "Celsius"
    result:
      healthy: "Module temperature is within safe range"
      unhealthy: "Module temperature is critically high (> 75°C)"

  - id: "temperature_high_warning"
    name: "Module Temperature Warning"
    description: |
      Early warning for elevated module temperature.
    eval:
      type: range
      range:
        field: "temperature_c"
        min: 65.0
        max: 75.0
        unit: "Celsius"
    result:
      healthy: "Module temperature is below warning level"
      unhealthy: "Module temperature is elevated (65-75°C) - monitor closely"

  # Trend Analysis
  - id: "rx_power_degrading"
    name: "RX Power Degradation Trend"
    description: |
      Detects gradual RX power degradation over time, indicating
      potential fiber aging or connector contamination.
    eval:
      type: trend
      trend:
        field: "rx_power_dbm"
        window: "7d"
        direction: decreasing
        rate: 0.5
    result:
      healthy: "RX power is stable over the past 7 days"
      unhealthy: "RX power is degrading (> 0.5 dB loss in 7 days)"

  # Lane-level Checks (for multi-lane optics)
  - id: "lane_power_imbalance"
    name: "Multi-Lane Power Imbalance"
    description: |
      Checks for significant power variation between lanes in
      multi-lane transceivers (QSFP28, QSFP-DD).
    eval:
      type: expression
      expression:
        formula: "max(lanes.tx_power) - min(lanes.tx_power) > 3.0"
        variables:
          - "lanes"
    result:
      healthy: "Lane power is balanced (< 3 dB variance)"
      unhealthy: "Significant power imbalance between lanes (> 3 dB)"

# Actions triggered by health check conditions
actions:
  - trigger: "rx_power_low_critical"
    type: alert
    priority: immediate
    alert:
      severity: CRITICAL
      message: |
        Critical RX power loss detected on {{ interface_name }}.
        Current: {{ rx_power_dbm }} dBm. Immediate attention required.

  - trigger: "rx_power_low_critical"
    type: collect_more
    priority: immediate
    collect_more:
      collection_list_ref: "OPTICS_EXTENDED_DIAGNOSTICS"

  - trigger: "rx_power_low_critical"
    type: escalate
    priority: immediate
    escalate:
      type: tac_case
      message: |
        Optical interface {{ interface_name }} has lost RX signal.
        Collected diagnostics attached. Suspected fiber or remote device issue.

  - trigger: "laser_state_off"
    type: alert
    priority: immediate
    alert:
      severity: MAJOR
      message: |
        Laser unexpectedly off on {{ interface_name }}.
        This may indicate a hardware fault or administrative action.

  - trigger: "laser_state_off"
    type: remediate
    priority: scheduled
    remediate:
      workflow_ref: "OPTICS_LASER_RECOVERY_WORKFLOW"

  - trigger: "temperature_high_critical"
    type: alert
    priority: immediate
    alert:
      severity: CRITICAL
      message: |
        Transceiver on {{ interface_name }} is overheating.
        Temperature: {{ temperature_c }}°C. Risk of permanent damage.

  - trigger: "temperature_high_critical"
    type: escalate
    priority: immediate
    escalate:
      type: engineering
      message: |
        Investigate environmental conditions and airflow for {{ interface_name }}.

  - trigger: "rx_power_degrading"
    type: alert
    priority: scheduled
    alert:
      severity: WARNING
      message: |
        Gradual RX power degradation detected on {{ interface_name }}.
        Consider fiber inspection and connector cleaning.

  - trigger: "lane_power_imbalance"
    type: escalate
    priority: scheduled
    escalate:
      type: rma
      message: |
        Multi-lane transceiver {{ interface_name }} showing lane imbalance.
        May indicate partial transceiver failure. RMA recommended.

tags:
  - optics
  - dom
  - transceiver
  - health-check
  - physical-layer

knowledge_refs:
  - "https://www.cisco.com/c/en/us/support/docs/optical/dwdm/..."
  - "FN-12345: Transceiver DOM Monitoring Best Practices"

created_by: "CX Health Intelligence Team"
created_date: "2026-01-15"
```
