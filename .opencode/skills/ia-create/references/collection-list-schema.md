---
source: source-data/HEALTH-IC-PROPOSAL.md
created: 2026-02-21
purpose: >-
  Full schema definition and example for Diagnostic Data Collection Lists
  (diagnostic-collection-list/v1.0.0). Referenced by the health-intelligence
  skill during YAML artifact generation.
---

# Diagnostic Data Collection List Schema

> **Status: STUB** — This artifact type is fully documented and schema-validated.
> Generation support is coming in a future release. The schema below is the
> authoritative reference for the Collection List data model.

**Schema**: `diagnostic-collection-list/v1.0.0`

Define curated sets of CLI commands, gNMI paths, and telemetry subscriptions for
systematic diagnostic data collection. Collection lists are organized by component,
use case, or diagnostic scenario.

## Schema Definition

```yaml
# Schema: diagnostic-collection-list/v1.0.0

name: string                    # Unique identifier (UPPERCASE_SNAKE_CASE)
id: string                      # Unique string ID, pattern "CL######" (6-digit zero-padded, e.g. "CL000001")
version: string                 # Semantic version (e.g., "1.0.0")
description: string             # Human-readable description of the collection purpose
category: enum                  # hardware, software, interface, protocol, system
component: string               # Target component (e.g., FAN, OPTICS, CPU, MEMORY)

# Applicability filters
product_ids: list[string]       # Supported hardware PIDs
os_types: list[string]          # Supported OS types (IOS-XR, NX-OS, IOS-XE, SONiC)
os_versions: string             # Version constraint (e.g., ">=7.5.0")

# Collection items
collections:
  - id: string                  # Unique item identifier within this list (lowercase_snake_case)
    name: string                # Human-readable name
    type: enum                  # cli, gnmi_get, gnmi_subscribe, netconf, api
    priority: enum              # required, recommended, optional

    # For CLI-based collection
    cli:
      command: string           # CLI command to execute
      parser_ref: string        # Reference to parser definition (optional)
      timeout: integer          # Command timeout in seconds

    # For gNMI-based collection
    gnmi:
      path: string              # YANG path (OpenConfig or native)
      origin: string            # Origin: openconfig, cisco-ios-xr, etc.
      encoding: enum            # json, json_ietf, proto
      mode: enum                # get, subscribe_once, subscribe_stream
      sample_interval: integer  # For streaming (milliseconds)

    # For NETCONF-based collection
    netconf:
      xpath: string             # XPath filter
      namespace: string         # XML namespace

    # Output handling
    output:
      format: enum              # text, json, xml, table
      store_as: string          # Variable name for parsed output

# Metadata
tags: list[string]              # Classification tags (lowercase)
created_by: string              # Author/team
created_date: string            # ISO 8601 date (YYYY-MM-DD)
```

## Field Notes

- **`name`**: Use `UPPERCASE_SNAKE_CASE`. Should describe the component and diagnostic purpose
  (e.g., `OPTICS_TRANSCEIVER_DIAGNOSTICS`, `CPU_UTILIZATION_COLLECTION`, `BGP_NEIGHBOR_DIAGNOSTICS`).
- **`id`**: String matching `^CL\d{6}$` (6-digit zero-padded, e.g. `CL000001`). Increment from the last known ID.
- **`collections[].id`**: Use `lowercase_snake_case` within each list. Must be unique within the list.
- **`collections[].type`**: Determines which sub-block (`cli`, `gnmi`, or `netconf`) to include.
  Only include the sub-block matching the type.
- **`collections[].cli.command`**: Use `{{ variable }}` for parameterized commands
  (e.g., `show controllers optics {{ interface }}`).
- **`collections[].cli.parser_ref`**: Optional reference to a Parser artifact by name.
  This creates a link from the Collection List to a Parser.
- **`collections[].output.store_as`**: Variable name used downstream by Parsers and
  Health Check Rules. Use `lowercase_snake_case`.
- **`os_versions`**: Use comparison operators: `>=7.5.0`, `>=7.0.0 <8.0.0`, `*` for any version.

## Example: Optics Diagnostic Collection List

```yaml
name: OPTICS_TRANSCEIVER_DIAGNOSTICS
id: "CL000001"
version: "1.2.0"
description: |
  Comprehensive diagnostic data collection for optical transceiver modules.
  Collects DOM (Digital Optical Monitoring) data, interface counters,
  and transceiver inventory information for health assessment.

category: hardware
component: OPTICS

product_ids:
  - "8201-SYS"
  - "8202-SYS"
  - "8808-SYS"
  - "NCS-55A1-36H-SE-S"

os_types:
  - "IOS-XR"

os_versions: ">=7.5.0"

collections:
  # CLI-based collections
  - id: "optics_inventory"
    name: "Transceiver Inventory"
    type: cli
    priority: required
    cli:
      command: "show inventory | include transceiver|Optics"
      parser_ref: "PARSE_INVENTORY_OPTICS"
      timeout: 30
    output:
      format: text
      store_as: optics_inventory

  - id: "optics_dom_all"
    name: "DOM Values - All Interfaces"
    type: cli
    priority: required
    cli:
      command: "show controllers optics {{ interface }}"
      parser_ref: "PARSE_OPTICS_CONTROLLER"
      timeout: 60
    output:
      format: text
      store_as: optics_dom

  - id: "interface_counters"
    name: "Interface Error Counters"
    type: cli
    priority: required
    cli:
      command: "show interfaces {{ interface }} | include errors|CRC|drops"
      parser_ref: "PARSE_INTERFACE_ERRORS"
      timeout: 30
    output:
      format: text
      store_as: interface_errors

  - id: "optics_phy_details"
    name: "Physical Layer Details"
    type: cli
    priority: recommended
    cli:
      command: "show controllers {{ interface }} phy"
      parser_ref: "PARSE_PHY_DETAILS"
      timeout: 45
    output:
      format: text
      store_as: phy_details

  # gNMI-based collections
  - id: "gnmi_optics_state"
    name: "OpenConfig Optics State"
    type: gnmi_get
    priority: recommended
    gnmi:
      path: "/components/component[name={{ interface }}]/optical-channel/state"
      origin: openconfig
      encoding: json_ietf
    output:
      format: json
      store_as: oc_optics_state

  - id: "gnmi_interface_counters"
    name: "OpenConfig Interface Counters"
    type: gnmi_get
    priority: recommended
    gnmi:
      path: "/interfaces/interface[name={{ interface }}]/state/counters"
      origin: openconfig
      encoding: json_ietf
    output:
      format: json
      store_as: oc_interface_counters

  - id: "gnmi_optics_stream"
    name: "Streaming DOM Telemetry"
    type: gnmi_subscribe
    priority: optional
    gnmi:
      path: "/components/component[name={{ interface }}]/optical-channel/state"
      origin: openconfig
      encoding: json_ietf
      mode: subscribe_stream
      sample_interval: 10000
    output:
      format: json
      store_as: optics_stream

tags:
  - optics
  - transceiver
  - dom
  - physical-layer
  - interface

created_by: "CX Health Intelligence Team"
created_date: "2026-01-15"
```
