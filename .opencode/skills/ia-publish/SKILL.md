---
name: ia-publish
description: >-
  Publish intelligence artifact changes to the associated Git repository via GitHub
  workflow. Discovers draft artifacts in ia-drafts/, lets the user select what to
  publish (all pre-selected), copies selected files into an intelligence-artifacts/
  staging folder, updates a root-level index, then executes a gh-based workflow —
  create issue, branch, commit, push, open PR. Never auto-merges — all PRs require
  human review. PR body is IA-aware: parses copied YAML to summarize artifact types,
  IDs, and names. Use when the user says "ia-publish", "publish to git",
  "push artifacts to repo", "ship artifacts", "open a PR for these artifacts",
  "publish artifacts", or "commit my artifacts".
---

# ia-publish

Publish draft Intelligence Artifacts from `ia-drafts/` to the `intelligence-artifacts/` staging folder in the repository, then ship those changes via GitHub Pull Request. PRs **never auto-merge** — all require human review.

## Prerequisites

- **gh CLI** installed and authenticated (`gh auth status` must show a logged-in account for the target host)
- **Git** repository with a remote origin
- Draft artifacts present in `ia-drafts/` (run `ia-create` first if empty)
- Agent must have `run_in_terminal` and `question` tools

---

## Procedure

### Step 1 — Discover & Select Content from ia-drafts

Scan `ia-drafts/` recursively. Each immediate subfolder is a **draft group** (e.g., `ia-drafts/AD000000-bgp-mtu-pmtud-xe/`). Draft groups created by `ia-create` use the `AD000000-<slug>` naming convention (placeholder IDs).

For each group, collect two categories of publishable files:

**A. YAML artifacts** (`*.yml`, `*.yaml`) — Fault Signatures and Repair Action Workflows. Read each file's top-level frontmatter to extract:
- `artifact_type` (or infer from filename suffix: no suffix → FS, `_REPAIR` → RAW)
- `id`
- `name` or `title`
- `version` (where present)

**B. Markdown Remediation Guides** (`RG######-*.md`) — `ia-create` produces Remediation Guides as Markdown files, not YAML. These are first-class publishable artifacts. Present them in the checklist with type `RG (Markdown)`. Extract the name from the filename stem (e.g., `BGP_HOLD_TIMER_EXPIRED_FAULT_GUIDE`).

**If `ia-drafts/` is empty or contains no publishable files (no YAML and no `.md` (RG))**, stop and tell the user:
> "No draft artifacts found in `ia-drafts/`. Run `ia-create` first to generate artifacts."

Use `question` to present a multi-select checklist of all discovered files. **All items are pre-selected** (`recommended: true`). Group items visually by draft folder:

```
question({
  questions: [
    {
      header: "Artifacts to publish",
      question: "Select the artifact files to publish. All are pre-selected — deselect any to exclude.",
      multiSelect: true,
      allowFreeformInput: false,
      options: [
        { label: "AD000000-bgp-hold-timer-expired / FS000000-bgp-hold-timer-expired.yml — FS", recommended: true },
        { label: "AD000000-bgp-hold-timer-expired / RG000000-bgp-hold-timer-expired.md — RG (Markdown)", recommended: true },
        { label: "AD000000-bgp-hold-timer-expired / RAW000000-bgp-hold-timer-expired.yml — RAW", recommended: true },
        { label: "AD000000-bgp-mtu-pmtud-xe / FS000000-bgp-mtu-pmtud.yml — FS", recommended: true },
        { label: "AD000000-bgp-mtu-pmtud-xe / RG000000-bgp-mtu-pmtud.md — RG (Markdown)", recommended: true },
        { label: "AD000000-bgp-mtu-pmtud-xe / RAW000000-bgp-mtu-pmtud.yml — RAW", recommended: true }
      ]
    }
  ]
})
```

If the user deselects **all** files, stop with:
> "At least one artifact file must be selected. Please re-run and select at least one file."

Also note any companion analysis `.md` files (`*.analysis.md (FS)`, `*.analysis.md (RG)`, `*.analysis.md (RAW)`) in the same group folder — they will be copied automatically alongside their paired YAML or `.md` (RG) file (no need to present them in the checklist).

---

### Step 1b — Allocate IDs (Deferred ID Assignment)

