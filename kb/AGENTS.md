# Network Operations Knowledge Base: LLM Wiki

Mode: B/C Hybrid — Network Operations (Agent-Optimized)
Purpose: Persistent knowledge base for a network troubleshooting agent and human operators.
Owner: [Your Name]
Created: 2026-05-06

## Bootstrap

If `wiki/hot.md` exists, silently read it at session start to restore recent context.

## Vault Structure

- `.raw/` — source documents (immutable, never modify)
- `wiki/` — AI-generated knowledge base
- `_templates/` — Obsidian Templater templates (not content)

## Folder Map

```
wiki/
├── entities/        — Devices, vendors, teams, tools, people
├── concepts/        — Protocols, technologies, terminology
├── sources/         — Ingested doc summaries (1:1 with .raw/ files)
├── incidents/       — Past outages, degradations, post-mortems
├── runbooks/        — Step-by-step troubleshooting and change procedures
├── known-issues/    — Recurring bugs, workarounds, vendor quirks
├── business-rules/  — SLAs, escalation paths, change policies
├── comparisons/     — Tool and protocol side-by-side analyses
├── questions/       — Filed Q&A pairs
└── meta/            — Dashboards and lint reports
```

## Troubleshooting Agent Lookup Sequence

When diagnosing an issue, the agent MUST follow this sequence:

1. Read `wiki/hot.md` — get recent context (fast)
2. Check `wiki/known-issues/` — does a known workaround apply? Apply and stop if yes.
3. Search `wiki/incidents/` — match symptom patterns to past incidents
4. Pull the relevant `wiki/runbooks/` procedure — execute steps
5. Consult `wiki/business-rules/` — check escalation, SLA, and change constraints before acting
6. Reference `wiki/entities/` and `wiki/concepts/` for device-specific or protocol context

## Conventions

- All notes use YAML frontmatter: type, status, created, updated, tags (minimum)
- Wikilinks: `[[Note Name]]` format — filenames are unique, no paths needed
- `.raw/` contains source documents: never modify them
- `wiki/index.md` is the master catalog: update on every ingest
- `wiki/log.md` is append-only, new entries at the top
- `wiki/hot.md` is overwritten completely each session

## Content Folder Contract

Each content folder must be populated with individual wiki pages (not just an index).
During source ingestion, the wiki-ingest skill must create pages in every content folder
where extracted content is relevant. One source may produce pages across multiple folders.

## Operations

- **Ingest:** Drop source in `.raw/`, say `ingest [filename]`
- **Query:** Ask any question — read `wiki/hot.md` first, then `wiki/index.md`, then drill in
- **Lint:** Say `lint the wiki` to run a health check
- **Archive:** Move cold sources to `.archive/` to keep `.raw/` clean

## Agent Constraints

Before taking any action that could affect the network or require human involvement, the agent MUST:
1. Check `wiki/business-rules/` for applicable SLAs, escalation requirements, and change windows
2. Verify it has the authorization level required for the action
3. Notify appropriate contacts per the escalation matrix documented in `wiki/business-rules/`
