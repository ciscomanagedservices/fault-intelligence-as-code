#!/usr/bin/env python3
"""
generate_index.py
Generate intelligence-artifacts/index.json from published YAML artifacts.

Walks the intelligence-artifacts/ directory for *.yml files, extracts metadata,
syslog patterns, cross-references, and computes summary stats. Outputs a single
JSON index file consumed by the ia-explorer HTML page and ia-research skill.

Usage:
  python generate_index.py [--pretty] [--output PATH]

Requirements:
  pip install pyyaml
"""

import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = SCRIPT_DIR.parent.parent.parent.parent  # scripts → ia-publish → skills → .agents → workspace root
IA_DIR = WORKSPACE_ROOT / "intelligence-artifacts"

# Files to skip inside intelligence-artifacts/
SKIP_FILES = {"index.json", "index.md"}


# ---------------------------------------------------------------------------
# Artifact type detection (mirrors validate_artifact.py logic)
# ---------------------------------------------------------------------------
# All artifact IDs are 6-digit zero-padded strings with a type prefix.
ID_PREFIXES = {
    "AD": "alert_definition",
    "FS": "fault_signature",
    "CL": "collection_list",
    "PARSE": "parser",
    "HCR": "health_check_rule",
    "RG": "remediation_guide",
    "RAW": "repair_action_workflow",
}

ID_PATTERN = re.compile(r"^([A-Z]+)\d{6}$")

TYPE_LABELS = {
    "alert_definition": "Alert Definition",
    "fault_signature": "Fault Signature",
    "collection_list": "Diagnostic Data Collection List",
    "parser": "Diagnostic Data Parser",
    "health_check_rule": "Health Check Rule",
    "remediation_guide": "Remediation Guide",
    "repair_action_workflow": "Repair Action Workflow",
}


def get_metadata(doc: dict) -> dict:
    """Return the metadata dict regardless of nesting."""
    if "workflow" in doc:
        return doc["workflow"].get("metadata", {})
    return doc.get("metadata", {})


def get_id(doc: dict):
    """Return the artifact ID regardless of nesting."""
    meta = get_metadata(doc)
    if "id" in doc and not isinstance(doc.get("id"), dict):
        return doc["id"]
    return meta.get("id")


def get_name(doc: dict) -> str:
    """Return the artifact name regardless of nesting."""
    if "workflow" in doc:
        return doc["workflow"].get("metadata", {}).get("name", "")
    if "metadata" in doc:
        return doc["metadata"].get("name", "")
    return doc.get("name", "")


def detect_artifact_type(doc: dict) -> str | None:
    """Detect artifact type from string ID prefix, name suffix, or structural keys."""
    artifact_id = get_id(doc)

    # 1. Try string ID prefix (e.g. "FS000004" → "fault_signature")
    if isinstance(artifact_id, str):
        m = ID_PATTERN.match(artifact_id)
        if m:
            prefix = m.group(1)
            if prefix in ID_PREFIXES:
                return ID_PREFIXES[prefix]

    # 2. Try name suffix
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

    return None


# ---------------------------------------------------------------------------
# Field extraction
# ---------------------------------------------------------------------------

def truncate(text: str, max_len: int = 300) -> str:
    """Truncate text to max_len chars, appending '...' if truncated."""
    if not text:
        return ""
    text = text.strip()
    if len(text) <= max_len:
        return text
    return text[:max_len].rstrip() + "..."


def extract_syslog_info(doc: dict) -> tuple[list[str], list[str], list[str]]:
    """Extract syslog mnemonics, regex patterns, and message samples from FS conditions.events."""
    mnemonics = []
    patterns = []
    samples = []
    conditions = doc.get("conditions", {})
    events = conditions.get("events", [])
    for entry in events:
        event = entry.get("event", entry)
        msg_type = event.get("message_type", "")
        if msg_type:
            mnemonics.append(msg_type)
        evaluation = event.get("evaluation", {})
        regex_val = evaluation.get("value", "")
        if regex_val:
            patterns.append(regex_val)
        sample = event.get("message_sample", "")
        if sample:
            # Truncate very long samples; strip trailing whitespace
            sample = sample.strip()
            if len(sample) > 500:
                sample = sample[:500].rstrip() + "..."
            samples.append(sample)
    return mnemonics, patterns, samples


