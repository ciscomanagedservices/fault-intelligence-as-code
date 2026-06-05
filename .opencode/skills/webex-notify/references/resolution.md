---
required_vars:
  - incident_id
  - alert_def_id
  - device
  - steps_run
  - kb_sev_level
optional_vars:
  - incident_title
  - fault_name
  - workflow_id
  - affected_entity
  - rca_summary
  - evidence_timeline
  - remediation_summary
  - verification_result
  - approvals_summary
  - residual_risk
  - follow_up_actions
  - alert_definition_bundle_url
  - splunk_results_link
  - session_log_path
  - troubleshooting_bundle_path
  - troubleshooting_report_path
  - attachment_path
  - test_title_prefix
  - test_run_id
---

---

**{{ test_title_prefix }}✅ Fault Resolved**

---

- **Incident ID:** {{ incident_id }}
- **Incident Title:** {{ incident_title }}
- **Fault / Alert Definition:** {{ alert_def_id }} — {{ fault_name }}
- **Device:** {{ device }}
- **Affected entity:** {{ affected_entity }}
- **Severity:** {{ kb_sev_level }}
- **Workflow:** {{ workflow_id }}
- **Steps executed:** {{ steps_run }}
- **Alert Definition bundle:** [Open bundle]({{ alert_definition_bundle_url }})

**RCA:** {{ rca_summary }}

**Evidence timeline:**
{{ evidence_timeline }}

**Remediation applied:**
{{ remediation_summary }}

**Verification:** {{ verification_result }}

**Approvals:** {{ approvals_summary }}

**Residual risk:** {{ residual_risk }}

**Follow-up:** {{ follow_up_actions }}

**Splunk alert:** [View alert results]({{ splunk_results_link }})

**Session log:** `{{ session_log_path }}`

**Troubleshooting bundle:** `{{ troubleshooting_bundle_path }}`

**HTML report:** `{{ troubleshooting_report_path }}`

The Repair Action Workflow completed successfully.
{% if test_run_id %}_test_run_id: {{ test_run_id }}_{% endif %}
