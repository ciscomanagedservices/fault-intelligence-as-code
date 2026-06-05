---
name: ia-start
description: >-
  Onboarding, environment setup, and dependency validation for the Intelligence
  Artifact Workspace. Validates MCP server connectivity, runs an interactive config
  interview to populate ia-config.yml (workspace identity and product scoping), detects
  in-progress draft work, and provides a guided walkthrough of available skills.
  Use this skill whenever the user says "ia-start", "get started", "setup",
  "set up workspace", "configure workspace", "check my setup", "hello", "welcome",
  "what can you do", "what skills are available", "how do I get started",
  "help me with intelligence artifacts", or "what can I do here".
---

# ia-start — Workspace Setup & Onboarding

You are the entry point for the **Intelligence Artifact Workspace**. Your job is to
validate that the workspace environment is ready, populate configuration if needed, surface
any in-progress work, and orient the user on available skills. You do not run research or
create artifacts — you prepare the workspace and tell users exactly how to proceed.

Run all stages sequentially. Do not skip stages.

---

## Welcome Message

Immediately after this skill is triggered — before any checks or questions — print a
friendly welcome message:

```
👋 Welcome to the Intelligence Artifact Workspace!

Here's what we're about to do:
  🔧 Check that your MCP servers (Cisco Support, Cisco Docs) are connected
  ⚙️ Configure your workspace identity and preferences
  📂 Detect any in-progress drafts from previous sessions
  🚀 Orient you on available skills and next steps

Let's get started!
```

Then proceed to Stage 0.

---

## Stage 0: MCP Server Dependency Check

Verify that all required MCP servers are reachable by making one lightweight,
read-only tool call per server. Display results as a checklist before proceeding.

### Probes

| Server | Tool to call | Interpret as |
|--------|-------------|-------------|
| `cisco-docs` | `mcp_cisco-docs_health_check` | ✅ if status is OK; ❌ if error |
| `cisco-support` | `mcp_cisco-support_get_bug_details` with bug ID `"CSCwr07525"` (known-valid test ID) | ✅ if it returns bug details; ❌ if the server fails to respond |

### Display results

After all probes, render a checklist like this (adapt based on actual results):

```
## Environment Check

✅ Cisco Docs MCP — connected
❌ Cisco Support MCP — not reachable

---
```

### If any server fails

1. **Explain that one or more MCP servers must be configured in MCP settings** before
   the workspace can use them:

   > One or more MCP servers are not reachable. Make sure the missing server is
   > configured in your MCP settings, then rerun `ia-start`.

2. **If helpful, point the user to their MCP setup flow** and tell them to verify that
   both required servers (Cisco Support, Cisco Docs) are installed and enabled.

3. **Manual fallback**: If automatic setup is not available in the current context,
   explain that credentials are configured in VS Code MCP settings
   (File → Preferences → MCP or `%APPDATA%\Code\User\mcp.json` on Windows).
   List the credential fields needed:
   - **cisco-support**: `CISCO_CLIENT_ID`, `CISCO_CLIENT_SECRET`, `SUPPORT_API`
   - **cisco-docs**: `cisco_docs_api_key`

4. Ask: "Would you like to continue without this server? Some skills work without both servers."
   - If yes: note the limitation and continue to Stage 1.
   - If no: prompt the user to configure the missing server in MCP settings and re-run `ia-start`.

### Skills affected by missing servers

| Missing server | Affected skills |
|----------------|----------------|
| `cisco-support` | `ia-research` (SR/defect research) |
| `cisco-docs` | `ia-research` (documentation lookup) |

---

## Stage 1: Config File Interview

Read `ia-config.yml` at the workspace root.

### If `workspace.customer` is already populated

Show a summary of current values:

```
## Current Workspace Config

  Customer:    <customer value>
  Engagement:  <engagement value or "(not set)">
  Repository:  <repository value or "(not set — will auto-detect from git remote)">
  Description: <description value or "(not set)">
  Platforms:   <product_scope list or "(not set)">
  OS types:    <os_types list>
```

Then use `question` to ask:

```
header: update_config
question: "Your workspace is already configured. Would you like to update any settings?"
options:
  - label: "No, keep current settings"
    recommended: true
  - label: "Yes, re-run the setup interview"
```

- If **No**: skip to Stage 2.
- If **Yes**: run the interview below.

### If `workspace.customer` is empty (first-time setup)

Tell the user: "Let's set up your workspace. I'll ask a few questions to configure
`ia-config.yml`. All fields except customer name are optional — press Enter to skip."

Then use `question` with these questions **all at once**:

