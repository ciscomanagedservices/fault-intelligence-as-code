---
name: raw-test-author
description: Author and validate RAW test bundles. Use when asked to create tests for RAW######, generate fixtures, add RAW branch coverage, validate *.tests.yml, or when a RAW changes without matching tests.
domain: fault-management
workflow: authoring
---

# raw-test-author — Focused RAW Test Bundle Authoring

## Tier 0

Create or validate co-located RAW test bundles at
`intelligence-artifacts/<AD######>-<slug>/tests/<RAW######>-<slug>.tests.yml`.
Default to a fast, narrow workflow: use the supplied RAW path/ID, its same-folder
FS, the schema, the validator, and the headless runner. Do not do repo-wide
searches unless exact paths are unknown or validation fails.

## Tier 1

### Fast authoring workflow

1. **Resolve exact files without broad search**
   - If the user gives `RAW######`, use targeted glob `intelligence-artifacts/**/RAW######*.yml`.
   - Once found, stay in that AD folder.
   - Pair the FS from the same folder: `FS*.yml` whose metadata `alert_def_id`
     matches the RAW metadata `alert_def_id`.
   - If a bundle already exists, read it and merge new tests; never overwrite
     existing test bodies.

2. **Read only what is needed first**
   - Required: RAW, paired FS, existing bundle if present.
   - Optional: one canonical example bundle only if unsure about formatting.
   - Do not inspect `scripts/`, `.opencode/agents/`, or unrelated artifact
     folders unless validation/headless execution fails and script behavior must
     be checked.

3. **Enumerate terminal leaves from the RAW**
   - Walk `workflow.steps` and each `action_select` branch.
   - One test per terminal `resolve`, `escalate`, or `fail` leaf, minimum.
   - Include `expected.step_path` and `expected.action_ids` whenever the path is
     deterministic.
   - Add approval-denial tests for service-impacting `exec_cli` or `config_cli`
     paths that benefit from explicit safety coverage.

4. **Generate minimal deterministic fixtures**
   - Build CLI output directly from the RAW regex and branch intent.
   - External docs are optional enrichment, not the default. Use them only when
     output shape is genuinely uncertain and the user asked for realism.
   - Use RFC 5737 documentation IPs and RFC 5398 private ASNs; never use real
    real hostnames, customer prefixes, or live ASNs.
   - For `eval_logs`, use `log_entries` fixtures:
     ```yaml
     log_entries:
       - "%ROUTING-BGP-5-ADJCHANGE : neighbor 192.0.2.17 Down - BGP Notification received, Maximum Number of Prefixes Reached"
       - timestamp: "2026-05-29T12:00:00Z"
         message: "%ROUTING-BGP-5-ADJCHANGE : neighbor 192.0.2.17 Up"
     ```
     Entries without timestamps are treated as within the RAW lookback window.

5. **Use the strict bundle shape**
   - `schema_version: "1.0.0"`
   - `raw_id`, `raw_path`, `fs_path`, `default_approvals`, `tests`
   - Each generated test sets `source: synthetic`.
   - Each test includes `alert_payload.mode` and `alert_payload.alert_vars`.
   - `approvals.overrides` is a list of `{step_id, command, decision}`.

6. **Validate and run headless before declaring done**
   ```bash
   python .opencode/skills/raw-test-author/scripts/validate_test_bundle.py <bundle>
   python .opencode/skills/raw-test-author/scripts/validate_test_bundle.py <bundle> --strict
   python scripts/run_raw_tests.py --bundle <bundle>
   ```
   Every deterministic test should pass headlessly. If not, fix the fixture or
   the runner. Do not mark deterministic RAW logic `agent_only` just to hide a
   runner limitation.

### Header required in every generated bundle

Start each bundle with a comment block containing:

- RAW ID/name and short scope description.
- Enumerated terminal leaves covered.
- Exact commands for all-tests, single-test, and report-output headless runs.
- Agent-runner sample prompt for `network-troubleshooter` test mode.

## Tier 2

### Validate-only mode

Input: `bundle_path`, optional `strict`.

Run the packaged validator. Do not edit files.

```bash
python .opencode/skills/raw-test-author/scripts/validate_test_bundle.py <bundle.tests.yml>
python .opencode/skills/raw-test-author/scripts/validate_test_bundle.py <bundle.tests.yml> --strict
python .opencode/skills/raw-test-author/scripts/validate_test_bundle.py <bundle.tests.yml> --quiet --format json
```

Exit codes:

| Code | Meaning |
|------|---------|
| `0` | Valid; warnings allowed unless `--strict`. |
| `1` | Schema violation, duplicate name, or strict warning. |
| `2` | Tool/file/YAML/dependency error. |

