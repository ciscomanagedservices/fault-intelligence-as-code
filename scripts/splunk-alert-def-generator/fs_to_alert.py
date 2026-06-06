"""
fs_to_alert.py — Convert a Fault Intelligence Alert Definition (AD) to a Splunk alert_config.yml.

Given an Alert Definition ID (e.g. AD000002), this script locates the
associated Fault Signature YAML under intelligence-artifacts/ and generates a
Splunk alert configuration consumable by splunk_alerts.py --create.

Only 'syslog' event types are supported. Events are translated into SPL queries
against a configurable index (default: 'syslog'). Every generated SPL search
includes an `eval alert_def_id="<AD-ID>"` so downstream consumers can correlate
fired alerts back to their source Alert Definition.

Usage:
  python fs_to_alert.py AD000002
  python fs_to_alert.py AD000002 --output my_alert.yml
  python fs_to_alert.py AD000002 --index syslog --cron "*/5 * * * *"
  python fs_to_alert.py AD000002 --sourcetype cisco:ios
  python fs_to_alert.py AD000002 --repo-root /path/to/fault-intelligence-as-code
"""

import argparse
import os
import pathlib
import re
import sys
import yaml


# Severity mapping: FS severity → Splunk alert.severity numeric value
SEVERITY_MAP = {
    "CRITICAL": "5",
    "MAJOR": "4",
    "WARNING": "3",
    "MINOR": "2",
    "UNKNOWN": "1",
}


def load_fault_signature(path: pathlib.Path) -> dict:
    """Load and validate a fault signature YAML file."""
    with open(path, encoding="utf-8") as f:
        fs = yaml.safe_load(f)

    if not fs:
        sys.exit(f"ERROR: '{path}' is empty or not valid YAML.")
    if "conditions" not in fs or "events" not in fs["conditions"]:
        sys.exit(f"ERROR: '{path}' missing required 'conditions.events' section.")
    if "metadata" not in fs:
        sys.exit(f"ERROR: '{path}' missing required 'metadata' section.")

    return fs


def extract_syslog_events(fs: dict) -> list:
    """Extract syslog-type events from the fault signature conditions."""
    events = []
    for item in fs["conditions"]["events"]:
        event = item.get("event", item)  # handle both wrapped and unwrapped
        if event.get("type") == "syslog":
            events.append(event)
        else:
            print(f"  WARN: Skipping non-syslog event '{event.get('id', '?')}' "
                  f"(type='{event.get('type', 'unknown')}')")
    return events


def parse_logic(logic_str: str) -> tuple:
    """Parse the conditions.logic expression into operator and event IDs.

    Returns (operator, [event_ids]).
    operator is 'SINGLE', 'OR', or 'AND'.
    """
    logic = logic_str.strip()

    # Strip outer parentheses
    if logic.startswith("(") and logic.endswith(")"):
        logic = logic[1:-1].strip()

    # Find all event IDs
    event_ids = re.findall(r"E\d+", logic)

    if len(event_ids) == 1:
        return ("SINGLE", event_ids)

    if " OR " in logic.upper():
        return ("OR", event_ids)
    elif " AND " in logic.upper():
        return ("AND", event_ids)
    else:
        # Default to OR for multiple events without explicit operator
        return ("OR", event_ids)


def match_period_to_seconds(match_period) -> int:
    """Convert match_period value to integer seconds.

    Accepts: int, "0", "0s", "300s", "5m", "1h", etc.
    """
    if isinstance(match_period, int):
        return match_period
    if isinstance(match_period, str):
        match_period = match_period.strip()
        if match_period.endswith("s"):
            return int(match_period[:-1])
        elif match_period.endswith("m"):
            return int(match_period[:-1]) * 60
        elif match_period.endswith("h"):
            return int(match_period[:-1]) * 3600
        else:
            return int(match_period)
    return 0


def seconds_to_splunk_time(seconds: int) -> str:
    """Convert seconds to Splunk relative time string (e.g., -5m, -1h)."""
    if seconds <= 0:
        return "-5m"  # minimum 5 minutes for scheduled searches
    if seconds >= 3600 and seconds % 3600 == 0:
        return f"-{seconds // 3600}h"
    if seconds >= 60 and seconds % 60 == 0:
        return f"-{seconds // 60}m"
    return f"-{seconds}s"


def escape_regex_for_splunk(pattern: str) -> str:
    """Double-escape backslashes for Splunk's `| regex "..."` eval-string parsing."""
    return pattern.replace("\\", "\\\\")


def extract_named_parameters(evaluation: dict) -> list:
    """Return ordered list of (group_num, name) from extract_to_variable params."""
    out = []
    for p in evaluation.get("parameters") or []:
        if p.get("type") != "extract_to_variable":
            continue
        name = p.get("name")
        src = (p.get("source") or "").strip()
        m = re.match(r"match\.group\(\s*(\d+)\s*\)\s*$", src)
        if not name or not m:
            continue
        out.append((int(m.group(1)), name))
    out.sort(key=lambda t: t[0])
    return out