Draft artifacts from `ia-create` carry **placeholder IDs** (suffix `000000`, e.g. `FS000000`, `RG000000`, `RAW000000`, `AD000000`). This step allocates real sequential IDs before copying to `intelligence-artifacts/`.

#### 1b.1 — Detect placeholders

For each selected draft group folder, check whether the folder name matches `AD000000-<slug>`. If it does, this group needs ID allocation. If the folder already has a non-zero suffix (e.g. `AD000005-<slug>`), it has been previously allocated — **skip ID allocation** for that group and pass it through unchanged.

#### 1b.2 — Read current max suffix from index.json

Load `intelligence-artifacts/index.json` (if it exists). Scan all entries to find the **maximum 6-digit suffix** across all Fault-Intelligence-pipeline types (`AD`, `FS`, `RG`, `RAW`):

```python
max_suffix = 0
for artifact in index["artifacts"]:
    id_str = artifact.get("id", "")
    # Match AD######, FS######, RG######, RAW######
    m = re.match(r"^(?:AD|FS|RG|RAW)(\d{6})$", id_str)
    if m:
        suffix = int(m.group(1))
        if suffix > max_suffix:
            max_suffix = suffix
```

If `index.json` does not exist or is empty, start from `max_suffix = 0`.

#### 1b.3 — Allocate suffixes

For each draft group needing allocation, assign `next_suffix = max_suffix + 1` (then increment for subsequent groups in the same batch):

```
Group 1: AD000000-bgp-hold-timer → allocated suffix 000005 (if max was 4)
Group 2: AD000000-ospf-nbr-down  → allocated suffix 000006
```

For **stub-type artifacts** (CL, PARSE, HCR) that are NOT part of a linked AD set, allocate independently using the max suffix of their own type only.

#### 1b.4 — Rewrite placeholders in draft files (in-place in ia-drafts/)

For each allocated group, rewrite all `000000` occurrences to the allocated suffix:

1. **YAML files** (`.yml`): Find-and-replace in file content:
   - `id: FS000000` → `id: FS<SUFFIX>`
   - `id: RAW000000` → `id: RAW<SUFFIX>`
   - `alert_def_id: AD000000` → `alert_def_id: AD<SUFFIX>`
   - Any other cross-reference containing `000000` matching `^[A-Z]+000000$`

2. **Markdown RG files** (`.md`): Find-and-replace header fields:
   - `**Guide ID:** RG000000` → `**Guide ID:** RG<SUFFIX>`
   - `**Alert Definition:** AD000000` → `**Alert Definition:** AD<SUFFIX>`
   - `**Linked Fault Signature:** FS000000` → `**Linked Fault Signature:** FS<SUFFIX>`
   - `**Linked Repair Action Workflow:** RAW000000` → `**Linked Repair Action Workflow:** RAW<SUFFIX>`

3. **Rename files**:
   - `FS000000-<slug>.yml` → `FS<SUFFIX>-<slug>.yml`
   - `RG000000-<slug>.md` → `RG<SUFFIX>-<slug>.md`
   - `RAW000000-<slug>.yml` → `RAW<SUFFIX>-<slug>.yml`
   - `*.analysis.md` files: rename matching prefix portion

4. **Rename folder**:
   - `ia-drafts/AD000000-<slug>/` → `ia-drafts/AD<SUFFIX>-<slug>/`

5. **Test bundles** (if `tests/` subfolder exists):
   - Rename `tests/RAW000000-<slug>.tests.yml` → `tests/RAW<SUFFIX>-<slug>.tests.yml`
   - Rewrite the following inside each test YAML:
     - `raw_id: RAW000000` → `raw_id: RAW<SUFFIX>`
     - `raw_path:` value (e.g., `../RAW000000-<slug>.yml` → `../RAW<SUFFIX>-<slug>.yml`)
     - `fs_path:` value (e.g., `../FS000000-<slug>.yml` → `../FS<SUFFIX>-<slug>.yml`)
     - `alert_payload.alert_def_id: AD000000` → `alert_payload.alert_def_id: AD<SUFFIX>`
     - Any header-comment references to artifact IDs (e.g., `# RAW: RAW000000-...`)
     - Any other `^[A-Z]+000000$` token inside the file

