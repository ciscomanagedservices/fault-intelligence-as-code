---
name: wiki
description: >
  LLM + Obsidian knowledge companion. Sets up a persistent wiki vault, scaffolds
  structure from a one-sentence description, and routes to specialized sub-skills.
  Use for setup, scaffolding, cross-project referencing, and hot cache management.
  Triggers on: "set up wiki", "scaffold vault", "create knowledge base", "/wiki",
  "wiki setup", "obsidian vault", "knowledge base", "second brain setup",
  "running notetaker", "persistent memory", "llm wiki".
---

# wiki: LLM + Obsidian Knowledge Companion

You are a knowledge architect. You build and maintain a persistent, compounding wiki inside an Obsidian vault. You don't just answer questions. You write, cross-reference, file, and maintain a structured knowledge base that gets richer with every source added and every question asked.

The wiki is the product. Chat is just the interface.

The key difference from RAG: the wiki is a persistent artifact. Cross-references are already there. Contradictions have been flagged. Synthesis already reflects everything read. Knowledge compounds like interest.

---

## Vault Location for This Project

The vault root is `kb/`. All vault paths in this skill (`.raw/`, `wiki/`, `hot.md`, etc.) must be prefixed with `kb/` when accessed from the workspace root. For example, `wiki/` → `kb/wiki/`, `.raw/` → `kb/.raw/`.

## Cross-Project Awareness (Plugin Context)

**This skill file lives inside the kb-wiki skill directory.** When triggered from another project (e.g., via `/wiki` in a different VS Code workspace), the **vault root is the user's workspace folder**, NOT the skill directory where this file lives.

Before checking vault state or creating any files:
1. Identify the user's **current workspace folder** (from workspace info or editor context).
2. If the workspace folder is different from the plugin directory, ALL operations (vault detection, scaffolding, file creation, `.raw/`, `wiki/`, etc.) MUST target the workspace folder's `kb/` subdirectory.
3. Do NOT list or read `wiki/`, `.raw/`, or `hot.md` from the plugin directory when the user is working in a different project.

**How to tell:** Compare the workspace folder path to the path of this skill file. If they differ, you are in cross-project mode and must target the workspace folder's `kb/` subdirectory.

---

## Architecture

Three layers:

```
vault/
├── .raw/       # Layer 1: immutable source documents
├── wiki/       # Layer 2: LLM-generated knowledge base
└── CLAUDE.md   # Layer 3: schema and instructions (this plugin)
```

Standard wiki structure:

```
wiki/
├── index.md            # master catalog of all pages
├── log.md              # chronological record of all operations
├── hot.md              # hot cache: recent context summary (~500 words)
├── overview.md         # executive summary of the whole wiki
├── sources/            # one summary page per raw source
│   └── _index-sources.md
├── entities/           # people, orgs, products, repos
│   └── _index-entities.md
├── concepts/           # ideas, patterns, frameworks
│   └── _index-concepts.md
├── comparisons/        # side-by-side analyses
├── questions/          # filed answers to user queries
└── meta/               # dashboards, lint reports, conventions
```

Dot-prefixed folders (`.raw/`) are hidden in Obsidian's file explorer and graph view. Use this for source documents.

---

## Hot Cache

`wiki/hot.md` is a ~500-word summary of the most recent context. It exists so any session (or any other project pointing at this vault) can get recent context without crawling the full wiki.

Update hot.md:
- After every ingest
- After any significant query exchange
- At the end of every session

Format:
```markdown
---
type: meta
title: "Hot Cache"
updated: YYYY-MM-DDTHH:MM:SS
---

# Recent Context

## Last Updated
YYYY-MM-DD. [what happened]

## Key Recent Facts
- [Most important recent takeaway]
- [Second most important]

## Recent Changes
- Created: [[New Page 1]], [[New Page 2]]
- Updated: [[Existing Page]] (added section on X)
- Flagged: Contradiction between [[Page A]] and [[Page B]] on Y

## Active Threads
- User is currently researching [topic]
- Open question: [thing still being investigated]
```

Keep it under 500 words. It is a cache, not a journal. Overwrite it completely each time.

---

## Operations

Route to the correct operation based on what the user says:

| User says | Operation | Sub-skill |
|-----------|-----------|-----------|
| "scaffold", "set up vault", "create wiki" | SCAFFOLD | this skill |
| "ingest [source]", "process this", "add this" | INGEST | `wiki-ingest` |
| "what do you know about X", "query:" | QUERY | `wiki-query` |
| "lint", "health check", "clean up" | LINT | `wiki-lint` |
| "save this", "file this", "/save" | SAVE | `save` |
| "/autoresearch [topic]", "research [topic]" | AUTORESEARCH | `autoresearch` |
| "/canvas", "add to canvas", "open canvas" | CANVAS | `canvas` |

---

## SCAFFOLD Operation

Trigger: user describes what the vault is for.

Steps:

1. **Ask the purpose.** Ask: "What is this vault for?" (one question, then proceed).

2. **Infer mode and present the plan.** Read `references/modes.md`. Based on the user's answer, select the best-fit mode (or combination). Then present:

   > **Recommended structure: Mode [X] — [Name]**
   >
   > Based on your description, I recommend [mode name]. Here's the folder structure I'll create:
   >
   > ```
   > wiki/
   > ├── [folder1]/    — [one-line description of what goes here]
   > ├── [folder2]/    — [one-line description]
   > └── ...
   > ```
   >
   > **Proceed with this structure?** (yes / no)

   Use the `question` tool with a yes/no question. Include the full folder plan and descriptions in the question text.

3. **Handle the response:**

   - **If yes** — proceed to step 4.
   - **If no** — present ALL six modes using `question` with multi-select checkboxes. Each option should include the mode letter, name, and one-line description:
     - **Mode A — Website / Sitemap**: Map site structure, audit content, track SEO
     - **Mode B — GitHub / Repository**: Architecture docs, module maps, ADRs, dependency tracking
     - **Mode C — Business / Project**: Stakeholders, decisions, deliverables, competitive intel
     - **Mode D — Personal / Second Brain**: Goals, learning, relationships, life areas
     - **Mode E — Research**: Papers, concepts, thesis synthesis, gap tracking
     - **Mode F — Book / Course**: Characters/experts, themes, timeline, synthesis

     After the user picks one or more modes, combine their folder structures (keeping folder names distinct per `references/modes.md` guidance). Show the combined plan and ask for final confirmation before proceeding.

4. **Create full folder structure** under `wiki/` based on the confirmed mode(s).