def convert_regex_to_named_groups(pattern: str, named_params: list) -> str:
    """Rewrite unnamed capture groups as (?<name>...) for Splunk rex."""
    name_by_num = {n: nm for n, nm in named_params}
    result = []
    group_idx = 0
    i = 0
    n = len(pattern)
    while i < n:
        c = pattern[i]
        if c == "\\" and i + 1 < n:
            result.append(pattern[i:i + 2])
            i += 2
            continue
        if c == "(":
            if i + 1 < n and pattern[i + 1] == "?":
                result.append(c)
                i += 1
                continue
            group_idx += 1
            nm = name_by_num.get(group_idx)
            if nm:
                result.append(f"(?<{nm}>")
            else:
                result.append(c)
            i += 1
            continue
        result.append(c)
        i += 1
    return "".join(result)


def build_event_spl_block(event: dict) -> dict:
    """Compile per-event SPL fragments: message_type, regex_raw, regex_named, var_names."""
    evaluation = event.get("evaluation") or {}
    pattern = ""
    named_params = []
    if evaluation.get("type") == "regex" and evaluation.get("value"):
        pattern = evaluation["value"]
        named_params = extract_named_parameters(evaluation)

    return {
        "message_type": event.get("message_type", ""),
        "regex_raw": pattern,
        "regex_named": convert_regex_to_named_groups(pattern, named_params) if pattern else "",
        "var_names": [nm for _, nm in named_params],
    }


def build_search_spl(events: list, logic_op: str, logic_event_ids: list,
                     index: str, sourcetype: str, alert_def_id: str) -> str:
    """Build the multi-line SPL search for the Splunk alert.

    Format:
        index=<idx> sourcetype=<st> "MNEMONIC"
        | regex _raw="<pcre, backslash-doubled>"
        | rex field=_raw "<pcre with (?<name>...) groups>"
        | eval alert_def_id="<AD-ID>"
        | table _time host alert_def_id <vars...> _raw
    """
    event_map = {e["id"]: e for e in events}
    active_events = [event_map[eid] for eid in logic_event_ids if eid in event_map]
    if not active_events:
        active_events = events

    blocks = [build_event_spl_block(e) for e in active_events]

    # First line: index + sourcetype + quoted mnemonic(s)
    first = f"index={index}"
    if sourcetype:
        first += f" sourcetype={sourcetype}"
    quoted_types = [f'"{b["message_type"]}"' for b in blocks if b["message_type"]]
    if len(quoted_types) == 1:
        first += f" {quoted_types[0]}"
    elif len(quoted_types) > 1:
        first += " (" + " OR ".join(quoted_types) + ")"

    lines = [first]

    # | regex lines — doubled backslashes
    for b in blocks:
        if b["regex_raw"]:
            lines.append(f'| regex _raw="{escape_regex_for_splunk(b["regex_raw"])}"')

    # | rex lines — single backslashes, named groups
    for b in blocks:
        if b["regex_named"] and b["var_names"]:
            lines.append(f'| rex field=_raw "{b["regex_named"]}"')

    if logic_op == "AND" and len(blocks) > 1:
        lines.append(
            '| `comment("FS logic is AND - cross-row correlation must be hand-tuned")`'
        )

    # | eval alert_def_id
    lines.append(f'| eval alert_def_id="{alert_def_id}"')

    # | table
    table_cols = ["_time", "device_name", "device_ip", "alert_def_id"]
    seen = set(table_cols)
    for b in blocks:
        for nm in b["var_names"]:
            if nm not in seen:
                table_cols.append(nm)
                seen.add(nm)
    table_cols.append("_raw")
    lines.append("| table " + " ".join(table_cols))

    return "\n".join(lines)


def compute_earliest_time(events: list) -> str:
    """Determine dispatch.earliest_time from the max match_period across events."""
    max_period = 0
    for event in events:
        period = match_period_to_seconds(event.get("match_period", 0))
        if period > max_period:
            max_period = period

    # Minimum 5 minutes for scheduled alert searches
    if max_period < 300:
        max_period = 300

    return seconds_to_splunk_time(max_period)


# Default webhook URL for a relay running on the local host.
DEFAULT_WEBHOOK_URL = "http://localhost:8080/fault-alert"


