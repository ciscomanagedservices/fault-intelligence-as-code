# Cisco Documentation Findings — [Issue Name]

**Research Date:** [YYYY-MM-DD]
**Server Status:** [healthy / unavailable]
**Platform Researched:** [resolved product name from search_products]

---

## Platform Context

| Field | Value |
|-------|-------|
| **Resolved Product Name** | [exact string returned by search_products — use this in ask_cisco_documentation calls] |
| **Technology Area** | [e.g., Security, Hardware, IOS XR Platform] |
| **Relevant Doc Categories** | [from list_categories if used] |

---

## Syslog Mnemonic Explanations

### `[FACILITY-MNEMONIC-SEVERITY-EVENT]`

**Question asked:** "[What does %FACILITY-N-EVENT mean on [product]?]"

**Explanation:**
[Answer from ask_cisco_documentation]

**Known Causes:**
- [cause 1]
- [cause 2]

**Recommended Actions (from documentation):**
1. [action step 1]
2. [action step 2]

**Session ID used:** [sessionId value — for cross-reference if follow-ups were chained]

---

<!-- Repeat mnemonic block for each syslog mnemonic researched -->

---

## Defect-Related Documentation

### [CSCxxxxxxx]

**Question asked:** "[Is there documentation for CSCxxxxxxx on [product]?]"

**Findings:**
[Release note text, field notice reference, or "No specific documentation found"]

**Fixed In / Recommended Version:**
[Software version recommendation from docs]

**Related Field Notices / Security Advisories:**
- [title, link if available]

---

<!-- Repeat defect documentation block for each defect researched -->

---

## Remediation Guidance

Steps documented by Cisco for resolving or mitigating the researched issue:

1. [step 1 — with CLI commands if provided by docs]
2. [step 2]
3. [step N]

**Relevant CLI Commands Referenced:**
```
[show command or config command from documentation]
```

---

## Software Version Recommendations

| Platform | Minimum Recommended | Latest Recommended | Notes |
|----------|--------------------|--------------------|-------|
| [product] | [version] | [version] | [e.g., addresses CSCxxxxxxx] |

---

## Key Findings

- [Bullet: primary cause explanation from official docs]
- [Bullet: recommended remediation from official docs]
- [Bullet: relevant software versions]
- [Bullet: any field notices or security advisories found]
- [Bullet: anything that should appear verbatim in the Remediation Guide objective or actions]
