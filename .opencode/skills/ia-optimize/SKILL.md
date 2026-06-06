---
name: ia-optimize
description: >-
  Optimize Remediation Guide intelligence artifacts by generating SME
  questionnaires, drafting platform-specific optimized `.md` (RG) files, and
  refining guides to resolve remaining gaps. Output format aligns with the
  `ia-create` Remediation Guide template (Overview, Applicability,
  Triggering Events, Symptoms, Diagnosis & Repair Steps, Escalation,
  Post-Repair Verification, References). Use this skill whenever the user says
  "ia-optimize", "optimize this RG", "optimize remediation guide",
  "optimize troubleshooting guide", or asks
  to improve, rewrite, or produce a platform-specific version of a Remediation
  Guide or troubleshooting guide. Accepts a local file path (`.md` (RG), markdown, or plain text), or
  inline text pasted into the message. Can optionally invoke cisco-support and
  cisco-docs MCP tools for on-demand research enrichment when SR IDs, defect
  IDs, or platform context are present. In the future, this skill will be
  extended to Fault Signatures and Repair Action Workflows.
---

# IA Optimize Skill

Produce focused, platform-specific optimized Remediation Guides (`.md` (RG) files)
from existing RG drafts or raw troubleshooting procedures. The
output format matches the `ia-create` Remediation Guide template exactly —
the same section structure, per-step format, and conventions used to create new
RGs from scratch.

Operates in three modes:

1. **Mode 1 — Questionnaire Generation**: Source input → SME questionnaire with
   targeted clarifying questions mapped to RG template sections
2. **Mode 2 — First Draft Generation**: Answered questionnaire → full optimized
   `.md` (RG) with platform CLI, pass/fail examples, gap markers
3. **Mode 3 — Refinement**: Optimized `.md` (RG) with newly answered questions →
   resolved gaps, updated guide

---

## Step 0: Resolve Input

Before detecting the mode, determine the source content. Four accepted input paths:

### A — Local `.md` (RG) File

If the user provides a path to an existing `.md` (RG) file (the ia-create Remediation Guide format):

1. Read the file.
2. Parse the RG sections: Overview, Applicability, Triggering Events, Symptoms, Diagnosis & Repair Steps, Escalation, Post-Repair Verification, References.
3. If the file already has `## Clarifying Questions` sections, this may be Mode 2 or Mode 3 input.
4. Construct a source object from the parsed content.

**Output location**: Save output files alongside the source file (same directory).

### B — Local File Path (other formats)

If the user provides a file path to a non-`.md` (RG) file:

1. Read the file using the file read tool.
2. Detect the format:
   - **YAML** — parse fields: `name`, `objective`, `troubleshooting_actions` (or `actions`), metadata fields
   - **Markdown** — detect sections; if it already has `## Clarifying Questions` or `## Diagnosis & Repair Steps` sections, this may be Mode 2 or Mode 3 input
   - **Plain text** — treat as raw `actions` / `troubleshooting_actions` content

3. Construct a source object from the parsed content.

**Output location**: Save output files alongside the source file (same directory).

### C — Inline Text

If the user pastes content directly in their message:

1. Parse as plain-text troubleshooting steps.
2. Ask for the guide name and platform if not provided (a brief clarifying question is acceptable here).
3. If the pasted content already has `## Clarifying Questions` or `## Diagnosis & Repair Steps` sections, treat as Mode 2 or Mode 3 input.

**Output location**: Save output files in `ia-drafts/<issue-name>/`.

---

## Step 1: Mode Detection

After resolving input content, determine which mode applies. These conditions are mutually exclusive and exhaustive.

| Mode | Condition |
|------|-----------|
| **Mode 1 — Questionnaire** | Input does NOT contain a `## Clarifying Questions` section |
| **Mode 2 — First Draft** | Input HAS `## Clarifying Questions` with ≥1 filled `> **Answer:**` block (non-empty, not `<your answer here>`) + HAS `## Original Source Reference` + does NOT have `## Diagnosis & Repair Steps` as a generated guide section |
| **Mode 3 — Refinement** | Input HAS `## Diagnosis & Repair Steps` sections (generated guide) + HAS `## Clarifying Questions` with ≥1 newly filled `> **Answer:**` block |

**Edge case**: If the input is a fresh file with no questionnaire structure, always enter Mode 1.

