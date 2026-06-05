---
name: webex-notify
description: >
  Send Webex notifications for fault remediation workflows using pre-defined
  message templates. Owns the Webex REST API integration and renders templates
  from references/ with variable substitution. Returns a structured status so
  the caller can decide policy when Webex is unconfigured. Use this skill
  whenever you need to send a fault-related notification to the NOC Webex room.
license: Apache-2.0
compatibility: opencode
---

# Webex Notify Skill

You send Webex notifications for the fault remediation system. You do NOT make
remediation decisions — you render a template and POST it to Webex.

---

## Inputs Required

The caller (typically the `network-troubleshooter` agent) provides:

- `event`: the template name. Must match one of the files in `references/`
  without the extension: `fault-received`, `step-progress`, `approval-card`,
  `resolution`, `escalation`, `failure`, `denial`.
- `vars`: a map of `{ key: value }` pairs used to fill `{{ key }}` placeholders
  in the template.

For Markdown templates only, the caller may include `attachment_path` in `vars`.
When present and non-empty, send the message with that local file attached. This
is used by `network-troubleshooter` terminal notifications to attach the zipped
troubleshooting bundle.

---

## Workflow

### 1. Check Webex credentials

Before doing anything else, check the environment:

```bash
if [ -z "$WEBEX_BOT_TOKEN" ] || [ -z "$WEBEX_ROOM_ID" ]; then
  echo '{"status": "skipped", "reason": "env-not-set"}'
  exit 0
fi
```

If either variable is missing, return the skipped JSON above and stop. Do NOT
attempt to send. The caller (`network-troubleshooter`) will treat `skipped` for
an `approval-card` event as auto-approve, with a warning written to the session
log.

### 2. Load the template

Read the matching file from `references/`:

- `fault-received` → `references/fault-received.md`
- `step-progress` → `references/step-progress.md`
- `approval-card` → `references/approval-card.json`
- `resolution` → `references/resolution.md`
- `escalation` → `references/escalation.md`
- `failure` → `references/failure.md`
- `denial` → `references/denial.md`

Each template has a required-variables declaration. For Markdown templates,
this is a YAML frontmatter block between leading `---` lines. For the JSON
template (`approval-card.json`), required vars live under a top-level
`_frontmatter.required_vars` key inside the JSON itself. Validate that every
required variable is present in `vars`. If any are missing, return:

```json
{"status": "failed", "error": "missing-vars", "missing": ["var1", "var2"]}
```

Templates may also declare `optional_vars`. Before rendering, ensure every
optional variable exists in the substitution map with a default empty string.
Do this for all templates, not only test-mode variables. This allows templates
to expose richer context when the caller has it without leaking unresolved
`{{ placeholder }}` text when a value is not available.

**Approval card invariants.** The approval card carries the fields used by
the webhook relay to route the click back to the agent. Do NOT alter these
when rendering — pass them through verbatim:

| Field | Required value |
|-------|----------------|
| `actions[*].data.callback_keyword` | `fault_approval` (relay routes by this) |
| `actions[*].data.incident_id` | The same `incident_id` used when registering the OpenCode session with the relay |
| `actions[*].data.alert_def_id` | Display/audit metadata only; keep it aligned with the operational fault identifier |
| `actions[*].data.decision` | `APPROVED` (Approve button) or `DENIED` (Deny button) |

If any of these are wrong, the relay's websocket bot will either drop the
click or forward an empty decision to the wrong session.

### 3. Render the template

Strip the frontmatter block (for Markdown templates: everything between the
leading `---` lines; for `approval-card.json`: remove the top-level
`_frontmatter` key before sending). Substitute every `{{ var_name }}` reference
with the matching value from `vars`.

If the template declares an optional variable that the caller did not provide,
substitute the empty string. Required variables must still be present and must
not be silently defaulted.

For the `approval-card` template (JSON), substitution happens inside the JSON
string values. Be careful to JSON-escape any value that contains special
characters (newlines in `commands`, for example, become `\n`).

**Note on `webex_room_id`.** The approval card template expects a
`webex_room_id` variable in `vars` (it becomes the top-level `roomId` in the
POST body). The caller — typically the `network-troubleshooter` agent — passes
this from the `WEBEX_ROOM_ID` environment variable. The skill does NOT read
env vars itself; it only substitutes values present in `vars`.