def build_alert_config(fs: dict, index: str, cron: str, sourcetype: str,
                       alert_def_id: str, webhook_url: str = "") -> dict:
    """Build the full alert_config dict from a fault signature."""
    metadata = fs["metadata"]
    conditions = fs["conditions"]

    # Extract syslog events
    syslog_events = extract_syslog_events(fs)
    if not syslog_events:
        sys.exit("ERROR: No syslog events found in fault signature.")

    # Parse logic
    logic_str = conditions.get("logic", "E1")
    logic_op, logic_event_ids = parse_logic(logic_str)

    # Build SPL search
    search_spl = build_search_spl(syslog_events, logic_op, logic_event_ids,
                                  index, sourcetype, alert_def_id)

    # Map severity
    fs_severity = metadata.get("severity", "WARNING")
    alert_severity = SEVERITY_MAP.get(fs_severity.upper(), "3")

    # Compute time range
    earliest_time = compute_earliest_time(syslog_events)

    # Build alert name: prefix with AD ID so it's unique and traceable.
    fs_name = metadata.get("name", "unnamed_fault_signature")
    alert_name = f"{alert_def_id}_{fs_name}".lower()

    # Build description
    description = metadata.get("description", "").strip()
    if not description:
        description = f"Alert generated from fault signature: {metadata.get('name', 'unknown')}"

    # Add provenance info to description
    fs_id = metadata.get("id", "")
    provenance = f"[Alert Definition: {alert_def_id}"
    if fs_id:
        provenance += f"; Fault Signature: {fs_id}"
    provenance += "]"
    description += f"\n{provenance}"

    config = {
        # Identity
        "name": alert_name,
        "description": description,
        # Search
        "search": search_spl,
        # Scheduling
        "is_scheduled": "1",
        "cron_schedule": cron,
        "realtime_schedule": "1",
        "schedule_priority": "default",
        "schedule_window": "0",
        "run_on_startup": "0",
        "max_concurrent": "1",
        # Trigger conditions — fire when number of events > 0
        "alert_type": "number of events",
        "alert_comparator": "greater than",
        "alert_threshold": "0",
        # Severity & tracking
        "alert.severity": alert_severity,
        "alert.track": "1",
        "alert.digest_mode": "0",
        "alert.expires": "7d",
        # Suppression — per-host, 1 hour (prevents alert storms)
        "alert.suppress": "1",
        "alert.suppress.period": "1h",
        "alert.suppress.fields": "host",
        "alert.suppress.group_name": "",
        # Dispatch / time range
        "dispatch.earliest_time": earliest_time,
        "dispatch.latest_time": "now",
        "dispatch.ttl": "2p",
        "dispatch.max_count": "500000",
        "dispatch.max_time": "0",
        "dispatch.lookups": "1",
        "dispatch.spawn_process": "1",
        "dispatch.auto_cancel": "0",
        "dispatch.auto_pause": "0",
        # General
        "disabled": "0",
        # Actions — webhook enabled by default with relay URL
        "actions": "webhook" if webhook_url else "",
        "action.webhook": "1" if webhook_url else "0",
        "action.webhook.param.url": webhook_url if webhook_url else "",
    }

    return config