---

## Guide Generation Rules

These rules apply during Mode 2 and Mode 3 when generating or modifying the optimized `.md` (RG) body. They do NOT apply in Mode 1 (questionnaire generation only).

The output **must** follow the section structure and per-step format defined in the
`ia-create` Remediation Guide template (`references/remediation-guide-template.md`
in the `ia-create` skill). The canonical section order is:

```
# Remediation Guide: [Fault Condition Title]
## Overview
## Applicability
## Triggering Events
## Symptoms
## Diagnosis & Repair Steps
## Escalation
## Post-Repair Verification
## References
```

### Content rules

1. Rewrite each step to be clear, concise, and unambiguous.
2. Determine the product and OS in use from available context; use correct platform-specific CLI commands and terminology. Valid operating systems: IOS XE, IOS XR, NX-OS, SONiC.
3. Use `{{ variable_name }}` (double braces with spaces, Jinja2 convention) for all variable substitution in CLI commands. Do NOT hardcode device names, IPs, or slot numbers.
4. For each CLI command, provide example output for BOTH the expected (healthy) and unexpected (fault confirmed) conditions, along with the decision path for each.
5. Flag any steps that might impact service with: `**Caution:**` followed by a description of the risk and any prerequisites (e.g., maintenance window, traffic drain, physical access).
6. Where instructions are missing for a condition or decision, do NOT invent new instructions. Use `[GAP: <description>]` placeholders instead.
7. If any instructions are added beyond the original source, call them out in `## Summary of Optimizations` at the end of the file.
8. For every conditional check or decision point, enumerate ALL possible outcomes (pass, fail, timeout, unexpected). Use `[GAP: <description>]` for outcomes the original guide does not address.
9. Every wait time, threshold, count, or rate MUST be a specific numeric value with units. Vague terms (e.g., "excessive", "wait for recovery") → `[THRESHOLD NEEDED: <description>]`.
10. Every diagnostic or repair sequence MUST terminate with one of: (a) "proceed to Step N", (b) a resolution confirmation, or (c) an explicit escalation path with who to contact, what data to collect, and the case/ticket reference format.
11. Do NOT add steps that merely re-verify the triggering condition. The trigger (syslog, alarm) is what causes the guide to run — re-checking it is redundant.
12. Keep the guide as simple as the source material and SME answers warrant. Do not add complexity beyond what the source or answers support.
13. The last step in Diagnosis & Repair Steps (or the Post-Repair Verification section) MUST verify that the fault is actually resolved — do not end without a verification step.

### Per-step format (inside `## Diagnosis & Repair Steps`)

Each step uses the ia-create RG format — flat `### Step N:` headings (no phase grouping):

```markdown
### Step N: [Purpose — what this step determines]

**Commands:**
```
[exact CLI commands — use {{ variable_name }} for extracted values]
```

**What to Look For:** [Plain-English description of what the output means]

**Sample Output — Healthy:**
```
[Realistic CLI output showing the non-faulted state]
```

**Sample Output — Fault Confirmed:**
```
[Realistic CLI output showing the faulted state]
```

**Decision Point:** [What to do based on the output — e.g., "If X, proceed to Step N.
If Y, escalate per the Escalation section."]

**Caution:** [Optional — safety warnings about the command or action]
```

Steps that involve physical actions (reseat, RMA, cable swap) use an **Actions:** list
instead of **Commands:** / **Sample Output** blocks.

---

## Mode 1: Questionnaire Generation

### Step 1.1: Analyze the Source Material

Walk through the resolved source content and identify gaps relative to the ia-create RG template sections:

- **Applicability gaps**: Platform, OS, product family, component, severity not specified or ambiguous
- **Triggering Events gaps**: Syslog mnemonic, example message, key values to extract, correlation logic, or recovery indicator missing or unclear
- **Symptoms gaps**: Observable behaviors not listed or too vague
- **Diagnosis & Repair Steps gaps**: Undefined thresholds, vague conditions, missing decision branches, missing CLI commands, missing pass/fail examples
- **Escalation gaps**: Who to contact, what data to collect, escalation conditions unspecified
- **Post-Repair Verification gaps**: No verification commands or expected healthy output defined
- **Service impact assumptions**: Steps that may disrupt traffic or require physical access without explicit callout

### Step 1.2: Offer On-Demand Research