### 4. Send the message

#### For Markdown templates (`fault-received`, `step-progress`, `resolution`, `escalation`, `failure`, `denial`)

Without an attachment, keep the existing JSON payload:

```bash
curl -s -X POST https://webexapis.com/v1/messages \
  -H "Authorization: Bearer $WEBEX_BOT_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg rid "$WEBEX_ROOM_ID" --arg md "$RENDERED_MARKDOWN" \
        '{roomId: $rid, markdown: $md}')"
```

For `event: fault-received` only, the template includes the `<@all>` Markdown
mention token so the initial alert notifies everyone in the Webex space. Keep
this limited to the initial message; do NOT add all-mention text or metadata to
`step-progress`, `resolution`, `escalation`, `failure`, `denial`, or
`approval-card` messages.

With `vars.attachment_path` set, use Webex's multipart message upload. Validate
the file exists before sending. If it does not exist, return
`{"status":"failed","error":"attachment-not-found","attachment_path":"..."}`.

```bash
curl -s -X POST https://webexapis.com/v1/messages \
  -H "Authorization: Bearer $WEBEX_BOT_TOKEN" \
  -F "roomId=$WEBEX_ROOM_ID" \
  -F "markdown=$RENDERED_MARKDOWN" \
  -F "files=@${ATTACHMENT_PATH}"
```

Only attach files for Markdown templates. Do not attach files to
`approval-card` messages.

#### For the Adaptive Card template (`approval-card`)

The template file IS the JSON payload (with `{{ }}` placeholders). After
substitution, POST it directly:

```bash
curl -s -X POST https://webexapis.com/v1/messages \
  -H "Authorization: Bearer $WEBEX_BOT_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$RENDERED_JSON"
```

### 5. Return structured status

On success:

```json
{"status": "sent", "message_id": "<id-from-webex-response>", "attachment_path": "<path-if-used>"}
```

On HTTP error:

```json
{"status": "failed", "error": "<curl-error-or-http-status>"}
```

---

## Constraints

- Do not embed any business logic from `fault-remediation` here. This skill is
  a pure transport layer.
- Do not invent template names. If the caller passes an unknown `event`, return
  `{"status": "failed", "error": "unknown-event", "event": "<value>"}`.
- Do not modify the templates. Only render and send.
- Do not retry on failure. The caller decides retry policy.

---

## Template Authoring Convention

Every template in `references/` MUST start with a YAML frontmatter block
listing its required variables, e.g.:

```markdown
---
required_vars:
  - incident_id
  - alert_def_id
  - device
  - kb_sev_level
---

**Fault Alert Received**

- Incident ID: {{ incident_id }}
- Fault ID: {{ alert_def_id }}
- Device: {{ device }}
- Severity: {{ kb_sev_level }}
```

This makes templates self-describing and lets the skill validate inputs before
attempting a render.

---

## Test Mode (Optional `[TEST]` Tagging)

When the caller is exercising a RAW under test (`raw-test-author` /
`scripts/run_raw_tests.py` / the agent in test mode), it will additionally
include these two **optional** variables in every `vars` map:

| Variable | Purpose |
|----------|---------|
| `test_title_prefix` | Set to `"[TEST]"` when the caller is in test mode, otherwise empty or absent. |
| `test_run_id` | Short identifier (e.g. 8 hex chars) tying every notification from one test run together. |

These two vars are **never required** by any template — they are pure
augmentations and follow the same optional-variable defaulting rules as other
optional vars. Each Markdown template's first body line begins with
`{{ test_title_prefix }}` and each renders a single trailing line:

```
_test_run_id: {{ test_run_id }}_
```

When the caller omits both vars, substitute the empty string for each
(`{{ test_title_prefix }}` → empty, `{{ test_run_id }}` → empty) as part of the
general optional-variable defaulting step.

For the `approval-card.json` template, `test_title_prefix` is concatenated to
the top-level `text` field and `test_run_id` is added as an extra fact-set
entry. The card's `actions[*].data.test_run_id` is also set so the eventual
webhook click can be correlated to the test run, but the relay must still
route by `callback_keyword: fault_approval` + `incident_id` — those invariants
do not change. `test_run_id` never replaces `incident_id`; it is supplemental
test-correlation metadata only.
