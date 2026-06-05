#!/usr/bin/env python3
"""Build a troubleshooting evidence bundle from session log and CLI captures.

The session log is the canonical execution record. CLI captures are stored as
separate text files and linked from the generated HTML report when referenced in
the log. The optional metadata.json file enriches the report header, but report
completeness should not depend on machine-generated event files.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class LogBlock:
    """One markdown section parsed from the session log."""

    title: str
    lines: list[str] = field(default_factory=list)
    fields: dict[str, str] = field(default_factory=dict)


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    return data if isinstance(data, dict) else {}


def _text(value: Any, default: str = "unknown") -> str:
    if value is None or value == "":
        return default
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def _as_list(value: Any) -> list[Any]:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return value
    return [value]


def _slug(value: str) -> str:
    safe = []
    for char in value.lower():
        if char.isalnum():
            safe.append(char)
        elif char in {"-", "_"}:
            safe.append(char)
        elif char.isspace() or char in {"/", ":", "."}:
            safe.append("-")
    result = "".join(safe).strip("-")
    while "--" in result:
        result = result.replace("--", "-")
    return result or "session"


def _parse_frontmatter(lines: list[str]) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in lines:
        match = re.match(r"^-\s+([^:]+):\s*(.*)$", line)
        if match:
            fields[match.group(1).strip()] = match.group(2).strip()
    return fields


def _parse_log_blocks(session_text: str) -> tuple[dict[str, str], list[LogBlock]]:
    lines = session_text.splitlines()
    header_fields: dict[str, str] = {}
    blocks: list[LogBlock] = []
    current: LogBlock | None = None
    preamble: list[str] = []

    for line in lines:
        if line.startswith("## "):
            if current is not None:
                current.fields = _parse_frontmatter(current.lines)
                blocks.append(current)
            elif preamble:
                header_fields.update(_parse_frontmatter(preamble))
            current = LogBlock(title=line[3:].strip())
            continue
        if current is None:
            preamble.append(line)
        else:
            current.lines.append(line)

    if current is not None:
        current.fields = _parse_frontmatter(current.lines)
        blocks.append(current)
    elif preamble:
        header_fields.update(_parse_frontmatter(preamble))
    return header_fields, blocks


def _extract_log_section(session_text: str, heading: str) -> list[str]:
    lines = session_text.splitlines()
    capture = False
    result: list[str] = []
    needle = f"### {heading}"
    for line in lines:
        if line.strip() == needle:
            capture = True
            continue
        if capture and (line.startswith("### ") or line.startswith("## ")):
            break
        if capture:
            result.append(line)
    return [line for line in result if line.strip()]


def _first_present(*values: Any, default: str = "unknown") -> str:
    for value in values:
        if value is not None and value != "":
            return _text(value, default)
    return default


def _find_block(blocks: list[LogBlock], marker: str) -> LogBlock | None:
    marker_upper = marker.upper()
    for block in blocks:
        if marker_upper in block.title.upper():
            return block
    return None


def _cli_files(bundle_dir: Path) -> list[Path]:
    cli_dir = bundle_dir / "cli"
    if not cli_dir.exists():
        return []
    return sorted(path for path in cli_dir.glob("*.txt") if path.is_file())


def _normalize_capture_path(value: str, bundle_dir: Path) -> str:
    cleaned = value.strip().strip("`")
    path = Path(cleaned)
    if path.is_absolute():
        try:
            return path.relative_to(bundle_dir).as_posix()
        except ValueError:
            return path.as_posix()
    if cleaned.startswith("logs/"):
        try:
            return Path(cleaned).resolve().relative_to(bundle_dir.resolve()).as_posix()
        except ValueError:
            return cleaned
    return cleaned


def _block_capture_links(block: LogBlock, bundle_dir: Path) -> list[str]:
    links: list[str] = []
    for key in ("capture_path", "cli_output", "cli_capture", "command_output"):
        value = block.fields.get(key)
        if value:
            links.append(_normalize_capture_path(value, bundle_dir))
    return links


def _render_links(paths: list[str]) -> str:
    if not paths:
        return "None recorded."
    rendered = []
    for path in paths:
        label = Path(path).name
        rendered.append(f'<a href="{html.escape(path)}">{html.escape(label)}</a>')
    return "<br>".join(rendered)


def _render_list(items: list[Any]) -> str:
    if not items:
        return "<p>None recorded.</p>"
    return "<ul>" + "".join(f"<li>{html.escape(_text(item, ''))}</li>" for item in items) + "</ul>"


def _render_markdown_lines(lines: list[str]) -> str:
    if not lines:
        return "<p>None recorded.</p>"
    items = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if re.match(r"^\d+\.\s+", stripped):
            stripped = re.sub(r"^\d+\.\s+", "", stripped)
        elif stripped.startswith("- "):
            stripped = stripped[2:]
        items.append(stripped)
    return _render_list(items)


def _timeline_blocks(blocks: list[LogBlock]) -> list[LogBlock]:
    markers = (
        "KB_CONTEXT_LOADED",
        "IA_ARTIFACTS_LOADED",
        "WEBEX_FAULT_RECEIVED",
        "STEP_COMPLETE",
        "APPROVAL_NEEDED",
        "AWAITING_APPROVAL",
        "APPROVED",
        "DENIED",
        "AUTO_APPROVE_WARNING",
        "EXEC_CLI_COMPLETE",
        "CONFIG_CLI_COMPLETE",
        "RESOLUTION",
        "ESCALATION",
        "FAILURE",
        "BUNDLE_GENERATED",
        "WEBEX_",
    )
    selected = []
    for block in blocks:
        title = block.title.upper()
        if any(marker in title for marker in markers):
            selected.append(block)
    return selected


def _render_timeline(blocks: list[LogBlock], bundle_dir: Path) -> tuple[str, set[str]]:
    rows = []
    referenced_cli: set[str] = set()
    for index, block in enumerate(_timeline_blocks(blocks), start=1):
        links = _block_capture_links(block, bundle_dir)
        referenced_cli.update(links)
        details = []
        for key in (
            "step_id",
            "step_name",
            "outcome",
            "validation_result",
            "action_selected",
            "command",
            "result",
            "evidence",
            "next",
            "reason",
            "decision",
            "verification_result",
        ):
            if key in block.fields:
                details.append(f"{key}: {block.fields[key]}")
        rows.append(
            "<tr>"
            f"<td>{index}</td>"
            f"<td>{html.escape(block.title)}</td>"
            f"<td>{html.escape('; '.join(details) if details else 'See session log for details.')}</td>"
            f"<td>{_render_links(links)}</td>"
            "</tr>"
        )
    if not rows:
        rows.append('<tr><td colspan="4">No timeline blocks found in session log.</td></tr>')
    return "".join(rows), referenced_cli


def _file_inventory(bundle_dir: Path) -> list[dict[str, Any]]:
    files = []
    for path in sorted(bundle_dir.rglob("*")):
        if not path.is_file() or path.suffix == ".zip":
            continue
        if path.name in {"events.jsonl", "report.html", "manifest.json"}:
            continue
        files.append({"path": path.relative_to(bundle_dir).as_posix(), "bytes": path.stat().st_size})
    return files


def _render_file_inventory(files: list[dict[str, Any]]) -> str:
    if not files:
        return "<p>No files recorded.</p>"
    rows = []
    for entry in files:
        path = str(entry["path"])
        rows.append(
            "<tr>"
            f'<td><a href="{html.escape(path)}">{html.escape(path)}</a></td>'
            f"<td>{entry['bytes']}</td>"
            "</tr>"
        )
    return "<table><tr><th>File</th><th>Bytes</th></tr>" + "".join(rows) + "</table>"


def _render_report(
    metadata: dict[str, Any],
    header_fields: dict[str, str],
    blocks: list[LogBlock],
    session_text: str,
    session_log_name: str,
    bundle_dir: Path,
    files: list[dict[str, Any]],
) -> tuple[str, list[str]]:
    kb_block = _find_block(blocks, "KB_CONTEXT_LOADED")
    resolution_block = _find_block(blocks, "RESOLUTION")
    summary_block = _find_block(blocks, "Session Summary")
    kb = metadata.get("kb_context") if isinstance(metadata.get("kb_context"), dict) else {}

    generated = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    cli_paths = [path.relative_to(bundle_dir).as_posix() for path in _cli_files(bundle_dir)]
    timeline_rows, referenced_cli = _render_timeline(blocks, bundle_dir)
    unreferenced_cli = [path for path in cli_paths if path not in referenced_cli]

    warnings: list[str] = []
    if unreferenced_cli:
        warnings.append("Some CLI captures were not directly referenced by session log timeline blocks.")
    if not cli_paths:
        warnings.append("No CLI capture files were found in the bundle.")
    incident_id = _first_present(metadata.get("incident_id"), header_fields.get("incident_id"))
    rows = "".join(
        f"<tr><th>{html.escape(key)}</th><td>{html.escape(_text(value))}</td></tr>"
        for key, value in [
            ("Incident ID", incident_id),
            ("Incident title", metadata.get("incident_title")),
            ("Alert definition", _first_present(metadata.get("alert_def_id"), header_fields.get("alert_def_id"))),
            ("Fault", metadata.get("fault_name")),
            ("Device", _first_present(metadata.get("device"), header_fields.get("device"))),
            ("Affected entity", metadata.get("affected_entity")),
            ("Mode", _first_present(metadata.get("mode"), header_fields.get("mode"))),
            ("Outcome", _first_present(metadata.get("outcome"), summary_block.fields.get("outcome") if summary_block else None)),
            ("Started", _first_present(metadata.get("started"), header_fields.get("started"))),
            ("Finished", _first_present(metadata.get("finished"), summary_block.fields.get("finished") if summary_block else None)),
            ("Generated", generated),
        ]
    )

    kb_fields = kb_block.fields if kb_block else {}
    kb_rows = "".join(
        f"<tr><th>{html.escape(key)}</th><td>{html.escape(_text(value))}</td></tr>"
        for key, value in [
            ("Severity", _first_present(kb.get("kb_sev_level"), kb_fields.get("severity"))),
            ("Response SLA", _first_present(kb.get("kb_response_sla"), "")),
            ("Change window active", _first_present(kb.get("kb_change_window_active"), kb_fields.get("change_window_active"))),
            ("Change approval required", kb.get("kb_change_requires_approval")),
            ("Known issue match", _first_present(kb.get("kb_known_issue_match"), kb_fields.get("known_issue_match"))),
            ("Prior incident match", _first_present(kb.get("kb_incident_match"), kb_fields.get("incident_match"))),
            ("Escalation path", _first_present(kb.get("kb_escalation_path"), kb_fields.get("escalation_path"))),
            ("Query mode", _first_present(kb.get("wiki_query_mode"), kb_fields.get("wiki_query_mode"))),
            ("Workflow influence", _first_present(kb.get("workflow_influence_summary"), kb_fields.get("workflow_influence_summary"))),
        ]
    )
    pages = _first_present(kb.get("pages_read"), kb_fields.get("pages_read"), default="")
    page_items = [item.strip() for item in pages.split(",") if item.strip()] if isinstance(pages, str) else _as_list(pages)

    rca_lines = _extract_log_section(session_text, "RCA")
    remediation_lines = _extract_log_section(session_text, "Remediation")
    residual_lines = _extract_log_section(session_text, "Residual Risk")
    rca = _first_present(metadata.get("rca_summary"), " ".join(rca_lines), default="Not recorded.")
    remediation = _render_markdown_lines(remediation_lines) if remediation_lines else _render_list(_as_list(metadata.get("remediation_summary")))
    residual = _render_markdown_lines(residual_lines) if residual_lines else html.escape(_text(metadata.get("residual_risk"), "Not recorded."))
    verification = _first_present(metadata.get("verification_result"), resolution_block.fields.get("verification_result") if resolution_block else None, default="Not recorded.")

    warning_html = ""
    if warnings:
        warning_html = '<section class="warnings"><h2>Report Warnings</h2>' + _render_list(warnings) + "</section>"
    unreferenced_html = ""
    if unreferenced_cli:
        unreferenced_items = "".join(
            f'<li><a href="{html.escape(path)}">{html.escape(path)}</a></li>'
            for path in unreferenced_cli
        )
        unreferenced_html = f"<h2>Unreferenced CLI Captures</h2><ul>{unreferenced_items}</ul>"

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Troubleshooting Report - {html.escape(incident_id)}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; color: #1f2933; line-height: 1.4; }}
    h1, h2 {{ color: #0b5cab; }}
    table {{ border-collapse: collapse; width: 100%; margin-bottom: 1.5rem; }}
    th, td {{ border: 1px solid #d9e2ec; padding: 0.5rem; text-align: left; vertical-align: top; }}
    th {{ background: #f0f4f8; }}
    .summary {{ border-left: 4px solid #0b5cab; padding-left: 1rem; margin-bottom: 1.5rem; }}
    .warnings {{ border-left: 4px solid #c2410c; background: #fff7ed; padding: 0.5rem 1rem; margin-bottom: 1.5rem; }}
    code {{ background: #f0f4f8; padding: 0.1rem 0.25rem; }}
  </style>
</head>
<body>
  <h1>Troubleshooting Report</h1>
  {warning_html}
  <section class="summary">
    <h2>RCA Summary</h2>
    <p>{html.escape(rca)}</p>
    <h2>Verification</h2>
    <p>{html.escape(verification)}</p>
    <h2>Residual Risk</h2>
    {residual if residual.startswith('<') else f'<p>{residual}</p>'}
  </section>

  <h2>Incident Summary</h2>
  <table>{rows}</table>

  <h2>Knowledge Base Context</h2>
  <table>{kb_rows}</table>
  <h3>Pages Read</h3>
  {_render_list(page_items)}

  <h2>Remediation Applied</h2>
  {remediation}

  <h2>Execution Timeline</h2>
  <table>
    <tr><th>#</th><th>Session Event</th><th>Details</th><th>CLI Output</th></tr>
    {timeline_rows}
  </table>

  {unreferenced_html}

  <h2>Session Log</h2>
  <p><a href="{html.escape(session_log_name)}">{html.escape(session_log_name)}</a></p>

  <h2>Bundle Contents</h2>
  {_render_file_inventory(files)}
</body>
</html>
""", warnings