Before generating the questionnaire, check if research would help fill the analysis gaps:

- If `cisco_defect_ids` or `cisco_sr_ids` are present in the source, offer to fetch defect/case details first
- If specific questions about platform CLI, thresholds, or known fixed releases would benefit from documentation, offer to query cisco-docs

Present a **multi-select checklist** via `question`:

> **Optional: enrich with additional research before generating questions?**
> Select any items to research, or skip to proceed directly.

Options (dynamically populated based on what was found in the source):

| Label | When to include |
|---|---|
| `Research defect CSCxx12345` | One option per defect ID found in source |
| `Research SR 69xxxxx` | One option per SR ID found in source |
| `Query cisco-docs for [platform] CLI and thresholds` | When platform context is available |
| `No additional research — proceed with questionnaire` | Always included; mark as `recommended: true` if `ia-research` output is already part of the source content |

> **Note:** If `ia-research` was already run and its output is part of the source
> content (e.g., the source is a research folder or references research findings), that
> research is already factored in — re-fetching is usually unnecessary.

If the user selects research items → run the **On-Demand Research** workflow (see below) for each selected item. Incorporate any resolved facts directly into the analysis and reduce the corresponding clarifying questions.

If the user selects "No additional research" or no research items → proceed directly to questionnaire generation.

### Step 1.3: Generate the Questionnaire

Produce a markdown file using the **questionnaire template** at [references/questionnaire-template.md](./references/questionnaire-template.md).

Organize questions into categories mapped to RG template sections (only include a category if it has questions):

1. **Applicability** — Platform, OS, component, severity clarifications needed to fill the `## Applicability` section.
2. **Triggering Events** — Syslog mnemonics, example messages, extraction targets, correlation logic, or recovery indicators missing or unclear for the `## Triggering Events` section.
3. **Undefined Thresholds** — Numeric values needed for any imprecise condition in the source. Quote the specific source text.
4. **Missing Decision Branches** — Outcomes with no defined next action in the troubleshooting steps. Reference the specific step.
5. **Service Impact Assumptions** — Whether isolation, a maintenance window, or physical access is needed. Reference the specific step.
6. **Escalation Procedures** — Who to contact and what data to collect when steps fail or are exhausted, for the `## Escalation` section.

Each question MUST cite the exact text from the source guide that triggered it.

### Step 1.4: Save and Instruct

Save the questionnaire as `<NAME>-questionnaire.md` in the output location determined in Step 0 (typically `ia-drafts/<issue-name>/`).

Tell the user:

> The questionnaire has been saved to `<filepath>`. It contains clarifying questions that will help produce a focused, right-sized optimized Remediation Guide.
>
> **Next steps:**
> 1. Open the generated markdown file.
> 2. Answer the questions in the **Clarifying Questions** section by replacing `<your answer here>` in each `> **Answer:**` block.
> 3. You can answer all questions or just the ones you know — partial answers are fine.
> 4. When ready, run `ia-optimize` again and provide the answered questionnaire as input.

---

## Mode 2: First Draft Generation

### Step 2.1: Extract Source and Answers

1. Parse the `## Original Source Reference` section to retrieve the original source content.
2. Parse the `## Clarifying Questions` section and extract all filled `> **Answer:**` blocks.
3. Build a list of answered questions (with their resolutions) and unanswered questions.

### Step 2.2: Offer On-Demand Research

After extracting answers, check if unanswered questions could be resolved via research.

Present a **multi-select checklist** via `question`:

> **Optional: research unanswered questions before drafting?**
> This may reduce `[GAP]` markers in the output.

Options (dynamically populated):

| Label | When to include |
|---|---|
| `Research defect CSCxx12345` | One option per defect ID found in source or answers |
| `Research SR 69xxxxx` | One option per SR ID found in source or answers |
| `Query cisco-docs for [specific topic]` | For unanswered questions about platform CLI, versions, or defect behavior |
| `No additional research — proceed with drafting` | Always included; mark as `recommended: true` if research was already done in Mode 1 |

> **Note:** If research was already performed during Mode 1 (Step 1.2), those findings
> are already incorporated — re-fetching the same sources is usually unnecessary.

If the user selects research items → run **On-Demand Research** workflow, then incorporate results as answers to the corresponding questions.

If the user selects "No additional research" → proceed to Step 2.3.

