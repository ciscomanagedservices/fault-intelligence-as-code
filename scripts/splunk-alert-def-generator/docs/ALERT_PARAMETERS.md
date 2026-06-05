# Splunk Alert Parameters Reference

Complete reference for all parameters accepted when creating a saved search / alert definition via the Splunk REST API (`/services/saved/searches`) or the Python SDK (`svc.saved_searches.create()`).

---

## Core Alert Settings

| Parameter | Type | Default | Description |
|---|---|---|---|
| `search` | string | `""` | The SPL search query that drives the alert. Required. |
| `description` | string | `""` | Human-readable description of the alert. |
| `disabled` | bool | `false` | Whether the alert is disabled (`0`=active, `1`=disabled). |
| `is_scheduled` | bool | `false` | Must be `1` for the alert to run on a schedule. |
| `cron_schedule` | string | `""` | Cron expression defining when the search runs (e.g. `*/5 * * * *`). |
| `realtime_schedule` | bool | `true` | If `true`, the scheduler runs at the scheduled time. If `false`, skips execution if the previous run hasn't finished. |
| `schedule_priority` | string | `"default"` | Priority: `default`, `higher`, or `highest`. |
| `schedule_window` | string | `"0"` | Number of seconds the scheduler may delay the start. `"auto"` lets Splunk decide. |
| `run_on_startup` | bool | `false` | If `true`, runs the search when Splunk restarts (catches up missed runs). |
| `max_concurrent` | int | `1` | Max concurrent instances of this scheduled search. |

---

## Trigger Conditions

| Parameter | Type | Default | Description |
|---|---|---|---|
| `alert_type` | string | `"always"` | When to trigger: `"always"` (fires if search returns results), `"custom"` (uses `alert_condition`). |
| `alert_condition` | string | `""` | Custom SPL condition evaluated against results (used when `alert_type=custom`). e.g. `search count > 10`. |
| `alert_comparator` | string | `""` | Legacy. Comparator for `counttype`/`quantity` mode (e.g. `greater than`, `less than`, `equal to`). |
| `alert_threshold` | string | `""` | Legacy. Threshold value used with `alert_comparator`. |
| `counttype` | string | — | Legacy trigger mode: `"number of events"`, `"number of hosts"`, `"number of sources"`, or `"custom"`. |
| `quantity` | int | — | Legacy. The numeric quantity compared against `relation`. |
| `relation` | string | — | Legacy. `"greater than"`, `"less than"`, `"equal to"`, `"not equal to"`, `"drops by"`, `"rises by"`. |

> **Note**: In modern Splunk versions the preferred approach is `alert_type=always` with threshold logic in SPL itself (e.g. `| where count > 10`), or `alert_type=custom` with `alert_condition`.

---

## Alert Severity & Tracking

| Parameter | Type | Default | Description |
|---|---|---|---|
| `alert.severity` | int | `3` | 1=debug, 2=info, 3=warn, 4=error, 5=critical, 6=fatal. |
| `alert.track` | bool | `false` | If `true`, triggered alerts appear in the Triggered Alerts page. |
| `alert.digest_mode` | bool | `true` | If `true`, one alert fires per scheduled execution. If `false`, one alert fires per result row. |
| `alert.expires` | string | `"24h"` | How long triggered alert records are retained (e.g. `"24h"`, `"7d"`, `"1h"`). |

---

## Alert Suppression (Throttling)

| Parameter | Type | Default | Description |
|---|---|---|---|
| `alert.suppress` | bool | `false` | Enable suppression (throttling) — prevents re-firing within the suppression period. |
| `alert.suppress.period` | string | `""` | Suppression window (e.g. `"10m"`, `"1h"`, `"1d"`). |
| `alert.suppress.fields` | string | `""` | Comma-separated list of fields to group suppression by. |
| `alert.suppress.group_name` | string | `""` | Custom group name for suppression grouping. |

---

## Dispatch / Time Range

| Parameter | Type | Default | Description |
|---|---|---|---|
| `dispatch.earliest_time` | string | `""` | Earliest time for the search window (e.g. `"-5m@m"`, `"-1d@d"`, `"-1h"`). |
| `dispatch.latest_time` | string | `""` | Latest time for the search window (e.g. `"now"`, `"@h"`). |
| `dispatch.ttl` | string | `"2p"` | Time-to-live for search artifacts. `"2p"` = 2× the schedule period. |
| `dispatch.max_count` | int | `500000` | Max number of results to return. |
| `dispatch.max_time` | int | `0` | Max search runtime in seconds (0=unlimited). |
| `dispatch.buckets` | int | `0` | Number of timeline buckets. |
| `dispatch.lookups` | bool | `true` | Whether to perform lookup field actions. |
| `dispatch.spawn_process` | bool | `true` | Whether to spawn a new process for the search. |
| `dispatch.auto_cancel` | string | `"0"` | Auto-cancel after N seconds of inactivity (0=disabled). |
| `dispatch.auto_pause` | string | `"0"` | Auto-pause after N seconds of inactivity (0=disabled). |
| `dispatch.reduce_freq` | int | `10` | How frequently (in seconds) to run the reduce phase for streaming searches. |
| `dispatch.rt_backfill` | bool | `false` | For real-time searches, backfill results from historical data. |
| `dispatch.sample_ratio` | string | `"1"` | Sample ratio for the search (1=no sampling). |
| `dispatchAs` | string | `"owner"` | Run the search as `"owner"` or `"user"`. |

---

## Alert Actions

