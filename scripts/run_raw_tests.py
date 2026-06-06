#!/usr/bin/env python3
"""Headless RAW test runner.

Executes RAW test bundles using the pure-Python interpreter in
``scripts/lib/raw_interpreter.py``. No LLM, no Webex, no RADKit — purely
deterministic logic-only validation suitable for CI.

Usage
-----
    python scripts/run_raw_tests.py --bundle <path-to-bundle.yaml>
    python scripts/run_raw_tests.py --bundle <path> --test <test-name>
    python scripts/run_raw_tests.py --all
    python scripts/run_raw_tests.py --all --junit out/results.xml --summary out/summary.md

Tests with ``mode: hybrid-reasoning`` are skipped (xfail) — they require an LLM.
The ``--no-webex`` flag is accepted but is a no-op (this runner never sends
Webex notifications under any circumstances).
"""

from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from dataclasses import asdict
from pathlib import Path

import yaml

# Ensure the scripts/ directory is on sys.path so ``lib`` imports cleanly when
# the script is run from the repo root.
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.raw_interpreter import TestResult, run_test  # noqa: E402

REPO_ROOT = SCRIPTS_DIR.parent
DEFAULT_BUNDLE_GLOB = "intelligence-artifacts/*/tests/*.tests.yml"


def _with_default_approvals(bundle: dict, test: dict) -> dict:
    """Return a test copy with top-level default_approvals applied.

    Per-test approvals still win. This makes the documented bundle-level
    default_approvals field effective for the headless runner.
    """
    if test.get("approvals"):
        return test
    defaults = bundle.get("default_approvals")
    if not defaults:
        return test
    merged = dict(test)
    merged["approvals"] = defaults
    return merged


def _load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def _resolve_raw_path(bundle: dict, bundle_path: Path) -> Path:
    raw_rel = bundle.get("raw_path")
    if not raw_rel:
        raise ValueError(f"bundle {bundle_path} missing 'raw_path'")
    raw_path = (bundle_path.parent / raw_rel).resolve()
    if not raw_path.exists():
        # Try repo-root relative.
        raw_path = (REPO_ROOT / raw_rel).resolve()
    if not raw_path.exists():
        raise FileNotFoundError(f"raw_path not found: {raw_rel} (from {bundle_path})")
    return raw_path


def _run_bundle(bundle_path: Path, only: str | None) -> list[TestResult]:
    bundle = _load_yaml(bundle_path)
    raw_path = _resolve_raw_path(bundle, bundle_path)
    raw_doc = _load_yaml(raw_path)

    tests = bundle.get("tests") or []
    if only:
        tests = [t for t in tests if t.get("name") == only]
        if not tests:
            raise ValueError(f"no test named {only!r} in {bundle_path}")

    results: list[TestResult] = []
    for test in tests:
        test = _with_default_approvals(bundle, test)
        name = str(test.get("name") or "<unnamed>")
        mode = (test.get("alert_payload") or {}).get("mode", "strict")
        if mode == "hybrid-reasoning":
            r = TestResult(name=name, status="skipped")
            r.error = "hybrid-reasoning mode requires an LLM (xfail in headless runner)"
            results.append(r)
            continue
        if test.get("agent_only"):
            r = TestResult(name=name, status="skipped")
            r.error = "agent_only test — requires agent runner with Webex approval semantics"
            results.append(r)
            continue
        try:
            r = run_test(raw_doc, test)
        except Exception as exc:  # pragma: no cover — defensive
            r = TestResult(name=name, status="error")
            r.error = repr(exc)
            r.diffs = [f"runner exception: {exc!r}"]
        results.append(r)
    return results


def _print_results(bundle_path: Path, results: list[TestResult]) -> int:
    failures = 0
    rel = bundle_path.relative_to(REPO_ROOT) if bundle_path.is_relative_to(REPO_ROOT) else bundle_path
    print(f"\n=== {rel} ===")
    for r in results:
        if r.status == "skipped":
            print(f"  SKIP  {r.name}  [{r.error or ''}]")
            continue
        if r.status == "pass":
            print(f"  PASS  {r.name}")
        else:
            failures += 1
            label = "ERROR" if r.status == "error" else "FAIL"
            print(f"  {label}  {r.name}")
            for d in r.diffs:
                print(f"        - {d}")
            if r.error and r.status == "error":
                print(f"        error: {r.error}")
            print(f"        outcome={r.actual_outcome!r}  path={r.actual_step_path}")
    return failures


