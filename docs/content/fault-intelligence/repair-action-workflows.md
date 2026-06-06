# Repair Action Workflows

A Repair Action Workflow (RAW) is a YAML artifact that turns troubleshooting guidance into ordered validation and repair logic. The `fault-remediation` skill interprets the RAW during live troubleshooting.

## Structure

```yaml
workflow:
  metadata:
    name: BGP_NEIGHBOR_ADMIN_SHUTDOWN_REPAIR
    id: "RAW000002"
    alert_def_id: "AD000002"
  inputs:
    - name: neighbor_ip
      source: "{{ alert_vars.neighbor_ip }}"
      type: string
  action_groups: []
  steps:
    - step_id: "1"
      validation:
        eval_cli:
          commands: []
          pattern: "..."
      action_select: []
```

## Step Model

Each step has two parts:

| Part | Purpose |
|------|---------|
| `validation` | Checks device state with `eval_cli`, `eval_logs`, `eval_var`, `and`, or `or`. |
| `action_select` | Chooses actions based on validation outputs. |

Steps flow sequentially by default. Use `goto` only for non-adjacent jumps.

## Actions

| Action | Meaning |
|--------|---------|
| `resolve` | Successful terminal outcome. |
| `escalate` | Permanent handoff to support or RMA. |
| `fail` | Workflow execution error, not an unresolved fault. |
| `goto` | Jump to another step. |
| `revalidate` | Restart workflow evaluation from the top. |
| `exec_cli` | Execute state-changing exec-mode commands; not for `show` commands. |
| `config_cli` | Apply persistent config changes after approval. Include the config delta and scope, not mode-entry or commit bookends. |
| `wait` | Pause for a duration in seconds. |
| `custom_action` | External action where the workflow resumes afterward. |

## Derivation from RG

`ia-create` derives RAW steps from the RG's Diagnosis and Repair Steps, escalation guidance, and post-repair verification. Commands become validations or actions, sample outputs become patterns, decision points become `action_select` branches, and escalation evidence becomes `escalate.data`.

## Runtime

At runtime, `network-troubleshooter` supplies the alert payload, KB context, and loaded artifact block. `fault-remediation` executes the RAW with RADKit MCP tools and reports events back to the parent agent for logging and Webex notification.