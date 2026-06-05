"""
Pure-Python Repair Action Workflow (RAW) interpreter for headless test runs.

This module implements a deterministic, LLM-free interpreter for the RAW YAML
schema used by the `fault-remediation` skill. It is consumed by
`scripts/run_raw_tests.py` to validate that a RAW's decision tree behaves as
expected against canned CLI responses defined in a test bundle.

It is intentionally NOT a re-implementation of the live troubleshooting agent. It does
not call RADKit, does not send Webex notifications, and does not invoke an
LLM. It only exercises the deterministic logic of the RAW:

- step traversal (goto / revalidate)
- eval_cli regex matching against canned responses
- eval_var / and / or validation combinators
- action_select condition evaluation
- exec_cli / config_cli scripted approval handling
- terminal actions (resolve / escalate / fail)

`mode: hybrid-reasoning` tests are skipped (xfail) because hybrid reasoning
requires the LLM in the loop. Those must be exercised via the agent runner.

Public API:
    run_test(raw_yaml: dict, test: dict) -> TestResult
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from typing import Any


# ────────────────────────────────────────────────────────────────────────────
# Result types
# ────────────────────────────────────────────────────────────────────────────

@dataclass
class TestResult:
    """Outcome of running a single test against a RAW."""

    name: str
    status: str  # "pass" | "fail" | "skipped" | "error"
    actual_outcome: str | None = None  # resolution | escalation | failure
    actual_step_path: list[str] = field(default_factory=list)
    actual_action_ids: list[str] = field(default_factory=list)
    actual_variables: dict[str, Any] = field(default_factory=dict)
    expected_outcome: str | None = None
    expected_step_path: list[str] | None = None
    expected_action_ids: list[str] | None = None
    expected_variables: dict[str, Any] | None = None
    diffs: list[str] = field(default_factory=list)
    events: list[dict] = field(default_factory=list)
    error: str | None = None
    final_message: str | None = None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "status": self.status,
            "actual": {
                "outcome": self.actual_outcome,
                "step_path": self.actual_step_path,
                "action_ids": self.actual_action_ids,
                "variables": self.actual_variables,
            },
            "expected": {
                "outcome": self.expected_outcome,
                "step_path": self.expected_step_path,
                "action_ids": self.expected_action_ids,
                "variables": self.expected_variables,
            },
            "diffs": self.diffs,
            "events": self.events,
            "error": self.error,
            "final_message": self.final_message,
        }


# ────────────────────────────────────────────────────────────────────────────
# Internal exceptions
# ────────────────────────────────────────────────────────────────────────────

class _Terminal(Exception):
    """Raised when the workflow reaches a terminal action."""

    def __init__(self, outcome: str, message: str = "") -> None:
        self.outcome = outcome  # "resolution" | "escalation" | "failure"
        self.message = message


class _MissingResponse(Exception):
    """Raised when a canned response cannot be found for a (step_id, command)."""


class _InterpreterError(Exception):
    """Raised on malformed RAW or test bundle input."""


# ────────────────────────────────────────────────────────────────────────────
# Variable interpolation
# ────────────────────────────────────────────────────────────────────────────

_INTERP_RE = re.compile(r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_.]*)\s*\}\}")


def _interpolate(text: str, variables: dict[str, Any]) -> str:
    """Replace `{{ var }}` references with values from the variable store.

    Supports dotted lookups like `{{ alert_vars.neighbor_address }}`.
    Unknown references are left as-is so the caller can detect them.
    """
    if not isinstance(text, str):
        return text

    def repl(match: re.Match) -> str:
        ref = match.group(1)
        parts = ref.split(".")
        cursor: Any = variables
        for part in parts:
            if isinstance(cursor, dict) and part in cursor:
                cursor = cursor[part]
            else:
                return match.group(0)  # leave unresolved
        return str(cursor)

    return _INTERP_RE.sub(repl, text)


# ──────────────────────────────────────────────────���─────────────────────────
# Response lookup
# ────────────────────────────────────────────────────────────��───────────────

def _lookup_response(
    responses: list[dict],
    step_id: str,
    command: str,
) -> str:
    """Find canned output for (step_id, command). step_id-scoped match wins.

    Falls back to a command-only match if no step-scoped entry exists. Raises
    `_MissingResponse` if nothing matches.
    """
    # Prefer (step_id, command) exact match.
    for entry in responses:
        if str(entry.get("step_id", "")) == str(step_id) and entry.get("command") == command:
            return entry.get("output", "")
    # Fall back to command-only match (when step_id is absent in the bundle).
    for entry in responses:
        if "step_id" not in entry and entry.get("command") == command:
            return entry.get("output", "")
    raise _MissingResponse(f"step_id={step_id!r} command={command!r}")


# ────────────────────────────────────────────────────────────────────────────
# Validation evaluation
# ────────────────────────────────────────────────────────────────────────────

def _eval_cli(
    block: dict,
    step_id: str,
    variables: dict[str, Any],
    responses: list[dict],
    events: list[dict],
) -> bool:
    """Run an eval_cli block against canned responses.

    Concatenates outputs from all `commands` and applies the regex `pattern`.
    Populates `outputs` variables based on the match. Returns True if the
    regex matched at least once, False otherwise.
    """
    commands = [_interpolate(c, variables) for c in block.get("commands", [])]
    pattern = _interpolate(block.get("pattern", ".*"), variables)
    outputs_spec = block.get("outputs", []) or []

    combined = []
    for cmd in commands:
        try:
            out = _lookup_response(responses, step_id, cmd)
        except _MissingResponse as exc:
            raise _MissingResponse(f"step {step_id}: {exc}") from exc
        combined.append(out)
    combined_text = "\n".join(combined)

    match = re.search(pattern, combined_text)
    matched = match is not None

    # Populate outputs.
    for spec in outputs_spec:
        name = spec.get("name")
        source = spec.get("source", "")
        if not name:
            continue
        value: Any
        if "result.matched" in source:
            value = matched
        elif "result.output" in source:
            value = combined_text
        else:
            # Look for `result.groups[N]` or `match.group(N)` style refs.
            grp_match = re.search(r"groups?\[?(\d+)\]?", source)
            if grp_match and match:
                idx = int(grp_match.group(1))
                try:
                    value = match.group(idx + 1) if "groups[" in source else match.group(idx)
                except IndexError:
                    value = None
            else:
                value = None
        variables[name] = value

    events.append({
        "type": "eval_cli",
        "step_id": step_id,
        "commands": commands,
        "matched": matched,
        "outputs": {s.get("name"): variables.get(s.get("name")) for s in outputs_spec if s.get("name")},
    })
    return matched


def _normalise_log_entry(entry: Any) -> str:
    """Return the message text from a synthetic log fixture entry."""
    if isinstance(entry, str):
        return entry
    if isinstance(entry, dict):
        for key in ("message", "output", "text"):
            if key in entry:
                return str(entry.get(key) or "")
    return str(entry)


def _eval_logs(
    block: dict,
    step_id: str,
    variables: dict[str, Any],
    log_entries: list[Any],
    events: list[dict],
) -> bool:
    """Run an eval_logs block against synthetic log fixtures.

    The current bundle format treats all entries without timestamps as within
    the requested lookback window. Timestamp-aware filtering can be added later
    without changing existing fixtures.
    """
    pattern = _interpolate(block.get("pattern", ".*"), variables)
    outputs_spec = block.get("outputs", []) or []
    combined_text = "\n".join(_normalise_log_entry(e) for e in (log_entries or []))
    match = re.search(pattern, combined_text)
    matched = match is not None

    for spec in outputs_spec:
        name = spec.get("name")
        source = spec.get("source", "")
        if not name:
            continue
        if "result.matched" in source:
            value: Any = matched
        elif "result.output" in source:
            value = combined_text
        else:
            grp_match = re.search(r"groups?\[?(\d+)\]?", source)
            if grp_match and match:
                idx = int(grp_match.group(1))
                try:
                    value = match.group(idx + 1) if "groups[" in source else match.group(idx)
                except IndexError:
                    value = None
            else:
                value = None
        variables[name] = value

    events.append({
        "type": "eval_logs",
        "step_id": step_id,
        "lookback_time": block.get("lookback_time"),
        "matched": matched,
        "outputs": {s.get("name"): variables.get(s.get("name")) for s in outputs_spec if s.get("name")},
    })
    return matched


def _eval_var(block: dict, variables: dict[str, Any]) -> bool:
    """Evaluate an eval_var block: compare a variable to a literal."""
    var_name = str(block.get("var_name") or "")
    operator = block.get("operator", "eq")
    expected = block.get("value")
    actual = variables.get(var_name) if var_name else None

    # Coerce the literal "True"/"False" strings the RAW author might write.
    if isinstance(expected, str) and expected.lower() in {"true", "false"}:
        expected = expected.lower() == "true"

    if operator == "eq":
        return actual == expected
    if operator == "ne":
        return actual != expected
    if operator == "gt":
        try:
            if actual is None or expected is None:
                return False
            return float(actual) > float(expected)  # pyright: ignore[reportArgumentType]
        except (TypeError, ValueError):
            return False
    if operator == "lt":
        try:
            if actual is None or expected is None:
                return False
            return float(actual) < float(expected)  # pyright: ignore[reportArgumentType]
        except (TypeError, ValueError):
            return False
    raise _InterpreterError(f"unsupported eval_var operator: {operator}")


def _eval_validation(
    validation: dict,
    step_id: str,
    variables: dict[str, Any],
    responses: list[dict],
    log_entries: list[Any],
    events: list[dict],
) -> bool:
    """Dispatch on validation block type."""
    if not validation:
        return True
    if "eval_cli" in validation:
        return _eval_cli(validation["eval_cli"], step_id, variables, responses, events)
    if "eval_logs" in validation:
        return _eval_logs(validation["eval_logs"], step_id, variables, log_entries, events)
    if "eval_var" in validation:
        return _eval_var(validation["eval_var"], variables)
    if "and" in validation:
        return all(_eval_validation(sub, step_id, variables, responses, log_entries, events) for sub in validation["and"])
    if "or" in validation:
        return any(_eval_validation(sub, step_id, variables, responses, log_entries, events) for sub in validation["or"])
    raise _InterpreterError(f"unknown validation type at step {step_id}: {list(validation)}")


# ────────────────────────────────────────────────────────────────────────────
# Condition expression evaluation
# ────────────────────────────────────────────────────────────────────────────

def _eval_condition(expr: str, variables: dict[str, Any]) -> bool:
    """Evaluate a small, safe boolean expression for action selection."""
    expr = expr.strip()
    if expr == "default":
        return True

    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as exc:
        raise _InterpreterError(f"unsupported condition expression: {expr!r}") from exc
    return bool(_eval_condition_node(tree.body, variables))


def _eval_condition_node(node: ast.AST, variables: dict[str, Any]) -> Any:
    if isinstance(node, ast.BoolOp):
        values = [_eval_condition_node(v, variables) for v in node.values]
        if isinstance(node.op, ast.And):
            return all(bool(v) for v in values)
        if isinstance(node.op, ast.Or):
            return any(bool(v) for v in values)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
        return not bool(_eval_condition_node(node.operand, variables))
    if isinstance(node, ast.Compare):
        left = _eval_condition_node(node.left, variables)
        for op, comparator in zip(node.ops, node.comparators):
            right = _eval_condition_node(comparator, variables)
            if isinstance(op, ast.Eq):
                ok = left == right
            elif isinstance(op, ast.NotEq):
                ok = left != right
            elif isinstance(op, ast.Gt):
                ok = left > right
            elif isinstance(op, ast.GtE):
                ok = left >= right
            elif isinstance(op, ast.Lt):
                ok = left < right
            elif isinstance(op, ast.LtE):
                ok = left <= right
            else:
                raise _InterpreterError(f"unsupported condition operator: {ast.dump(op)}")
            if not ok:
                return False
            left = right
        return True
    if isinstance(node, ast.Name):
        return _resolve_operand(node.id, variables)
    if isinstance(node, ast.Constant):
        return node.value
    raise _InterpreterError(f"unsupported condition node: {ast.dump(node)}")


def _resolve_operand(token: str, variables: dict[str, Any]) -> Any:
    """Resolve a token to a Python value (variable lookup or literal)."""
    token = token.strip()
    # Literal True/False.
    if token in {"True", "true"}:
        return True
    if token in {"False", "false"}:
        return False
    # Quoted string literal.
    if (token.startswith('"') and token.endswith('"')) or (token.startswith("'") and token.endswith("'")):
        return token[1:-1]
    # Numeric literal.
    try:
        return int(token)
    except ValueError:
        pass
    try:
        return float(token)
    except ValueError:
        pass
    # Variable lookup (with dotted path support).
    parts = token.split(".")
    cursor: Any = variables
    for part in parts:
        if isinstance(cursor, dict) and part in cursor:
            cursor = cursor[part]
        else:
            return None
    return cursor


# ────────────────────────────────────────────────────────────────────────────
# Step execution
# ────────────────────────────────────────────────────────────────────────────

def _execute_actions(
    actions: list[dict],
    step_id: str,
    variables: dict[str, Any],
    approvals: dict[str, Any],
    events: list[dict],
) -> str | None:
    """Execute a list of actions. Returns the next step_id, or None to stay.

    Raises `_Terminal` on resolve / escalate / fail.
    """
    next_step: str | None = None
    for action in actions:
        if "goto" in action:
            next_step = str(action["goto"]["step_id"])
            events.append({"type": "goto", "step_id": step_id, "target": next_step})
        elif "wait" in action:
            duration = action["wait"].get("duration", 0)
            events.append({"type": "wait", "step_id": step_id, "duration": duration})
        elif "exec_cli" in action or "config_cli" in action:
            kind = "exec_cli" if "exec_cli" in action else "config_cli"
            action_body = action[kind]
            raw_commands = action_body.get("commands") or [action_body.get("command", "")]
            for raw_cmd in raw_commands:
                cmd = _interpolate(raw_cmd, variables)
                decision = _approval_decision(approvals, step_id, cmd)
                events.append({
                    "type": "approval-needed",
                    "step_id": step_id,
                    "kind": kind,
                    "command": cmd,
                    "scripted_decision": decision,
                })
                if decision == "DENIED":
                    raise _Terminal("escalation", f"Operator denied {kind} at step {step_id}: {cmd}")
                # APPROVED → record execution but do not actually run anything.
                events.append({"type": f"{kind}-executed", "step_id": step_id, "command": cmd})
        elif "revalidate" in action:
            events.append({"type": "revalidate", "step_id": step_id})
            # Signal to the caller that revalidation is requested.
            return f"__revalidate__{step_id}"
        elif "resolve" in action:
            msg = _interpolate(action["resolve"].get("message", ""), variables)
            events.append({"type": "resolve", "step_id": step_id, "message": msg})
            raise _Terminal("resolution", msg)
        elif "escalate" in action:
            msg = _interpolate(action["escalate"].get("message", ""), variables)
            events.append({"type": "escalate", "step_id": step_id, "message": msg})
            raise _Terminal("escalation", msg)
        elif "fail" in action:
            msg = _interpolate(action["fail"].get("message", ""), variables)
            events.append({"type": "fail", "step_id": step_id, "message": msg})
            raise _Terminal("failure", msg)
        else:
            raise _InterpreterError(f"unknown action keys at step {step_id}: {list(action)}")
    return next_step


def _approval_decision(approvals: dict[str, Any], step_id: str, command: str) -> str:
    """Return scripted approval decision, supporting schema-list overrides.

    Older tests used a dict keyed by step_id; keep that shape as a lenient
    fallback while making the JSON-schema list format authoritative.
    """
    default = approvals.get("default", "APPROVED") if isinstance(approvals, dict) else "APPROVED"
    overrides = approvals.get("overrides", []) if isinstance(approvals, dict) else []
    if isinstance(overrides, list):
        for entry in overrides:
            if not isinstance(entry, dict):
                continue
            if str(entry.get("step_id")) == str(step_id) and entry.get("command") == command:
                return entry.get("decision", default)
    elif isinstance(overrides, dict):
        scoped = overrides.get(str(step_id))
        if isinstance(scoped, dict):
            if scoped.get("command") in (None, command):
                return scoped.get("decision", default)
        elif scoped in {"APPROVED", "DENIED"}:
            return scoped
    return default


def _execute_step(
    step: dict,
    variables: dict[str, Any],
    responses: list[dict],
    log_entries: list[Any],
    approvals: dict[str, Any],
    events: list[dict],
) -> str | None:
    """Execute one step: validate → action_select → execute first matching branch.

    Returns the next step_id, or None to advance sequentially.
    """
    step_id = str(step.get("step_id"))
    events.append({"type": "step-start", "step_id": step_id, "name": step.get("name")})

    # Validation.
    matched = _eval_validation(step.get("validation") or {}, step_id, variables, responses, log_entries, events)

    # Action select.
    selects = step.get("action_select", []) or []
    chosen = None
    for entry in selects:
        conditions = entry.get("conditions", []) or []
        # All conditions on an entry must evaluate truthy. `default` is always true.
        ok = True
        for cond in conditions:
            expr = cond.get("condition", "default")
            if not _eval_condition(expr, variables):
                ok = False
                break
        if ok:
            chosen = entry
            break

    if chosen is None:
        raise _Terminal("escalation", f"no action_select entry matched at step {step_id}")

    events.append({
        "type": "action-selected",
        "step_id": step_id,
        "action_id": chosen.get("action_id"),
        "action_name": chosen.get("name"),
        "validation_matched": matched,
    })

    # Execute action_groups[0].actions (the canonical RAW shape).
    groups = chosen.get("action_groups", []) or []
    next_step: str | None = None
    if groups:
        actions = groups[0].get("actions", []) or []
        next_step = _execute_actions(actions, step_id, variables, approvals, events)

    events.append({"type": "step-complete", "step_id": step_id})
    return next_step


# ────────────────────────────────────────────────────────────────────────────
# Public entry point
# ────────────────────────────────────────────────────────────────────────────

REVALIDATE_LIMIT = 6


def run_test(raw_yaml: dict, test: dict) -> TestResult:
    """Run a single test from a bundle against a parsed RAW YAML.

    Args:
        raw_yaml: The full RAW YAML loaded as a dict (top-level `workflow` key).
        test: A single test entry from the bundle (with `alert_payload`,
              `responses`, `approvals`, `expected`, etc.).

    Returns:
        TestResult capturing pass/fail/skip and the actual vs expected diff.
    """
    name = test.get("name", "<unnamed>")
    expected = test.get("expected", {}) or {}
    expected_outcome = expected.get("outcome")
    expected_step_path = expected.get("step_path")
    expected_action_ids = expected.get("action_ids")
    expected_variables = expected.get("variables") or {}

    result = TestResult(
        name=name,
        status="error",
        expected_outcome=expected_outcome,
        expected_step_path=expected_step_path,
        expected_action_ids=expected_action_ids,
        expected_variables=expected_variables,
    )

    # Skip hybrid-reasoning tests — the runner cannot exercise LLM judgement.
    payload = test.get("alert_payload", {}) or {}
    if payload.get("mode") == "hybrid-reasoning":
        result.status = "skipped"
        result.error = "hybrid-reasoning mode requires the agent runner"
        return result

    workflow = raw_yaml.get("workflow")
    if not workflow:
        result.error = "RAW YAML missing top-level `workflow` key"
        return result

    steps_by_id = {str(s.get("step_id")): s for s in workflow.get("steps", []) or []}
    if not steps_by_id:
        result.error = "RAW has no steps"
        return result

    # Build the variable store. Order: workflow.inputs (resolved against
    # alert_payload.alert_vars), KB context, FS-extracted vars (none in test
    # mode unless the bundle stubs them), then a few first-class fields.
    variables: dict[str, Any] = {}
    variables["alert_vars"] = payload.get("alert_vars", {}) or {}

    # Resolve workflow.inputs[].source references against the variable store.
    for inp in workflow.get("inputs", []) or []:
        iname = inp.get("name")
        isource = inp.get("source", "")
        if iname:
            variables[iname] = _interpolate(isource, variables)

    # Merge KB context override if provided (otherwise the runner has no KB).
    kb_ctx = test.get("kb_context_override") or {}
    if isinstance(kb_ctx, dict):
        variables.update(kb_ctx)

    # Initialise the step path tracker.
    step_path: list[str] = []
    events: list[dict] = []
    responses = test.get("responses", []) or []
    log_entries = test.get("log_entries", []) or []
    approvals = test.get("approvals", {}) or {"default": "APPROVED"}

    # Determine the entry step. RAW convention: first step in the list.
    current = str(workflow["steps"][0]["step_id"])
    revalidate_count: dict[str, int] = {}

    try:
        # Execute steps until a terminal action is raised or a safety cap hits.
        max_iterations = 64
        for _ in range(max_iterations):
            if current not in steps_by_id:
                raise _Terminal("failure", f"unknown step_id: {current}")

            step_path.append(current)
            step = steps_by_id[current]

            try:
                next_step = _execute_step(step, variables, responses, log_entries, approvals, events)
            except _MissingResponse as exc:
                raise _Terminal("failure", f"missing canned response: {exc}") from exc

            if next_step is None:
                # No goto/revalidate — advance to the next step in the YAML
                # ordering. If we're at the last step, treat as failure (no
                # explicit terminal action).
                ordered_ids = [str(s.get("step_id")) for s in workflow["steps"]]
                idx = ordered_ids.index(current)
                if idx + 1 < len(ordered_ids):
                    current = ordered_ids[idx + 1]
                else:
                    raise _Terminal("failure", f"workflow ran off the end after step {current}")
            elif next_step.startswith("__revalidate__"):
                revalidate_count[current] = revalidate_count.get(current, 0) + 1
                if revalidate_count[current] > REVALIDATE_LIMIT:
                    raise _Terminal("escalation", f"revalidate limit exceeded at step {current}")
                # current stays the same; fall through to next iteration.
            else:
                current = next_step
        else:
            raise _Terminal("failure", f"max iterations ({max_iterations}) exceeded")
    except _Terminal as terminal:
        result.actual_outcome = terminal.outcome
        result.final_message = terminal.message

    result.actual_step_path = step_path
    result.actual_action_ids = [str(e.get("action_id")) for e in events if e.get("type") == "action-selected"]
    # Expose only JSON-serialisable variables in the result.
    result.actual_variables = {
        k: v for k, v in variables.items()
        if isinstance(v, (str, int, float, bool, list, dict)) or v is None
    }
    result.events = events

    # Compute diffs.
    diffs: list[str] = []
    if expected_outcome and result.actual_outcome != expected_outcome:
        diffs.append(f"outcome: expected {expected_outcome!r}, got {result.actual_outcome!r}")
    if expected_step_path is not None and step_path != [str(s) for s in expected_step_path]:
        diffs.append(f"step_path: expected {expected_step_path}, got {step_path}")
    if expected_action_ids is not None and result.actual_action_ids != [str(a) for a in expected_action_ids]:
        diffs.append(f"action_ids: expected {expected_action_ids}, got {result.actual_action_ids}")
    for vname, vexpected in expected_variables.items():
        vactual = variables.get(vname)
        if vactual != vexpected:
            diffs.append(f"variables.{vname}: expected {vexpected!r}, got {vactual!r}")

    # must_visit / must_not_visit assertions.
    for sid in expected.get("must_visit", []) or []:
        if str(sid) not in step_path:
            diffs.append(f"must_visit: step {sid!r} not in actual path {step_path}")
    for sid in expected.get("must_not_visit", []) or []:
        if str(sid) in step_path:
            diffs.append(f"must_not_visit: step {sid!r} unexpectedly visited")

    result.diffs = diffs
    result.status = "pass" if not diffs else "fail"
    return result