### Step 2.3: Generate the Optimized Remediation Guide

Using the original source AND SME answers, generate the full optimized guide following all **Guide Generation Rules** and the ia-create RG template structure.

The output file is a `.md` (RG) markdown file with these sections in order:

1. **`# Remediation Guide: [Fault Condition Title]`**
2. **`## Overview`** — 2–4 sentences: fault, technology area, general remediation approach
3. **`## Applicability`** — Products, Operating Systems, Component, Severity, Related Defects
4. **`## Triggering Events`** — Per-event subsections (Type, Message ID, Example Message, Key Values to Extract), Correlation logic, Recovery Indicator
5. **`## Symptoms`** — Bullet list of observable behaviors
6. **`## Diagnosis & Repair Steps`** — Flat `### Step N:` structure with Commands, What to Look For, Sample Output — Healthy, Sample Output — Fault Confirmed, Decision Point, Caution
7. **`## Escalation`** — When to Escalate conditions + Evidence to Collect Before Escalating
8. **`## Post-Repair Verification`** — Commands + Expected Healthy Output
9. **`## References`** — Bug IDs, doc links (optional)

**Handling gaps:**

- **Answered questions**: incorporate directly as concrete instructions, thresholds, or decision branches in the appropriate RG section
- **Unanswered questions**: use `[GAP: <description>]` or `[THRESHOLD NEEDED: <description>]` placeholders at the relevant location in the guide
- **Clarifying Questions section**: append ONLY unanswered questions after `## References` as `## Clarifying Questions` (optimization-specific section)
- If ALL questions are answered, omit `## Clarifying Questions` entirely

After the guide body, include:

- **`## Summary of Optimizations`** — lists any steps, thresholds, branches, or sections added or modified beyond the original source, with justification. Notes which items were informed by research vs. SME answers vs. original source. If nothing was added, write "No instructions were added beyond the original source."

Use the **optimized guide template** at [references/optimized-guide-template.md](./references/optimized-guide-template.md) for the full structural reference.

### Step 2.4: Save and Report

Save the guide as `RG######-<NAME>.md` in the output location (typically `ia-drafts/<issue-name>/`).

If all questions were answered:
> The optimized Remediation Guide has been saved to `<filepath>`. All clarifying questions were answered — no gaps remain.

If some questions were unanswered:
> The optimized Remediation Guide has been saved to `<filepath>`. The following questions were not answered and have `[GAP]` placeholders in the guide: [list]. Answer the remaining questions in the `## Clarifying Questions` section of the file and run `ia-optimize` again to resolve them.

---

## Mode 3: Refinement

### Step 3.1: Extract New Answers

Parse `## Clarifying Questions` and identify which `> **Answer:**` blocks have been newly filled in (non-empty, not `<your answer here>`).

### Step 3.2: Resolve Gaps

For each newly answered question:
1. Find the corresponding `[GAP: ...]` or `[THRESHOLD NEEDED: ...]` placeholders in the guide body by matching the question topic/ID.
2. Replace each placeholder with concrete instructions, thresholds, or decision branches derived from the SME's answer, following all **Guide Generation Rules** and the ia-create RG per-step format.

For still-unanswered questions: leave corresponding placeholders in place.

### Step 3.3: Update and Save

1. Remove answered questions from `## Clarifying Questions`. If all are answered, remove the `## Clarifying Questions` section entirely.
2. Update `## Summary of Optimizations` to reflect newly resolved gaps.
3. Update the status line (Draft — N gaps remaining → Final if zero).
4. Overwrite the existing `.md` (RG) file.

If all gaps resolved:
> All gaps have been resolved. The final optimized Remediation Guide has been saved to `<filepath>`.

If some gaps remain:
> Some gaps have been resolved. The following questions still need input: [list unanswered questions]. Update the `> **Answer:**` blocks and run `ia-optimize` again.

---

## On-Demand Research

Run this workflow when the user consents to research in Mode 1 Step 1.2 or Mode 2 Step 2.2.

### Tools Reference

