---
required_vars:
  - incident_id
  - alert_def_id
  - device
  - step_id
  - step_name
  - outcome
  - action
optional_vars:
  - incident_title
  - fault_name
  - command_summary
  - evidence_summary
  - validation_result
  - decision_basis
  - variables_summary
  - next_step
  - reasoning
  - test_title_prefix
  - test_run_id
---

---

**{{ test_title_prefix }}Step {{ step_id }} complete** — {{ step_name }}

---

- **Incident ID:** {{ incident_id }}
- **Incident Title:** {{ incident_title }}
- **Fault / Alert Definition:** {{ alert_def_id }} — {{ fault_name }} on **{{ device }}**
- **Outcome:** {{ outcome }}
- **Validation:** {{ validation_result }}
- **Next action:** {{ action }}

**Command / action:**
{{ command_summary }}

**Evidence observed:**
{{ evidence_summary }}

**Decision basis:** {{ decision_basis }}

**Variables updated:** {{ variables_summary }}

**Next step:** {{ next_step }}

{% if reasoning %}**Reasoning:** {{ reasoning }}{% endif %}
{% if test_run_id %}_test_run_id: {{ test_run_id }}_{% endif %}
