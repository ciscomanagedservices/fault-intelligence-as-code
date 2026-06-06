# Local Agent Prompt Test

This quickstart runs the demo the easiest way: install OpenCode, open this repository in OpenCode, select the `network-troubleshooter` agent, paste one test prompt, and watch the agent execute a Repair Action Workflow with simulated network-device responses.

You do not need Splunk, Docker, Webex, RADKit, or Python for this path. The prompt points the agent at a checked-in RAW test bundle, so the agent uses canned CLI output instead of touching a real device.

For the other setup paths:

| Goal | Start here |
|------|------------|
| Connect the demo to your own routers, RADKit MCP, Splunk, and Webex | [Lab Environment](lab-environment.md) |
| Create your own Fault Signature, Repair Action Workflow, and Remediation Guide artifacts | [Artifact Authoring](artifact-authoring.md) |
| Maintain the KB vault | [Knowledge Base Curator](kb-curator.md) |

## 1. Open a Terminal in This Repo

From a command prompt or terminal:

```bash
cd c:/src/fault-intelligence-as-code
```

If you cloned the repo somewhere else, use that path instead.

## 2. Start OpenCode

For the browser UI:

```bash
opencode web
```

OpenCode will launch or print a local browser URL, usually `http://localhost:4096`.

If you prefer the terminal UI, run:

```bash
opencode
```

## 3. Select the Network Troubleshooter Agent

In OpenCode, start a new chat and select the `network-troubleshooter` agent.

This matters because the test-mode behavior is defined on that agent. In test mode, it must read the test bundle, simulate CLI responses, avoid RADKit, apply scripted approvals, and write test-run artifacts under `logs/test-runs/`.

## 4. Paste One Test Prompt

Pick either scenario and paste the full prompt into the `network-troubleshooter` chat.

### Option A: AD000002 Admin Shutdown

This is the primary demo scenario. It simulates a BGP neighbor that is down because `shutdown` is present in the IOS XR BGP neighbor configuration. The workflow confirms the state, applies the scripted `no shutdown` repair, and verifies the neighbor returns to `Established`.

```text
Run the RAW test bundle for AD000002 / RAW000002 in test mode.

Simulate network-device responses from the test bundle. Do not use RADKit, Splunk, Webex, Docker, or the alert simulator script. Use the network-troubleshooter test-mode behavior and write the generated test artifacts under logs/test-runs/.

{
  "alert_def_id": "AD000002",
  "device_hostname": "xr-43",
  "mode": "strict",
  "test_bundle_path": "intelligence-artifacts/AD000002-bgp-neighbor-admin-shutdown-xr/tests/RAW000002-BGP_NEIGHBOR_ADMIN_SHUTDOWN_REPAIR.tests.yml",
  "test_name": "resolve_via_no_shutdown",
  "webex_notify": false
}
```

### Option B: AD000003 Maximum Prefix

This scenario simulates a BGP neighbor reset caused by maximum-prefix enforcement. The workflow uses canned device responses to identify the recovery path, run the scripted rollback/clear actions, and verify recovery.

```text
Run the RAW test bundle for AD000003 / RAW000003 in test mode.

Simulate network-device responses from the test bundle. Do not use RADKit, Splunk, Webex, Docker, or the alert simulator script. Use the network-troubleshooter test-mode behavior and write the generated test artifacts under logs/test-runs/.

{
  "alert_def_id": "AD000003",
  "device_hostname": "xr-edge-01",
  "mode": "strict",
  "test_bundle_path": "intelligence-artifacts/AD000003-bgp-max-prefix-adjchange-xr/tests/RAW000003-BGP_NEIGHBOR_MAX_PREFIX_LIMIT_EXCEEDED_REPAIR.tests.yml",
  "test_name": "resolve_default_vrf_recovery",
  "webex_notify": false
}
```

## 5. Watch the Remediation Flow

The agent should move through the same major stages as a live alert, but with simulated device responses:

| Stage | What to watch for |
|-------|-------------------|
| Test-mode detection | The agent notices `test_bundle_path` and avoids live RADKit calls. |
| Artifact loading | The agent loads the matching FS, RAW, RG, and test bundle. |
| Validation | The RAW validation steps consume canned CLI output from the test bundle. |
| Approval handling | Config actions use scripted approvals from the test bundle. |
| Remediation | The agent follows the RAW action path and reports the terminal outcome. |
| Summary | The agent emits a session summary with the step path, variables, and result. |

For this quickstart, a successful run should not ask you to start Splunk, configure Webex, run Docker, or connect to a router.

## 6. Inspect the Generated Artifacts

After the run finishes, look under:

```text
logs/test-runs/
```

Each agent test run creates a timestamped folder. The exact contents depend on the scenario and agent path, but expect artifacts like:

| Artifact | Purpose |
|----------|---------|
| `session.md` | Human-readable troubleshooting transcript and decision log. |
| `result.json` | Structured test result: outcome, step path, variables, expectations, and diffs. |
| `bundle/cli/` | Captured or simulated command evidence used by the workflow. |
| `bundle/report.html` | Troubleshooting bundle report, when generated. |

If you use VS Code, open `logs/test-runs/` in the Explorer and sort by modified time. From PowerShell, you can list the newest folders with:

```powershell
Get-ChildItem logs\test-runs | Sort-Object LastWriteTime -Descending | Select-Object -First 5
```

## 7. Try More Test Paths

The prompts above run one happy-path test each. To run every canned path in a bundle, paste the same prompt but remove the `test_name` line.

For `AD000002`, the bundle includes paths for successful repair, non-admin shutdown escalation, transient recovery, failed recovery, external recovery, and approval denial.

For `AD000003`, the bundle includes paths for already-recovered sessions, rollback recovery, policy discovery failures, approval denial, and post-rollback recurrence.

## 8. Next Steps

| Need | Doc |
|------|-----|
| Connect to a real lab | [Lab Environment](lab-environment.md) |
| Create a new fault scenario | [Artifact Authoring](artifact-authoring.md) |
| Understand the agent architecture | [Agents](../architecture/agents.md) |
| Troubleshoot setup issues | [Troubleshooting](../operations/troubleshooting.md) |