def extract_linked_artifacts(doc: dict, artifact_type: str) -> dict:
    """Extract cross-reference links from the artifact."""
    links = {}
    meta = get_metadata(doc)

    if artifact_type == "fault_signature":
        raw_ref = meta.get("repair_action_workflow_ref", "")
        if raw_ref:
            links["repair_action_workflow"] = raw_ref
        # Infer RG link from naming convention: NAME -> NAME_GUIDE
        name = get_name(doc)
        if name and not name.endswith("_GUIDE"):
            links["remediation_guide"] = name + "_GUIDE"

    elif artifact_type == "remediation_guide":
        fs_ref = doc.get("fault_signature_ref", "")
        if fs_ref:
            links["fault_signature"] = fs_ref

    elif artifact_type == "repair_action_workflow":
        # RAW doesn't have explicit back-refs; infer from naming
        name = get_name(doc)
        if name and name.endswith("_REPAIR"):
            base = name.rsplit("_REPAIR", 1)[0]
            links["fault_signature"] = base
            links["remediation_guide"] = base + "_GUIDE"

    return links


def count_design_questions(yaml_path: Path) -> int:
    """Count open design questions from the YAML comment block."""
    count = 0
    with yaml_path.open(encoding="utf-8") as f:
        in_block = False
        for line in f:
            if "OPEN DESIGN QUESTIONS" in line:
                in_block = True
                continue
            if in_block:
                if line.startswith("# ─") or (not line.startswith("#") and line.strip()):
                    break
                # Count numbered questions: "# 1.", "# 2.", etc.
                if re.match(r"^#\s+\d+\.", line):
                    count += 1
    return count


def extract_artifact(yaml_path: Path, doc: dict, artifact_type: str) -> dict | None:
    """Extract a single artifact entry for the index."""
    meta = get_metadata(doc)
    name = get_name(doc)
    artifact_id = get_id(doc)

    if not name:
        return None

    # Relative file path from workspace root
    try:
        rel_path = yaml_path.relative_to(WORKSPACE_ROOT).as_posix()
    except ValueError:
        rel_path = yaml_path.name

    # Group = parent folder name. If it matches AD######-*, use that as the
    # alert_definition group; otherwise fall back to folder name.
    group = yaml_path.parent.name
    if group == "intelligence-artifacts":
        group = ""

    # Pull alert_def_id from metadata (FS required, RAW optional).
    alert_def_id = meta.get("alert_def_id", "")
    # Fallback: derive from parent folder if it matches AD######-<slug>
    if not alert_def_id:
        m = re.match(r"^(AD\d{6})-", group or "")
        if m:
            alert_def_id = m.group(1)

    entry = {
        "id": str(artifact_id) if artifact_id is not None else "",
        "name": name,
        "type": artifact_type,
        "type_label": TYPE_LABELS.get(artifact_type, artifact_type),
        "version": meta.get("version", ""),
        "group": group,
        "alert_def_id": alert_def_id,
        "file": rel_path,
        "description": truncate(meta.get("description", "")),
        "severity": meta.get("severity", ""),
        "component": meta.get("component", ""),
        "product_ids": meta.get("product_ids", []),
        "os_versions": meta.get("os_versions", []),
        "tags": meta.get("tags", []),
        "created_date": meta.get("created_date", ""),
        "modified_date": meta.get("modified_date", ""),
        "design_questions": count_design_questions(yaml_path),
    }

    # FS-specific: syslog mnemonics, regex patterns, and message samples
    if artifact_type == "fault_signature":
        mnemonics, patterns, samples = extract_syslog_info(doc)
        entry["syslog_mnemonics"] = mnemonics
        entry["regex_patterns"] = patterns
        entry["message_samples"] = samples

    # RG-specific: symptoms
    if artifact_type == "remediation_guide":
        entry["symptoms"] = doc.get("symptoms", [])

    # Cross-references
    entry["linked_artifacts"] = extract_linked_artifacts(doc, artifact_type)

    return entry


# ---------------------------------------------------------------------------
# Stats computation
# ---------------------------------------------------------------------------

def compute_stats(artifacts: list[dict]) -> dict:
    """Compute summary statistics from the artifact list."""
    by_type = defaultdict(int)
    by_severity = defaultdict(int)
    by_component = defaultdict(int)
    all_platforms = set()
    all_mnemonics = set()
    all_groups = set()

    for a in artifacts:
        by_type[a["type"]] += 1
        if a["severity"]:
            by_severity[a["severity"]] += 1
        if a["component"]:
            by_component[a["component"]] += 1
        for p in a.get("product_ids", []):
            all_platforms.add(p)
        for m in a.get("syslog_mnemonics", []):
            all_mnemonics.add(m)
        if a["group"]:
            all_groups.add(a["group"])

    return {
        "total": len(artifacts),
        "groups": len(all_groups),
        "by_type": dict(by_type),
        "by_severity": dict(by_severity),
        "by_component": dict(by_component),
        "platforms": sorted(all_platforms),
        "syslog_mnemonics": sorted(all_mnemonics),
    }


