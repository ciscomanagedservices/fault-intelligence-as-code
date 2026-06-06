# Remediation Guide: <Title> (<Platform>)

> **Source:** `<source file path, TSG ID, or "inline input">`
> **Generated:** <date>
> **Status:** <Final | Draft — N gaps remaining>

---

## Overview

[2–4 sentences: What fault does this guide address? What technology area is affected?
What is the general approach to diagnosis and repair?]

## Applicability

- **Products:** [List of hardware platforms or product families]
- **Operating Systems:** [OS name and version ranges]
- **Component:** [Primary subsystem: Fan, PSU, Optics, Route Processor, etc.]
- **Severity:** [Critical / Major / Warning / Minor]
- **Related Defects:** [Bug IDs, if any — e.g., CSCxx12345]

## Triggering Events

### Event 1: [Short event name]

- **Type:** [Syslog / Alarm / State Counter / Metric]
- **Message ID:** [Syslog mnemonic, e.g., BGP-5-ADJCHANGE]
- **Example Message:**
  ```
  [Paste a complete, realistic sample message exactly as it appears in the log]
  ```
- **Key Values to Extract:** [Describe what to capture — e.g., "The neighbor IP address
  appearing after 'neighbor' in the message", "The fan tray number in the FT<n> field"]

### Event 2: [Short event name] *(if applicable)*

[Same structure as Event 1]

### Correlation *(if multiple events)*

- **Logic:** [Both events must occur (AND) / Either event triggers the fault (OR)]
- **Time Window:** [e.g., "Both events within 5 minutes" or omit for single-event]

### Recovery Indicator *(optional)*

- **Recovery Event:** [Description + example message that indicates the fault cleared]
- **Recovery Window:** [e.g., "Within 5 minutes of the triggering event"]

## Symptoms

- [Observable behavior 1 — what the engineer notices]
- [Observable behavior 2]
- [Observable behavior 3]

## Diagnosis & Repair Steps

### Step 1: [Purpose — what this step determines]

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

**Decision Point:** [What to do based on the output — e.g., "If X is confirmed, proceed
to Step 2. If Y, this guide does not apply."]

**Caution:** [Optional — safety warnings about the command or action]

---

### Step 2: [Purpose]

[Same structure as Step 1. Repeat for each diagnosis and repair step.]

## Escalation

**When to Escalate:**
- [Condition 1 — e.g., "All repair steps applied but fault persists"]
- [Condition 2]

**Evidence to Collect Before Escalating:**
```
[List of show commands and data to gather]
```

## Post-Repair Verification

**Commands:**
```
[CLI commands to confirm the fault is resolved]
```

**Expected Healthy Output:**
```
[What the output should look like after successful repair]
```

## References *(optional)*

- [Bug ID or doc title — URL if available]

---

## Clarifying Questions

*(Only present if unanswered questions remain. Contains ONLY the unanswered questions from the questionnaire. Remove this section when all gaps are resolved.)*

**<ID>.** <Question text>

> **Answer:** <your answer here>

---

## Summary of Optimizations

*(Always present. Lists any steps, thresholds, branches, or sections added or modified beyond the original source, with justification. Notes which items were informed by research vs. SME answers vs. original source. If nothing was added, write "No instructions were added beyond the original source.")*
