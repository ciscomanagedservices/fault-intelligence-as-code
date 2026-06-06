# Fault Signatures

A Fault Signature (FS) is a YAML artifact that defines when a known fault is present. It is consumed by a fault management system or detection pipeline.

## Structure

```yaml
schema_version: "0.0.1"
metadata:
  name: BGP_NEIGHBOR_ADMIN_SHUTDOWN
  id: "FS000002"
  alert_def_id: "AD000002"
conditions:
  logic: "E1"
  events:
    - event:
        id: "E1"
        type: syslog
        evaluation:
          type: regex
          value: "..."
```

## Key Fields

| Field | Purpose |
|-------|---------|
| `schema_version` | Schema revision for validation. |
| `metadata.name` | Stable uppercase name for the fault. |
| `metadata.id` | `FS######`, aligned with the linked set. |
| `metadata.alert_def_id` | Parent alert definition ID, such as `AD000002`. |
| `metadata.severity` | `CRITICAL`, `MAJOR`, `WARNING`, `MINOR`, or `UNKNOWN`. |
| `conditions.logic` | Boolean expression over event IDs, such as `E1` or `E1 OR E2`. |
| `conditions.events[]` | Event definitions for syslog, alarm, telemetry, SNMP trap, or YANG sources. |
| `evaluation.parameters[]` | Extracted variables passed to the RAW as `alert_vars`. |
| `clear_event` | Optional pattern and lookback window for automatic fault clear. |

## Derivation from RG

`ia-create` derives an FS from the RG's Triggering Events section. Example messages become regex patterns, key values become extraction parameters, and correlation prose becomes `conditions.logic` plus `logic_lookback_time`.

## Example

For `AD000002`, the FS detects an IOS XR BGP adjacency change with `Down - Admin. shutdown` and extracts `neighbor_ip`, `vrf_name`, and `neighbor_as`.

## Pitfalls

- Anchor regex patterns to the specific message type and relevant fields.
- Define one FS event per unique syslog mnemonic.
- Avoid hardcoded device names, slots, interfaces, and neighbor addresses.
- Test regex patterns against representative platform output.
- Include a clear event for faults that can self-recover.