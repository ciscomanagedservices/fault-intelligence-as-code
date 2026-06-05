# RAW Test Framework

The RAW test framework is the deterministic test harness for Repair Action
Workflows. It exercises RAW decision branches without a live device, without
RADKit, without an LLM in the headless path, and optionally without Webex.

A RAW is a decision tree. Every terminal leaf - resolution, escalation,
failure, and denial paths where applicable - should have a test with known CLI
or log output. That makes RAW changes reviewable in pull requests and practical
to run in CI.

## What the Framework Provides

Two runners share one bundle format:

| Runner | Purpose |
|--------|---------|
| `scripts/run_raw_tests.py` | Pure-Python headless runner for CI and local validation. It uses `scripts/lib/raw_interpreter.py` and does not use an LLM, Webex, or RADKit. |
| `network-troubleshooter` test mode | Agent runner for the full demo path, including Webex messages tagged `[TEST]`, scripted approvals, troubleshooting bundle output, and parent-agent orchestration. |

Bundles are co-located with the artifacts they validate so RAW logic, fixtures,
and expected outcomes can move through review together.

## Bundle Layout

Use one test bundle per RAW:

```text
intelligence-artifacts/
  AD000004-example-fault/
    FS000004-EXAMPLE_FAULT.yml
    RAW000004-EXAMPLE_FAULT_REPAIR.yml
    tests/
      RAW000004-EXAMPLE_FAULT_REPAIR.tests.yml
```

The minimum coverage target is one test for each terminal leaf of the RAW's
decision tree.

## Bundle Schema

The current schema version is `"1.0.0"`. The authoritative JSON Schema is
packaged with the `raw-test-author` skill at
`.opencode/skills/raw-test-author/assets/test-bundle.schema.json`.

Validate a bundle through the skill or directly with the packaged validator:

```bash
python .opencode/skills/raw-test-author/scripts/validate_test_bundle.py <bundle-path>
python .opencode/skills/raw-test-author/scripts/validate_test_bundle.py <bundle-path> --strict
```

Other skills and agents should refer to the validator by skill ownership
(`raw-test-author`) rather than treating the script path as a separate public
API.

```yaml
schema_version: "1.0.0"
raw_id: RAW000004
raw_path: intelligence-artifacts/AD000004-example-fault/RAW000004-EXAMPLE_FAULT_REPAIR.yml
fs_path: intelligence-artifacts/AD000004-example-fault/FS000004-EXAMPLE_FAULT.yml

default_approvals:
  default: APPROVED
  overrides: []

tests:
  - name: resolve_via_rollback
    description: Happy path with rollback and verification.
    source: synthetic
    mode: strict
    agent_only: false
    webex_notify: true

    alert_payload:
      incident_id: INC-20260529T120102Z
      alert_def_id: AD000004
      device_hostname: r1
      alert_vars:
        peer_ip: 192.0.2.10
        prefix_count: 142000

    kb_context_override: |
      sev_level: P2
      change_window_active: true
      known_issue_match: KB002
    ia_artifacts_override: null

    responses:
      - step_id: "1"
        command: "show bgp ipv4 unicast neighbors 192.0.2.10 received-routes | count"
        output: |
          Number of routes: 142000

    approvals:
      default: APPROVED
      overrides:
        - step_id: "4"
          command: "rollback configuration to checkpoint pre-anomaly"
          decision: APPROVED

    expected:
      outcome: resolution
      step_path: ["1", "2", "3", "4", "5"]
      must_visit: []
      must_not_visit: []
      variables:
        rollback_applied: true
      webex_events:
        - fault-received
        - step-progress
        - approval-card
        - resolution
```

### Field Reference

| Field | Required | Notes |
|-------|----------|-------|
| `schema_version` | yes | Current value is `"1.0.0"`. |
| `raw_id` | yes | Matches the RAW metadata ID. |
| `raw_path` / `fs_path` | yes | Repo-relative paths resolved by both runners. |
| `default_approvals` | no | Applied to every test that does not set `approvals`. |
| `tests[].name` | yes | Snake case and unique within the bundle. |
| `tests[].source` | yes if synthetic | Use `synthetic` or `captured`; generated fixtures must be marked `synthetic`. |
| `tests[].mode` | no | Defaults to `strict`. `hybrid-reasoning` tests are skipped by the headless runner. |
| `tests[].agent_only` | no | Defaults to `false`. `true` means the headless runner skips the test. |
| `tests[].webex_notify` | no | Defaults to `true`. `false` suppresses Webex notification in the agent runner. |
| `tests[].alert_payload` | yes | Same shape as the webhook relay payload. |
| `tests[].alert_payload.incident_id` | no | Display and correlation metadata for logs and notifications. The agent can mint a local fallback when omitted. |
| `tests[].responses` | yes | Canned CLI responses. Match by `(step_id, command)`, then by `command` only. |
| `tests[].approvals` | no | Same shape as `default_approvals`; consulted for every approval-needed event. |
| `tests[].expected` | yes | Must include at least `outcome`. `step_path` is strongly recommended for `strict` tests. |