6. **Companion docs** (if `docs/` subfolder exists):
   - Rename `docs/<TYPE>000000.analysis.md` → `docs/<TYPE><SUFFIX>.analysis.md`
   - Rewrite ID references inside each analysis file using the same patterns as Step 1b.4(2)

Where `<SUFFIX>` is the 6-digit zero-padded allocated suffix (e.g., `000005`).

#### 1b.5 — Validation gate

After rewriting, run strict validation on the allocated artifacts:

```bash
python .opencode/skills/ia-create/scripts/validate_artifact.py ia-drafts/<renamed-folder>/
```

If validation fails, **stop** and report the error. Do NOT proceed to copy.

#### 1b.6 — Refuse leftover placeholders

Scan all files in the allocated group for any remaining `000000` suffix patterns. If found, **stop** with an error:
> "ERROR: Placeholder ID `000000` still present after allocation in `<file>`. Cannot publish."

#### 1b.7 — Record allocated IDs

Store the mapping for use in subsequent steps (PR body, index update, summary):

```
| Group | AD | FS | RG | RAW |
|-------|----|----|----|----|
| bgp-hold-timer | AD000005 | FS000005 | RG000005 | RAW000005 |
```

Present the allocated IDs to the user for confirmation before proceeding:
> "Allocated IDs for this publish batch: AD000005, FS000005, RG000005, RAW000005. Proceed?"

---

### Step 1c — Test Coverage Gate (Soft)

After ID allocation, check test coverage for every published `RAW######-*.yml` in
each allocated group.

#### 1c.1 — Detect missing bundles

For each `RAW<SUFFIX>-<slug>.yml` in the allocated draft group, check whether a
matching `tests/RAW<SUFFIX>-<slug>.tests.yml` exists in the same group folder.
Build a list of RAWs **without** test bundles.

If every RAW has a bundle, skip to Step 2.

#### 1c.2 — Prompt the user

For each RAW without coverage, present a three-way choice (default = Author):

```
question({
  questions: [
    {
      header: "Missing test coverage: RAW<SUFFIX>-<slug>",
      question: "RAW<SUFFIX>-<slug>.yml has no test bundle in tests/. How do you want to proceed?",
      options: [
        { label: "Author now (Recommended)", description: "Invoke raw-test-author to generate tests/RAW<SUFFIX>-<slug>.tests.yml, then continue.", recommended: true },
        { label: "Skip with warning", description: "Publish without tests. The PR body will include a ⚠️ Missing Test Coverage section." },
        { label: "Abort publish", description: "Stop now. Nothing is committed or pushed." }
      ]
    }
  ]
})
```

#### 1c.3 — Act on the choice

- **Author now**: Load the `raw-test-author` skill in `author` mode with
  `raw_path` = allocated RAW file and `fs_path` = paired FS file. After it
  writes the bundle, re-run validation (Step 1b.5) and continue.
- **Skip with warning**: Record the RAW ID in the **missing-coverage list**
  used by Step 8e (PR body).
- **Abort publish**: Stop. Do not copy, commit, or push.

> The gate is **soft** — it never blocks publishing. The user can always choose
> Skip. Aborting is an explicit user action, not an automatic failure.

---

### Step 2 — Copy Selected Files to intelligence-artifacts/

> **Prerequisite:** Step 1b has already allocated real IDs and rewritten/renamed
> the draft files in `ia-drafts/`. The folder names and filenames now carry their
> final published IDs (e.g., `AD000005-bgp-hold-timer-expired/`).

For each selected file (YAML FS/RAW **or** Markdown RG):

1. Determine its **destination Alert Definition folder**: the kebab-case subfolder from `ia-drafts/`, normalized to `AD######-<slug>/` form (e.g., `AD000006-bgp-mtu-pmtud-xe`). The 6-digit suffix MUST match the `FS######`/`RAW######`/`RG######` suffix of the artifacts inside.
2. Copy primary artifact files (`FS######-*.yml`, `RG######-*.md`, `RAW######-*.yml`) **flat** into `intelligence-artifacts/AD######-<slug>/` (no subdirectories at the artifact level).
3. **Preserve the `tests/` subfolder**: copy `ia-drafts/<group>/tests/*.tests.yml` to `intelligence-artifacts/AD######-<slug>/tests/`. Create the `tests/` directory if missing.
4. **Preserve the `docs/` subfolder**: copy `ia-drafts/<group>/docs/*` to `intelligence-artifacts/AD######-<slug>/docs/`. All companion analysis files (`<TYPE>######.analysis.md`) and any other non-artifact, non-test documentation live under `docs/`. Create the `docs/` directory if missing.
5. Track each copy as **Added** (new file) or **Updated** (file already existed in destination).