def write_alert_config(config: dict, output_path: pathlib.Path):
    """Write alert config to YAML with informative header comment."""
    header = (
        "# alert_config.yml\n"
        "# Auto-generated by fs_to_alert.py from Fault Intelligence Fault Signature.\n"
        "# Compatible with splunk_alerts.py --create --config <this_file>\n"
        "#\n"
        f"# Alert: {config['name']}\n"
        f"# Severity: {config['alert.severity']} "
        f"(5=critical, 4=major, 3=warning, 2=minor, 1=unknown)\n"
        f"# Schedule: {config['cron_schedule']}\n"
        f"# Time range: {config['dispatch.earliest_time']} to "
        f"{config['dispatch.latest_time']}\n"
        "#\n"
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(header)
        yaml.dump(config, f, default_flow_style=False, sort_keys=False,
                  allow_unicode=True)

    print(f"  Written to: {output_path}")


# Default repo root: scripts/splunk-alert-def-generator/fs_to_alert.py → up 3
DEFAULT_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
ARTIFACTS_SUBDIR = "intelligence-artifacts"


def resolve_fs_path(alert_def_id: str, repo_root: pathlib.Path) -> pathlib.Path:
    """Find the Fault Signature YAML for an Alert Definition ID.

    Looks for `intelligence-artifacts/<alert_def_id>-*/FS*.yml`. If multiple
    FS files are found, prefers one whose filename starts with the matching
    FS ID (numeric suffix of the AD ID).
    """
    artifacts_dir = repo_root / ARTIFACTS_SUBDIR
    if not artifacts_dir.is_dir():
        sys.exit(f"ERROR: intelligence-artifacts directory not found: {artifacts_dir}")

    # Match directories like AD000002-* (case-insensitive on Windows is fine)
    candidates = sorted(artifacts_dir.glob(f"{alert_def_id}-*"))
    if not candidates:
        sys.exit(
            f"ERROR: No directory found for Alert Definition '{alert_def_id}' "
            f"under {artifacts_dir}"
        )
    if len(candidates) > 1:
        print(f"  WARN: Multiple directories match '{alert_def_id}-*'; using {candidates[0].name}")

    ad_dir = candidates[0]
    fs_files = sorted(ad_dir.glob("FS*.yml"))
    if not fs_files:
        sys.exit(f"ERROR: No FS*.yml file found in {ad_dir}")

    # Prefer FS file whose numeric suffix matches the AD numeric suffix
    ad_num = "".join(c for c in alert_def_id if c.isdigit())
    if ad_num:
        preferred = [f for f in fs_files if f.name.startswith(f"FS{ad_num}")]
        if preferred:
            return preferred[0]

    if len(fs_files) > 1:
        print(f"  WARN: Multiple FS files in {ad_dir.name}; using {fs_files[0].name}")
    return fs_files[0]


def main():
    parser = argparse.ArgumentParser(
        description="Convert a Fault Intelligence Alert Definition (AD ID) to a Splunk alert_config.yml"
    )
    parser.add_argument(
        "alert_def_id",
        help="Alert Definition ID (e.g. AD000002). The associated Fault "
             "Signature is resolved from intelligence-artifacts/<AD-ID>-*/FS*.yml.",
    )
    parser.add_argument(
        "--output", "-o",
        type=pathlib.Path,
        default=pathlib.Path("alert_config.yml"),
        help="Output path for the alert config (default: alert_config.yml)",
    )
    parser.add_argument(
        "--index",
        default="syslog",
        help="Splunk index name to query (default: syslog)",
    )
    parser.add_argument(
        "--cron",
        default="*/5 * * * *",
        help="Cron schedule for the alert (default: '*/5 * * * *')",
    )
    parser.add_argument(
        "--sourcetype",
        default="cisco:ios",
        help="Splunk sourcetype filter (default: cisco:ios). "
             "Pass empty string to omit.",
    )
    parser.add_argument(
        "--webhook-url",
        default=os.environ.get("ALERT_WEBHOOK_URL", DEFAULT_WEBHOOK_URL),
        help=f"Webhook URL for alert action (default: {DEFAULT_WEBHOOK_URL} "
             f"or $ALERT_WEBHOOK_URL). Pass empty string to disable.",
    )
    parser.add_argument(
        "--repo-root",
        type=pathlib.Path,
        default=DEFAULT_REPO_ROOT,
        help=f"Repository root containing intelligence-artifacts/ "
             f"(default: {DEFAULT_REPO_ROOT})",
    )
    args = parser.parse_args()

    alert_def_id = args.alert_def_id.strip().upper()
    if not alert_def_id.startswith("AD"):
        sys.exit(f"ERROR: Alert Definition ID must start with 'AD' (got '{args.alert_def_id}')")

    print(f"Resolving Fault Signature for Alert Definition: {alert_def_id}")
    fs_path = resolve_fs_path(alert_def_id, args.repo_root)
    print(f"  Fault signature file: {fs_path}")

    fs = load_fault_signature(fs_path)

    metadata = fs["metadata"]
    logic = fs["conditions"].get("logic", "E1")
    print(f"  Name: {metadata.get('name', 'unknown')}")
    print(f"  FS ID: {metadata.get('id', 'unknown')}")
    print(f"  Severity: {metadata.get('severity', 'unknown')}")
    print(f"  Logic: {logic}")

    # Sanity check: warn if FS metadata's alert_def_id disagrees
    fs_ad_id = metadata.get("alert_def_id")
    if fs_ad_id and fs_ad_id.upper() != alert_def_id:
        print(f"  WARN: FS metadata.alert_def_id='{fs_ad_id}' does not match requested '{alert_def_id}'")

    # Count syslog vs non-syslog events
    all_events = fs["conditions"]["events"]
    syslog_count = sum(
        1 for item in all_events
        if (item.get("event", item)).get("type") == "syslog"
    )
    total_count = len(all_events)
    print(f"  Events: {syslog_count} syslog / {total_count} total")

    if syslog_count == 0:
        sys.exit("ERROR: No syslog events found — nothing to convert.")

    print(f"\nGenerating alert config (index={args.index}, sourcetype='{args.sourcetype}', cron='{args.cron}')...")
    if args.webhook_url:
        print(f"  Webhook: {args.webhook_url}")
    config = build_alert_config(fs, args.index, args.cron, args.sourcetype,
                                alert_def_id, webhook_url=args.webhook_url)

    print("\n  Generated SPL:")
    for ln in config["search"].splitlines():
        print(f"    {ln}")
    print()

    write_alert_config(config, args.output)
    print("\nDone.")


if __name__ == "__main__":
    main()
