"""
test_alert_deployment.py — End-to-end test: generate alert config from a fault
signature using fs_to_alert.py, then deploy it with splunk_alerts.py.

Requires a running Splunk container (admin / clus26demo on localhost:8089).

Usage:
  python tests/test_alert_deployment.py
"""

import subprocess
import sys
import pathlib
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
FS_TO_ALERT = ROOT / "fs_to_alert.py"
SPLUNK_ALERTS = ROOT / "splunk_alerts.py"
SAMPLE_FS = (
    ROOT / ".opencode" / "skills" / "ia-create" / "references" / "examples"
    / "fault-signature-example.yaml"
)


def run(cmd: list, label: str):
    """Run a subprocess, print output, and exit on failure."""
    print(f"\n{'='*60}")
    print(f"STEP: {label}")
    print(f"  CMD: {' '.join(str(c) for c in cmd)}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if result.returncode != 0:
        print(f"FAILED (exit code {result.returncode})")
        sys.exit(result.returncode)
    return result


def main():
    # Validate prerequisites
    if not SAMPLE_FS.exists():
        sys.exit(f"ERROR: Sample fault signature not found: {SAMPLE_FS}")
    if not FS_TO_ALERT.exists():
        sys.exit(f"ERROR: fs_to_alert.py not found: {FS_TO_ALERT}")
    if not SPLUNK_ALERTS.exists():
        sys.exit(f"ERROR: splunk_alerts.py not found: {SPLUNK_ALERTS}")

    # Use a temp file for the generated alert config
    with tempfile.NamedTemporaryFile(
        suffix=".yml", prefix="test_alert_", delete=False, dir=str(ROOT)
    ) as tmp:
        generated_config = pathlib.Path(tmp.name)

    try:
        # Step 1: Generate alert config from fault signature
        run(
            [sys.executable, str(FS_TO_ALERT), str(SAMPLE_FS),
             "--output", str(generated_config),
             "--index", "syslog",
             "--cron", "*/5 * * * *"],
            "Generate alert_config.yml from fault signature"
        )

        # Step 2: Deploy the alert to Splunk
        run(
            [sys.executable, str(SPLUNK_ALERTS),
             "--create", "--config", str(generated_config)],
            "Deploy generated alert to Splunk"
        )

        # Step 3: Verify it appears in the alert list
        run(
            [sys.executable, str(SPLUNK_ALERTS)],
            "List alerts (verify deployment)"
        )

        # Step 4: Clean up — delete the alert from Splunk
        run(
            [sys.executable, str(SPLUNK_ALERTS),
             "--delete", "--config", str(generated_config)],
            "Delete deployed alert (cleanup)"
        )

        print(f"\n{'='*60}")
        print("ALL STEPS PASSED")
        print(f"{'='*60}")

    finally:
        # Remove the temp config file
        if generated_config.exists():
            generated_config.unlink()
            print(f"\nCleaned up temp file: {generated_config.name}")


if __name__ == "__main__":
    main()
