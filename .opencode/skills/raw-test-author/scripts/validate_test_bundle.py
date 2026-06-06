#!/usr/bin/env python3
"""Validate a RAW test bundle against the raw-test-author schema.

Two-stage validation:
  1. JSON Schema (Draft 7) — structural correctness. Failures => exit 1.
  2. Cross-reference checks — raw_path/fs_path existence, raw_id <-> RAW.metadata.id
     alignment (skipped in draft mode), unique test names, step_id/action_ids
     resolution against the RAW. Failures default to WARNINGS (exit 0); use
     --strict to promote warnings to errors (exit 1).

Exit codes:
  0  All checks passed (warnings allowed without --strict).
  1  Schema violation or strict-mode warning.
  2  Tool-level error (file missing, YAML parse error, jsonschema missing).

Usage:
  python validate_test_bundle.py <bundle.tests.yml>
  python validate_test_bundle.py <bundle.tests.yml> --strict
  python validate_test_bundle.py <bundle.tests.yml> --quiet --format json

This script is invoked by the raw-test-author skill in validate-only mode. It is
self-contained: the JSON Schema lives next to it under
.opencode/skills/raw-test-author/assets/test-bundle.schema.json.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except ImportError:
    print("ERROR: pyyaml is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

try:
    from jsonschema import Draft7Validator
except ImportError:
    print("ERROR: jsonschema is required. Install with: pip install jsonschema", file=sys.stderr)
    sys.exit(2)


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
SCHEMA_PATH = SKILL_DIR / "assets" / "test-bundle.schema.json"

DRAFT_RAW_ID = "RAW000000"


def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def load_schema() -> dict:
    if not SCHEMA_PATH.exists():
        print(f"ERROR: schema not found at {SCHEMA_PATH}", file=sys.stderr)
        sys.exit(2)
    with SCHEMA_PATH.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def run_schema_validation(bundle: Any, schema: dict) -> list[str]:
    """Return list of structural error messages. Empty list => valid."""
    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(bundle), key=lambda e: list(e.absolute_path))
    return [
        f"schema: {'/'.join(str(p) for p in err.absolute_path) or '<root>'}: {err.message}"
        for err in errors
    ]


def collect_raw_step_ids(raw: Any) -> set[str]:
    steps = raw.get("workflow", {}).get("steps", []) if isinstance(raw, dict) else []
    return {str(s.get("step_id")) for s in steps if isinstance(s, dict) and s.get("step_id") is not None}


def collect_raw_action_ids(raw: Any) -> set[str]:
    ids: set[str] = set()
    if not isinstance(raw, dict):
        return ids
    for step in raw.get("workflow", {}).get("steps", []):
        if not isinstance(step, dict):
            continue
        for entry in step.get("action_select", []) or []:
            if isinstance(entry, dict) and entry.get("action_id") is not None:
                ids.add(str(entry["action_id"]))
    return ids


def raw_step_uses_eval_logs(step: dict) -> bool:
    """Return True when a step validation tree contains eval_logs."""
    def walk(node: Any) -> bool:
        if isinstance(node, dict):
            if "eval_logs" in node:
                return True
            return any(walk(v) for v in node.values())
        if isinstance(node, list):
            return any(walk(v) for v in node)
        return False

    return walk(step.get("validation", {}))


def cross_ref_checks(bundle: dict, bundle_path: Path) -> list[tuple[str, str]]:
    """Return list of (severity, message) tuples. severity is 'WARN' or 'ERROR'.

    ERROR is only emitted for unrecoverable issues that JSON Schema cannot catch
    (e.g. duplicate test names). Missing referenced files and unresolved
    step_id/action_ids are WARN — they're commonly hit during draft authoring
    when the RAW isn't finalized.
    """
    findings: list[tuple[str, str]] = []
    raw_id = bundle.get("raw_id", "")
    is_draft = raw_id == DRAFT_RAW_ID

    # Duplicate test names (hard error — schema cannot enforce uniqueness across array items easily)
    seen: dict[str, int] = {}
    for idx, test in enumerate(bundle.get("tests", []) or []):
        name = test.get("name") if isinstance(test, dict) else None
        if name:
            seen[name] = seen.get(name, 0) + 1
    for name, count in seen.items():
        if count > 1:
            findings.append(("ERROR", f"duplicate test name '{name}' ({count} occurrences)"))

    # Resolve raw_path and fs_path (relative to bundle file)
    bundle_dir = bundle_path.parent
    raw_rel = bundle.get("raw_path", "")
    fs_rel = bundle.get("fs_path", "")
    raw_full = (bundle_dir / raw_rel).resolve() if raw_rel else None
    fs_full = (bundle_dir / fs_rel).resolve() if fs_rel else None

    raw_doc: Any = None
    if raw_full is None or not raw_full.exists():
        findings.append(("WARN", f"raw_path does not resolve to an existing file: {raw_rel!r} (resolved: {raw_full})"))
    else:
        try:
            raw_doc = load_yaml(raw_full)
        except yaml.YAMLError as exc:
            findings.append(("WARN", f"raw_path file failed to parse as YAML: {exc}"))
            raw_doc = None

    if fs_full is None or not fs_full.exists():
        findings.append(("WARN", f"fs_path does not resolve to an existing file: {fs_rel!r} (resolved: {fs_full})"))

    # raw_id <-> RAW.metadata.id alignment (skip in draft mode)
    if raw_doc and isinstance(raw_doc, dict):
        meta = raw_doc.get("workflow", {}).get("metadata", {}) if isinstance(raw_doc.get("workflow"), dict) else {}
        raw_meta_id = str(meta.get("id", "")) if isinstance(meta, dict) else ""
        if not is_draft and raw_meta_id and raw_meta_id != raw_id:
            findings.append(("WARN", f"raw_id '{raw_id}' does not match RAW.metadata.id '{raw_meta_id}'"))

        # Resolve step_id / action_ids
        valid_step_ids = collect_raw_step_ids(raw_doc)
        valid_action_ids = collect_raw_action_ids(raw_doc)
        eval_log_steps = {
            str(s.get("step_id"))
            for s in raw_doc.get("workflow", {}).get("steps", []) or []
            if isinstance(s, dict) and s.get("step_id") is not None and raw_step_uses_eval_logs(s)
        }

        for t_idx, test in enumerate(bundle.get("tests", []) or []):
            if not isinstance(test, dict):
                continue
            tname = test.get("name", f"#{t_idx}")
            # responses[].step_id
            for r_idx, resp in enumerate(test.get("responses", []) or []):
                if not isinstance(resp, dict):
                    continue
                sid = str(resp.get("step_id", ""))
                if valid_step_ids and sid and sid not in valid_step_ids:
                    findings.append(("WARN", f"test '{tname}' responses[{r_idx}].step_id '{sid}' not found in RAW steps {sorted(valid_step_ids)}"))
            # expected.action_ids / step_path / must_visit / must_not_visit
            expected = test.get("expected", {}) or {}
            if isinstance(expected, dict):
                for field, valid_set in (
                    ("action_ids", valid_action_ids),
                    ("step_path", valid_step_ids),
                    ("must_visit", valid_step_ids),
                    ("must_not_visit", valid_step_ids),
                ):
                    if not valid_set:
                        continue
                    for v in expected.get(field, []) or []:
                        if str(v) not in valid_set:
                            kind = "step_ids" if field != "action_ids" else "action_select entry IDs"
                            findings.append(("WARN", f"test '{tname}' expected.{field}: '{v}' not found in RAW {kind}"))
                expected_path = {str(v) for v in expected.get("step_path", []) or []}
                if eval_log_steps.intersection(expected_path) and not test.get("log_entries"):
                    findings.append(("WARN", f"test '{tname}' visits eval_logs step(s) {sorted(eval_log_steps.intersection(expected_path))} but has no log_entries fixtures"))
            # approvals.overrides[].step_id
            approvals = test.get("approvals", {}) or {}
            if isinstance(approvals, dict):
                for o_idx, ov in enumerate(approvals.get("overrides", []) or []):
                    if not isinstance(ov, dict):
                        continue
                    sid = str(ov.get("step_id", ""))
                    if valid_step_ids and sid and sid not in valid_step_ids:
                        findings.append(("WARN", f"test '{tname}' approvals.overrides[{o_idx}].step_id '{sid}' not found in RAW steps"))

    if is_draft:
        findings.append(("WARN", f"draft mode: raw_id is {DRAFT_RAW_ID}; ID-alignment checks skipped"))

    return findings


def emit_text(schema_errors: list[str], findings: list[tuple[str, str]], quiet: bool) -> None:
    if schema_errors:
        for msg in schema_errors:
            print(f"ERROR: {msg}", file=sys.stderr)
    if not quiet:
        for sev, msg in findings:
            stream = sys.stderr if sev == "ERROR" else sys.stdout
            print(f"{sev}: {msg}", file=stream)


def emit_json(schema_errors: list[str], findings: list[tuple[str, str]]) -> None:
    payload = {
        "schema_errors": schema_errors,
        "warnings": [m for s, m in findings if s == "WARN"],
        "errors": [m for s, m in findings if s == "ERROR"],
    }
    print(json.dumps(payload, indent=2))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a RAW test bundle.")
    parser.add_argument("bundle", help="Path to <RAW######>.tests.yml")
    parser.add_argument("--strict", action="store_true", help="Promote cross-ref warnings to errors (exit 1).")
    parser.add_argument("--quiet", action="store_true", help="Suppress non-error output in text mode.")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args(argv)

    bundle_path = Path(args.bundle).resolve()
    if not bundle_path.exists():
        print(f"ERROR: bundle file not found: {bundle_path}", file=sys.stderr)
        return 2

    try:
        bundle = load_yaml(bundle_path)
    except yaml.YAMLError as exc:
        print(f"ERROR: bundle is not valid YAML: {exc}", file=sys.stderr)
        return 2

    if not isinstance(bundle, dict):
        print("ERROR: bundle root must be a YAML mapping.", file=sys.stderr)
        return 2

    schema = load_schema()
    schema_errors = run_schema_validation(bundle, schema)

    # Cross-ref checks always run, even if schema failed — gives the author maximum
    # information per invocation. They short-circuit gracefully on missing fields.
    findings = cross_ref_checks(bundle, bundle_path)

    if args.format == "json":
        emit_json(schema_errors, findings)
    else:
        emit_text(schema_errors, findings, args.quiet)

    if schema_errors:
        return 1

    has_cross_ref_errors = any(s == "ERROR" for s, _ in findings)
    has_warnings = any(s == "WARN" for s, _ in findings)
    if has_cross_ref_errors:
        return 1
    if args.strict and has_warnings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