```
questions:
  - header: customer
    question: "What customer or account are you working on?"
    # Required — do not mark as optional

  - header: engagement
    question: "What's the engagement or project label? (e.g., 'CX FY26 Q3')"
    # Optional

  - header: repository
    question: "What's the Git repository URL for this workspace? (leave blank to auto-detect from git remote)"
    # Optional

  - header: description
    question: "Brief description of this workspace's purpose?"
    # Optional

  - header: product_scope
    question: "Which products/platforms are you working on? Select all that apply."
    multiSelect: true
    options:
      - label: "Cisco 8000 Series"
      - label: "NCS 5500 Series"
      - label: "NCS 5700 Series"
      - label: "NCS 540 Series"
      - label: "ASR 9000 Series"
      - label: "ASR 1000 Series"
      - label: "Catalyst 9000 Series"
      - label: "Other (specify in freeform)"

  - header: os_types
    question: "Which OS types are in scope? Select all that apply."
    multiSelect: true
    options:
      - label: "IOS-XR"
        recommended: true
      - label: "IOS-XE"
      - label: "NX-OS"
```

### Writing answers to ia-config.yml

After the user responds, write the answers to `ia-config.yml` using the file editing tools:

- `workspace.customer` ← customer answer
- `workspace.engagement` ← engagement answer (if provided)
- `workspace.repository` ← repository answer; if blank, run `git remote get-url origin`
  in terminal to auto-detect and fill it in
- `workspace.description` ← description answer (if provided)
- `defaults.product_scope` ← product_scope selections (convert to YAML list)
- `defaults.os_types` ← os_types selections (convert to YAML list)

After writing, confirm:

```
✅ ia-config.yml updated with workspace settings.
```

Show a brief summary of what was written.

### Commit and push config changes

After the config is written, commit and push the changes so they are saved to the
repository:

1. Run `git add ia-config.yml`
2. Run `git commit -m "Configure workspace identity via ia-start"`
3. Run `git push`
4. Report success: `✅ Configuration committed and pushed to the repository.`
5. If the push fails (e.g., no remote access, authentication issue), note it as
   non-blocking: `⚠️ Could not push to remote — config is saved locally. You can
   push later with 'git push'.`

---

## Stage 2: Draft Detection & Contextual Suggestions

Check the workspace for in-progress work before showing the full onboarding.

### Check ia-drafts/

List all subdirectories of `ia-drafts/`. For each folder, count the YAML files present
to give a quick sense of how far along the work is.

### Check research/

List all subdirectories of `research/`. Note their presence as available starting points.

### Display results

**If ia-drafts/ or research/ contain work:**

```
## In-Progress Work Found

📁 ia-drafts/
  • bgp-mtu-pmtud-xe/       — 3 YAML artifacts (FS + RG + RAW)
  • fan-tray-absent-8000/   — 2 YAML artifacts (FS + RAW)

📁 research/
  • bgp-mtu-research.md
```

Then use `question`:

```
header: continue_or_new
question: "It looks like you have in-progress work. Would you like to continue with an existing draft, or start something new?"
options:
  - label: "Continue with existing work"
    recommended: true
  - label: "Start something new"
  - label: "Show me the full walkthrough first"
```

- If **Continue**: ask which folder and suggest the appropriate next step:
  - Folder has YAML artifacts → suggest `ia-create` to review, validate, or extend
  - Folder has `.md (RG)` files → suggest `ia-optimize`
  - Both → offer both options
  - Provide the exact prompt to type (e.g., `ia-create using ia-drafts/bgp-mtu-pmtud-xe/`)
- If **Start something new** or **no drafts found**: proceed to Stage 3.
- If **Show walkthrough first**: proceed to Stage 3, then offer routing at Stage 4.

---

## Stage 3: Onboarding Walkthrough

Present the workspace introduction and skill overview. Render the content below as a
formatted response.

---

## 👋 Welcome to the Intelligence Artifact Workspace

This workspace automates the end-to-end lifecycle of **Intelligence Artifacts** —
fault signatures, Remediation Guides, and repair action workflows — using AI-assisted
skills backed by two MCP servers (Cisco Support, Cisco Docs).

Whether you're starting from a raw syslog, an open support case, or an existing guide
that needs polishing, this workspace takes you from raw data to publishable artifacts
entirely in this chat window.

---

### 🗺️ The Skill Pipeline

```
ia-start  →  ia-research  →  ia-create  →  ia-optimize  →  ia-publish
```

| Skill | What It Does | Trigger Phrases |
|-------|-------------|----------------|
| **`ia-start`** | Set up workspace, validate MCP servers, populate config, detect in-progress work | `ia-start`, `get started`, `setup`, `hello` |
| **`ia-research`** | Pull structured findings from Cisco Support and Cisco docs for a given syslog, SR, or defect | `ia-research`, `ia-research`, `research SR 697123456`, `ia-research %MNEMONIC` |
| **`ia-create`** | Generate Fault Signatures, Remediation Guides, and Repair Action Workflows from research or raw input | `ia-create`, `create fault signatures`, `draft a remediation guide` |
| **`ia-optimize`** | Improve an existing Remediation Guide through SME questionnaires and platform-specific refinement | `ia-optimize`, `optimize this RG`, `optimize remediation guide` |
| **`ia-publish`** | Publish draft artifacts to Git (creates issue, branch, commit, PR) | `ia-publish`, `publish to git`, `ship artifacts`, `open a PR` |

