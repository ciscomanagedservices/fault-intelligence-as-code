---
name: ia-research
description: Perform structured multi-source research to prepare source data for Intelligence Artifacts — fault signatures, remediation guides, repair action workflows, and future health intelligence types. Use this skill whenever the user wants to research a network event, syslog, Cisco support case, or defect before creating intelligence artifacts. Trigger when the user says "ia-research", "ia-research", "research this syslog", "prepare research for a new signature", "investigate this network event", "research SR <ID>", "look up defect <ID>", or anything suggesting they want to gather data before publishing intelligence artifacts. When only a single data source is provided (e.g., just an SR ID or just a defect ID), the skill performs an iterative enrichment pass first — fetching that source to extract syslog strings, defect IDs, and platform context — before running the full multi-source research. Research spans two MCP servers: cisco-support (SRs and bugs) and cisco-docs (Cisco product documentation). Outputs are structured markdown files written to a dynamically-named research/ folder.
---

# IA Research Skill

Orchestrate multi-source research to produce ready-to-use source data for Intelligence Artifacts.
Four stages:

1. **Intake** — Gather inputs (syslogs, SR IDs, defect IDs, reference files) and select data sources
2. **Enrichment** — If inputs are sparse (single source only), do a quick pivot pass to extract missing signals (syslogs, defect IDs, platform) before proceeding
3. **Research** — Query each selected source; write per-source findings files
4. **Analysis** — Synthesize findings into an aggregate recommendations file

Output files are written to `research/<issue-name>/` at the workspace root. Derive `<issue-name>`
as a short kebab-case label from the research topic (e.g., `tam-entropy-varlog-8000`). Use the
primary syslog mnemonic, platform shortname, and defect reference when available.

---

## Stage 1: Intake

### Fast-Mode Detection

Before asking any questions, extract inputs **explicitly stated by the user in their message**:
- Syslog strings or facility codes (e.g., `%SECURITY-TAMSVCS-3-ENTROPY`, full log lines)
- SR IDs (7–9 digit numbers, e.g., `699754648`)
- Defect IDs (e.g., `CSCwr07525`)
- File paths the user has **explicitly referenced or attached**
- Platform, product, or technology context

**Do not inspect the workspace for related files.** Do not read, infer from, or silently
incorporate any workspace files (docs, reports, markdown, etc.) unless the user has explicitly
named them in their message or attached them. Workspace files may belong to unrelated work.

Only prompt for what is genuinely missing. Don't re-ask for things already established.

### Guided Interview

Use `question` to collect missing inputs. Present all questions in a single call.
Keep question text concise (tool enforces a 200-character limit per question field).

Collect the following (all optional individually, but at least one input is required):

| Header | What to ask |
|--------|-------------|
| `syslogs` | Syslog event(s) to research — facility codes or full log strings, one per line |
| `sr_ids` | Cisco SR (support case) IDs, one per line |
| `defect_ids` | Cisco defect IDs (e.g., CSCwr07525), one per line |
| `reference_files` | Workspace file paths to include as reference context |
| `extra_context` | Platform, product, technology, symptom, or anything else useful |

After collecting inputs, briefly confirm: restate what will be researched and the chosen folder name,
then proceed.

### Artifact Intent Selection

Before selecting data sources, ask which artifact type(s) the user intends to create from this
research. This determines which fields and data points to prioritise in Stage 3 analysis.

**Step 1 — Discover available artifact types dynamically:**

Read `.opencode/skills/ia-create/SKILL.md` (the **Artifact Routing Table** section) to
discover the current set of available artifact types, their descriptions, and ID formats. Do not
hard-code artifact names here — always derive them from that skill file so this skill stays in
sync as `ia-create` evolves.

**Step 2 — Ask the user:**

Use `question` with a multi-select question:

> **What artifact type(s) do you plan to create from this research?**
> Select all that apply. This helps focus the research summary on the right fields.

