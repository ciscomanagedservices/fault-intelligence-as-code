---
name: save
description: >
  Save the current conversation, answer, or insight into the Obsidian wiki vault as a
  structured note. Analyzes the chat, determines the right note type, creates frontmatter,
  files it in the correct wiki folder, and updates index, log, and hot cache.
  Triggers on: "save this", "save that answer", "/save", "file this",
  "save to wiki", "save this session", "file this conversation", "keep this",
  "save this analysis", "add this to the wiki".
---

# save: File Conversations Into the Wiki

Good answers and insights shouldn't disappear into chat history. This skill takes what was just discussed and files it as a permanent wiki page.

The wiki compounds. Save often.

> **Vault location for this project:** The vault root is `kb/`. All vault paths in this skill (`wiki/`, `wiki/questions/`, `wiki/concepts/`, etc.) must be prefixed with `kb/` when accessed from the workspace root. For example, `wiki/questions/` → `kb/wiki/questions/`.

> **Cross-project awareness:** This skill file lives in the kb-wiki skill directory. All vault paths (`wiki/`, `wiki/questions/`, `wiki/concepts/`, etc.) are relative to the **vault root** (`kb/`), NOT the workspace root or this skill directory. Identify the workspace folder before writing any files.

---

## Note Type Decision

Use **two-stage routing**. Custom folders take priority over defaults.

### Stage 1 — Custom Folders

Before using the default type table, discover whether the vault has custom content folders:
1. Read the project's `AGENTS.md` (or `CLAUDE.md`, `WIKI.md`, or equivalent) for any folder definitions and their described purpose.
2. Scan `wiki/*/` directories — any folder with an `_index-*.md` file is a custom content folder.
3. If the conversation content clearly matches a custom folder's described purpose (e.g., mentoring notes → `wiki/mentoring/`, impact data → `wiki/impact/`), file the note there.
4. Check the folder's `_index-*.md` if you are unsure whether the content fits.

If a custom folder matches, skip Stage 2 and proceed with the Save Workflow.

### Stage 2 — Default Types (fallback)

Use only when Stage 1 found no matching custom folder:

| Type | Folder | Use when |
|------|--------|----------|
| synthesis | wiki/questions/ | Multi-step analysis, comparison, or answer to a specific question |
| concept | wiki/concepts/ | Explaining or defining an idea, pattern, or framework |
| source | wiki/sources/ | Summary of external material discussed in the session |
| decision | wiki/meta/ | Architectural, project, or strategic decision that was made |
| session | wiki/meta/ | Full session summary: captures everything discussed |

If the user specifies a type, use that. If not, pick the best fit. When in doubt, use `synthesis`.

---

## Save Workflow

1. **Scan** the current conversation. Identify the most valuable content to preserve.
2. **Ask** (if not already named): "What should I call this note?" Keep the name short and descriptive.
3. **Determine** note type using two-stage routing: check custom folders first (Stage 1), then the default type table (Stage 2).
4. **Extract** all relevant content from the conversation. Rewrite it in declarative present tense (not "the user asked" but the actual content itself).
5. **Create** the note in the correct folder with full frontmatter.
6. **Collect links**: identify any wiki pages mentioned in the conversation. Add them to `related` in frontmatter.
7. **Update** `wiki/index.md`. Add the new entry at the top of the relevant section.
8. **Append** to `wiki/log.md`. New entry at the TOP:
   ```
   ## [YYYY-MM-DD] save | Note Title
   - Type: [note type]
   - Location: wiki/[folder]/Note Title.md
   - From: conversation on [brief topic description]
   ```
9. **Update** `wiki/hot.md` to reflect the new addition.
10. **Confirm**: "Saved as [[Note Title]] in wiki/[folder]/."

---

## Frontmatter Template

```yaml
---
type: <synthesis|concept|source|decision|session>
title: "Note Title"
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags:
  - <relevant-tag>
status: developing
related:
  - "[[Any Wiki Page Mentioned]]"
sources:
  - "[[.raw/source-if-applicable.md]]"
---
```

For `question` type, add:
```yaml
question: "The original query as asked."
answer_quality: solid
```

For `decision` type, add:
```yaml
decision_date: YYYY-MM-DD
status: active
```

---

## Writing Style

- Declarative, present tense. Write the knowledge, not the conversation.
- Not: "The user asked about X and Claude explained..."
- Yes: "X works by doing Y. The key insight is Z."
- Include all relevant context. Future sessions should be able to read this page cold.
- Link every mentioned concept, entity, or wiki page with wikilinks.
- Cite sources where applicable: `(Source: [[Page]])`.

---

## What to Save vs. Skip

Save:
- Non-obvious insights or synthesis
- Decisions with rationale
- Analyses that took significant effort
- Comparisons that are likely to be referenced again
- Research findings

Skip:
- Mechanical Q&A (lookup questions with obvious answers)
- Setup steps already documented elsewhere
- Temporary debugging sessions with no lasting insight
- Anything already in the wiki

If it's already in the wiki, update the existing page instead of creating a duplicate.