Actions determine what happens when the alert fires. Set `actions` to a comma-separated list of enabled actions.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `actions` | string | `""` | Comma-separated list of actions to trigger (e.g. `"email"`, `"webhook"`, `"logevent"`, `"script"`, `"lookup"`). |

### Email Action (`action.email.*`)

| Parameter | Default | Description |
|---|---|---|
| `action.email` | `false` | Enable the email action. |
| `action.email.to` | `""` | Recipient email addresses (comma-separated). |
| `action.email.cc` | `""` | CC recipients. |
| `action.email.bcc` | `""` | BCC recipients. |
| `action.email.from` | `"splunk"` | Sender address. |
| `action.email.subject` | `"Splunk Alert: $name$"` | Subject line (supports `$name$`, `$results.count$`, etc.). |
| `action.email.message.alert` | `"The alert condition for '$name$' was triggered."` | Email body text. |
| `action.email.format` | `"table"` | Result format: `"table"`, `"raw"`, `"csv"`, `"html"`. |
| `action.email.sendresults` | `false` | Attach results to the email. |
| `action.email.sendpdf` | `false` | Attach a PDF report. |
| `action.email.sendcsv` | `"0"` | Attach results as CSV. |
| `action.email.inline` | `false` | Inline results in the email body. |
| `action.email.include.results_link` | `"1"` | Include a link to results. |
| `action.email.include.search` | `"0"` | Include the search string in the email. |
| `action.email.include.trigger` | `"0"` | Include trigger condition details. |
| `action.email.include.trigger_time` | `"0"` | Include the trigger timestamp. |
| `action.email.include.view_link` | `"1"` | Include a link to the view. |
| `action.email.mailserver` | `"localhost"` | SMTP server hostname. |
| `action.email.use_tls` | `false` | Enable TLS for the SMTP connection. |
| `action.email.use_ssl` | `false` | Enable SSL for the SMTP connection. |
| `action.email.auth_username` | `""` | SMTP auth username. |
| `action.email.auth_password` | `""` | SMTP auth password. |
| `action.email.maxresults` | `10000` | Max results to include. |
| `action.email.maxtime` | `"5m"` | Max time to spend generating email. |
| `action.email.priority` | `"3"` | Email priority (1=highest, 5=lowest). |
| `action.email.content_type` | `"html"` | Email content type: `"html"` or `"plain"`. |
| `action.email.useNSSubject` | `"0"` | Use namespace-qualified subject. |
| `action.email.width_sort_columns` | `true` | Sort columns by width in table format. |

### Webhook Action (`action.webhook.*`)

| Parameter | Default | Description |
|---|---|---|
| `action.webhook` | `"0"` | Enable the webhook action. |
| `action.webhook.param.url` | `""` | URL to POST alert data to. |

### Log Event Action (`action.logevent.*`)

| Parameter | Default | Description |
|---|---|---|
| `action.logevent` | `"0"` | Enable the log event action. |
| `action.logevent.param.event` | `""` | Event text to log. |
| `action.logevent.param.host` | `""` | Host value for the logged event. |
| `action.logevent.param.index` | `"main"` | Target index. |
| `action.logevent.param.source` | `"alert:$name$"` | Source value. |
| `action.logevent.param.sourcetype` | `"generic_single_line"` | Sourcetype value. |

### Script Action (`action.script.*`)

| Parameter | Default | Description |
|---|---|---|
| `action.script` | `"0"` | Enable the script action. |
| `action.script.filename` | `""` | Script filename (in `$SPLUNK_HOME/bin/scripts/`). |

### Lookup Action (`action.lookup.*`)

| Parameter | Default | Description |
|---|---|---|
| `action.lookup` | `"0"` | Enable the lookup action. |
| `action.lookup.filename` | `""` | Target CSV lookup filename. |
| `action.lookup.append` | `"0"` | Append to existing lookup (`1`) or overwrite (`0`). |

---

## Cron Schedule Reference

The `cron_schedule` field uses standard 5-field cron syntax:

```
┌───── minute (0–59)
│ ┌───── hour (0–23)
│ │ ┌───── day of month (1–31)
│ │ │ ┌───── month (1–12)
│ │ │ │ ┌───── day of week (0–7, 0 and 7 = Sunday)
│ │ │ │ │
* * * * *
```

| Example | Meaning |
|---|---|
| `*/5 * * * *` | Every 5 minutes |
| `0 * * * *` | Every hour at :00 |
| `0 6 * * *` | Daily at 06:00 |
| `0 14 * * *` | Daily at 14:00 |
| `0 0 * * 1` | Every Monday at midnight |
| `*/15 9-17 * * 1-5` | Every 15 min during business hours (Mon–Fri) |

---

## Time Modifier Reference (for `dispatch.earliest_time` / `dispatch.latest_time`)

| Modifier | Meaning |
|---|---|
| `-5m` | 5 minutes ago |
| `-1h` | 1 hour ago |
| `-1d` | 1 day ago |
| `-7d` | 7 days ago |
| `-5m@m` | 5 minutes ago, snapped to minute boundary |
| `-1h@h` | 1 hour ago, snapped to hour boundary |
| `-1d@d` | 1 day ago, snapped to day boundary |
| `now` | Current time |
| `@h` | Beginning of current hour |
| `@d` | Beginning of current day |

---

## Notes

- Parameters are passed as keyword arguments to `svc.saved_searches.create(name, **params)` in the Python SDK.
- Boolean values should be passed as strings `"1"` / `"0"` or `"true"` / `"false"`.
- The `$name$`, `$results.count$`, `$results.url$`, `$search$` tokens are expanded at runtime in action parameters.
- Action parameters use dot-notation (e.g. `action.email.to`) as flat keys.
