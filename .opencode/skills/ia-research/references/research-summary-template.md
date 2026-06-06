# Research Summary — [Issue Name]

**Research Date:** [YYYY-MM-DD]
**Prepared by:** IA Research Skill
**Sources Used:** [cisco-support] [cisco-docs]
**Artifact Types Selected:** [comma-separated list of artifact types chosen in Stage 1 intake]

**Reference Files:**
- [cisco-support-findings.md](./cisco-support-findings.md)
- [cisco-docs-findings.md](./cisco-docs-findings.md)

---

## Findings Overview

[2–4 sentence synthesis: what was the root cause, what syslogs characterize it, and what platforms are
affected.]

---

## Artifact Recommendations

<!-- INSTRUCTIONS (remove before saving):
  This section is generated dynamically based on the artifact types selected in Stage 1.
  For each selected artifact type, create a sub-section using the pattern below.
  The field list or required section structure for each sub-section comes from the artifact
  reference file read in Stage 1 (for example,
  .opencode/skills/ia-create/references/fault-signature-schema.md or
  .opencode/skills/ia-create/references/remediation-guide-template.md).
  Do NOT hard-code field names here — derive them from the live artifact references.

  SECTION PATTERN per artifact type:

    ### Recommended [Artifact Type Name]s

    #### [Artifact Type] [N]: [Short Descriptive Name]

    | Field | Proposed Value | Source |
    |-------|---------------|--------|
    ... (one row per field or required section defined in the artifact reference for this type)

    **Coverage status:** `new` / `existing (ID: [id])`
    <!-- For new artifacts: ID will be assigned at publish time (draft uses placeholder 000000).
         For existing: cite the real published ID. -->

    **Notes:** [Assumptions, open questions, validation steps specific to this instance]

  EXAMPLE SUB-SECTION HEADINGS (adapt to selected types):
    ### Recommended Fault Signatures
    ### Recommended Remediation Guides
    ### Recommended Repair Action Workflows
    ### Recommended Collection Lists
    ### Recommended Parsers
    ### Recommended Health Check Rules
-->

[For each artifact type selected in Stage 1, insert a sub-section here following the pattern
 above. Populate field values from the per-source findings files, using cisco-support-findings.md
 and cisco-docs-findings.md as the primary evidence sources.]

<!-- Repeat the sub-section block for each recommended artifact instance -->

---

## Coverage Gap Summary

| Syslog | Existing Coverage? | Recommended Action |
|--------|-------------------|--------------------|
| `[syslog string]` | ✅ TSG [id] already covers this | Review existing; consider supplemental artifact |
| `[syslog string]` | ❌ No coverage | Create artifacts for this syslog (see recommendations above) |

---

## Next Steps

<!-- Generate this checklist based on the artifact types selected in Stage 1.
  Steps must reflect creation order constraints from ia-create/SKILL.md.
  Key constraints to apply:
    - Remediation Guides should be created before Fault Signatures (RG-first workflow)
    - Fault Signatures must reference an existing Remediation Guide / TSG by numeric ID
    - The `categories` field is required on Remediation Guide creation (causes 400 if omitted)
  Always end with the ia-create step.
-->

- [ ] Review proposed artifact fields above — confirm IDs, regexes, and field values with a SME
- [ ] [Per-artifact validation steps — derived from schemas read in Stage 1]
- [ ] [Artifact creation order steps — derived from ia-create creation order constraints]
- [ ] Proceed to `ia-create` with this research folder as input
- [ ] [Any additional steps specific to this issue]
