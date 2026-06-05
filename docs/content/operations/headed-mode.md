# Headed Mode (TUI)

Headed mode runs OpenCode interactively in your terminal. It is the easiest way to develop, rehearse, and watch the agent reason through a fault without a Splunk webhook or relay service.

Use `network-troubleshooter` for the actual fault workflow. Use **Builder** if you need help preparing the prompt, checking local files, or adapting simulator values.

## Prerequisites

1. OpenCode installed and authenticated.
2. `opencode.json` updated for your RADKit MCP endpoint.
3. Network devices reachable through RADKit MCP.
4. Python dependencies installed if you want to use `scripts/simulate_alert.py` locally.

## Start OpenCode

Primary action: open OpenCode in this repository and select `network-troubleshooter`.

Manual command:

From the repository root:

```bash
opencode
```

Use the `network-troubleshooter` agent for live fault remediation.

## Generate a Paste-Ready Prompt

The simulator's current default is `AD000002`, BGP Neighbor Administrative Shutdown on IOS XR:

```bash
python scripts/simulate_alert.py --direct
```

It prints a prompt like this:

````text
A fault alert has been received. Diagnose and remediate this fault:

```json
{
  "alert_def_id": "AD000002",
  "device_hostname": "xr-43",
  "mode": "strict",
  "alert_vars": {
    "_time": "1779776665",
    "device_ip": "192.0.2.43",
    "neighbor_ip": "172.20.20.18",
    "vrf_name": "default",
    "neighbor_as": "3334",
    "_raw": "May 26 ... %ROUTING-BGP-5-ADJCHANGE : neighbor 172.20.20.18 Down - Admin. shutdown ...",
    "splunk_sid": "scheduler__admin__search__...",
    "splunk_search_name": "ad000002_bgp_neighbor_admin_shutdown_v2",
    "splunk_app": "search",
    "splunk_owner": "admin",
    "splunk_results_link": "http://splunk-server1:8000/app/search/search?..."
  },
  "raw_message": null
}
```
````

Paste the full prompt into the OpenCode TUI.

## Useful Simulator Flags

| Flag | Default | Purpose |
|------|---------|---------|
| `--mode` | `strict` | Sets `strict` or `hybrid-reasoning` in direct prompt output. |
| `--kb-query-mode` | unset | Adds `quick`, `standard`, or `deep` as an explicit KB retrieval override. |
| `--system` | `xr-43` | Device hostname used as `device_hostname`. |
| `--device-ip` | `192.0.2.43` | Management IP carried in `alert_vars`. |
| `--neighbor-ip` | `172.20.20.18` | BGP neighbor passed to the RAW. |
| `--vrf-name` | `default` | VRF passed to the RAW. |
| `--neighbor-as` | `3334` | Neighbor AS passed to the RAW. |

Example:

```bash
python scripts/simulate_alert.py --direct --mode hybrid-reasoning --kb-query-mode standard
```

## Approval Flow

When the RAW reaches a `config_cli` action, the agent requests approval before changing the device.

In headed mode, you can type the operator response directly into the TUI:

```text
APPROVED
```

or:

```text
DENIED
```

If Webex is configured, the approval card may also appear in the Webex room. The TUI remains useful for demos because you can see the agent's state, RADKit tool calls, and intermediate results as they happen.

## Session Logs

`network-troubleshooter` writes a Markdown log for each live session under:

```text
logs/troubleshooting/<UTC>-<alert_def_id>-<device>.md
```

Use these logs for post-demo review and troubleshooting.