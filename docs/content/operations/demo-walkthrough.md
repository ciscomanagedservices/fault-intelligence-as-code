# Demo Walkthrough

This walkthrough uses `AD000002`: BGP Neighbor Administrative Shutdown on IOS XR. The fault is triggered when an IOS XR router logs `%ROUTING-BGP-5-ADJCHANGE` with `Down - Admin. shutdown`.

Use **Builder** to prepare lab commands and prompts. Use `network-troubleshooter` for the actual fault workflow and approval sequence.

## Scenario

| Field | Value |
|-------|-------|
| Alert definition | `AD000002` |
| Fault Signature | `FS000002-BGP_NEIGHBOR_ADMIN_SHUTDOWN.yml` |
| Repair Action Workflow | `RAW000002-BGP_NEIGHBOR_ADMIN_SHUTDOWN_REPAIR.yml` |
| Remediation Guide | `RG000002-BGP_NEIGHBOR_ADMIN_SHUTDOWN_GUIDE.md` |
| Default device | `xr-43` |
| Default device IP | `192.0.2.43` |
| Default neighbor | `172.20.20.18` |
| Default VRF | `default` |
| Default neighbor AS | `3334` |

## 1. Verify the Baseline

Use RADKit, console access, or your normal lab access path to verify the BGP session is healthy before staging the fault:

Primary prompt for Builder:

```text
Prepare baseline verification commands
```

Manual/reference commands:

```text
show bgp neighbors 172.20.20.18 | include "BGP state"
show bgp summary
show running-config router bgp neighbor 172.20.20.18
```

Expected healthy signal:

```text
BGP state = Established
```

The neighbor stanza should not contain `shutdown`.

## 2. Stage the Fault

Apply administrative shutdown to the BGP neighbor on the IOS XR router. Adjust the local AS if your lab differs; the RAW extracts it later from `show running-config router bgp`.

Primary prompt for Builder:

```text
Prepare AD000002 fault staging commands
```

Manual/reference commands:

```text
configure terminal
router bgp <local_as>
 neighbor 172.20.20.18
  shutdown
 commit
end
```

Verify the fault state:

```text
show bgp neighbors 172.20.20.18 | include "BGP state|Last reset|shutdown"
show running-config router bgp neighbor 172.20.20.18
```

Expected fault signal:

```text
BGP state = Idle (Admin)
```

The running config should show `shutdown` under the neighbor stanza.

## 3. Trigger the Alert

Primary prompt for Builder:

```text
Trigger the AD000002 demo alert
```

=== "Headed mode"

    Generate a prompt and paste it into the OpenCode TUI:

    ```bash
    python scripts/simulate_alert.py --direct
    ```

=== "Headless mode"

    Start OpenCode and the relay, then post the simulated Splunk alert:

    ```bash
    python scripts/simulate_alert.py --api http://localhost:8080
    ```

    The relay creates an OpenCode session and targets `network-troubleshooter` automatically.

## 4. Watch the Workflow

The RAW has four steps:

| Step | Name | What the agent does |
|------|------|---------------------|
| 1 | `confirm_admin_shutdown` | Runs `show bgp neighbors <neighbor> | include "BGP state|Last reset|shutdown"` and confirms `Idle (Admin)`. It also extracts the local BGP AS from `show running-config router bgp`. |
| 2 | `confirm_shutdown_in_config` | Runs `show running-config router bgp neighbor <neighbor>` and confirms the `shutdown` command is present. |
| 3 | `remove_admin_shutdown` | Re-checks the state, requests human approval, then applies `no shutdown` under the neighbor. |
| 4 | `verify_session_reestablishment` | Confirms `BGP state = Established`; otherwise escalates with diagnostic commands. |

Progress appears in the OpenCode session and, when configured, in the Webex room.

## 5. Approve the Change

The approval card proposes the config change equivalent to:

Primary action: approve or deny through the channel shown by the active workflow. In headed mode this is the OpenCode TUI; with Webex configured this is the Webex card.

Reference command equivalent:

```text
configure terminal
router bgp <local_as>
 neighbor 172.20.20.18
  no shutdown
 commit
end
```

=== "Headed mode"

    Type this into the OpenCode TUI when prompted:

    ```text
    APPROVED
    ```

=== "Headless mode with Webex"

    Click Approve on the Webex adaptive card. The relay receives the card submit over its outbound websocket bot and forwards the decision to OpenCode.

If Webex is not configured, the `webex-notify` approval-card event is skipped and the agent auto-approves with a warning in the session log. This is useful for local testing; use Webex approvals for shared lab demos where a human approval step should be visible.

## 6. Verify Resolution

After approval, the agent removes the shutdown, waits as directed by the RAW, and checks the BGP state.

Healthy output:

```text
BGP state = Established
```

If the neighbor does not recover within the RAW's expected window, the workflow escalates and includes evidence commands such as:

```text
show bgp neighbors 172.20.20.18
show bgp summary
show running-config router bgp
show logging | include ADJCHANGE
show tcp brief | include 172.20.20.18
```

## 7. Clean Up

If the agent successfully applied `no shutdown`, the staged fault is removed. Verify the neighbor stanza no longer contains `shutdown`:

```text
show running-config router bgp neighbor 172.20.20.18
```

To manually restore the session if the demo is stopped before approval:

```text
configure terminal
router bgp <local_as>
 neighbor 172.20.20.18
  no shutdown
 commit
end
```