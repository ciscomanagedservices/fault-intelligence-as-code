#!/usr/bin/env python3
"""
validate_artifact.py
Unified Intelligence Artifact Validator

Validates one or more Intelligence Artifact YAML files against their JSON Schema
definitions and applies cross-reference integrity checks.

Supported artifact types (all IDs are 6-digit zero-padded strings):
    - Fault Signatures                    (id prefix: FS,    e.g. FS000004)
  - Diagnostic Data Collection Lists    (id prefix: CL,    e.g. CL000001)
  - Diagnostic Data Parsers             (id prefix: PARSE, e.g. PARSE000001)
  - Health Check Rules                  (id prefix: HCR,   e.g. HCR000001)
    - Remediation Guides                  (id prefix: RG,    e.g. RG000004)
    - Repair Action Workflows             (id prefix: RAW,   e.g. RAW000004)

Alert Definitions (AD######) are a folder-level grouping concept, not a standalone
artifact. Each AD######-<slug>/ folder bundles an FS, RAW, and RG that share the
same 6-digit suffix.

Usage:
  python validate_artifact.py <file_or_dir> [<file_or_dir> ...]
  python validate_artifact.py *.yaml
  python validate_artifact.py ia-drafts/

Options:
  --strict    Treat warnings as errors (non-zero exit code)
  --quiet     Only print errors and the final summary
  --format    Output format: text (default) or json

Requirements:
  pip install pyyaml jsonschema
"""

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

try:
    import jsonschema
    from jsonschema import Draft7Validator
except ImportError:
    print("ERROR: jsonschema is not installed. Run: pip install jsonschema", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Schema paths — relative to this script's location
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).parent
SCHEMA_DIR = SCRIPT_DIR.parent / "assets"

SCHEMAS = {
    "fault_signature":        SCHEMA_DIR / "fault-signature.schema.json",
    "collection_list":        SCHEMA_DIR / "collection-list.schema.json",
    "parser":                 SCHEMA_DIR / "parser.schema.json",
    "health_check_rule":      SCHEMA_DIR / "health-check-rule.schema.json",
    "repair_action_workflow": SCHEMA_DIR / "repair-action-workflow.schema.json",
}

# ID prefix → artifact type map (string IDs, 6-digit zero-padded)
ID_PREFIXES = {
    "FS":    "fault_signature",
    "CL":    "collection_list",
    "PARSE": "parser",
    "HCR":   "health_check_rule",
    "RG":    "remediation_guide",
    "RAW":   "repair_action_workflow",
}

