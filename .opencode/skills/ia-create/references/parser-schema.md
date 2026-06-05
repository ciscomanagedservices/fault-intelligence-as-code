---
source: source-data/HEALTH-IC-PROPOSAL.md
created: 2026-02-21
purpose: >-
  Full schema definition and examples for Diagnostic Data Parsers
  (diagnostic-parser/v1.0.0). Includes regex-based and TextFSM-based examples.
  Referenced by the health-intelligence skill during YAML artifact generation.
---

# Diagnostic Data Parser Schema

> **Status: STUB** — This artifact type is fully documented and schema-validated.
> Generation support is coming in a future release. The schema below is the
> authoritative reference for the Parser data model.

**Schema**: `diagnostic-parser/v1.0.0`

Define parsing logic to extract structured data from CLI output, log messages, or
raw telemetry. Parsers normalize vendor-specific formats into consistent data
structures for health analysis.

## Schema Definition

```yaml
# Schema: diagnostic-parser/v1.0.0

name: string                    # Unique parser identifier (PARSE_ prefix, UPPERCASE_SNAKE_CASE)
id: string                      # Unique string ID, pattern "PARSE######" (6-digit zero-padded, e.g. "PARSE000001")
version: string                 # Semantic version
description: string             # Human-readable description

# Parser scope
input_type: enum                # cli_output, syslog, gnmi_response, snmp_response
source_format: enum             # text, json, xml, table

# Applicability
os_types: list[string]          # Supported OS types
os_versions: string             # Version constraint

# Parsing rules
parser:
  type: enum                    # regex, textfsm, grok, jq, xpath, ttp

  # For regex-based parsing
  regex:
    patterns: list
      - name: string            # Field name to extract
        pattern: string         # Regex pattern with named groups (?P<name>...)
        type: enum              # string, integer, float, boolean, list
        required: boolean       # Is this field required?

  # For TextFSM-based parsing
  textfsm:
    template: string            # Embedded TextFSM template (use | block scalar)

  # For TTP (Template Text Parser)
  ttp:
    template: string            # TTP template

  # For jq-based parsing (JSON input)
  jq:
    expression: string          # jq filter expression

  # For XPath-based parsing (XML input)
  xpath:
    expressions: list
      - name: string            # Field name
        path: string            # XPath expression
        type: enum              # string, integer, float, boolean

  # For grok-based parsing (log/syslog input)
  grok:
    patterns: list
      - name: string            # Pattern name
        pattern: string         # Grok pattern

# Output schema
output:
  schema:
    - name: string              # Output field name
      type: enum                # string, integer, float, boolean, list, object
      description: string       # Field description
      unit: string              # Unit of measure (optional)

# Validation
validation:
  required_fields: list[string] # Fields that must be present in output
  type_checks: boolean          # Enforce type validation on output

tags: list[string]              # Classification tags (lowercase)
created_by: string              # Author/team
created_date: string            # ISO 8601 date (YYYY-MM-DD)
```

## Field Notes

- **`name`**: Always use `PARSE_` prefix followed by `UPPERCASE_SNAKE_CASE`
  (e.g., `PARSE_OPTICS_CONTROLLER`, `PARSE_BGP_SUMMARY`, `PARSE_INTERFACE_ERRORS`).
- **`id`**: String matching `^PARSE\d{6}$` (6-digit zero-padded, e.g. `PARSE000001`).
- **`parser.type`**: Must match the sub-block provided. If `type: regex`, include `regex:` block only.
  Never include multiple parser type blocks.
- **`regex.patterns[].pattern`**: Use Python named groups `(?P<field_name>...)`.
  Escape backslashes in YAML strings (use double backslash `\\` or single-quoted strings).
- **`textfsm.template`**: Use YAML `|` block scalar for multi-line TextFSM templates.
  Follow standard TextFSM syntax: `Value` declarations, `Start` state, `Record` transitions.
- **`output.schema[]`**: Must include every field the parser extracts. Health Check Rules
  reference these field names in `eval` blocks — missing fields cause runtime failures.
- **`validation.required_fields`**: Must be a subset of `output.schema[].name`.
  Lists the fields that must always be present in parser output for downstream consumers.
- **`unit`**: Include physical units where applicable (dBm, mA, Celsius, V, packets, bytes, percent).

## Example 1: Regex-Based Parser (Optics DOM)

