# Knowledge Base Curator Quickstart

Use this quickstart when you want to add, query, save, or clean up operational knowledge in the project KB vault. The KB vault lives under `kb/` and is maintained manually through the `kb-curator` agent.

The important boundary: `network-troubleshooter` can read KB context through `kb-reader`, but it cannot call `kb-curator` and cannot write to the vault. KB writes are human-initiated only.

Use `kb-curator` for every write or maintenance action in this quickstart. Use **Builder** only for general repository setup tasks before you open the curator agent.

## 1. Start OpenCode

From the repository root:

```bash
opencode web
```

Open the local browser URL, usually `http://localhost:4096`. You can also use the terminal UI:

```bash
opencode
```

## 2. Select the KB Curator Agent

Start a new chat and select the `kb-curator` agent.

Use this agent for vault maintenance tasks:

| Task | Prompt pattern | Skill used |
|------|----------------|------------|
| Query existing KB knowledge | `query quick: what business rules apply to BGP remediation?` | `wiki-query` |
| Ingest a source document | `ingest kb/.raw/acme_corp_netops_handbook.md` | `wiki-ingest` |
| Ingest unprocessed raw sources | `ingest all unprocessed files in kb/.raw/` | `wiki-ingest` |
| Save an insight from chat | `save this analysis as a runbook note` | `save` |
| Check vault health | `lint the wiki and show the report before fixing anything` | `wiki-lint` |
| Scaffold a missing vault | `set up the wiki vault for network operations` | `wiki` |

The curator agent dispatches directly to these skills. You do not need to name the skill explicitly if the request is clear.

## 3. Query the Vault First

Before adding duplicate content, ask the curator what is already known:

```text
query quick: what does the KB already know about BGP neighbor administrative shutdown?
```

Use query modes based on depth:

| Mode | Prompt | Best for |
|------|--------|----------|
| Quick | `query quick: ...` | Hot-cache or index lookups. |
| Standard | `query: ...` | Normal questions using `hot.md`, `index.md`, and a few relevant pages. |
| Deep | `query deep: ...` | Cross-vault synthesis, comparisons, or gap analysis. |

Good answers may be saved back into `kb/wiki/questions/` so future sessions can reuse them.

## 4. Add a Source Document

Place durable source material under `kb/.raw/`. This folder is immutable source storage; after a source is placed there, do not edit it in place.

Example:

```text
kb/.raw/acme_corp_netops_handbook.md
```

Then ask `kb-curator`:

```text
ingest kb/.raw/acme_corp_netops_handbook.md
```

During ingest, the curator uses `wiki-ingest` to create or update pages across the vault, including source summaries, entities, concepts, runbooks, known issues, incidents, business rules, indexes, the hot cache, and the operation log.

For URLs, paste the URL directly:

```text
ingest https://example.com/vendor-advisory
```

The skill fetches the page, stores a cleaned copy under `kb/.raw/articles/`, then ingests that raw source.

## 5. Save an Operational Insight

Use `save` when the useful knowledge came from a chat discussion rather than a standalone source file:

```text
save this as a business rule: BGP config changes require maintenance-window approval unless the incident is Severity 1 and the escalation manager approves emergency remediation.
```

The save skill chooses the best wiki folder, creates frontmatter, writes the note, updates `kb/wiki/index.md`, appends `kb/wiki/log.md`, and refreshes `kb/wiki/hot.md`.

## 6. Run Vault Maintenance

After several ingests, run a lint pass:

```text
lint the wiki and show the report before fixing anything
```

`wiki-lint` checks for orphan pages, dead wikilinks, stale claims, missing pages, missing cross-references, frontmatter gaps, empty sections, stale index entries, and empty content folders. It writes reports under:

```text
kb/wiki/meta/
```

Review the report before allowing auto-fixes. Deleting or merging pages and resolving contradictions require human judgment.

## 7. Inspect What Changed

Common files and folders to review after curator work:

| Path | Purpose |
|------|---------|
| `kb/.raw/` | Immutable source documents and ingest manifest. |
| `kb/wiki/sources/` | One summary page per ingested source. |
| `kb/wiki/entities/` | Devices, vendors, teams, tools, people, and other named entities. |
| `kb/wiki/concepts/` | Protocols, technologies, terminology, and operating concepts. |
| `kb/wiki/incidents/` | Past outages, degradations, and postmortems. |
| `kb/wiki/runbooks/` | Step-by-step troubleshooting and change procedures. |
| `kb/wiki/known-issues/` | Recurring bugs, workarounds, and vendor quirks. |
| `kb/wiki/business-rules/` | SLAs, escalation paths, approval rules, and change policies. |
| `kb/wiki/index.md` | Master catalog of wiki pages. |
| `kb/wiki/hot.md` | Short recent-context cache read first by wiki queries. |
| `kb/wiki/log.md` | Append-only operation log with newest entries at the top. |

Use Git to review curator changes before committing:

```bash
git status --short kb/
git diff -- kb/
```

## 8. Keep the Runtime Boundary Intact

- Use `kb-curator` for author-time KB writes.
- Use `kb-reader` or `wiki-query` for read-only lookups.
- Do not route live fault sessions to `kb-curator`.
- Keep real customer-sensitive values out of committed KB pages unless the repository is private and approved for that data.
- Keep source documents in `kb/.raw/`; write synthesized pages under `kb/wiki/`.