If artifacts from multiple draft groups are selected, each group gets its own AD folder under `intelligence-artifacts/`.

**Standard AD folder layout** (enforced by convention, see `raw-test-author` skill `## AD Folder Layout`):

```
intelligence-artifacts/AD######-<slug>/
  FS######-<slug>.yml          ← artifact (root)
  RG######-<slug>.md           ← artifact (root)
  RAW######-<slug>.yml         ← artifact (root)
  tests/
    RAW######-<slug>.tests.yml ← test bundle
  docs/
    FS######.analysis.md       ← companion docs
    RG######.analysis.md
    RAW######.analysis.md
```

Only artifact files (`FS|RG|RAW######-*.{yml,md}`) belong at the AD root. Everything else goes under `tests/` or `docs/`.

**Example result:**
```
intelligence-artifacts/
  AD000005-bgp-hold-timer-expired/
    FS000005-bgp-hold-timer-expired.yml
    RG000005-bgp-hold-timer-expired.md
    RAW000005-bgp-hold-timer-expired.yml
    tests/
      RAW000005-bgp-hold-timer-expired.tests.yml
    docs/
      FS000005.analysis.md
      RG000005.analysis.md
      RAW000005.analysis.md
  AD000006-bgp-mtu-pmtud-xe/
    FS000006-bgp-mtu-pmtud.yml
    RG000006-bgp-mtu-pmtud.md             ← Markdown RG (always Markdown, never YAML)
    RAW000006-bgp-mtu-pmtud.yml
    tests/
      RAW000006-bgp-mtu-pmtud.tests.yml
    docs/
      FS000006.analysis.md
      RG000006.analysis.md
      RAW000006.analysis.md
```

> **Convention enforcement:** Non-artifact files at the AD folder root (anything not matching `(FS|RG|RAW)\d{6}-.+\.(yml|md)`) produce a **WARN** in the publish summary. The validator does not hard-fail this round — the warning is informational only. Move such files under `docs/` (or `tests/` if they are test bundles) to clear the warning.

---

### Step 3 — Update intelligence-artifacts/index.md

Read `intelligence-artifacts/index.md` if it exists; create it from scratch if not.

**Index file format:**

```markdown
# Intelligence Artifacts Index

> Auto-maintained by ia-publish. Last updated: YYYY-MM-DD.

## Summary

| Alert Definition | Artifacts | Last Published | PR |
|------------------|-----------|----------------|----|
| AD000006-bgp-mtu-pmtud-xe | FS, RG, RAW | 2026-04-20 | — |

## AD000006-bgp-mtu-pmtud-xe

| Action | Type | ID | Name | Version | File |
|--------|------|----|------|---------|------|
| Added | Fault Signature | FS000006 | BGP_MTU_PMTUD_FAULT | 1.0.0 | FS000006-bgp-mtu-pmtud.yml |
| Added | Remediation Guide | RG000006 | BGP_MTU_PMTUD_FAULT_GUIDE | 1.0.0 | RG000006-bgp-mtu-pmtud.md |
| Added | Repair Action Workflow | RAW000006 | BGP_MTU_PMTUD_FAULT_REPAIR | 1.0.0 | RAW000006-bgp-mtu-pmtud.yml |

<!-- last-updated: 2026-04-20 -->
```

Rules:
- **Per-artifact rows**: match on `id` (`FS######`, `RAW######`, `RG######`). **Add** if new, **update** if existing (change Action to `Updated`).
- **Summary table row**: upsert per Alert Definition folder. Artifact type abbreviations: FS, RG, RAW, CL, P, HCR. Multiple types comma-separated.
- **PR column**: leave as `—` at this step. Back-filled in Step 8e after the PR is created.
- **`<!-- last-updated: YYYY-MM-DD -->`**: always update to today's date; placed at the very end of the file.

---

### Step 3b — Regenerate intelligence-artifacts/index.json

After copying files and updating `index.md`, regenerate the machine-readable artifact index:

```bash
python .opencode/skills/ia-publish/scripts/generate_index.py
```