Populate the options dynamically from the **Artifact Routing Table** you just read in Step 1.
Pre-select **Remediation Guide** by default (matches the recommended RG-first workflow).
Mark stub types (Collection List, Parser, Health Check Rule) with a note that generation support
is coming, but research can still be gathered now.

**Step 3 — Load artifact references for each selected type:**

For each artifact type the user selected, read the artifact reference listed in the
`ia-create` Artifact Routing Table. For example: `fault-signature-schema.md`,
`remediation-guide-template.md`, `repair-action-workflow-schema.md`.

Extract and retain:
- The **required fields or sections** for each type (names, descriptions, required vs optional
   where applicable)
- Any **validation rules, formatting rules, or constraints** noted in the reference
- The **output file format** (YAML vs Markdown) and naming conventions

Store this as working context labelled **"selected artifact references"**. It will be used in
Stage 3 to generate artifact-specific recommendation blocks in the research summary.

> **Example:** If the user selects Fault Signature + Remediation Guide, you will have read
> `fault-signature-schema.md` and `remediation-guide-template.md`. In Stage 3, for each artifact
> type you will generate a recommendation block whose field list or section structure is drawn
> from those references — not from any hard-coded template.

### Data Source Selection

Ask a multi-select question for which data sources to use. Present both as recommended defaults:

- `cisco-support` — SR details, bug details, and related defect search via Cisco Support APIs
- `cisco-docs` — Cisco product documentation, release notes, and troubleshooting guides

Allow freeform input for any additional MCP server the user wants to include. If they write one in,
ask them to describe it briefly so you know what tools are available.

### Create Output Folder

Create `research/<issue-name>/` in the workspace root. Confirm the folder name to the user before
proceeding.

---

## Stage 1.5: Iterative Enrichment (Sparse Input)

Before launching full parallel research, check whether the inputs are sparse — meaning only a
**single data source** was provided and key signals are still missing.

### Sparse Input Detection

Inputs are sparse if **exactly one** of the following is true AND the others are absent:
- Only SR ID(s) provided — no syslogs, no defect IDs
- Only defect ID(s) provided — no syslogs, no SR IDs
- Only a reference file is provided — no syslogs, no SR IDs, no defect IDs

If syslogs are already present (even one), inputs are sufficient; skip this stage and proceed
directly to Stage 2.

### Enrichment Workflow

Perform a **quick first-pass** using only the available source to extract the missing signals.
This is a targeted lookup, not a full research pass — do not write findings files yet.

