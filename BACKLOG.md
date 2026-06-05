# BACKLOG — DEVNET-3171

Action items from Jason's review of the fault-remediation skill and AGENTS.md (2026-05-14).

---

## Priority 1: Agent Architecture

- [ ] **Talk with Steve about REST API vs SDK usage**
  We are currently using the OpenCode REST API rather than the OpenCode SDK.
  Determine whether that difference matters for architecture, capabilities,
  maintainability, or the demo story.

- [ ] **Create a dedicated OpenCode agent for network troubleshooting**
  Configure as code (agent file in repo) so OpenCode recognizes it as an available
  agent and the OpenCode SDK can select it as the target agent for a session.
  Purpose: expert network troubleshooter.

- [ ] **Agent instructions should describe available skills**
  The agent should know when to select the fault-remediation skill (and eventually
  others) and what each skill's purpose is.

- [ ] **Move high-level context from skill into agent instructions**
  Concepts like RAW structure, wiki/RAG awareness, and domain context belong in
  the agent's system prompt — the skill should only contain execution logic.

- [ ] **Set up sub-agent architecture for wiki reading**
  Consider creating a dedicated wiki-reading sub-agent instead of skill-to-skill
  delegation. Research how agent → sub-agent handoffs work in OpenCode
  (permission.task glob, hidden:true, task prompt vs. full history).

- [ ] **Configure agent permissions**
  The troubleshooting agent should only be allowed to invoke the wiki sub-agent.
  Sub-agent receives a specific task prompt, not full conversation history.

- [ ] **Specify models for primary agent and sub-agent**
  Pin which LLM model is used for the troubleshooting agent and for the wiki agent.

---

## Priority 2: Skill Fixes (fault-remediation)

- [ ] **Prevent agent from using Ask Questions tool to pause workflow**
  Questions should be treated as escalations, not interactive pauses. Add explicit
  instruction: do not use ask-questions tool; if you need information you don't
  have, escalate.

- [ ] **Fix typo: "knowledge base article" → "knowledge base articles" (plural)**
  In hybrid-reasoning mode description.

- [ ] **Remove hardcoded KB article reference from step 0a-3**
  Currently hardcodes `KB002-bgp-acl-tcp179.yaml`. KB articles should be read
  via wiki-query in hybrid mode, not loaded directly in step 0a.

- [ ] **Add schema validation before execution**
  Validate that the loaded RAW file matches the expected schema before building
  the action plan. Fail early if the RAW is malformed.

- [ ] **Load RAW schema as context for the agent**
  The schema itself should be loaded so the agent knows the workflow language
  and can correctly interpret and build the action plan.

- [ ] **Add detailed workflow-language documentation**
  Ensure extremely detailed docs on how to interpret RAW concepts (action_select,
  validation, action_groups, revalidate semantics, etc.) so the agent builds
  correct action plans.

- [ ] **Fix `revalidate` action description**
  Currently says "Go back to the validation block of the CURRENT step." Correct
  meaning: go back to the first step and begin evaluation again (re-run the
  entire workflow). Needs clarification and testing.

- [x] **Fix `config_cli` assumption about `conf t` / `end`** *(resolved — SKILL.md now specifies OS-aware wrapping; interpreter adds `configure terminal`/`commit`/`end` bookends)*

- [ ] **Fix `wait` action implementation**
  LLMs cannot reliably measure time. Execute a script/sleep command via a tool
  call instead of relying on the LLM to "wait."

- [ ] **Consider a variable store file**
  Instead of hoping the LLM tracks variables correctly, write/read variables
  to a temporary file for reliability.

- [ ] **Add structured action logging**
  Capture actions being taken in a structured log (separate from or in addition
  to OpenCode session logs). Evaluate whether session logs are sufficient or if
  explicit logging instructions are needed.

- [ ] **Move IOS XE CLI quirks to wiki or golden-rules file**
  These are lab-specific and may grow over time. Options: (a) put in wiki as
  execution rules that always get included, or (b) keep as a dedicated
  golden-rules file in the skill that is always loaded.

- [ ] **Remove happy-path execution example from the skill**
  The "Complete Example: Fault AD000002" section will influence LLM behavior and
  looks like cheating when open-sourced. Move to docs/project-docs/ or a test fixture.

- [x] **Fix `config_cli` vs `config-cli` naming inconsistency** *(resolved — all action names normalized to underscore form project-wide)*

---

## Priority 3: Webex Integration

- [ ] **Extract Webex notifications into a separate skill**
  For maximum flexibility. The Webex skill would own the send logic, templates,
  and scripts for interacting with the Webex API.

- [ ] **Templatize Webex notification messages**
  Include customizable templates for each notification type (fault received,
  step progress, approval card, resolution, escalation, failure).

- [ ] **Figure out WEBEX_BOT_TOKEN / WEBEX_ROOM_ID population from .env**
  Currently these must be manually set in the environment before launching
  OpenCode. Automate loading from .env file.

- [ ] **Track: Webex bot API service as potential architecture**
  (Deprioritized) A separate bot service with an API that handles send/receive.
  Probably not worth the complexity for the demo, but track for future.

---

## Priority 4: Test Mode

