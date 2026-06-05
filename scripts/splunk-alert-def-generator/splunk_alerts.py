"""
splunk_alerts.py — List and optionally create Splunk alert definitions via the SDK.

Usage:
  python splunk_alerts.py                          # list only
  python splunk_alerts.py --create                 # create from alert_config.yaml
  python splunk_alerts.py --create --config x.yaml # create from custom YAML
  python splunk_alerts.py --delete                 # remove the alert defined in YAML
    python splunk_alerts.py --host <splunk-host> --port 8089 --username admin --password ...
    python splunk_alerts.py --host <relay-host> --port 443 --scheme https --base-path /splunk

Connection defaults (overridable via CLI flags or env vars):
  SPLUNK_HOST     (default: 127.0.0.1)
  SPLUNK_PORT     (default: 8089)
  SPLUNK_USERNAME (default: admin)
    SPLUNK_PASSWORD (required unless --password is provided)
  SPLUNK_SCHEME   (default: https)
    SPLUNK_BASE_PATH (default: empty)
"""

import argparse
import os
import pathlib
import yaml
import splunklib.client as client
from splunklib.binding import UrlEncoded
from splunklib.binding import HTTPError

DEFAULT_CONFIG = pathlib.Path(__file__).parent / "examples" / "alert_config.yml"


def build_service_kwargs(args: argparse.Namespace) -> dict:
    """Resolve Splunk connection parameters from CLI args + env vars + defaults."""
    return dict(
        host=args.host or os.environ.get("SPLUNK_HOST", "127.0.0.1"),
        port=int(args.port or os.environ.get("SPLUNK_PORT", "8089")),
        username=args.username or os.environ.get("SPLUNK_USERNAME", "admin"),
        password=args.password or os.environ.get("SPLUNK_PASSWORD", ""),
        scheme=args.scheme or os.environ.get("SPLUNK_SCHEME", "https"),
        verify=False,
    )


def normalize_base_path(base_path: str | None) -> str:
    """Normalize an optional reverse-proxy base path such as /splunk."""
    if base_path is None:
        return os.environ.get("SPLUNK_BASE_PATH", "").strip().rstrip("/")

    normalized = base_path.strip()
    if not normalized:
        return ""
    if not normalized.startswith("/"):
        normalized = f"/{normalized}"
    return normalized.rstrip("/")


def connect_service(service_kwargs: dict, base_path: str = "") -> client.Service:
    """Create and log in to the Splunk service, optionally through a proxy prefix."""
    svc = client.Service(**service_kwargs)
    if base_path:
        svc.authority = UrlEncoded(f"{svc.authority}{base_path}", skip_encode=True)
    svc.login()
    return svc


def load_alert_config(config_path: pathlib.Path) -> tuple:
    """Load alert name and params from a YAML config file."""
    with open(config_path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    name = cfg.pop("name")
    # Remove empty-string values so they don't override Splunk defaults
    params = {k: v for k, v in cfg.items() if v != ""}
    return name, params


def list_alerts(svc: client.Service) -> list:
    """Print all saved searches that have alerting enabled."""
    saved_searches = svc.saved_searches.list()
    alerts = [ss for ss in saved_searches if ss["is_scheduled"] == "1"]

    if not alerts:
        print("No scheduled alert definitions found.")
        return []

    print(f"Found {len(alerts)} alert definition(s):\n")
    print(f"  {'Name':<45} {'Severity':<10} {'Schedule':<20} {'Disabled'}")
    print(f"  {'-'*45} {'-'*10} {'-'*20} {'-'*8}")
    for a in alerts:
        content = a.content
        severity = content.get("alert.severity", "—")
        schedule = content.get("cron_schedule", "—")
        disabled = content.get("disabled", "0")
        disabled_str = "yes" if disabled == "1" else "no"
        print(f"  {a.name:<45} {severity:<10} {schedule:<20} {disabled_str}")

    return alerts


def create_alert_from_config(svc: client.Service, config_path: pathlib.Path):
    """Create an alert definition from YAML config, or report if it already exists."""
    name, params = load_alert_config(config_path)

    # Check if it already exists
    existing = [ss for ss in svc.saved_searches.list() if ss.name == name]
    if existing:
        print(f"\n[!] Alert '{name}' already exists — skipping creation.")
        return name, existing[0]

    print(f"\nCreating alert '{name}' ...")
    try:
        alert = svc.saved_searches.create(name, **params)
        print(f"  Created successfully.")
        return name, alert
    except HTTPError as e:
        print(f"  ERROR: {e}")
        return name, None


def verify_alert(svc: client.Service, name: str):
    """Re-fetch the alert and print its key properties to confirm it was saved."""
    try:
        alert = svc.saved_searches[name]
        c = alert.content
        print(f"\nVerification of '{name}':")
        print(f"  search   : {c.get('search', '')}")
        print(f"  schedule : {c.get('cron_schedule', '')}")
        print(f"  severity : {c.get('alert.severity', '')}")
        print(f"  disabled : {c.get('disabled', '')}")
        print(f"  description: {c.get('description', '')}")
    except KeyError:
        print(f"  ERROR: alert '{name}' not found after creation.")


def delete_alert(svc: client.Service, config_path: pathlib.Path):
    """Remove the alert defined in the YAML config."""
    name, _ = load_alert_config(config_path)
    try:
        svc.saved_searches[name].delete()
        print(f"Deleted alert '{name}'.")
    except KeyError:
        print(f"Alert '{name}' not found.")


def main():
    parser = argparse.ArgumentParser(description="Splunk alert manager")
    parser.add_argument("--create", action="store_true", help="Create alert from YAML config")
    parser.add_argument("--delete", action="store_true", help="Delete the alert defined in YAML config")
    parser.add_argument("--config", type=pathlib.Path, default=DEFAULT_CONFIG,
                        help=f"Path to YAML alert config (default: {DEFAULT_CONFIG.name})")
    parser.add_argument("--host", default=None, help="Splunk host (default: 127.0.0.1 or $SPLUNK_HOST)")
    parser.add_argument("--port", default=None, help="Splunk management port (default: 8089 or $SPLUNK_PORT)")
    parser.add_argument("--username", default=None, help="Splunk username (default: admin or $SPLUNK_USERNAME)")
    parser.add_argument("--password", default=None, help="Splunk password (or $SPLUNK_PASSWORD)")
    parser.add_argument("--scheme", default=None, choices=[None, "http", "https"],
                        help="Splunk scheme (default: https or $SPLUNK_SCHEME)")
    parser.add_argument("--base-path", default=None,
                help="Optional reverse-proxy path prefix (for example: /splunk or $SPLUNK_BASE_PATH)")
    args = parser.parse_args()

    service_kwargs = build_service_kwargs(args)
    if not service_kwargs["password"]:
        parser.error("Splunk password required. Set --password or SPLUNK_PASSWORD.")
    base_path = normalize_base_path(args.base_path)
    print(f"Connecting to Splunk at {service_kwargs['scheme']}://"
        f"{service_kwargs['host']}:{service_kwargs['port']}{base_path or ''} "
          f"as {service_kwargs['username']} ...")
    svc = connect_service(service_kwargs, base_path=base_path)
    print(f"Connected — Splunk build: {svc.info['build']}\n")

    if args.delete:
        delete_alert(svc, args.config)
        return

    # Always list first
    list_alerts(svc)

    if args.create:
        name, _ = create_alert_from_config(svc, args.config)
        verify_alert(svc, name)
        print("\nRe-listing after creation:")
        list_alerts(svc)


if __name__ == "__main__":
    main()
