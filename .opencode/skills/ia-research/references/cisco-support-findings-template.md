# Cisco Support Findings — [Issue Name]

**Research Date:** [YYYY-MM-DD]
**Inputs:** SR IDs: [list] | Defect IDs: [list] | Syslog keywords: [list]

---

## SR Summaries

### SR [ID] — [Title]

| Field | Value |
|-------|-------|
| **SR Number** | [ID] |
| **Title** | [title] |
| **Status** | [Open / Closed] |
| **Severity** | [1–4] |
| **Platform** | [e.g., Cisco 8808, IOS XR 7.x] |
| **Technology** | [e.g., XR-Routing-Platforms] |
| **Sub-technology** | [e.g., 8000 Series — Hardware Failures] |
| **Opened** | [date] |
| **Closed** | [date or N/A] |
| **Customer** | [customer name] |
| **Case Owner** | [name, email] |

**Problem Statement:**
[Brief description of the reported issue]

**Key Syslogs Mentioned in Case:**
```
[Paste exact syslog strings from case notes here — these are used verbatim for regex design]
```

**Referenced Defects:**
- [CSCxxxxxxx] — [brief description]

**Resolution:**
[How the case was resolved — reload, RMA, process restart, software upgrade, etc.]

**Software Version(s):**
- Affected: [version]
- Fixed (if known): [version]

---

<!-- Repeat SR Summary block for each SR researched -->

---

## Defect Summaries

### [CSCxxxxxxx] — [Defect Title]

| Field | Value |
|-------|-------|
| **Defect ID** | [CSCxxxxxxx] |
| **Status** | [Open / Resolved / Duplicate] |
| **Severity** | [1–6] |
| **Product** | [product family] |
| **Platform** | [platforms affected] |

**Symptom:**
[What the customer observes]

**Conditions:**
[When/why this triggers]

**Workaround:**
[Workaround if any, or "None"]

**Fixed In Release(s):**
- [release version]

**Affected Releases:**
- [release version]

**Related SRs / Bugs:**
- [cross-references]

---

<!-- Repeat Defect Summary block for each defect researched -->

---

## Keyword Search Results

Bugs found via `mcp_cisco-support_search_bugs_by_keyword`:

| Keyword Used | Defect ID | Title | Severity | Status | Relevance |
|-------------|-----------|-------|----------|--------|-----------|
| [mnemonic] | [CSCxxxxxxx] | [title] | [1–6] | [status] | [High / Medium / Low — why?] |

---

## Consolidated Syslog Strings

All exact syslog strings extracted from cases — use these as the basis for regex pattern design:

```
[exact syslog line 1]
[exact syslog line 2]
[exact syslog line N]
```

**Facility codes identified:**
- `[FACILITY-MNEMONIC-SEVERITY-EVENT]` — from SR [ID]

---

## Key Findings

- [Bullet: most important finding for IA creation]
- [Bullet: platform scope, software version scope]
- [Bullet: any workaround that should appear in Remediation Guide repair steps]
- [Bullet: any cross-referenced defects or SRs that expand coverage]