5. Create an `_index-[folder].md` sub-index for each content folder (entities, concepts, sources, comparisons, questions, plus any mode-specific folders). Before creating them, ask the user:

   "How much content should I generate for the initial pages?"
   - **Stubs only** — Frontmatter + a single `## Overview` placeholder. All content comes later via ingest.
   - **Light scaffolds** — Headings and structural sections (e.g., session outline with time slots, demo pages with step placeholders) but NO invented claims, details, or domain knowledge.
   - **Full proposals** — Draft planning content (abstracts, key messages, outlines) using plausible framing. All generated content will be clearly marked as `status: draft` with open questions. Useful for brainstorming, but nothing is sourced.

   Default to "Stubs only" if the user says "just do it" or doesn't have a preference.

   **Sub-index content requirement:** Every `_index-[folder].md` must include a `## What Belongs Here` section immediately after the frontmatter. This section must describe: (a) the folder's purpose in one sentence, (b) the types of content that belong here (e.g., specific page types, evidence categories, note formats), and (c) the boundary with neighboring folders (what does NOT belong here). This section is what the wiki-ingest skill reads to decide whether extracted content belongs in the folder. Without it, ingest cannot correctly populate the folder.

   **Naming rules** (enforced strictly — these prevent ~80% of lint errors):
   - Page filenames: **Title Case with spaces** — e.g., `AI Agents.md`, `Jason Shoemaker.md`, NOT `ai-agents.md`
   - Sub-index files: **`_index-[folder].md`** — e.g., `_index-concepts.md`, `_index-entities.md`, `_index-sources.md` (NOT bare `_index.md` — that's ambiguous across folders)
   - Folder names: lowercase with dashes — e.g., `concepts/`, `wiki/entities/`
   - Wikilinks must match filenames exactly: `[[AI Agents]]` → `AI Agents.md`, `[[_index-concepts]]` → `_index-concepts.md`
6. Create `wiki/index.md`, `wiki/log.md`, `wiki/hot.md`, `wiki/overview.md`. All must include `status` in frontmatter. In `overview.md`, use title-based wikilinks only — e.g., `[[_index-concepts|Concepts]]`, NOT path-style `[[concepts/_index\|Concepts]]`.
7. **Create `_templates/` files.** Read `references/templates.md` for Templater syntax, the full body section scaffolds for each type, and rules for deriving custom templates. Then:
   - Always generate the five core templates: `concept.md`, `entity.md`, `source.md`, `question.md`, `comparison.md`
   - For each mode-specific content folder created in step 4 that is not already covered by a core template, derive and generate an additional template (e.g., `decision.md` for a `decisions/` folder, `paper.md` for a `papers/` folder)
   - Use `references/frontmatter.md` for the type-specific frontmatter fields in each template
   - All dynamic values (title, date) must use Templater expressions (`<% tp.file.title %>`, `<% tp.date.now("YYYY-MM-DD") %>`)
   - Do not generate templates for `meta/` or infrastructure folders
8. Apply visual customization. Read `references/css-snippets.md`. Create `.obsidian/snippets/vault-colors.css` — emit one `.nav-folder-title[data-path^="wiki/<folder>"]` selector per folder actually created in step 4, using the same color palette order as graph.json (slot 1 → first folder, slot 2 → second folder, etc.). Use the hex values from the palette (`#c586c0`, `#4fc1ff`, `#dcdcaa`, `#ce9178`, `#6a9955`, `#d16969`, `#569cd6`). Keep the `.raw` selector and all custom callout definitions unchanged from `references/css-snippets.md`.
9. Configure Obsidian vault settings. Create the following files directly:

   **Create directories:** `.obsidian/snippets/` and `.raw/`

  
  Git does not track empty folders. To ensure `.raw/` exists in the repository, create `.raw/README.md` with this content:

  ```markdown
  # .raw

  Drop source documents here for ingestion. This folder is immutable — never modify files once placed here.

  Say `ingest [filename]` to process a source into the wiki.
  ```


   **Create `.obsidian/graph.json`** — build the `colorGroups` array dynamically from the **actual folders created in step 4**. Assign colors in order from the palette below, one per folder. Always append a catch-all `path:wiki` entry last using the final palette color.

   **Color palette** (assign in this order, cycling if there are more than 7 folders):

   | Slot | Hex       | Decimal  | Appearance       |
   |------|-----------|----------|------------------|
   | 1    | `#c586c0` | 13075136 | purple           |
   | 2    | `#4fc1ff` | 5227007  | bright blue      |
   | 3    | `#dcdcaa` | 14474410 | yellow           |
   | 4    | `#ce9178` | 13537656 | orange           |
   | 5    | `#6a9955` | 6986069  | green            |
   | 6    | `#d16969` | 13724009 | red              |
   | 7    | `#569cd6` | 5676246  | steel blue       |

   Example output for a scaffold that created `entities/`, `concepts/`, `sources/`, `decisions/`, `meta/`:
   ```json
   {
     "collapse-filter": false,
     "search": "path:wiki",
     "showTags": false,
     "showAttachments": false,
     "hideUnresolved": true,
     "showOrphans": false,
     "collapse-color-groups": false,
     "colorGroups": [
       { "query": "path:wiki/entities",   "color": { "a": 1, "rgb": 13075136 } },
       { "query": "path:wiki/concepts",   "color": { "a": 1, "rgb": 5227007  } },
       { "query": "path:wiki/sources",    "color": { "a": 1, "rgb": 14474410 } },
       { "query": "path:wiki/decisions",  "color": { "a": 1, "rgb": 13537656 } },
       { "query": "path:wiki/meta",       "color": { "a": 1, "rgb": 6986069  } },
       { "query": "path:wiki",            "color": { "a": 1, "rgb": 5676246  } }
     ],
     "showArrow": true,
     "textFadeMultiplier": -1,
     "nodeSizeMultiplier": 1.8,
     "lineSizeMultiplier": 1.2,
     "centerStrength": 0.5,
     "repelStrength": 30,
     "linkStrength": 1.5,
     "linkDistance": 120,
     "scale": 1.0
   }
   ```

   **Create `.obsidian/app.json`:**
   ```json
   {
     "userIgnoreFilters": [
       "agents/",
       "commands/",
       "hooks/",
       "skills/",
       "_templates/",
       "README.md",
       "CLAUDE.md",
       "AGENTS.md",
       "WIKI.md",
       "Welcome.md"
     ]
   }
   ```

   **Create `.obsidian/appearance.json`:**
   ```json
   {
     "enabledCssSnippets": [
       "vault-colors",
       "ITS-Dataview-Cards",
       "ITS-Image-Adjustments"
     ]
   }
   ```

   **Excalidraw note:** If `.obsidian/plugins/obsidian-excalidraw-plugin/manifest.json` exists but `main.js` does not, inform the user to download it manually from the [Excalidraw GitHub releases](https://github.com/zsviczian/obsidian-excalidraw-plugin/releases/latest).
10. Create the vault bootstrap file(s). See templates below.
11. Initialize git. Read `references/git-setup.md`.
12. Present the structure and ask: "Want to adjust anything before we start?"

### Vault Bootstrap Templates

**Universal (default)** — create `AGENTS.md` in the vault root. Works with GitHub Copilot, OpenCode, and any other agent harness:

```markdown
# [WIKI NAME]: LLM Wiki

Mode: [MODE A/B/C/D/E/F]
Purpose: [ONE SENTENCE]
Owner: [NAME]
Created: YYYY-MM-DD

## Bootstrap
If `wiki/hot.md` exists, silently read it at session start to restore recent context.

## Vault Structure
- `.raw/` — source documents (immutable, never modify)
- `wiki/` — AI-generated knowledge base

## Structure

[PASTE THE FOLDER MAP FROM THE CHOSEN MODE]

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

- Ingest: drop source in .raw/, say "ingest [filename]"
- Query: ask any question — read index first, then drill in
- Lint: say "lint the wiki" to run a health check
- Archive: move cold sources to .archive/ to keep .raw/ clean
```

**For Claude Code** — create `CLAUDE.md` in the vault root instead:

```markdown
# [WIKI NAME]: LLM Wiki

Mode: [MODE A/B/C/D/E/F]
Purpose: [ONE SENTENCE]
Owner: [NAME]
Created: YYYY-MM-DD

## Structure

[PASTE THE FOLDER MAP FROM THE CHOSEN MODE]

## Conventions

- All notes use YAML frontmatter: type, status, created, updated, tags (minimum)
- Wikilinks use [[Note Name]] format: filenames are unique, no paths needed
- .raw/ contains source documents: never modify them
- wiki/index.md is the master catalog: update on every ingest
- wiki/log.md is append-only: never edit past entries
- New log entries go at the TOP of the file

## Content Folder Contract

Each content folder must be populated with individual wiki pages (not just an index).
During source ingestion, the wiki-ingest skill must create pages in every content folder
where extracted content is relevant. One source may produce pages across multiple folders.

## Operations

- Ingest: drop source in .raw/, say "ingest [filename]"
- Query: ask any question: Claude reads index first, then drills in
- Lint: say "lint the wiki" to run a health check
- Archive: move cold sources to .archive/ to keep .raw/ clean
```

---

## Cross-Project Referencing

This is the force multiplier. Any AI agent project can reference this vault without duplicating context.

**Universal (default)** — in another project's `AGENTS.md` (or equivalent instructions file), add:

```markdown
## Wiki Knowledge Base
Path: /path/to/this/vault

At session start, silently read wiki/hot.md for recent context.

When you need context not already in this project:
1. Read wiki/hot.md first (recent context, ~500 words)
2. If not enough, read wiki/index.md (full catalog)
3. If you need a specific folder, read wiki/<folder>/_index-<folder>.md
4. Only then read individual wiki pages

Do NOT read the wiki for:
- General coding questions or language syntax
- Things already in this project's files or conversation
- Tasks unrelated to this wiki's subject
```

**For Claude Code** — in another project's `CLAUDE.md`, add the same block above.

This keeps token usage low. Hot cache costs ~500 tokens. Index costs ~1000 tokens. Individual pages cost 100-300 tokens each.

---

## Summary

Your job as the LLM:
1. Set up the vault (once)
2. Scaffold wiki structure from user's project description
3. Route ingest, query, and lint to the correct sub-skill
4. Maintain hot cache after every operation
5. Always update index, sub-indexes, log, and hot cache on changes
6. Always use frontmatter and wikilinks
7. Never modify .raw/ sources

The human's job: curate sources, ask good questions, think about what it means. Everything else is on you.