- [x] **Add a test mode that simulates device responses**
  Implemented as RAW test bundles at `intelligence-artifacts/<alert-def-id>/tests/<raw-id>.tests.yml`.
  See `docs/content/fault-intelligence/test-framework.md`. Headless runner: `scripts/run_raw_tests.py`.
  Agent test mode: see **Test Mode** section in `.opencode/agents/network-troubleshooter.md`
  and `.opencode/skills/fault-remediation/SKILL.md`.

- [x] **Test mode should simulate MCP server tool responses**
  Skill detects `test_bundle` input and routes CLI execution through canned
  `(step_id, command) → output` responses. `radkit_*` calls are forbidden while
  a `test_bundle` is in play (`TEST_MODE_VIOLATION`).

- [x] **Create a test-creation skill**
  `.opencode/skills/raw-test-author/SKILL.md`. Enumerates terminal leaves of a
  RAW, generates one test per leaf, fills synthetic CLI output (marked
  `source: synthetic`), and writes the canonical bundle path. Worked example:
  `intelligence-artifacts/AD000002-bgp-neighbor-admin-shutdown-xr/tests/RAW000002-BGP_NEIGHBOR_ADMIN_SHUTDOWN_REPAIR.tests.yml`
  (5 tests, 4 pass + 1 agent-only skipped under the headless runner).

---

## Priority 5: Skills & Repository Organization

- [ ] **Move skills from `.opencode/skills/` to `.agents/skills/`**
  For backwards compatibility with other agent harnesses.

- [ ] **Add vendored wiki skills to repository**
  Bring in: wiki, wiki-query, wiki-ingest, wiki-lint, save skills from
  kb-wiki upstream into `.agents/skills/`.

- [ ] **Add intelligence artifact skills to repository**
  (Details TBD — whatever Jason refers to as "intelligence artifact skills".)

- [x] **Update wiki vault location**
  Moved from `samples/knowledge/wiki/` to `kb/`. Updated all skill overrides, AGENTS.md, README, and docs.

---

## Priority 6: AGENTS.md Overhaul

- [ ] **Rewrite AGENTS.md from scratch**
  Current content is largely noise and outdated. Strip and rebuild with only
  what is accurate and actionable for the current project state.

- [ ] **Update or remove Build and Test Commands section**
  The listed test, lint, and typecheck commands are probably no longer valid.

- [ ] **Update or remove input/context/output pipeline section**
  This workflow is not being followed in practice.

---

## Priority 7: Research & Questions

- [ ] **Research: do metadata fields (domain, workflow) in SKILL.md frontmatter
  actually impact skill selection in OpenCode?**
  Or are they just decorative?

- [ ] **Research: can you force the input format sent to the agent?**
  Can we constrain what structure the fault alert payload must have?

- [ ] **Research: how do file system reads translate to deployed frameworks?**
  If porting to LangGraph/Identric/etc., how would inputs be provided instead
  of file reads? Be ready to explain this at the session.

- [ ] **Assess KB query mode value**
  Is the quick/standard/deep mode system actually useful? Is it a carryover
  from the original wiki skills or invented for this project? Does it add
  meaningful value or just complexity?

- [ ] **Presentation note: highlight skills as "tools for your agent"**
  In the session, explain how invoking a skill in OpenCode is analogous to
  calling a native tool — just configured as code rather than via MCP.

- [ ] **Question for Steve: how are you launching for testing?**
  What's your current test loop?

---

## Completed

- [x] **Defer ID assignment + integrate raw-test-author + standardize AD folder layout** (2026-05-29)
  - Draft artifacts in `ia-drafts/` now carry placeholder IDs (`<PREFIX>000000`); real sequential IDs allocated by `ia-publish` at publish time from `intelligence-artifacts/index.json`.
  - `raw-test-author` made self-contained: packaged JSON Schema (`assets/test-bundle.schema.json`) + validator (`scripts/validate_test_bundle.py`); standardized `schema_version: "1.0.0"`; added Invocation Modes (author / validate-only), Draft vs Published Mode, Bundle Schema, Validation, AD Folder Layout sections. External callers reference by skill name, never by path.
  - `ia-create` Stage 5 gained "Generate RAW test bundle" option; routes companion analysis files to `docs/`; trusts `raw-test-author` validate-only output.
  - `ia-publish` Step 1b.4 expanded to rewrite all `000000` references in test bundles (`raw_id`, `raw_path`, `fs_path`, `alert_def_id`, header comments) and companion `docs/` analysis files. New Step 1c soft-gate for missing test coverage (Author / Skip with warning / Abort; default Author). Step 2 preserves `tests/` + `docs/` subfolders. PR body now includes test bundle row, "⚠️ Missing Test Coverage" section, and layout/coverage review-checklist items.
  - Standard AD folder layout codified: artifacts (`FS|RG|RAW######-*.{yml,md}`) + `tests/` + `docs/` at root only. Non-artifact files at root emit WARN (no hard fail this round).
  - Migrated `AD000002-bgp-neighbor-admin-shutdown-xr/` analysis files into `docs/` via `git mv`.
  - Docs synced: RAW test framework schema version `"1.0.0"` + validator cross-ref; `artifact-registry.md` strengthened layout mandate with diagram and convention rules.