This walks `intelligence-artifacts/` for all published YAML files, extracts metadata, and writes `intelligence-artifacts/index.json`. The `index.json` file is committed alongside the other artifacts so consumers (e.g., `ia-explorer`, `ia-research` duplicate checks) always have an up-to-date index after merge.

If the script fails or is not present, warn the user but do not block the publish workflow.

---

### Step 3c — Regenerate docs/index.html (Explorer)

After regenerating `index.json`, regenerate the interactive HTML explorer:

```bash
python .opencode/skills/ia-explorer/generate_explorer.py
```

This reads the template from `.opencode/skills/ia-explorer/template.html`, inlines the updated `index.json`, and writes `docs/index.html`. The `docs/` directory is created automatically if it does not exist.

The `docs/index.html` file is committed in the same commit as the artifacts (Step 8c) so the GitHub Pages explorer is always current after merge.

If the script fails or is not present, warn the user but do not block the publish workflow.

---

### Step 4 — Gather Context

#### 4a. Read workspace config

Read `ia-config.yml` from the repository root (if it exists) and extract:
- **`WORKSPACE_CUSTOMER`** — `workspace.customer` (may be empty)
- **`WORKSPACE_ENGAGEMENT`** — `workspace.engagement` (may be empty)
- **`WORKSPACE_REPO_URL`** — `workspace.repository` (may be empty)
- **`WORKSPACE_DESCRIPTION`** — `workspace.description` (may be empty)

If `ia-config.yml` does not exist or the key is absent/empty, treat each value as empty string.

#### 4b. Gather Git context

Run these commands silently and parse the output:

```bash
git status --porcelain
git diff --stat
git log --oneline -5
git branch --show-current
git remote get-url origin
gh repo view --json defaultBranchRef,name,owner,url
```

Derive:
- **`REPO_OWNER`** and **`REPO_NAME`** — from `gh repo view`
- **`DEFAULT_BRANCH`** — from `defaultBranchRef.name`
- **`CURRENT_BRANCH`** — from `git branch --show-current`
- **`HAS_CHANGES`** — whether `git status --porcelain` is non-empty (it should be after Step 2–3)
- **`ON_DEFAULT_BRANCH`** — whether `CURRENT_BRANCH == DEFAULT_BRANCH`
- **`CHANGED_FILES`** — list of changed paths from `git status --porcelain` (will include `intelligence-artifacts/` files, `index.md`, and `docs/index.html`)
- **`REPO_URL`** — use `WORKSPACE_REPO_URL` if set, otherwise use the URL from `gh repo view`

> **Note:** If `git status --porcelain` is empty after Step 2–3 (all copied files were identical to existing), warn the user:
> "No changes detected — copied files appear identical to existing `intelligence-artifacts/` content. Proceed anyway? (PR will be empty)"
> Offer to continue or abort.

---

### Step 5 — Build Artifact Change Summary

Using the copy records from Step 2, build the **Artifact Change Summary** table. Do **not** re-scan git diff — the copy step is the source of truth.

```
| Action  | Type                        | ID         | Name                               |
|---------|-----------------------------|------------|------------------------------------|
| Added   | Fault Signature             | FS000005   | BGP_HOLD_TIMER_EXPIRED_FAULT       |
| Added   | Remediation Guide           | RG000005   | BGP_HOLD_TIMER_EXPIRED_FAULT_GUIDE |
| Added   | Repair Action Workflow      | RAW000005  | BGP_HOLD_TIMER_EXPIRED_FAULT_REPAIR|
| Updated | Fault Signature             | FS000006   | BGP_MTU_PMTUD_FAULT                |
| Added   | Remediation Guide           | RG000006   | BGP_MTU_PMTUD_FAULT_GUIDE          |
```

Also scan all copied YAML files **and Markdown RG files** for any `OPEN DESIGN QUESTIONS` blocks (look for lines matching `# OPEN DESIGN QUESTIONS` or `OPEN DESIGN QUESTIONS:`). Collect them — they will be surfaced in the issue and PR body for reviewer attention.

---

### Step 6 — Infer Change Description

From the artifact change summary and workspace config, derive:

- **One-line summary**: `Add <N> <type(s)> for <group-name>` (e.g., `Add fault signature, remediation guide, and repair workflow for BGP MTU PMTUD`). If `WORKSPACE_CUSTOMER` is set, append ` [<customer>]` (e.g., `Add fault signature for BGP MTU PMTUD [Acme Corp]`).
- **Multi-line description**: include the artifact change summary table and any open design questions
- **Customer context line** (include if `WORKSPACE_CUSTOMER` is non-empty):
  - `**Customer:** <WORKSPACE_CUSTOMER>` and, if set, `**Engagement:** <WORKSPACE_ENGAGEMENT>`
- **Conventional commit prefix**:
  - `feat:` — new artifacts (Action = Added)
  - `fix:` — corrected artifacts (Action = Updated, content is a fix)
  - `docs:` — research or doc-only files with no YAML artifacts
  - Default: `feat:`
- **Issue labels**: always include `intelligence-artifact`; add `enhancement` for new artifacts, `bug` for fixes
- **Branch name**: `<type>/<group-name>` (e.g., `feat/bgp-mtu-pmtud-xe`)

---

### Step 7 — Present Checklist

Use `question` with multi-select. **All items are pre-selected** (`recommended: true`). **No merge step is offered.**

```
question({
  questions: [
    {
      header: "Workflow steps",
      question: "Select the GitHub workflow steps to run. Deselect any you want to skip. Note: PRs require human review — auto-merge is not available.",
      multiSelect: true,
      allowFreeformInput: false,
      options: [
        { label: "1. Create GitHub issue", description: "<inferred title>", recommended: true },
        { label: "2. Create branch", description: "<inferred branch name>", recommended: true },
        { label: "3. Stage & commit changes", description: "<inferred commit message>", recommended: true },
        { label: "4. Push branch to origin", recommended: true },
        { label: "5. Open pull request", description: "linked to issue, targeting <DEFAULT_BRANCH>", recommended: true }
      ]
    },
    {
      header: "Issue title",
      question: "Edit the issue title if needed:",
      options: [{ label: "<inferred title>", recommended: true }]
    },
    {
      header: "Commit message",
      question: "Edit the commit message if needed:",
      options: [{ label: "<type>: <inferred summary>", recommended: true }]
    }
  ]
})
```

Wait for the user's response before proceeding.

---

### Step 8 — Execute Selected Steps

Execute only the steps the user selected, in order. Use the user's edited title/message if they provided freeform text.

#### 8a. Create GitHub issue

```bash
gh issue create \
  --title "<ISSUE_TITLE>" \
  --body "<ISSUE_BODY>" \
  --label "intelligence-artifact,<INFERRED_LABEL>"
```

- Capture the issue number from the output URL (the number at the end). Store as **`ISSUE_NUMBER`**.
- If label creation fails, retry without `--label` and note the skip.

**Issue body format:**

