---
required_vars:
  - incident_id
  - alert_def_id
  - device
  - step_id
  - reason
optional_vars:
  - incident_title
  - fault_name
  - affected_entity
  - last_command_summary
  - evidence_summary
  - failed_condition
  - recommended_next_steps
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

**{{ test_title_prefix }}❌ Workflow Failed**

---

- **Incident ID:** {{ incident_id }}
- **Incident Title:** {{ incident_title }}
- **Fault / Alert Definition:** {{ alert_def_id }} — {{ fault_name }}
- **Device:** {{ device }}
- **Affected entity:** {{ affected_entity }}
- **Failed at step:** {{ step_id }}
- **Reason:** {{ reason }}
- **Alert Definition bundle:** [Open bundle]({{ alert_definition_bundle_url }})

**Last command/action:**
{{ last_command_summary }}

**Evidence collected:**
{{ evidence_summary }}

**Failed condition:** {{ failed_condition }}

**Recommended next steps:**
{{ recommended_next_steps }}

**Splunk alert:** [View alert results]({{ splunk_results_link }})

**Session log:** `{{ session_log_path }}`

**Troubleshooting bundle:** `{{ troubleshooting_bundle_path }}`

**HTML report:** `{{ troubleshooting_report_path }}`

The Repair Action Workflow exited with FAILURE. Manual investigation required.
{% if test_run_id %}_test_run_id: {{ test_run_id }}_{% endif %}