### Bundle schema and runner usage

The authoritative schema is packaged with this skill at
`assets/test-bundle.schema.json`; the validator is
`scripts/validate_test_bundle.py`. The current `schema_version` is `"1.0.0"`.
Generated bundles must include `raw_id`, `raw_path`, `fs_path`,
`default_approvals`, and `tests`. Each test must include `name`,
`alert_payload`, `responses`, and `expected`; generated fixtures must include
`source: synthetic`. `approvals.overrides` entries use
`{step_id, command, decision}`.

Headless runner commands to include in generated bundle headers:

```bash
python scripts/run_raw_tests.py --bundle <bundle>
python scripts/run_raw_tests.py --bundle <bundle> --test <test_name>
python scripts/run_raw_tests.py --bundle <bundle> --junit out/raw-test-results.xml --summary out/raw-test-summary.md --json out/raw-test-results.json
```

Agent-runner prompt shape to include in generated bundle headers:

```text
Run the RAW test bundle in test mode.

{
  "alert_def_id": "<AD######>",
  "device_hostname": "<test-device>",
  "mode": "strict",
  "test_bundle_path": "<bundle>",
  "test_name": "<test_name>",
  "webex_notify": false
}
```

The headless runner skips `agent_only: true` and `mode: hybrid-reasoning`
tests. Agent-only tests are for behavior outside the deterministic RAW
interpreter, such as Webex click verification or LLM judgement.

### Draft vs published IDs

Use `RAW000000` / `FS000000` only for drafts. Published bundles must match the
artifact metadata IDs. `ia-publish` rewrites draft placeholders when publishing.

### Runner capability policy

Prefer expanding the deterministic runner over skipping tests when a RAW feature
is deterministic:

| RAW feature | Headless expectation |
|-------------|----------------------|
| `eval_cli` | Supported by `responses`. |
| `eval_var` | Supported. Quote string literals in RAW conditions, e.g. `vrf_name == "default"`. |
| validation `and`/`or` | Supported. |
| action-select boolean `and`/`or`/`not` | Supported. |
| interpolated regex patterns | Supported. |
| `eval_logs` | Supported by `log_entries`. |
| `exec_cli` / `config_cli` approvals | Supported through scripted `approvals`. |
| Webex rendering/click verification | Agent-only; integration behavior, not RAW logic. |
| LLM judgement (`hybrid-reasoning`) | Agent-only; headless cannot evaluate free-form judgement. |

### AD folder layout

Only these entries belong at the AD root:

```text
FS*.yml
RAW*.yml
RG*.md
tests/<RAW######>-<slug>.tests.yml
docs/
```

Put notes, analysis, screenshots, and research under `docs/`, not beside the
artifacts.

## Common failure modes

- **Broad repo searching by default.** Start with exact paths and same-folder
  files. Search wider only when exact lookup fails.
- **Using external docs before reading the RAW.** The RAW regex tells you the
  minimum fixture content needed.
- **Marking deterministic branches `agent_only`.** Patch fixtures or runner
  capability instead.
- **Forgetting `source: synthetic`.** Generated CLI/log output must be labeled.
- **Missing action IDs.** Include `expected.action_ids` for deterministic paths;
  the runner asserts them.
- **Unquoted RAW string literals.** Conditions should use quoted strings, e.g.
  `vrf_name == "default"`, not `vrf_name == default`.
- **Missing log fixtures.** Any RAW with `eval_logs` needs `log_entries` tests.
- **Skipping functional verification.** Always run validator and headless runner
  before reporting completion.

## Reference

- Schema: `.opencode/skills/raw-test-author/assets/test-bundle.schema.json`
- Validator: `.opencode/skills/raw-test-author/scripts/validate_test_bundle.py`
- Runner: `scripts/run_raw_tests.py`
- Interpreter: `scripts/lib/raw_interpreter.py`
- User-facing test framework: `docs/content/fault-intelligence/test-framework.md`
- Agent test contract: `.opencode/agents/network-troubleshooter.md`
- Canonical examples:
  - `intelligence-artifacts/AD000002-bgp-neighbor-admin-shutdown-xr/tests/RAW000002-BGP_NEIGHBOR_ADMIN_SHUTDOWN_REPAIR.tests.yml`
  - `intelligence-artifacts/AD000003-bgp-max-prefix-adjchange-xr/tests/RAW000003-BGP_NEIGHBOR_MAX_PREFIX_LIMIT_EXCEEDED_REPAIR.tests.yml`