def _write_manifest(bundle_dir: Path, metadata: dict[str, Any], warnings: list[str]) -> None:
    files = _file_inventory(bundle_dir)
    manifest = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "metadata": metadata,
        "warnings": warnings,
        "files": files,
    }
    (bundle_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def build_bundle(bundle_dir: Path, session_log: Path | None, output: Path | None) -> Path:
    bundle_dir.mkdir(parents=True, exist_ok=True)
    metadata = _load_json(bundle_dir / "metadata.json")

    # Avoid stale self-references when regenerating an existing bundle.
    for generated_file in (bundle_dir / "report.html", bundle_dir / "manifest.json"):
        if generated_file.exists():
            generated_file.unlink()

    session_log_name = "session.md"
    session_copy = bundle_dir / session_log_name
    if session_log and session_log.exists():
        shutil.copy2(session_log, session_copy)
    elif not session_copy.exists():
        session_copy.write_text("# Session log unavailable\n", encoding="utf-8")

    session_text = session_copy.read_text(encoding="utf-8")
    header_fields, blocks = _parse_log_blocks(session_text)
    files_before_report = _file_inventory(bundle_dir)
    report, warnings = _render_report(
        metadata,
        header_fields,
        blocks,
        session_text,
        session_log_name,
        bundle_dir,
        files_before_report,
    )
    (bundle_dir / "report.html").write_text(report, encoding="utf-8")
    _write_manifest(bundle_dir, metadata, warnings)

    if output is None:
        incident = _slug(_first_present(metadata.get("incident_id"), header_fields.get("incident_id"), default=bundle_dir.name))
        output = bundle_dir / f"{incident}-troubleshooting-bundle.zip"
    output.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(bundle_dir.rglob("*")):
            if path.is_file() and path.resolve() != output.resolve():
                archive.write(path, path.relative_to(bundle_dir).as_posix())
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Build troubleshooting HTML report and zip bundle")
    parser.add_argument("--bundle-dir", type=Path, required=True, help="Directory containing session.md and cli/")
    parser.add_argument("--session-log", type=Path, help="Markdown session log to copy into the bundle")
    parser.add_argument("--output", type=Path, help="Zip file path to write")
    args = parser.parse_args()

    output = build_bundle(
        args.bundle_dir.resolve(),
        args.session_log.resolve() if args.session_log else None,
        args.output.resolve() if args.output else None,
    )
    print(json.dumps({"status": "ok", "bundle_zip": str(output)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
