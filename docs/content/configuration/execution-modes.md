# Execution Modes

Execution mode controls how strictly the remediation agent follows the Repair Action Workflow (RAW). The mode is carried in the alert prompt and interpreted by the `fault-remediation` skill.

Treat the mode as an operations policy, not only a runtime flag. Strict mode is the foundation for reliable agentic operations with validated intelligence artifacts. Hybrid mode is for ambiguous incidents where the approved workflow is still useful, but more investigation is needed before the agent can decide whether to continue or escalate.

## Setting the Mode

The relay sets `mode` from the `REMEDIATION_MODE` environment variable. The default is `strict`.

```bash
export REMEDIATION_MODE="hybrid-reasoning"
```

The alert simulator also accepts a per-run mode:

```bash
python scripts/simulate_alert.py --direct --mode hybrid-reasoning
python scripts/simulate_alert.py --api http://localhost:8080 --mode strict
```

In headless mode, `scripts/simulate_alert.py --mode` affects the direct prompt it prints, but the relay still uses its own `REMEDIATION_MODE` when building prompts from posted alerts.

## Prompt Example

```json
{
  "alert_def_id": "AD000002",
  "device_hostname": "xr-43",
  "mode": "strict",
  "alert_vars": {
    "device_ip": "192.0.2.43",
    "neighbor_ip": "172.20.20.18",
    "vrf_name": "default",
    "neighbor_as": "3334"
  },
  "raw_message": null
}
```

## Mode Comparison

| Mode | Behavior | Best for |
|------|----------|----------|
| `strict` | Follow the RAW exactly. Do not skip steps, reorder steps, or add diagnostics beyond the workflow. Escalate when outputs do not match and no action condition applies. | Auditable demos, compliance-sensitive operations, reproducible testing, and known faults with approved workflows. |
| `hybrid-reasoning` | Treat the RAW as the guide but apply network-engineering judgment when output is ambiguous or the prescribed path does not fit observed reality. Explain any deviation. | Lab testing, real operations, passive diagnostics, and incidents where the known workflow needs additional investigation. |

## Operating Model

Use strict mode when the fault is known, the artifact has been reviewed, and the organization wants deterministic behavior. This is the demo path and the intended starting point for active remediation.

Use hybrid mode when the workflow gets the agent partway through the incident but the observed state does not fully match the expected pattern. Hybrid mode can gather additional evidence and reason from the RAW, KB context, and live output, but it is still governed.

Hybrid mode does not mean unconstrained autonomy:

- Service-impacting actions still require approval.
- The agent must explain deviations from the RAW.
- If there is no safe next step, the workflow should escalate.
- Active remediation should stay tied to known issues with approved workflows.
- Passive diagnostics can be used more broadly when the risk is low.

## Divergence Points

| Situation | `strict` | `hybrid-reasoning` |
|-----------|----------|--------------------|
| Validation pattern mismatch | Record the mismatch and continue to action selection. Escalate if no condition matches. | Interpret whether the required information is present in another format and explain the deviation. |
| No matching `action_select` condition | Escalate with the collected context. | Use the RAW, KB context, and observed CLI output to choose the safest next step or escalate. |
| Unexpected CLI output | Ignore data that the RAW did not ask for. | Use relevant unexpected data to improve the diagnosis. |
| Config command adjustment | Execute exactly what the RAW prescribes after approval. | Adjust only when clearly required by observed state and explain why. |
| Recovery timing | Obey RAW wait and retry limits. | Allow limited extra observation if the session is visibly progressing and the risk is acceptable. |

## Approval and Questions

Both modes require human approval before `config_cli` actions when Webex is configured. If Webex credentials are missing, `webex-notify` returns `status: skipped`, and the parent agent treats the approval as auto-approved with an explicit warning in the session log. Use this skipped path for local testing, not as the governance model for shared lab or production-like runs.

The live troubleshooting agent is not allowed to pause the workflow with an interactive ask-questions mechanism. If required context is missing and cannot be inferred from artifacts, KB, or device state, the correct behavior is to escalate through the workflow and Webex notification path.