```markdown
## Summary

<One-paragraph description of what artifacts are being added/updated and why.>

<!-- Include the following block only if WORKSPACE_CUSTOMER is non-empty -->
| Field | Value |
|---|---|
| Customer | <WORKSPACE_CUSTOMER> |
| Engagement | <WORKSPACE_ENGAGEMENT> |
<!-- End customer block -->

## Artifact Changes

| Action | Type | ID | Name |
|--------|----|----|----|
| Added | Fault Signature | FS000006 | BGP_MTU_PMTUD_FAULT |
| Added | Remediation Guide | RG000006 | BGP_MTU_PMTUD_FAULT_GUIDE |
| Added | Repair Action Workflow | RAW000006 | BGP_MTU_PMTUD_FAULT_REPAIR |

## Files Changed

- `intelligence-artifacts/AD000006-bgp-mtu-pmtud-xe/FS000006-bgp-mtu-pmtud.yml`
- `intelligence-artifacts/AD000006-bgp-mtu-pmtud-xe/RG000006-bgp-mtu-pmtud.md`
- `intelligence-artifacts/AD000006-bgp-mtu-pmtud-xe/RAW000006-bgp-mtu-pmtud.yml`
- `intelligence-artifacts/AD000006-bgp-mtu-pmtud-xe/tests/RAW000006-bgp-mtu-pmtud.tests.yml`
- `intelligence-artifacts/AD000006-bgp-mtu-pmtud-xe/docs/*.analysis.md`
- `intelligence-artifacts/index.md` (updated)
- `intelligence-artifacts/index.json` (regenerated)
- `docs/index.html` (explorer regenerated)

## Open Design Questions

<Include any OPEN DESIGN QUESTIONS blocks found in the YAML files, or omit this section if none.>
```

#### 8b. Create branch

If `ON_DEFAULT_BRANCH` is true:
```bash
git checkout -b <BRANCH_NAME>
```

If already on a non-default branch, ask the user whether to keep the current branch or create a new one. If they keep it, use `CURRENT_BRANCH` as `BRANCH_NAME`.

#### 8c. Stage & commit changes

Stage the `intelligence-artifacts/` directory and `docs/index.html` (which includes the index and explorer):

```bash
git add intelligence-artifacts/ docs/index.html
git commit -m "<TYPE>: <SUMMARY>" -m "Resolves #<ISSUE_NUMBER>"
```

- Subject line: conventional commit format, max 72 chars.
- Body: always include `Resolves #<ISSUE_NUMBER>` to auto-close the issue when the PR merges.
- If there are no staged changes after `git add` (files were identical), skip this step and note it.

#### 8d. Push branch

```bash
git push -u origin <BRANCH_NAME>
```

If push fails because branch already exists on remote:
```bash
git push origin <BRANCH_NAME>
```

#### 8e. Open pull request

```bash
gh pr create \
  --title "<ISSUE_TITLE>" \
  --body "<PR_BODY>" \
  --base <DEFAULT_BRANCH> \
  --head <BRANCH_NAME>
```

- Capture the PR number. Store as **`PR_NUMBER`**.

**PR body format:**

```markdown
Resolves #<ISSUE_NUMBER>

## Summary

<One-paragraph description of what artifacts are being added/updated.>

<!-- Include the following block only if WORKSPACE_CUSTOMER is non-empty -->
| Field | Value |
|---|---|
| Customer | <WORKSPACE_CUSTOMER> |
| Engagement | <WORKSPACE_ENGAGEMENT> |
<!-- End customer block -->

## Artifact Changes

| Action | Type | ID | Name |
|--------|----|----|----|
| Added | Fault Signature | FS000006 | BGP_MTU_PMTUD_FAULT |
| Added | Remediation Guide | RG000006 | BGP_MTU_PMTUD_FAULT_GUIDE |
| Added | Repair Action Workflow | RAW000006 | BGP_MTU_PMTUD_FAULT_REPAIR |
| Added | RAW Test Bundle | RAW000006 | RAW000006-bgp-mtu-pmtud.tests.yml (N tests) |

## Open Design Questions

<Include any OPEN DESIGN QUESTIONS blocks from the YAML files, or omit if none.>

<!-- Include the following section ONLY if any RAW lacks a test bundle (Step 1c.3 "Skip with warning") -->
## ⚠️ Missing Test Coverage

The following RAWs are being published **without** test bundles. Reviewers should
require tests before merge, or accept the gap explicitly:

- `RAW000006-bgp-mtu-pmtud` — no `tests/RAW000006-bgp-mtu-pmtud.tests.yml`

Run the `raw-test-author` skill to generate coverage.
<!-- End missing-coverage section -->

## Review Checklist

Reviewers, please verify:
- [ ] Artifact YAML conforms to Intelligence Artifact schema (artifact_type, id, name, version fields present)
- [ ] `regex` and `splunk_regex` patterns are correct for Fault Signatures
- [ ] IDs are unique, non-placeholder (no `000000` suffix), and fall within the correct range
- [ ] Allocated IDs: <AD_ID>, <FS_ID>, <RG_ID>, <RAW_ID>
- [ ] AD folder layout follows standard: artifacts + `tests/` + `docs/` at root only
- [ ] Each published RAW has a matching `tests/RAW######-*.tests.yml` (or Missing Coverage section is acknowledged)
- [ ] `intelligence-artifacts/index.md` rows are accurate
- [ ] `intelligence-artifacts/index.json` is present and artifact count matches
- [ ] No sensitive data (credentials, PII) in artifact content

---

> ⚠️ **This PR requires human review before merge.** Auto-merge is not enabled.
```

**After the PR is opened**, back-fill the PR number/URL in `intelligence-artifacts/index.md`:
- In the Summary table, replace the `—` in the PR column for the affected group(s) with `[#<PR_NUMBER>](<PR_URL>)`.
- Update the `<!-- last-updated: YYYY-MM-DD -->` comment.
- Amend the commit and force-push:

```bash
git add intelligence-artifacts/index.md
git commit --amend --no-edit
git push --force-with-lease origin <BRANCH_NAME>
```

---

### Step 9 — Summary

Present a summary table:

```
## ia-publish complete

| Step | Status | Details |
|------|--------|---------|
| Artifacts selected | ✅ | 3 files from bgp-mtu-pmtud-xe |
| Files copied | ✅ | intelligence-artifacts/AD000006-bgp-mtu-pmtud-xe/ (3 Added) |
| Index updated | ✅ | intelligence-artifacts/index.md |
| Issue | ✅ Created | #<NUMBER> — <TITLE> |
| Branch | ✅ Created | feat/bgp-mtu-pmtud-xe |
| Commit | ✅ Committed | <SHORT_HASH> feat: <summary> |
| Push | ✅ Pushed | origin/feat/bgp-mtu-pmtud-xe |
| PR | ✅ Opened | #<NUMBER> — <TITLE> |
```

Include clickable PR and issue URLs.

Append a reminder:
> "PR #<PR_NUMBER> is open and awaiting review. Merge is not automatic — a team member must approve and merge."

---

## Edge Cases

| Situation | Handling |
|-----------|----------|
| `ia-drafts/` empty or no YAML and no `.md` (RG) files | Stop: "No draft artifacts found. Run ia-create first." |
| Group has `.md` (RG) but no `_GUIDE.yml` | Present the `.md` (RG) in the checklist as `RG (Markdown)`; copy it directly; record with ID `—` in index |
| User deselects all files | Stop: "At least one artifact must be selected." |
| Artifact already in `intelligence-artifacts/<group>/` | Overwrite; record action as **Updated** |
| Multiple draft groups selected | Each gets its own subfolder under `intelligence-artifacts/`; each gets a unique allocated suffix |
| `intelligence-artifacts/index.md` does not exist | Create from scratch using the format in Step 3 |
| `intelligence-artifacts/index.json` does not exist | Start allocation from suffix `000001` |
| No git changes after copy (files identical) | Warn user; offer to proceed or abort |
| Already on a non-default feature branch | Skip branch creation; ask user to confirm keeping current branch |
| `gh pr create` fails (no upstream, auth error) | Show the error; suggest `gh auth login` or checking remote |
| Issue label does not exist | Retry without `--label`; note the skip in summary |
| Enterprise GitHub (GHE) | gh CLI auto-routes; no special handling needed |
| Multiple remotes | Use `origin` by default |
| Merge conflicts on PR | Inform user; do not attempt to resolve automatically |
| OPEN DESIGN QUESTIONS present in YAML | Surface in issue body and PR body under "Open Design Questions" section |
| Draft has non-placeholder IDs (already allocated) | Pass through unchanged — do NOT re-allocate. Only `000000` suffixes trigger allocation |
| Mixed placeholder + real IDs in one group | Error: "Inconsistent IDs in group `<slug>` — some placeholder, some real. Fix manually." |
| Placeholder `000000` found after allocation rewrite | Error: "Leftover placeholder in `<file>`. Cannot publish." — stop and report |
| Two PRs claim the same suffix (collision) | Detected in PR review; second PR re-allocates on rebase |
| RAW published without a test bundle | Step 1c soft-gate prompts Author / Skip / Abort (default Author); Skip adds ⚠️ Missing Test Coverage section to PR body |
| `raw-test-author` invocation fails during Step 1c "Author now" | Report the error; re-prompt user with Author (retry) / Skip / Abort |
| Test bundle present but validation fails during 1b.5 | Stop publish; report the bundle path + validator output; user fixes and re-runs ia-publish |
| Non-artifact file at AD folder root (not matching `(FS\|RG\|RAW)\d{6}-.+\.(yml\|md)`) | Emit WARN in publish summary recommending move under `docs/`; do not block publish |
| `tests/` or `docs/` subfolder missing in draft group | OK — only copy what exists; do not create empty dirs |

---

## Closing Message

When this skill completes and the user is about to proceed to another skill, append
this tip to your final output:

> ---
> **💡 Tip:** Start a **new chat** (click the **+** button at the top of the Copilot
> Chat panel) before running the next skill. This resets the context window and gives
> the next skill a clean slate to work with.
> ---
