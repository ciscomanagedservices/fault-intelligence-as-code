# Optimization Questionnaire: <Title> (<Platform>)

> **Source:** `<source file path, TSG ID, or "inline input">`
> **Generated:** <date>
> **Status:** Questionnaire — Pending SME Input

---

## Analysis Summary

<2–4 sentence summary: what the source guide covers, the detected platform/OS, the trigger condition, and the key areas that need clarification before an optimized Remediation Guide can be drafted.>

---

## Clarifying Questions

The following questions must be answered before the optimized Remediation Guide can be generated. Replace `<your answer here>` in each **Answer** block with your response. You may answer all or some — partial answers are accepted, and unanswered questions will become `[GAP]` placeholders in the generated guide.

### Applicability

*(Only present if applicability questions exist — platform, OS, component, or severity cannot be inferred from the source.)*

**A1.** <Question text. Reference the source content that triggered this question.>

> **Answer:** <your answer here>

### Triggering Events

*(Only present if triggering event questions exist — syslog mnemonics, example messages, extraction targets, correlation logic, or recovery indicators are missing or unclear.)*

**TE1.** <Question text. Reference the source content that triggered this question.>

> **Answer:** <your answer here>

### Undefined Thresholds

*(Only present if threshold questions exist.)*

**T1.** <Question text. Reference the exact source text that triggered this question.>

> **Answer:** <your answer here>

### Missing Decision Branches

*(Only present if decision branch questions exist.)*

**D1.** <Question text. Reference the specific step and outcome that has no defined next action.>

> **Answer:** <your answer here>

### Service Impact Assumptions

*(Only present if service impact questions exist.)*

**S1.** <Question text. Reference the specific step that may require a maintenance window, traffic drain, or physical access.>

> **Answer:** <your answer here>

### Escalation Procedures

*(Only present if escalation questions exist.)*

**E1.** <Question text. Reference the step where escalation is implied but the procedure is not defined.>

> **Answer:** <your answer here>

---

## Original Source Reference

The following is the original source content for reference while answering the questions above.

### Overview

<overview text, reproduced verbatim or summarized from the source>

### Applicability

| Field | Value |
|-------|-------|
| Products | <products/platforms from source, or "not specified"> |
| Operating Systems | <OS and versions from source, or "not specified"> |
| Component | <component from source, or "not specified"> |
| Severity | <severity from source, or "not specified"> |
| Related Defects | <defect IDs from source, or "none"> |

### Triggering Events

*(Populated from the source guide's trigger conditions — syslog messages, alarms, or linked signatures. If the source has no explicit trigger information, note "No triggering events defined in source.")*

| Field | Value |
|-------|-------|
| Event Type | <Syslog / Alarm / State Counter / Metric, or "not specified"> |
| Message ID | <syslog mnemonic, or "not specified"> |
| Example Message | <sample syslog string, or "not available"> |
| Key Values to Extract | <variables to capture, or "not specified"> |
| Correlation Logic | <AND / OR, or "single event"> |
| Recovery Indicator | <recovery event description, or "not specified"> |

### Symptoms

<symptom bullets from the source, or "not specified">

### Troubleshooting / Repair Actions (Original)

<actions or troubleshooting steps text, reproduced verbatim from the source>

### Escalation (Original)

<escalation text from the source, or "not specified">

### Post-Repair Verification (Original)

<verification text from the source, or "not specified">

---

## Instructions for SME Review

1. Review the **Clarifying Questions** section above and fill in your answers by replacing `<your answer here>` in each `> **Answer:**` block.
2. You do not need to answer every question — answer what you can. Unanswered questions will produce `[GAP]` placeholders in the generated guide that can be resolved later.
3. When you are ready, run `ia-optimize` again and provide this file as input. The agent will generate the full optimized Remediation Guide (`.md` (RG)) using your answers and the original source reference.