**If only SR ID(s) provided:**
1. Call `mcp_cisco-support_get_case_details` for each SR.
2. Extract from the response:
   - Exact syslog strings or facility-mnemonic codes mentioned anywhere in the case
   - Referenced defect IDs (CSCxx##### patterns)
   - Platform / product / software version context
3. Merge extracted syslog strings and defect IDs into the working inputs.
4. Derive or refine `<issue-name>` using the syslog mnemonic and platform now known.

**If only defect ID(s) provided:**
1. Call `mcp_cisco-support_get_bug_details` for each defect.
2. Extract from the response:
   - Syslog strings or mnemonics mentioned in the symptom or description
   - Affected platforms and software releases
   - Any linked SR IDs
3. Merge extracted syslog strings, SR IDs, and platform context into the working inputs.

**If only a reference file provided:**
1. Read the file.
2. Scan for syslog strings, SR IDs (7–9 digit numbers), and defect IDs (CSCxx#####).
3. Merge any discovered values into the working inputs.

### After Enrichment

Briefly tell the user what was discovered:

> Enrichment pass complete. Extracted from SR `<id>`: syslog(s) `<list>`, defect(s) `<list>`.
> Proceeding with full research.

If enrichment yields no additional signals (e.g., SR has no syslog content), note this and
continue with whatever inputs are available — do not block progress.

Update `<issue-name>` if a better label is now derivable from the enriched inputs.

---

## Stage 2: Research Execution

Run research for each selected source. The three sources are fully independent — run them in
parallel via sub-agents when parallel execution is available. Write each findings file as it
completes rather than waiting for all sources.

Read any user-provided reference files before issuing tool calls and incorporate their context into
queries (e.g., platform details, syslog strings, resolution steps).

### cisco-support Research

**Tools:**

| Tool | Purpose |
|------|---------|
| `mcp_cisco-support_get_case_details` | Full SR: title, technology, syslogs mentioned, resolution, linked bugs |
| `mcp_cisco-support_get_bug_details` | Full defect: symptom, workaround, affected/fixed releases, platform scope |
| `mcp_cisco-support_search_bugs_by_keyword` | Find related defects by syslog facility/mnemonic keyword |

**Workflow:**
1. For each SR ID → `get_case_details`. Extract: exact syslog strings mentioned, referenced defect
   IDs, platform/software version, resolution steps.
2. For each defect ID → `get_bug_details`. Extract: symptom, workaround, fixed releases, affected
   platforms.
3. For each syslog not tied to an SR → `search_bugs_by_keyword` with the facility mnemonic
   (e.g., `SECURITY-TAMSVCS-3-ENTROPY`) to surface related defects.
4. Cross-reference: if the SR references additional defects, fetch those too. If a defect mentions
   related SRs or bugs, note them.

**Output:** `research/<name>/cisco-support-findings.md`

Use the template at [references/cisco-support-findings-template.md](./references/cisco-support-findings-template.md).
Key sections: SR summaries, defect summaries, keyword-search discoveries, and a consolidated list
of exact syslog strings extracted from the cases (used verbatim in regex design later).

---

### cisco-docs Research

**Tools:**

| Tool | Purpose |
|------|---------|
| `mcp_cisco-docs_health_check` | Verify server is up before starting |
| `mcp_cisco-docs_search_products` | Resolve platform name to the official product string |
| `mcp_cisco-docs_list_cisco_products` | Browse product catalog if platform is ambiguous |
| `mcp_cisco-docs_list_technologies` | Browse technology/protocol context for scoping |
| `mcp_cisco-docs_list_categories` | Enumerate available doc categories |
| `mcp_cisco-docs_ask_cisco_documentation` | **Primary**: technical Q&A scoped to a product; requires `product` param; returns `sessionId` for chaining |

**Workflow:**
1. Call `health_check` once. If it fails, skip this source and note it in the findings file.
2. Call `search_products` with the platform derived from SR or syslog context to get the exact
   product string required by `ask_cisco_documentation` (e.g., `"Cisco 8000"` →
   `"Cisco 8000 Series Routers"`). If platform is unknown, call `list_cisco_products` to browse.
3. For each syslog mnemonic → `ask_cisco_documentation` asking: what does this mnemonic mean,
   what are the causes, and what are the recommended actions? Save the returned `sessionId`.
4. Chain follow-ups in the same `sessionId`: ask about recommended software versions, relevant
   configuration guides, or specific remediation commands for the defect.
5. For each defect ID → ask for any related field notices, release notes, or known docs.

**Output:** `research/<name>/cisco-docs-findings.md`

Use the template at [references/cisco-docs-findings-template.md](./references/cisco-docs-findings-template.md).
Key sections: platform context, syslog mnemonic explanations, remediation guidance from docs,
relevant software versions and release notes.

---

## Stage 3: Aggregate Analysis

Synthesize all per-source findings into `research/<name>/research-summary.md`.

Use the template at [references/research-summary-template.md](./references/research-summary-template.md).

### Artifact Recommendations

For each artifact type the user selected in Stage 1 (Artifact Intent Selection), generate a
dedicated recommendation block. **Use the "selected artifact references" context loaded in Stage 1**
— do not hard-code field names here. The correct fields, their types, and their constraints come
from the artifact references read in Stage 1 Step 3.

**Fault Signature consolidation rule:** When multiple related syslog events are discovered
(e.g., different mnemonics or severity levels for the same underlying fault), the research
summary MUST group them under a **single** recommended Fault Signature with multiple events
— not as separate Fault Signature recommendations. Each syslog pattern becomes one entry in
`evaluation.events[]`. The `conditions.logic` field defines how they relate (e.g., `"1 OR 2"`
if any event triggers the fault, `"1 AND 2"` if both are required). Only recommend separate
Fault Signatures when the syslog events represent genuinely **different faults** (different
root cause, different remediation path).

**For each selected artifact type:**

1. Create a sub-section headed `### Recommended [Artifact Type Name]s` (e.g.,
   `### Recommended Fault Signatures`, `### Recommended Remediation Guides`).
2. For each recommended artifact instance (new or existing), produce a table with two columns:
   **Field** and **Proposed Value / Source**. Populate every field defined in that artifact's
   reference, or every required section for template-driven artifacts, using evidence from the
   per-source findings files:
   - Names, patterns, and syslog strings → from cisco-support-findings.md
   - Causes, remediation steps, software versions → from cisco-docs-findings.md
3. Note whether the artifact appears to already exist based on research results.
4. Add a **Notes** block below each table explaining any assumptions, open questions, or
   validation steps specific to that artifact instance (e.g., regex edge cases for a Fault
   Signature, or unresolved validation questions for a Remediation Guide).

> **Why reference-driven?** The field list or section structure comes from the live artifact
> reference files in `ia-create/references/` — schema references for YAML artifacts and
> `remediation-guide-template.md` for Remediation Guides. If those references change, this
> research summary automatically reflects those changes without any edits to this skill.

### Coverage Gaps

List every syslog that has no existing signature based on research results. These are the
highest-priority candidates for new signature creation.

| Syslog | Existing Coverage? | Recommended Action |
|--------|-------------------|--------------------|
| `[syslog string]` | ✅ Covered (existing signature found) | Review existing; supplement if needed |
| `[syslog string]` | ❌ No coverage | Create artifacts for this syslog |

### Next Steps

Generate a **Next Steps checklist tailored to the user's selected artifact types**. Base the
steps on:
1. The creation order constraints documented in `ia-create/SKILL.md` (e.g., Remediation
   Guides must exist before Fault Signatures can reference them)
2. Any validation or required-field warnings from the research findings
3. The recommended RG-first workflow if both Fault Signatures and Remediation Guides are selected

**Always include as a final step:**
- Suggest running `ia-create` with the research folder as input

---

### Final Interaction

After writing all three files, present a brief summary:

> Research complete. Files written to `research/<name>/`:
> - `cisco-support-findings.md`
> - `cisco-docs-findings.md`
> - `research-summary.md`
>
> Summary: [N] syslog(s) researched — [N] already covered, [N] new gaps found.
> Selected artifact types: [comma-separated list of selected types].
>
> Would you like to refine the research, add a data source, or proceed to `ia-create`?

---

## Tips

- **Parallel where possible**: The research sources are independent. Run them concurrently
  via sub-agents whenever parallel execution is available.
- **Reference-driven recommendations**: Field names, required sections, and constraints in the
   research summary come from the live `ia-create` artifact references, not from this skill file.
   If those references change, re-read them — don't rely on cached knowledge from a previous
   session.
- **Two regex fields, two syntaxes**: `splunk_regex` uses `*` (Splunk KV store); `regex` uses `.*`
  (Python). Both are required on Fault Signature create — missing either causes a validation
  error. Surface this in the Fault Signature recommendation block.
- **sessionId chaining in cisco-docs**: `ask_cisco_documentation` returns a `sessionId`. Pass it
  in follow-up calls to maintain conversation context. Start a new session for unrelated topics.

---

## Closing Message

When this skill completes and the user is about to proceed to another skill, append
this tip to your final output:

> ---
> **💡 Tip:** Start a **new chat** (click the **+** button at the top of the Copilot
> Chat panel) before running the next skill. This resets the context window and gives
> the next skill a clean slate to work with.
> ---