# ---------------------------------------------------------------------------
# Repository metadata
# ---------------------------------------------------------------------------

def detect_repo_info(workspace_root: Path) -> tuple[str, str]:
    """Detect repo URL and default branch from git. Returns (repo_url, default_branch)."""
    try:
        repo_url = subprocess.check_output(
            ["git", "remote", "get-url", "origin"],
            cwd=str(workspace_root), stderr=subprocess.DEVNULL, text=True
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        repo_url = ""

    # Normalize SSH URLs to HTTPS for web linking
    # git@github.com:org/repo.git → https://github.com/org/repo
    ssh_match = re.match(r"git@([^:]+):([^/]+)/(.+?)(?:\.git)?$", repo_url)
    if ssh_match:
        host, org, name = ssh_match.groups()
        repo_url = f"https://{host}/{org}/{name}"
    elif repo_url.endswith(".git"):
        repo_url = repo_url[:-4]

    # Detect default branch from symbolic-ref (HEAD → origin/main or origin/master)
    default_branch = "main"
    try:
        ref = subprocess.check_output(
            ["git", "symbolic-ref", "refs/remotes/origin/HEAD"],
            cwd=str(workspace_root), stderr=subprocess.DEVNULL, text=True
        ).strip()
        # refs/remotes/origin/main → main
        default_branch = ref.split("/")[-1] or "main"
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    return repo_url, default_branch


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def collect_yaml_files(base_dir: Path) -> list[Path]:
    """Collect all .yml/.yaml files under base_dir, deduplicating when both exist.

    Excludes anything under a `tests/` directory (test bundles are not artifacts).
    """
    seen_stems: dict[str, Path] = {}  # key = parent/stem, value = chosen path
    for pattern in ("**/*.yml", "**/*.yaml"):
        for yml in sorted(base_dir.glob(pattern)):
            if yml.name in SKIP_FILES:
                continue
            # Skip RAW test bundles under any tests/ folder
            if "tests" in yml.parts:
                continue
            key = str(yml.parent / yml.stem)
            if key in seen_stems:
                # Prefer .yml over .yaml
                if yml.suffix == ".yml":
                    seen_stems[key] = yml
            else:
                seen_stems[key] = yml
    return sorted(seen_stems.values())


def collect_rg_md_files(base_dir: Path) -> list[Path]:
    """Collect all Markdown Remediation Guide files under base_dir.

    Matches the canonical `RG######-*.md` naming.
    """
    return sorted(base_dir.glob("**/RG[0-9][0-9][0-9][0-9][0-9][0-9]-*.md"))


def _parse_rg_md_header(text: str) -> dict:
    """Extract Alert Definition / Guide ID / Linked FS / Linked RAW from RG markdown header."""
    out: dict = {}
    patterns = {
        "alert_def_id": r"\*\*Alert Definition:\*\*\s*(AD\d{6})",
        "id": r"\*\*Guide ID:\*\*\s*(RG\d{6})",
        "linked_fs": r"\*\*Linked Fault Signature:\*\*\s*(FS\d{6})",
        "linked_raw": r"\*\*Linked Repair Action Workflow:\*\*\s*(RAW\d{6})",
    }
    for key, pat in patterns.items():
        m = re.search(pat, text)
        if m:
            out[key] = m.group(1)
    # Title (first H1)
    m = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    if m:
        out["title"] = m.group(1).strip()
    return out


def extract_rg_md_overview(md_path: Path) -> str:
    """Extract the first paragraph of the Overview section from a .md file."""
    text = md_path.read_text(encoding="utf-8")
    # Find ## Overview section
    m = re.search(r"##\s+Overview\s*\n+(.*?)(?:\n##|\Z)", text, re.DOTALL)
    if not m:
        return ""
    # Take the first non-empty paragraph
    paragraphs = [p.strip() for p in m.group(1).strip().split("\n\n") if p.strip()]
    return paragraphs[0] if paragraphs else ""


def extract_rg_md_artifact(md_path: Path) -> dict | None:
    """Extract an index entry from a Markdown Remediation Guide file.

    Expects the canonical `RG######-<slug>.md` naming.
    """
    text = md_path.read_text(encoding="utf-8")
    header = _parse_rg_md_header(text)

    # Determine name (used for cross-linking by name)
    fname = md_path.name
    # RG######-<slug>.md → prefer title from header, else strip extension
    name = header.get("title", "") or fname[: -len(".md")]

    # Relative file path from workspace root
    try:
        rel_path = md_path.relative_to(WORKSPACE_ROOT).as_posix()
    except ValueError:
        rel_path = md_path.name

    # Group = parent folder name
    group = md_path.parent.name
    if group == "intelligence-artifacts":
        group = ""

    # Pull AD ID from header, else derive from folder
    alert_def_id = header.get("alert_def_id", "")
    if not alert_def_id:
        m = re.match(r"^(AD\d{6})-", group or "")
        if m:
            alert_def_id = m.group(1)

    # Linked artifacts
    linked: dict = {}
    if "linked_fs" in header:
        linked["fault_signature"] = header["linked_fs"]
    if "linked_raw" in header:
        linked["repair_action_workflow"] = header["linked_raw"]
    # Legacy fallback: infer FS from name pattern NAME_GUIDE → NAME
    if "fault_signature" not in linked and name.endswith("_GUIDE"):
        base = name[: -len("_GUIDE")]
        linked["fault_signature"] = base

    artifact_id = header.get("id", "")

    description = truncate(extract_rg_md_overview(md_path))

    return {
        "id": artifact_id,
        "name": name,
        "type": "remediation_guide",
        "type_label": TYPE_LABELS["remediation_guide"],
        "version": "",
        "group": group,
        "alert_def_id": alert_def_id,
        "file": rel_path,
        "description": description,
        "severity": "",
        "component": "",
        "product_ids": [],
        "os_versions": [],
        "tags": [],
        "created_date": "",
        "modified_date": "",
        "design_questions": 0,
        "symptoms": [],
        "linked_artifacts": linked,
    }


def _synthesize_alert_definitions(artifacts: list[dict]) -> list[dict]:
    """Add synthetic Alert Definition entries grouping FS/RAW/RG by alert_def_id.

    An Alert Definition is a folder-level grouping (AD######) with no manifest
    file. We synthesize one index entry per distinct alert_def_id that appears
    on any artifact, summarizing the linked children.
    """
    by_ad: dict[str, list[dict]] = defaultdict(list)
    for a in artifacts:
        ad = a.get("alert_def_id", "")
        if ad and a["type"] != "alert_definition":
            by_ad[ad].append(a)

    synthesized: list[dict] = []
    for ad_id, members in sorted(by_ad.items()):
        # Pick the FS as the canonical source for shared metadata
        fs = next((m for m in members if m["type"] == "fault_signature"), None)
        raw = next((m for m in members if m["type"] == "repair_action_workflow"), None)
        rg = next((m for m in members if m["type"] == "remediation_guide"), None)

        # Group folder name from any member (all should share the same parent)
        group = members[0].get("group", "")

        # Reconstruct folder path
        try:
            folder_rel = (IA_DIR / group).relative_to(WORKSPACE_ROOT).as_posix() if group else ""
        except ValueError:
            folder_rel = group

        name = fs["name"] if fs else (rg["name"] if rg else (raw["name"] if raw else ad_id))
        entry = {
            "id": ad_id,
            "name": name,
            "type": "alert_definition",
            "type_label": TYPE_LABELS["alert_definition"],
            "version": fs["version"] if fs else "",
            "group": group,
            "alert_def_id": ad_id,
            "file": folder_rel,
            "description": (fs or rg or raw or {}).get("description", ""),
            "severity": (fs or {}).get("severity", ""),
            "component": (fs or {}).get("component", ""),
            "product_ids": (fs or {}).get("product_ids", []),
            "os_versions": (fs or {}).get("os_versions", []),
            "tags": (fs or {}).get("tags", []),
            "created_date": (fs or {}).get("created_date", ""),
            "modified_date": (fs or {}).get("modified_date", ""),
            "design_questions": 0,
            "members": {
                "fault_signature": fs["id"] if fs else "",
                "remediation_guide": rg["id"] if rg else "",
                "repair_action_workflow": raw["id"] if raw else "",
            },
        }
        synthesized.append(entry)

    return synthesized + artifacts


def generate_index(
    pretty: bool = False,
    output_path: Path | None = None,
    repo_url: str | None = None,
    default_branch: str | None = None,
) -> dict:
    """Generate the index from intelligence-artifacts/ and return the index dict."""
    if not IA_DIR.exists():
        print(f"ERROR: intelligence-artifacts/ directory not found at {IA_DIR}", file=sys.stderr)
        sys.exit(1)

    yaml_files = collect_yaml_files(IA_DIR)
    rg_md_files = collect_rg_md_files(IA_DIR)
    if not yaml_files and not rg_md_files:
        print("WARNING: No YAML or .md files found in intelligence-artifacts/", file=sys.stderr)

    artifacts = []
    errors = []

    for yf in yaml_files:
        try:
            with yf.open(encoding="utf-8") as f:
                doc = yaml.safe_load(f)
            if not doc or not isinstance(doc, dict):
                errors.append(f"  SKIP {yf.name}: empty or non-dict YAML")
                continue

            artifact_type = detect_artifact_type(doc)
            if not artifact_type:
                errors.append(f"  SKIP {yf.name}: could not detect artifact type")
                continue

            # Reject placeholder IDs (000000 suffix) in published artifacts
            artifact_id = get_id(doc)
            if isinstance(artifact_id, str) and re.match(r"^[A-Z]+000000$", artifact_id):
                errors.append(
                    f"  ERROR {yf.name}: placeholder ID '{artifact_id}' found in "
                    f"intelligence-artifacts/ — drafts must have IDs allocated before publishing"
                )
                continue

            entry = extract_artifact(yf, doc, artifact_type)
            if entry:
                artifacts.append(entry)
            else:
                errors.append(f"  SKIP {yf.name}: could not extract artifact metadata")
        except yaml.YAMLError as e:
            errors.append(f"  ERROR {yf.name}: YAML parse error: {e}")
        except Exception as e:
            errors.append(f"  ERROR {yf.name}: {e}")

    # Index Markdown Remediation Guides — skip if a YAML RG with the same name
    # OR a YAML RG with the same id is already indexed.
    yaml_rg_names = {a["name"] for a in artifacts if a["type"] == "remediation_guide"}
    yaml_rg_ids = {a["id"] for a in artifacts if a["type"] == "remediation_guide" and a.get("id")}
    for mf in rg_md_files:
        try:
            # Reject placeholder RG IDs (RG000000) in published artifacts
            if re.match(r"^RG000000-", mf.name):
                errors.append(
                    f"  ERROR {mf.name}: placeholder ID 'RG000000' found in "
                    f"intelligence-artifacts/ — drafts must have IDs allocated before publishing"
                )
                continue

            entry = extract_rg_md_artifact(mf)
            if not entry:
                errors.append(f"  SKIP {mf.name}: could not extract RG metadata")
                continue
            if entry["name"] in yaml_rg_names:
                continue
            if entry.get("id") and entry["id"] in yaml_rg_ids:
                continue
            artifacts.append(entry)
        except Exception as e:
            errors.append(f"  ERROR {mf.name}: {e}")

    # Synthesize Alert Definition entries by grouping artifacts that share an alert_def_id.
    artifacts = _synthesize_alert_definitions(artifacts)

    # Detect or accept repo metadata for GitHub URL construction
    if repo_url is None or default_branch is None:
        detected_url, detected_branch = detect_repo_info(WORKSPACE_ROOT)
        repo_url = repo_url if repo_url is not None else detected_url
        default_branch = default_branch if default_branch is not None else detected_branch

    index = {
        "version": "1.0.0",
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "intelligence-artifacts",
        "repo_url": repo_url,
        "default_branch": default_branch,
        "artifacts": artifacts,
        "stats": compute_stats(artifacts),
    }

    # Write output
    out = output_path or (IA_DIR / "index.json")
    indent = 2 if pretty else None
    with out.open("w", encoding="utf-8") as f:
        json.dump(index, f, indent=indent, ensure_ascii=False)
        f.write("\n")

    # Print summary
    stats = index["stats"]
    print(f"Index generated: {out}")
    print(f"  Artifacts: {stats['total']} ({', '.join(f'{v} {k}' for k, v in stats['by_type'].items())})")
    print(f"  Groups: {stats['groups']}")
    print(f"  Platforms: {len(stats['platforms'])}")
    print(f"  Syslog mnemonics: {len(stats['syslog_mnemonics'])}")

    if errors:
        print(f"\n  Warnings/Errors ({len(errors)}):")
        for e in errors:
            print(e)

    return index


def main():
    parser = argparse.ArgumentParser(description="Generate intelligence-artifacts/index.json")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    parser.add_argument("--output", type=Path, help="Output file path (default: intelligence-artifacts/index.json)")
    parser.add_argument("--repo-url", dest="repo_url", default=None, help="Override repository URL for GitHub links")
    parser.add_argument("--default-branch", dest="default_branch", default=None, help="Override default branch name for GitHub links")
    args = parser.parse_args()
    generate_index(pretty=args.pretty, output_path=args.output, repo_url=args.repo_url, default_branch=args.default_branch)


if __name__ == "__main__":
    main()
