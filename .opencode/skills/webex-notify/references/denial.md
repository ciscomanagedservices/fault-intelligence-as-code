---
required_vars:
  - incident_id
  - alert_def_id
  - device
  - step_id
  - commands
optional_vars:
  - incident_title
  - fault_name
  - affected_entity
  - approval_context
  - evidence_summary
  - operator
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

**{{ test_title_prefix }}🛑 Config Change Denied**

---

- **Incident ID:** {{ incident_id }}
- **Incident Title:** {{ incident_title }}
- **Fault / Alert Definition:** {{ alert_def_id }} — {{ fault_name }}
- **Device:** {{ device }}
- **Affected entity:** {{ affected_entity }}
- **Step:** {{ step_id }}
- **Operator:** {{ operator }}
- **Alert Definition bundle:** [Open bundle]({{ alert_definition_bundle_url }})

**Approval context:** {{ approval_context }}

**Evidence summary:**
{{ evidence_summary }}

Operator denied the following proposed commands:

```
{{ commands }}
```

**Splunk alert:** [View alert results]({{ splunk_results_link }})

**Session log:** `{{ session_log_path }}`

**Troubleshooting bundle:** `{{ troubleshooting_bundle_path }}`

**HTML report:** `{{ troubleshooting_report_path }}`

Workflow has been escalated for manual review.
{% if test_run_id %}_test_run_id: {{ test_run_id }}_{% endif %}
