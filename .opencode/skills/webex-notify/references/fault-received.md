---
required_vars:
  - incident_id
  - alert_def_id
  - device
  - kb_sev_level
  - kb_response_sla
  - kb_change_window_active
  - kb_known_issue_match
optional_vars:
  - incident_title
  - fault_name
  - workflow_id
  - workflow_mode
  - affected_entity
  - alert_summary
  - extracted_vars_summary
  - initial_evidence
  - alert_definition_bundle_url
  - splunk_results_link
  - session_log_path
  - test_title_prefix
  - test_run_id
---

---

<@all>

**{{ test_title_prefix }}🚨 Fault Alert Received — Beginning Remediation**

---

- **Incident ID:** {{ incident_id }}
- **Incident Title:** {{ incident_title }}
- **Fault / Alert Definition:** {{ alert_def_id }} — {{ fault_name }}
- **Device:** {{ device }}
- **Affected entity:** {{ affected_entity }}
- **Severity:** {{ kb_sev_level }} ({{ kb_response_sla }} response SLA)
- **Change window active:** {{ kb_change_window_active }}
- **Known issue match:** {{ kb_known_issue_match }}
- **Workflow:** {{ workflow_id }} ({{ workflow_mode }})
- **Alert Definition bundle:** [Open bundle]({{ alert_definition_bundle_url }})
- **Splunk alert:** [View alert results]({{ splunk_results_link }})

**Alert summary:** {{ alert_summary }}

**Extracted context:** {{ extracted_vars_summary }}

**Initial evidence:**
{{ initial_evidence }}

**Session log:** `{{ session_log_path }}`

Starting Repair Action Workflow now. Step-by-step progress will follow in this room.
{% if test_run_id %}_test_run_id: {{ test_run_id }}_{% endif %}