## Headless Runner

Use the headless runner for CI and deterministic local checks:

```bash
python scripts/run_raw_tests.py --bundle intelligence-artifacts/AD000002-bgp-neighbor-admin-shutdown-xr/tests/RAW000002-BGP_NEIGHBOR_ADMIN_SHUTDOWN_REPAIR.tests.yml
python scripts/run_raw_tests.py --all
python scripts/run_raw_tests.py --bundle <path> --test resolve_via_rollback
python scripts/run_raw_tests.py --all --junit out/raw-test-results.xml --summary out/raw-test-summary.md --json out/raw-test-results.json
python scripts/run_raw_tests.py --all --no-webex
```

The runner skips tests with `agent_only: true` or `mode: hybrid-reasoning`.
It exits with `0` when all selected tests pass or skip, and non-zero on any
failure or error. Per-test artifacts are written under
`logs/test-runs/<UTC>-<raw-id>-<test-name>/`.

`TestResult.status` is one of `pass`, `fail`, `skipped`, or `error`.

## Agent Runner

Invoke the `network-troubleshooter` agent with a payload containing
`test_bundle_path` and, optionally, `test_name`.

```text
Run the RAW test bundle for AD000002 / RAW000002 in test mode.

{
  "alert_def_id": "AD000002",
  "device_hostname": "xr-43",
  "mode": "strict",
  "test_bundle_path": "intelligence-artifacts/AD000002-bgp-neighbor-admin-shutdown-xr/tests/RAW000002-BGP_NEIGHBOR_ADMIN_SHUTDOWN_REPAIR.tests.yml",
  "test_name": "resolve_via_no_shutdown",
  "webex_notify": false
}
```

When `test_name` is omitted, the agent runs every test in the bundle
sequentially and emits one result block per test.

The agent runner:

- Reads the bundle and loads the FS and RAW declared by `fs_path` and
  `raw_path`.
- Uses `kb_context_override` or `ia_artifacts_override` when provided;
  otherwise it uses the normal reader path.
- Injects each test's `responses` and `approvals` into `fault-remediation` as
  `test_bundle`.
- Tags Webex messages with `[TEST]` and `test_run_id` when Webex is enabled.
- Writes `session.md`, `result.json`, and bundle artifacts under
  `logs/test-runs/<UTC>-<raw-id>-<test-name>/`.

## Hard Rules

- Do not call `radkit_*` while a `test_bundle` is in play. Any such call is a
  `TEST_MODE_VIOLATION` and the agent must abort the test.
- Do not execute real waits. `wait` actions are no-ops in test mode.
- Do not write test sessions under `logs/troubleshooting/`; use
  `logs/test-runs/`.
- Missing canned CLI output is a test failure with
  `reason: missing-canned-response` and must name the `(step_id, command)`
  pair.
- Approval cards can still be posted when Webex is enabled, but the agent must
  consume the scripted decision from `approvals.overrides` or
  `approvals.default` without waiting for a human click.
- Tests that depend on parent-agent behavior the headless RAW interpreter
  cannot see, such as Webex click verification or LLM judgement, must set
  `agent_only: true`.

## Authoring Bundles

Use the `raw-test-author` skill for new RAWs. It reads the RAW and paired FS,
enumerates terminal leaves, creates deterministic CLI or log fixtures, marks
generated fixtures as `source: synthetic`, and writes the bundle at the
canonical `tests/<RAW-id>-<slug>.tests.yml` path.

Do not hand-author bundles for new RAWs when the skill is available. Let the
skill enumerate paths so coverage gaps are visible in review.

## Published Examples

- `intelligence-artifacts/AD000002-bgp-neighbor-admin-shutdown-xr/tests/RAW000002-BGP_NEIGHBOR_ADMIN_SHUTDOWN_REPAIR.tests.yml`
- `intelligence-artifacts/AD000003-bgp-max-prefix-adjchange-xr/tests/RAW000003-BGP_NEIGHBOR_MAX_PREFIX_LIMIT_EXCEEDED_REPAIR.tests.yml`

## File Map

| Path | Role |
|------|------|
| `scripts/lib/raw_interpreter.py` | Pure-Python RAW interpreter. |
| `scripts/run_raw_tests.py` | Headless test runner CLI. |
| `.opencode/skills/fault-remediation/SKILL.md` | Runtime RAW interpreter skill with `test_bundle` handling. |
| `.opencode/agents/network-troubleshooter.md` | Parent agent test-mode orchestration. |
| `.opencode/skills/webex-notify/SKILL.md` | Webex templates; accepts `test_title_prefix` and `test_run_id`. |
| `.opencode/skills/raw-test-author/SKILL.md` | Test bundle authoring and validation skill. |
| `intelligence-artifacts/<alert-def-id>/tests/<raw-id>.tests.yml` | Co-located RAW test bundle. |
| `logs/test-runs/<UTC>-<raw-id>-<test-name>/` | Per-test session log and `result.json`. |