# Human-friendly labels
TYPE_LABELS = {
    "fault_signature":        "Fault Signature",
    "collection_list":        "Diagnostic Data Collection List",
    "parser":                 "Diagnostic Data Parser",
    "health_check_rule":      "Health Check Rule",
    "remediation_guide":      "Remediation Guide",
    "repair_action_workflow": "Repair Action Workflow",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_metadata_id(doc: dict):
    """Return (id, metadata_dict) regardless of nesting."""
    if "workflow" in doc:
        meta = doc["workflow"].get("metadata", {})
    else:
        meta = doc.get("metadata", {})
    # HI artifacts have id at root level
    if "id" in doc and not isinstance(doc.get("id"), dict):
        return doc.get("id"), meta if meta else doc
    return meta.get("id"), meta


def get_name(doc: dict) -> str:
    """Return the artifact name regardless of nesting."""
    if "workflow" in doc:
        return doc["workflow"].get("metadata", {}).get("name", "")
    if "metadata" in doc:
        return doc["metadata"].get("name", "")
    return doc.get("name", "")


def detect_artifact_type(doc: dict) -> str | None:
    """Detect artifact type from ID range, name suffix, or structural keys."""
    artifact_id, meta = get_metadata_id(doc)

    # 1. Try ID prefix (string IDs like FS000004, RAW000042)
    if isinstance(artifact_id, str):
        m = re.match(r"^([A-Z]+)\d{6}$", artifact_id)
        if m and m.group(1) in ID_PREFIXES:
            return ID_PREFIXES[m.group(1)]

    # 2. Try name suffix/prefix
    name = get_name(doc)
    if name:
        if name.endswith("_REPAIR"):
            return "repair_action_workflow"
        if name.endswith("_GUIDE"):
            return "remediation_guide"
        if name.startswith("PARSE_"):
            return "parser"
        if re.search(r"_HEALTH_CHECK$|_HEALTH_RULE$", name):
            return "health_check_rule"
        if re.search(r"_DIAGNOSTICS$|_COLLECTION$|_DATA$", name):
            return "collection_list"

    # 3. Try structural keys
    if "conditions" in doc and "events" in doc.get("conditions", {}):
        return "fault_signature"
    if "workflow" in doc:
        return "repair_action_workflow"
    if "diagnosis_steps" in doc or "repair_steps" in doc:
        return "remediation_guide"
    if "collections" in doc:
        return "collection_list"
    if "parser" in doc and "output" in doc:
        return "parser"
    if "requires" in doc and "actions" in doc:
        return "health_check_rule"

    return None


def load_schema(artifact_type: str) -> dict:
    path = SCHEMAS[artifact_type]
    if not path.exists():
        raise FileNotFoundError(f"Schema file not found: {path}")
    with path.open(encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Semantic checkers — Fault Intelligence
# ---------------------------------------------------------------------------

def check_fault_signature(doc: dict, errors: list, warnings: list):
    """Cross-reference checks specific to Fault Signatures."""
    conditions = doc.get("conditions", {})
    logic_expr = conditions.get("logic", "")
    events = conditions.get("events", [])

    # Collect declared event IDs
    declared_ids = set()
    for wrapper in events:
        ev = wrapper.get("event", {})
        eid = ev.get("id")
        if eid is not None:
            declared_ids.add(str(eid))

    # Check every ID referenced in logic is declared (supports E1, E2 or 1, 2 formats)
    referenced_ids = set(re.findall(r"\b(E?\d+)\b", logic_expr))
    undeclared = referenced_ids - declared_ids
    if undeclared:
        errors.append(f"Logic expression references undeclared event IDs: {sorted(undeclared)}")
    unused = declared_ids - referenced_ids
    if unused:
        warnings.append(f"Declared events not referenced in logic expression: {sorted(unused)}")

    # Validate regex patterns compile
    for wrapper in events:
        ev = wrapper.get("event", {})
        eid = ev.get("id", "?")
        evaluation = ev.get("evaluation", {})
        if evaluation.get("type") in ("regex", "exact-match"):
            pattern = evaluation.get("value", "")
            if pattern:
                try:
                    re.compile(pattern)
                except re.error as exc:
                    errors.append(f"Event {eid}: invalid regex pattern '{pattern}': {exc}")

        # Extraction parameter regex
        ext_param = ev.get("extraction_parameter", {})
        if ext_param:
            ext_pattern = ext_param.get("pattern", "")
            if ext_pattern:
                try:
                    re.compile(ext_pattern)
                except re.error as exc:
                    errors.append(f"Event {eid} extraction_parameter: invalid regex '{ext_pattern}': {exc}")

        # Clear event regex
        clear_ev = ev.get("clear_event", {})
        if clear_ev:
            clear_pattern = clear_ev.get("pattern", "")
            if clear_pattern:
                try:
                    re.compile(clear_pattern)
                except re.error as exc:
                    errors.append(f"Event {eid} clear_event: invalid regex '{clear_pattern}': {exc}")

        # Syslog events must have message_type
        if ev.get("type") == "syslog" and not ev.get("message_type"):
            errors.append(f"Event {eid}: type='syslog' requires 'message_type' field")


def check_remediation_guide(doc: dict, errors: list, warnings: list):
    """Cross-reference checks specific to Remediation Guides."""
    fs_ref = doc.get("fault_signature_ref", "")
    if fs_ref and not re.match(r"^[A-Z][A-Z0-9_]+$", fs_ref):
        errors.append(
            f"fault_signature_ref '{fs_ref}' must be UPPER_SNAKE_CASE without suffix"
        )

    # Check step_id uniqueness in diagnosis_steps
    diag_ids = [s.get("step_id") for s in doc.get("diagnosis_steps", [])]
    diag_seen = set()
    for sid in diag_ids:
        if sid in diag_seen:
            errors.append(f"Duplicate diagnosis step_id: {sid}")
        diag_seen.add(sid)

    # Check step_id uniqueness in repair_steps
    repair_ids = [s.get("step_id") for s in doc.get("repair_steps", [])]
    repair_seen = set()
    for sid in repair_ids:
        if sid in repair_seen:
            errors.append(f"Duplicate repair step_id: {sid}")
        repair_seen.add(sid)

    if diag_seen & repair_seen:
        warnings.append(
            f"Step IDs overlap between diagnosis and repair: {sorted(diag_seen & repair_seen)}"
        )


def check_repair_action_workflow(doc: dict, errors: list, warnings: list):
    """Cross-reference checks specific to Repair Action Workflows."""
    workflow = doc.get("workflow", {})
    steps = workflow.get("steps", [])
    reusable_action_groups = workflow.get("action_groups", [])

    reusable_names = set()
    for group in reusable_action_groups:
        name = group.get("name")
        if name:
            if name in reusable_names:
                errors.append(f"Duplicate reusable action_group name: {name}")
            reusable_names.add(name)

    # Collect all step IDs
    step_ids = [s.get("step_id") for s in steps]
    unique_ids = set()
    for sid in step_ids:
        if sid is None:
            continue
        if sid in unique_ids:
            errors.append(f"Duplicate step_id: {sid}")
        unique_ids.add(sid)

    def collect_goto_targets(actions, targets):
        for action in actions or []:
            if not isinstance(action, dict):
                continue
            goto = action.get("goto")
            if isinstance(goto, dict):
                target = goto.get("step_id")
                if target:
                    targets.add(str(target))

    goto_targets = set()

    for group in reusable_action_groups:
        actions = group.get("actions", []) if isinstance(group, dict) else []
        collect_goto_targets(actions, goto_targets)

    for step in steps:
        for entry in step.get("action_select", []):
            if not isinstance(entry, dict):
                continue
            for ag in entry.get("action_groups", []):
                if isinstance(ag, str):
                    if ag not in reusable_names:
                        errors.append(
                            f"Step {step.get('step_id', '?')}: references unknown action_group '{ag}'"
                        )
                    continue
                if isinstance(ag, dict):
                    collect_goto_targets(ag.get("actions", []), goto_targets)

    # Validate goto targets exist
    for target in goto_targets:
        if target not in unique_ids:
            errors.append(f"goto target '{target}' does not match any step_id")

    # Check branch exits
    exit_actions = {"resolve", "escalate", "fail", "goto", "revalidate"}
    for step in steps:
        sid = step.get("step_id", "?")
        for entry in step.get("action_select", []):
            if not isinstance(entry, dict):
                continue
            action_id = entry.get("action_id", "?")
            has_exit = False
            for ag in entry.get("action_groups", []):
                if isinstance(ag, str):
                    reusable = next(
                        (x for x in reusable_action_groups if isinstance(x, dict) and x.get("name") == ag),
                        None,
                    )
                    actions = reusable.get("actions", []) if reusable else []
                elif isinstance(ag, dict):
                    actions = ag.get("actions", [])
                else:
                    actions = []
                if any(
                    isinstance(a, dict) and any(k in exit_actions for k in a.keys())
                    for a in actions
                ):
                    has_exit = True
            if not has_exit:
                warnings.append(
                    f"Step {sid} action_id {action_id}: no terminal/control action found"
                )

    # Check inputs Jinja2 syntax
    for inp in workflow.get("inputs", []):
        source = inp.get("source", "")
        if source and "{{" not in source:
            warnings.append(
                f"Input '{inp.get('name')}': source '{source}' may need Jinja2 syntax"
            )


# ---------------------------------------------------------------------------
# Semantic checkers — Health Intelligence
# ---------------------------------------------------------------------------

def check_collection_list(doc: dict, errors: list, warnings: list):
    """Cross-reference checks specific to Collection Lists."""
    collections = doc.get("collections", [])
    seen_ids = set()
    for item in collections:
        item_id = item.get("id", "")
        if item_id in seen_ids:
            errors.append(f"Duplicate collection item id: '{item_id}'")
        seen_ids.add(item_id)

        col_type = item.get("type", "")
        if col_type == "cli" and "cli" not in item:
            errors.append(f"Collection item '{item_id}': type 'cli' requires 'cli' block")
        if col_type in ("gnmi_get", "gnmi_subscribe") and "gnmi" not in item:
            errors.append(f"Collection item '{item_id}': type '{col_type}' requires 'gnmi' block")
        if col_type == "netconf" and "netconf" not in item:
            errors.append(f"Collection item '{item_id}': type 'netconf' requires 'netconf' block")

        parser_ref = (item.get("cli") or {}).get("parser_ref")
        if parser_ref and not re.match(r"^PARSE_[A-Z][A-Z0-9_]+$", parser_ref):
            warnings.append(
                f"Collection item '{item_id}': parser_ref '{parser_ref}' doesn't follow PARSE_ convention"
            )


def check_parser(doc: dict, errors: list, warnings: list):
    """Cross-reference checks specific to Parsers."""
    output_schema = {f["name"] for f in doc.get("output", {}).get("schema", [])}
    required_fields = doc.get("validation", {}).get("required_fields", [])

    for field in required_fields:
        if field not in output_schema:
            errors.append(
                f"validation.required_fields references '{field}' not in output.schema"
            )

    parser_type = doc.get("parser", {}).get("type")
    if parser_type == "regex":
        patterns = doc.get("parser", {}).get("regex", {}).get("patterns", [])
        for pat in patterns:
            pattern_str = pat.get("pattern", "")
            if pattern_str:
                try:
                    re.compile(pattern_str)
                except re.error as exc:
                    errors.append(f"Parser regex '{pat.get('name', '?')}': invalid pattern: {exc}")


def check_health_check_rule(doc: dict, errors: list, warnings: list):
    """Cross-reference checks specific to Health Check Rules."""
    conditions = doc.get("conditions", [])
    actions = doc.get("actions", [])

    condition_ids = set()
    for cond in conditions:
        cid = cond.get("id", "")
        if cid in condition_ids:
            errors.append(f"Duplicate condition id: '{cid}'")
        condition_ids.add(cid)

        # Verify eval type matches sub-block
        eval_block = cond.get("eval", {})
        eval_type = eval_block.get("type", "")
        eval_sub_keys = set(eval_block.keys()) - {"type"}
        if eval_type and eval_type not in eval_sub_keys:
            errors.append(
                f"Condition '{cid}': eval.type is '{eval_type}' but no '{eval_type}' sub-block found"
            )

        # Verify result block
        result = cond.get("result", {})
        if "healthy" not in result:
            errors.append(f"Condition '{cid}' missing result.healthy")
        if "unhealthy" not in result:
            errors.append(f"Condition '{cid}' missing result.unhealthy")

    # Verify action triggers
    for i, action in enumerate(actions):
        trigger = action.get("trigger", "")
        if trigger not in condition_ids:
            errors.append(
                f"Action [{i}] trigger '{trigger}' doesn't match any condition id"
            )
        action_type = action.get("type", "")
        action_sub_keys = set(action.keys()) - {"trigger", "type", "priority"}
        if action_type and action_type not in action_sub_keys:
            errors.append(
                f"Action [{i}]: type '{action_type}' but no '{action_type}' sub-block found"
            )

    # Check requires block naming
    requires = doc.get("requires", {})
    for cl_name in requires.get("collection_lists", []):
        if not re.match(r"^[A-Z][A-Z0-9_]+$", cl_name):
            warnings.append(f"requires.collection_lists '{cl_name}': not UPPERCASE_SNAKE_CASE")
    for parser_name in requires.get("parsers", []):
        if not re.match(r"^PARSE_[A-Z][A-Z0-9_]+$", parser_name):
            warnings.append(f"requires.parsers '{parser_name}': not PARSE_ convention")


# ---------------------------------------------------------------------------
# Semantic check dispatcher
# ---------------------------------------------------------------------------

SEMANTIC_CHECKS = {
    "fault_signature":        check_fault_signature,
    "remediation_guide":      check_remediation_guide,
    "repair_action_workflow": check_repair_action_workflow,
    "collection_list":        check_collection_list,
    "parser":                 check_parser,
    "health_check_rule":      check_health_check_rule,
}


# ---------------------------------------------------------------------------
# Core validator
# ---------------------------------------------------------------------------

class ValidationResult:
    def __init__(self, path: Path):
        self.path = path
        self.artifact_type: str | None = None
        self.schema_errors: list[str] = []
        self.semantic_errors: list[str] = []
        self.warnings: list[str] = []
        self.load_error: str | None = None

    @property
    def passed(self) -> bool:
        return self.load_error is None and not self.schema_errors and not self.semantic_errors

    @property
    def error_count(self) -> int:
        return len(self.schema_errors) + len(self.semantic_errors)


def validate_file(path: Path) -> ValidationResult:
    result = ValidationResult(path)

    # 1. Load YAML
    try:
        with path.open(encoding="utf-8") as f:
            doc = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        result.load_error = f"YAML parse error: {exc}"
        return result
    except OSError as exc:
        result.load_error = f"Cannot read file: {exc}"
        return result

    if not isinstance(doc, dict):
        result.load_error = "File does not contain a YAML mapping at root level"
        return result

    # 2. Detect artifact type
    artifact_type = detect_artifact_type(doc)
    if artifact_type is None:
        result.load_error = (
            "Cannot determine artifact type. Ensure metadata.id uses a known "
            "6-digit prefix (FS######, CL######, PARSE######, HCR######, "
            "RG######, RAW######) or name follows a known pattern."
        )
        return result
    result.artifact_type = artifact_type

    # 3. JSON Schema validation
    try:
        schema = load_schema(artifact_type)
    except FileNotFoundError as exc:
        result.load_error = str(exc)
        return result

    validator = Draft7Validator(schema)
    for err in sorted(validator.iter_errors(doc), key=lambda e: list(e.path)):
        path_str = " > ".join(str(p) for p in err.path) if err.path else "(root)"
        result.schema_errors.append(f"[{path_str}] {err.message}")

    # 4. Semantic checks (only if schema validation didn't produce errors)
    if not result.schema_errors:
        checker = SEMANTIC_CHECKS.get(artifact_type)
        if checker:
            checker(doc, result.semantic_errors, result.warnings)

    return result


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------

def format_text(results: list[ValidationResult], quiet: bool) -> str:
    lines = []
    for r in results:
        label = TYPE_LABELS.get(r.artifact_type, "Unknown") if r.artifact_type else "Unknown"
        status = "PASS" if r.passed else "FAIL"
        lines.append(f"\n{'='*60}")
        lines.append(f"FILE:   {r.path}")
        lines.append(f"TYPE:   {label}")
        lines.append(f"STATUS: {status}")

        if r.load_error:
            lines.append(f"  LOAD ERROR: {r.load_error}")
            continue

        if not quiet or not r.passed:
            for e in r.schema_errors:
                lines.append(f"  SCHEMA ERROR:   {e}")
            for e in r.semantic_errors:
                lines.append(f"  SEMANTIC ERROR: {e}")
            for w in r.warnings:
                lines.append(f"  WARNING:        {w}")

    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed
    warnings = sum(len(r.warnings) for r in results)
    lines.append(f"\n{'='*60}")
    lines.append(f"SUMMARY: {passed}/{total} passed, {failed} failed")
    if warnings:
        lines.append(f"         {warnings} warning(s)")
    return "\n".join(lines)


def format_json(results: list[ValidationResult]) -> str:
    out = []
    for r in results:
        out.append({
            "file": str(r.path),
            "type": TYPE_LABELS.get(r.artifact_type) if r.artifact_type else None,
            "passed": r.passed,
            "load_error": r.load_error,
            "schema_errors": r.schema_errors,
            "semantic_errors": r.semantic_errors,
            "warnings": r.warnings,
        })
    return json.dumps(out, indent=2)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def collect_yaml_files(paths: list[Path]) -> list[Path]:
    files = []
    for p in paths:
        if p.is_dir():
            files.extend(sorted(p.rglob("*.yaml")))
            files.extend(sorted(p.rglob("*.yml")))
        elif p.is_file():
            files.append(p)
        else:
            print(f"WARNING: path not found: {p}", file=sys.stderr)
    return files


def main():
    parser = argparse.ArgumentParser(
        description="Validate Intelligence Artifact YAML files.",
    )
    parser.add_argument(
        "paths",
        nargs="+",
        type=Path,
        help="One or more YAML files or directories to validate",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors (non-zero exit code)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only print errors and the final summary",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    args = parser.parse_args()

    yaml_files = collect_yaml_files(args.paths)
    if not yaml_files:
        print("No YAML files found.", file=sys.stderr)
        sys.exit(1)

    results = [validate_file(f) for f in yaml_files]

    if args.format == "json":
        print(format_json(results))
    else:
        print(format_text(results, quiet=args.quiet))

    any_failed = any(not r.passed for r in results)
    any_warnings = any(r.warnings for r in results)

    if any_failed:
        sys.exit(1)
    elif args.strict and any_warnings:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