**Typical end-to-end flow:**

1. `ia-start` — set up the workspace (you're here now)
2. `ia-research` — gather source data from Cisco Support and Cisco docs
3. `ia-create` — generate draft artifacts from that research
4. `ia-optimize` — work with SMEs to produce a polished, platform-specific guide
5. `ia-publish` — open a PR to publish finished artifacts to the Git repository

---

### 📁 Workspace Layout

| Folder / File | Purpose |
|---------------|---------|
| `ia-config.yml` | Workspace identity, defaults, and governance rules |
| `research/<issue-name>/` | `ia-research` outputs — 4 structured markdown findings files |
| `ia-drafts/<issue-name>/` | `ia-create` outputs — YAML artifacts + analysis docs |
| `intelligence-artifacts/` | Published artifacts (committed to repo via `ia-publish`) |
| `context/` | Project docs and meeting notes (read-only reference material) |
| `kb/.raw/` | Raw source files for wiki ingestion |

---

## Stage 4: Route to Next Action

After the walkthrough, use `question` to ask:

```
header: next_action
question: "What would you like to do? I'll tell you exactly what to type."
options:
  - label: "🔍 Research a network event, syslog, or support case"
  - label: "✏️ Create intelligence artifacts (signatures, RG, RAW)"
  - label: "⚡ Optimize an existing Remediation Guide"
  - label: "📦 Publish draft artifacts to Git"
  - label: "❓ Something else — I'll describe it"
```

Based on the selection, respond with guidance and the **exact prompt to type**. Do NOT
run the skill automatically — the user stays in the driver's seat.

---

### "🔍 Research a network event, syslog, or support case"

> **Type one of the following in the chat box and press Enter:**
>
> ```
> ia-research SR 697123456
> ia-research defect CSCwh12345
> ia-research %FAN_TRAY-3-ABSENT
> ia-research
> ```
>
> The research skill will query Cisco Support and Cisco documentation in
> parallel, then save structured findings to `research/<issue-name>/`. Review and edit
> those files before moving to artifact creation.
>
> **When ready to generate artifacts**, type `ia-create` and the skill will
> pick up the research automatically.

---

### "✏️ Create intelligence artifacts (signatures, RG, RAW)"

> **Type one of the following:**
>
> ```
> ia-create
> ia-create using research/bgp-mtu-pmtud-xe/
> ia-create from this syslog: <paste syslog here>
> ```
>
> The skill will generate draft Fault Signatures, Remediation Guides, and Repair Action
> Workflows in `ia-drafts/<issue-name>/`. You review and edit the drafts, then publish
> via `ia-publish`.
>
> If you don't have research yet, run `ia-research` first.

---

### "⚡ Optimize an existing Remediation Guide"

> **Type one of the following:**
>
> ```
> ia-optimize 1014
> ia-optimize
> optimize this remediation guide: <paste guide text>
> ```
>
> The skill runs in three modes: generate an SME questionnaire (Mode 1), draft an
> optimized platform-specific guide from answered questionnaire (Mode 2), or refine
> an existing draft (Mode 3). After optimization, use `ia-publish` to ship it.

---

### "📦 Publish draft artifacts to Git"

> **Type:**
>
> ```
> ia-publish
> ```
>
> The skill will discover all `ia-drafts/` folders, let you select what to publish
> (all pre-selected), copy files to `intelligence-artifacts/`, update the index,
> and open a PR via `gh` CLI. Nothing merges automatically — all PRs require human review.
>
> **Prerequisites:** `gh` CLI must be authenticated (`gh auth login`).

---

## Closing Message

When this skill completes and the user is about to proceed to another skill, append
this tip to your final output:

> ---
> **💡 Tip:** Start a **new chat** (click the **+** button at the top of the Copilot
> Chat panel) before running the next skill. This resets the context window and gives
> the next skill a clean slate to work with.
> ---

---

### "❓ Something else"

Ask the user to describe what they want to accomplish. Based on their description, suggest
the most appropriate skill combination. If none of the skills fit, help
them accomplish the task directly using the MCP tools available.

---

## Notes for the Agent

- **Always complete all four stages** — do not short-circuit to Stage 4 without checking
  MCP connectivity (Stage 0) and config (Stage 1). Users may hit blockers silently.
- **If ia-config.yml does not exist**, create it from the template at
  `.opencode/skills/ia-create/references/config-reference.md` (Annotated Full Example
  section) with all fields empty, then run the Stage 1 interview.
- **Never edit ia-config.yml sections 3–5** (governance rules, per-type rules, output
  settings) during setup — these are advanced fields reserved for manual configuration.
- **Workspace files are not read speculatively.** Only read files the user has explicitly
  referenced, except `ia-config.yml` and the `ia-drafts/` + `research/` directory listings,
  which are always safe to read as part of this skill's procedure.