| Tool | Purpose | Required Parameters |
|------|---------|---------------------|
| `mcp_cisco-support_get_case_details` | Fetch full SR: title, technology, syslogs, resolution, linked bugs | SR ID (7–9 digit string) |
| `mcp_cisco-support_get_bug_details` | Fetch defect: symptom, workaround, affected/fixed releases, platform scope | Defect ID (e.g., `CSCwr07525`) |
| `mcp_cisco-support_search_bugs_by_keyword` | Search for related defects by syslog mnemonic or keyword | keyword string |
| `mcp_cisco-docs_health_check` | Verify cisco-docs MCP server is available before querying | (none) |
| `mcp_cisco-docs_search_products` | Resolve platform shortname to the official product string required by `ask_cisco_documentation` | platform name |
| `mcp_cisco-docs_list_cisco_products` | Browse the full product catalog when platform is ambiguous | (none) |
| `mcp_cisco-docs_ask_cisco_documentation` | Technical Q&A scoped to a product; returns `sessionId` for chaining follow-ups | `product` (string), `question` (string), optionally `sessionId` |

### Research Workflow

1. **cisco-support** (if SR IDs or defect IDs are present):
   - For each SR ID → `get_case_details`. Extract: syslog strings, linked defects, platform/software version, resolution steps.
   - For each defect ID → `get_bug_details`. Extract: symptom description, workaround, fixed releases, affected platforms.
   - For any syslog mnemonic in the trigger condition → `search_bugs_by_keyword` to find related defects.

2. **cisco-docs** (if platform context is available):
   - Call `health_check` once. If it fails, skip this source and note it.
   - Call `search_products` with the platform name to get the exact product string.
   - For the primary syslog mnemonic → `ask_cisco_documentation` asking: meaning, causes, recommended CLI commands, and remediation steps. Save the returned `sessionId`.
   - Chain follow-ups via the same `sessionId`: platform-specific CLI syntax, show commands, expected output format, known software versions that address the issue.

3. **Incorporate results**:
   - In Mode 1: use research findings to provide concrete answers to threshold and procedure questions, reducing the number of questions that need SME input
   - In Mode 2: use research findings to fill in SME answers for unanswered questions, reducing `[GAP]` placeholders
   - Always note in `## Summary of Optimizations` which steps were informed by research vs. the original source

---

## Future IA Types

*(These are not yet implemented. Stubs are included here to document the intended extension pattern.)*

### Fault Signature Optimization *(Future)*

Optimizing fault signatures will follow the same three-mode pattern (questionnaire → optimized signature → refinement) with additional validation steps specific to signature authoring:

- **Regex validation**: verify that `splunk_regex` and `regex` both compile correctly and match the intended syslog string; include test cases for both true-positive and false-positive scenarios
- **Platform scope review**: confirm the regex and threshold are appropriate for the declared platforms and OS versions

The questionnaire for a fault signature will cover: regex specificity, false-positive risk, threshold appropriateness, platform scope, and linking to an existing (or planned) RG.

### Repair Action Workflow Optimization *(Future)*

Optimizing repair action workflows will extend Mode 2/3 with structured workflow-specific checks:

- **Step dependency validation**: ensure each workflow step's inputs are produced by a prior step or available from the trigger context
- **Rollback coverage**: every destructive or service-impacting step must have a documented rollback or recovery path
- **Automation feasibility assessment**: steps that require physical access or human judgment should be clearly identified

---

## Tips

- **Research reduces gaps**: even a single `get_bug_details` call often resolves the most common threshold and behavior questions before they become SME questionnaire items
- **sessionId chaining in cisco-docs**: `ask_cisco_documentation` returns a `sessionId`. Pass it in follow-up calls to maintain conversation context. Start a new session for unrelated topics.
- **Keep complexity proportional**: Rule 12 matters — avoid adding steps or decision branches that the source material and answers don't support. The guide should be exactly as complex as necessary, no more.
- **Mode 3 is surgical**: do not rewrite the whole guide during refinement. Only replace the specific `[GAP]` and `[THRESHOLD NEEDED]` placeholders that correspond to newly answered questions.
- **`.md` (RG) is the native format**: the optimized output is always a `.md` (RG) file matching the ia-create template. This means the optimized guide can be fed directly into `ia-create` to derive Fault Signatures and Repair Action Workflows.

---

## Closing Message

When this skill completes and the user is about to proceed to another skill, append
this tip to your final output:

> ---
> **💡 Tip:** Start a **new chat** (click the **+** button at the top of the Copilot
> Chat panel) before running the next skill. This resets the context window and gives
> the next skill a clean slate to work with.
> ---