```yaml
name: PARSE_OPTICS_CONTROLLER
id: "PARSE000001"
version: "1.1.0"
description: |
  Parses output from 'show controllers optics' command on IOS-XR devices.
  Extracts DOM (Digital Optical Monitoring) values including TX/RX power,
  laser bias current, temperature, and voltage readings with alarm thresholds.

input_type: cli_output
source_format: text

os_types:
  - "IOS-XR"
os_versions: ">=7.0.0"

parser:
  type: regex
  regex:
    patterns:
      - name: interface_name
        pattern: "Controller State:\\s+(?P<interface_name>\\S+)"
        type: string
        required: true

      - name: laser_state
        pattern: "Laser State:\\s+(?P<laser_state>\\w+)"
        type: string
        required: true

      - name: tx_power_dbm
        pattern: "Transmit Power\\s+=\\s+(?P<tx_power_dbm>[-\\d.]+)\\s+dBm"
        type: float
        required: true

      - name: rx_power_dbm
        pattern: "Receive Power\\s+=\\s+(?P<rx_power_dbm>[-\\d.]+)\\s+dBm"
        type: float
        required: true

      - name: laser_bias_ma
        pattern: "Laser Bias Current\\s+=\\s+(?P<laser_bias_ma>[\\d.]+)\\s+mA"
        type: float
        required: false

      - name: temperature_c
        pattern: "Module Temperature\\s+=\\s+(?P<temperature_c>[\\d.]+)\\s+Celsius"
        type: float
        required: false

      - name: voltage_v
        pattern: "Module Voltage\\s+=\\s+(?P<voltage_v>[\\d.]+)\\s+V"
        type: float
        required: false

      - name: tx_power_high_alarm
        pattern: "Tx Power High Alarm\\s+=\\s+(?P<tx_power_high_alarm>[-\\d.]+)"
        type: float
        required: false

      - name: tx_power_low_alarm
        pattern: "Tx Power Low Alarm\\s+=\\s+(?P<tx_power_low_alarm>[-\\d.]+)"
        type: float
        required: false

      - name: rx_power_high_alarm
        pattern: "Rx Power High Alarm\\s+=\\s+(?P<rx_power_high_alarm>[-\\d.]+)"
        type: float
        required: false

      - name: rx_power_low_alarm
        pattern: "Rx Power Low Alarm\\s+=\\s+(?P<rx_power_low_alarm>[-\\d.]+)"
        type: float
        required: false

      - name: lane_data
        pattern: "Lane\\s+(?P<lane_id>\\d+).*?TX Power\\s+(?P<lane_tx_power>[-\\d.]+).*?RX Power\\s+(?P<lane_rx_power>[-\\d.]+)"
        type: list
        required: false

output:
  schema:
    - name: interface_name
      type: string
      description: "Controller/interface name"

    - name: laser_state
      type: string
      description: "Current laser state (On, Off, Unknown)"

    - name: tx_power_dbm
      type: float
      description: "Transmit optical power"
      unit: "dBm"

    - name: rx_power_dbm
      type: float
      description: "Receive optical power"
      unit: "dBm"

    - name: laser_bias_ma
      type: float
      description: "Laser bias current"
      unit: "mA"

    - name: temperature_c
      type: float
      description: "Module temperature"
      unit: "Celsius"

    - name: voltage_v
      type: float
      description: "Module supply voltage"
      unit: "V"

    - name: thresholds
      type: object
      description: "DOM alarm thresholds (high/low for TX/RX power)"

    - name: lanes
      type: list
      description: "Per-lane DOM values for multi-lane optics"

validation:
  required_fields:
    - interface_name
    - laser_state
    - tx_power_dbm
    - rx_power_dbm
  type_checks: true

tags:
  - optics
  - dom
  - parser
  - ios-xr

created_by: "CX Health Intelligence Team"
created_date: "2026-01-15"
```

## Example 2: TextFSM-Based Parser (Interface Errors)

```yaml
name: PARSE_INTERFACE_ERRORS
id: "PARSE000002"
version: "1.0.0"
description: |
  Parses interface error counters from IOS-XR show interfaces output.
  Extracts CRC errors, input/output errors, drops, and overruns.

input_type: cli_output
source_format: text

os_types:
  - "IOS-XR"
os_versions: ">=7.0.0"

parser:
  type: textfsm
  textfsm:
    template: |
      Value INTERFACE (\S+)
      Value INPUT_ERRORS (\d+)
      Value OUTPUT_ERRORS (\d+)
      Value CRC_ERRORS (\d+)
      Value INPUT_DROPS (\d+)
      Value OUTPUT_DROPS (\d+)
      Value OVERRUNS (\d+)
      Value GIANTS (\d+)
      Value RUNTS (\d+)

      Start
        ^${INTERFACE} is
        ^\s+${INPUT_ERRORS} input errors, ${CRC_ERRORS} CRC
        ^\s+${INPUT_DROPS} input drops
        ^\s+${OUTPUT_ERRORS} output errors
        ^\s+${OUTPUT_DROPS} output drops
        ^\s+${OVERRUNS} overruns, ${GIANTS} giants, ${RUNTS} runts -> Record

output:
  schema:
    - name: interface
      type: string
      description: "Interface name"

    - name: input_errors
      type: integer
      description: "Total input errors"
      unit: "packets"

    - name: output_errors
      type: integer
      description: "Total output errors"
      unit: "packets"

    - name: crc_errors
      type: integer
      description: "CRC error count"
      unit: "packets"

    - name: input_drops
      type: integer
      description: "Input packet drops"
      unit: "packets"

    - name: output_drops
      type: integer
      description: "Output packet drops"
      unit: "packets"

validation:
  required_fields:
    - interface
  type_checks: true

tags:
  - interface
  - errors
  - counters
  - parser

created_by: "CX Health Intelligence Team"
created_date: "2026-01-15"
```
