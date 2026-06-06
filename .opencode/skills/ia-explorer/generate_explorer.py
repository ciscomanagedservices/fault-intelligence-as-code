#!/usr/bin/env python3
"""
generate_explorer.py
Generate docs/index.html by inlining index.json into the HTML template.
Output goes to docs/ so it can be served via GitHub Pages.

Usage:
  python generate_explorer.py
"""

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATE = SCRIPT_DIR / "template.html"
WORKSPACE_ROOT = SCRIPT_DIR.parent.parent.parent  # ia-explorer → skills → .agents → root
IA_DIR = WORKSPACE_ROOT / "intelligence-artifacts"
INDEX_FILE = IA_DIR / "index.json"
DOCS_DIR = WORKSPACE_ROOT / "docs"
OUTPUT_FILE = DOCS_DIR / "index.html"


def main():
    if not INDEX_FILE.exists():
        print(f"ERROR: {INDEX_FILE} not found. Run ia-publish to generate it.", file=sys.stderr)
        sys.exit(1)

    if not TEMPLATE.exists():
        print(f"ERROR: Template not found at {TEMPLATE}", file=sys.stderr)
        sys.exit(1)

    # Read index JSON
    with INDEX_FILE.open(encoding="utf-8") as f:
        index_data = json.load(f)

    # Compact JSON for inlining
    index_json = json.dumps(index_data, ensure_ascii=False)

    # Read template and replace placeholder
    template = TEMPLATE.read_text(encoding="utf-8")
    html = template.replace("__INDEX_JSON__", index_json)

    # Ensure docs/ directory exists
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    # Write output
    OUTPUT_FILE.write_text(html, encoding="utf-8")

    total = len(index_data.get("artifacts", []))
    groups = index_data.get("stats", {}).get("groups", 0)
    print(f"Explorer generated: {OUTPUT_FILE}")
    print(f"  {total} artifacts across {groups} groups")


if __name__ == "__main__":
    main()
