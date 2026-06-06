# Obsidian Templates

Reference for generating `_templates/` files during vault scaffold. The LLM creates these files dynamically based on the vault's actual folders and mode — not from a static folder.

---

## How Templater Works

The [Templater](https://github.com/SilverStrikeV2/obsidian-templater) community plugin auto-populates a new note's frontmatter and body when a user creates a file in Obsidian. It reads template files from a configured folder (set to `_templates/` in this vault) and applies them based on the current folder or a manual trigger.

**The configured folder** (`_templates/`) is excluded from Obsidian's file explorer and graph via `.obsidian/app.json` `userIgnoreFilters`. Users never see it in the vault UI — it only activates when Templater runs.

**To enable:** Settings → Templater → Template folder location → `_templates`

---

## Template File Anatomy

Every file in `_templates/` follows this structure:

```
_templates/[note-type].md
```

Each template has two parts:

1. **Frontmatter** — YAML block with Templater expressions for dynamic fields. Static fields (like `type`, `status`) are hardcoded. Dynamic fields use `<% %>` expressions.
2. **Body** — Section headings with placeholder text in `[brackets]`. Placeholders tell the user (or the LLM) what to put in each section.

**Templater expression reference:**

| Expression | Output |
|---|---|
| `<% tp.file.title %>` | The filename (without `.md`) of the note being created |
| `<% tp.date.now("YYYY-MM-DD") %>` | Today's date in ISO format |
| `<% tp.date.now("YYYY-MM-DDTHH:MM:SS") %>` | Today's datetime (for hot.md) |
| `<% tp.file.folder(true) %>` | The folder path of the note being created |
| `<% tp.file.cursor() %>` | Places the cursor here after template runs |

Only use expressions that Templater supports. Do not invent expressions.

---

## Core Note Type Templates

Generate these for every vault, regardless of mode. File names must match the `type` field value exactly.

### `concept.md`

```markdown
---
type: concept
title: "<% tp.file.title %>"
complexity: intermediate
domain: ""
aliases: []
created: <% tp.date.now("YYYY-MM-DD") %>
updated: <% tp.date.now("YYYY-MM-DD") %>
tags:
  - concept
status: seed
related: []
sources: []
---

# <% tp.file.title %>

## Definition

[What this concept is. Declarative, present tense. One clear paragraph.]

## How It Works

[Mechanism or explanation]

## Why It Matters

[Significance in this domain]

## Examples

-

## Connections

-

## Sources

-
```

### `entity.md`

```markdown
---
type: entity
title: "<% tp.file.title %>"
entity_type: person
role: ""
first_mentioned: "[[]]"
created: <% tp.date.now("YYYY-MM-DD") %>
updated: <% tp.date.now("YYYY-MM-DD") %>
tags:
  - entity
status: seed
related: []
sources: []
---

# <% tp.file.title %>

## Overview

[Who or what this is. One paragraph.]

## Key Facts

-

## Connections

-

## Sources

-
```

### `source.md`

```markdown
---
type: source
title: "<% tp.file.title %>"
source_type: article
author: ""
date_published: <% tp.date.now("YYYY-MM-DD") %>
url: ""
confidence: medium
key_claims:
  - ""
created: <% tp.date.now("YYYY-MM-DD") %>
updated: <% tp.date.now("YYYY-MM-DD") %>
tags:
  - source
status: seed
related: []
sources: []
---

# <% tp.file.title %>

## Summary

[2-3 sentence summary of the source]

## Key Claims

-

## Entities Mentioned

- [[]] —

## Concepts Introduced

- [[]] —

## Notes

```

### `question.md`

```markdown
---
type: question
title: "<% tp.file.title %>"
question: ""
answer_quality: draft
created: <% tp.date.now("YYYY-MM-DD") %>
updated: <% tp.date.now("YYYY-MM-DD") %>
tags:
  - question
status: developing
related: []
sources: []
---

# <% tp.file.title %>

**Question:** [restate the original query]

## Answer

[The synthesized answer, with citations to specific wiki pages]

(Source: [[]])

## Confidence

[draft | solid | definitive] — [why]

## Related Questions

-
```

### `comparison.md`

```markdown
---
type: comparison
title: "<% tp.file.title %>"
subjects:
  - "[[Subject A]]"
  - "[[Subject B]]"
dimensions:
  - "dimension 1"
  - "dimension 2"
verdict: "Replace with one-line conclusion."
created: <% tp.date.now("YYYY-MM-DD") %>
updated: <% tp.date.now("YYYY-MM-DD") %>
tags:
  - comparison
status: seed
related: []
sources: []
---

# <% tp.file.title %>

## Overview

Replace with: why these two things are being compared and what question this answers.

## Comparison

| Dimension | Subject A | Subject B |
|-----------|-----------|-----------|
| | | |
| | | |

## Verdict

Replace with: one clear conclusion — which is better for what use case.

## Sources

-
```

---

## Mode-Specific Templates

For folders created by a specific mode (e.g., `decisions/` from Mode C, `papers/` from Mode E), generate a matching template. The type-specific frontmatter fields come from `references/frontmatter.md`.

**Rules for deriving a custom template:**

1. The filename must match the folder's singular noun — e.g., `decisions/` → `decision.md`, `papers/` → `paper.md`.
2. The `type` frontmatter field must match the filename stem.
3. Add type-specific frontmatter fields appropriate to the content. Use flat YAML only (no nested objects).
4. Body sections should reflect the folder's purpose as described in its `_index-[folder].md`.
5. Always include `## Sources` and `## Connections` as the final two sections.

### Example: `decision.md` (Mode C — Business / Project)

```markdown
---
type: decision
title: "<% tp.file.title %>"
decision_date: <% tp.date.now("YYYY-MM-DD") %>
status: active
decision_makers:
  - ""
alternatives_considered:
  - ""
created: <% tp.date.now("YYYY-MM-DD") %>
updated: <% tp.date.now("YYYY-MM-DD") %>
tags:
  - decision
related: []
sources: []
---

# <% tp.file.title %>

## Context

[What situation prompted this decision. One paragraph.]

## Decision

[What was decided. One clear statement.]

## Rationale

[Why this option was chosen over the alternatives.]

## Alternatives Considered

-

## Consequences

[What changes as a result. Include both positive and negative.]

## Sources

-
```

### Example: `paper.md` (Mode E — Research)

```markdown
---
type: paper
title: "<% tp.file.title %>"
authors:
  - ""
year: ""
venue: ""
url: ""
confidence: medium
key_claims:
  - ""
created: <% tp.date.now("YYYY-MM-DD") %>
updated: <% tp.date.now("YYYY-MM-DD") %>
tags:
  - paper
status: seed
related: []
sources: []
---

# <% tp.file.title %>

## Abstract Summary

[2-3 sentence summary of the paper's argument and contribution]

## Key Claims

-

## Methodology

[How the research was conducted]

## Findings

-

## Critiques / Gaps

-

## Connections

-

## Sources

-
```

### Example: `person.md` (Mode D — Personal / Second Brain)

```markdown
---
type: person
title: "<% tp.file.title %>"
relationship: ""
last_contact: <% tp.date.now("YYYY-MM-DD") %>
created: <% tp.date.now("YYYY-MM-DD") %>
updated: <% tp.date.now("YYYY-MM-DD") %>
tags:
  - person
status: seed
related: []
sources: []
---

# <% tp.file.title %>

## Who They Are

[One paragraph. Role, context, how you know them.]

## Key Notes

-

## Open Threads

-

## History

-
```

---

## What to Generate at Scaffold Time

At scaffold time, generate templates for:

1. **Always** — the five core types: `concept.md`, `entity.md`, `source.md`, `question.md`, `comparison.md`
2. **If the vault has a `decisions/` folder** — add `decision.md`
3. **If the vault has a `papers/` folder** — add `paper.md`
4. **For any other mode-specific content folder** — derive a template using the rules in "Mode-Specific Templates" above, based on the folder's `_index-[folder].md` description

Do not generate templates for `meta/`, `questions/` (already covered by `question.md`), or `comparisons/` (already covered by `comparison.md`).