def _write_junit(all_results: list[tuple[Path, list[TestResult]]], out_path: Path) -> None:
    suites = ET.Element("testsuites")
    for bundle_path, results in all_results:
        suite = ET.SubElement(
            suites,
            "testsuite",
            name=bundle_path.stem,
            tests=str(len(results)),
            failures=str(sum(1 for r in results if r.status not in ("pass", "skipped"))),
            skipped=str(sum(1 for r in results if r.status == "skipped")),
        )
        for r in results:
            tc = ET.SubElement(suite, "testcase", classname=bundle_path.stem, name=r.name)
            if r.status == "skipped":
                ET.SubElement(tc, "skipped", message=r.error or "")
            elif r.status != "pass":
                fail = ET.SubElement(tc, "failure", message="; ".join(r.diffs)[:200] or (r.error or ""))
                fail.text = "\n".join(r.diffs) + f"\n\nactual_outcome={r.actual_outcome}\nactual_step_path={r.actual_step_path}"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(suites).write(out_path, encoding="utf-8", xml_declaration=True)


def _write_summary(all_results: list[tuple[Path, list[TestResult]]], out_path: Path) -> None:
    lines = ["# RAW test summary", ""]
    total = 0
    failed = 0
    skipped = 0
    for bundle_path, results in all_results:
        lines.append(f"## {bundle_path.name}")
        for r in results:
            total += 1
            if r.status == "skipped":
                skipped += 1
                lines.append(f"- ⏭️ `{r.name}` — {r.error or ''}")
            elif r.status == "pass":
                lines.append(f"- ✅ `{r.name}`")
            else:
                failed += 1
                lines.append(f"- ❌ `{r.name}`")
                for d in r.diffs:
                    lines.append(f"  - {d}")
        lines.append("")
    lines.insert(2, f"**Total:** {total}  **Failed:** {failed}  **Skipped:** {skipped}")
    lines.insert(3, "")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Headless RAW test runner")
    parser.add_argument("--bundle", type=Path, help="Path to a single test bundle YAML")
    parser.add_argument("--test", type=str, help="Run only the named test in the bundle")
    parser.add_argument("--all", action="store_true", help=f"Discover and run all bundles matching {DEFAULT_BUNDLE_GLOB}")
    parser.add_argument("--junit", type=Path, help="Write junit XML to this path")
    parser.add_argument("--summary", type=Path, help="Write Markdown summary to this path")
    parser.add_argument("--json", type=Path, help="Write full JSON results to this path")
    parser.add_argument("--no-webex", action="store_true", help="No-op (this runner never sends Webex)")
    args = parser.parse_args()

    if not args.bundle and not args.all:
        parser.error("must specify --bundle or --all")

    bundle_paths: list[Path]
    if args.all:
        bundle_paths = sorted(REPO_ROOT.glob(DEFAULT_BUNDLE_GLOB))
        if not bundle_paths:
            print(f"No bundles found matching {DEFAULT_BUNDLE_GLOB}")
            return 0
    else:
        bundle_paths = [args.bundle.resolve()]

    all_results: list[tuple[Path, list[TestResult]]] = []
    total_failures = 0
    for bp in bundle_paths:
        results = _run_bundle(bp, args.test)
        all_results.append((bp, results))
        total_failures += _print_results(bp, results)

    if args.junit:
        _write_junit(all_results, args.junit)
    if args.summary:
        _write_summary(all_results, args.summary)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            str(bp.relative_to(REPO_ROOT) if bp.is_relative_to(REPO_ROOT) else bp): [asdict(r) for r in rs]
            for bp, rs in all_results
        }
        args.json.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")

    print(f"\nTotal failures: {total_failures}")
    return 1 if total_failures else 0


if __name__ == "__main__":
    sys.exit(main())
