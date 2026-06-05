---
name: golden-rules
description: Manage agent-specific Golden Rules stored directly in `.opencode/agents/*.md`. Use when the user asks to add, view, edit, remove, or audit golden rules for agents. Golden rules are per-agent invariants; there are no global golden rules.
license: Apache-2.0
compatibility: opencode
metadata:
  domain: agent-governance
  workflow: agent-prompt-maintenance
---

# Skill: golden-rules

## Tier 0

Manage **agent-specific Golden Rules** embedded in `.opencode/agents/*.md`.
Trigger on: "golden rules", "add a golden rule", "view golden rules", "edit GR-###", "remove golden rule".
Never create global golden rules. Never store golden rules only in the KB, config, or a separate policy file.
Use this skill only for explicit user-initiated agent maintenance, not during live fault execution.

---

## Tier 1

### Core model

Golden rules are stored in each agent file under this exact managed block:

```markdown
## Golden Rules

Golden rules are agent-specific invariants managed by the `golden-rules` skill.
They override ordinary workflow guidance in this agent file. If a requested action
conflicts with a golden rule, follow the golden rule and report the conflict.

<!-- GOLDEN_RULES_START -->
- **GR-001:** Example rule text.
<!-- GOLDEN_RULES_END -->
```

Rules use globally unique IDs of the form `GR-001`, `GR-002`, ... across all agent files.
If the same rule applies to multiple agents, use the same `GR-###` ID in each selected agent file.

### Agent inventory

When operating in this repository, discover agent files from:

```text
.opencode/agents/*.md
```

Use the filename stem as the agent name, for example:

```text
.opencode/agents/network-troubleshooter.md -> network-troubleshooter
```

### Before any mutation

1. Read all `.opencode/agents/*.md` files.
2. Parse every managed Golden Rules block.
3. Build an in-memory index:
   - `agent_name`
   - `agent_path`
   - `rule_id`
   - `rule_text`
4. Run the contradiction check described below.
5. Confirm the intended operation with the user when the operation is destructive (`edit` or `remove`).

### Add rule(s)

1. Ask the user for the rule text(s) if not already provided.
   - Accept one rule per line.
   - Preserve user wording unless a safety or clarity issue requires a suggested rewrite.
2. Run a contradiction check against all existing golden rules.
3. Assign the next available global `GR-###` IDs by scanning all existing IDs and incrementing the highest suffix.
4. Present a checkbox-style selection of agents to apply the rule(s) to.
   - Use the `question` tool with `multiple: true` when available.
   - If checkbox UI is unavailable, present a numbered list and ask the user to reply with numbers or agent names.
5. Ensure each selected agent has a `## Golden Rules` section with managed markers.
6. Insert each new rule inside the selected agents' managed blocks, before `<!-- GOLDEN_RULES_END -->`.
7. Report the IDs, target agents, and file paths changed.

### View rules

Scan all agent files and print rules grouped by agent:

```markdown
### network-troubleshooter
- **GR-001:** Create the session log before any network-affecting action.

### kb-reader
- No golden rules defined.
```

Do not use a matrix view unless the user explicitly asks for one.

### Edit rule

1. Show all existing rules grouped by agent.
2. Ask which `GR-###` to edit if not specified.
3. Show all agents currently carrying that ID.
4. Ask for the replacement text.
5. Run a contradiction check using the replacement text.
6. Ask whether to apply the edit to:
   - all agents carrying that rule ID, or
   - selected agents only.
7. Replace only the text after `:**` for the chosen ID. Keep the same `GR-###` ID.
8. Report changed files.

### Remove rule

1. Show all existing rules grouped by agent.
2. Ask which `GR-###` to remove if not specified.
3. Show all agents currently carrying that ID.
4. Ask whether to remove it from:
   - all agents carrying that rule ID, or
   - selected agents only.
5. Remove the matching lines from selected managed blocks.
6. If a managed block becomes empty, leave the markers and insert:

```markdown
_No golden rules defined yet._
```

7. Report changed files.

---

## Tier 2

### Contradiction check

Before adding or editing a golden rule, compare the proposed text against:

1. Existing golden rules in all agent files.
2. The target agent's Hard Constraints section.
3. The target agent's tool/permission frontmatter.
4. Project architecture constraints in `AGENTS.md` if relevant.

Flag possible contradictions before writing. Examples:

| Proposed rule | Potential contradiction |
|---|---|
| "kb-reader may update wiki pages" | `kb-reader` is explicitly read-only and must recommend `kb-curator` for writes. |
| "network-troubleshooter may invoke kb-curator" | Project architecture forbids live fault sessions from reaching vault writes. |
| "Always auto-approve config changes" | Existing approval flow may require Webex/human review or explicit auto-approve warning. |
| "Use raw device IPs for RADKit calls" | Existing instructions require RADKit inventory hostnames. |

If the contradiction is clear and severe, do not mutate files until the user confirms they want to change the underlying constraint as well. If the issue is only wording ambiguity, propose a safer rewrite and ask for confirmation.

### Section creation rules

If an agent lacks a `## Golden Rules` section, insert it immediately after the first Hard Constraints section. Recognize these headings:

```text
## Hard Constraints
## Hard Constraints (Allow-List)
```

Insert before the next `---` separator after that section when possible. If no Hard Constraints section exists, insert immediately after the opening identity paragraph and first `---` separator.

### Marker rules

- Only mutate content between `<!-- GOLDEN_RULES_START -->` and `<!-- GOLDEN_RULES_END -->`.
- If a `## Golden Rules` section exists without markers, add markers around the existing list before editing.
- Preserve all non-golden-rule content exactly.
- Preserve CRLF/LF style where practical.

### ID rules

- Treat `GR-001` and `gr-001` as the same ID, but write IDs uppercase.
- Never reuse an ID that appears anywhere in `.opencode/agents/*.md`, even if it was removed from one agent but still exists in another.
- If the user explicitly wants the same rule applied to additional agents, reuse the existing ID.
- If the text differs materially, assign a new ID.

### Permission limitations

This skill requires file edit capability for add/edit/remove operations. If invoked by an agent that has read-only permissions, it may still perform `view`, but it must refuse mutations and tell the user to invoke a write-enabled primary agent.

---

## Common failure modes

- **Creating global golden rules:** Do not write a global policy file as the authoritative source. Golden rules live in individual agent files.
- **Editing outside markers:** Never rewrite unrelated prompt text while adding/removing rules.
- **Duplicate IDs:** Always scan every agent file before assigning IDs.
- **Rule drift across agents:** When editing a shared `GR-###`, ask whether to update all agents carrying that ID.
- **Bypassing contradictions:** Always flag conflicts before writing, especially when a rule weakens read-only boundaries, live-network safety, or curator separation.
- **Using the skill during a fault session:** Golden-rule management is maintenance work. Do not invoke it as part of live troubleshooting.
