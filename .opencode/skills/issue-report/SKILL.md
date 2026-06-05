---
name: issue-report
description: Use when asked to file an issue report or document agent misbehavior or a workflow problem. Writes a structured markdown file to docs/project-docs/issues/. Use when the user says "file an issue", "write up what went wrong", "document this issue", or similar. Do NOT use for "save this session" requests.
---

# Skill: issue-report

File a structured issue report and save it to `docs/project-docs/issues/`.

---

## When to Use

- An agent misbehaved or deviated from expected workflow
- A workflow escalated unexpectedly and the cause should be recorded
- The user says "file an issue", "write up what went wrong", "document this issue", etc.

## When NOT to Use

- Do not trigger on "save this session" — that phrase is not an issue report request.

---

## Step 1: Ask Before Writing

**Before drafting or writing anything**, ask the user:

> "What went wrong? Please describe the issue in your own words — I'll use that
> as the basis for the report."

Wait for the user's response. Use it to populate the Agent Behavior Note and
Root Cause sections. Do not infer the issue solely from session history.

---

## Output Location

All issue reports go to:

```
docs/project-docs/issues/<date>-<short-slug>.md
```

- `<date>`: `YYYY-MM-DD` using today's UTC date
- `<short-slug>`: kebab-case summary of the issue (e.g., `fault-2000002-device-not-found`)

Create `docs/project-docs/issues/` if it does not exist.

---

## File Structure

```markdown
# Issue: <title>

**Date:** YYYY-MM-DD
**Session ID:** <opencode session ID — check the session filename in sessions/ or the sessions list>
**Fault ID / Workflow / Context:** <if applicable>
**Mode:** <e.g., strict / hybrid-reasoning — if applicable>
**Outcome:** <e.g., ESCALATION / RESOLUTION / FAILURE / INCOMPLETE>

---

> **AGENT BEHAVIOR NOTE — DO NOT REPEAT**
>
> <One or more paragraphs describing what the agent did incorrectly in this
> session. Be specific: quote the tool calls or steps taken. State clearly
> what the correct behavior should have been. Use imperative language:
> "The agent should have X, not Y.">
>
> Omit this block if there was no agent misbehavior — the session was simply
> worth documenting for other reasons.

---

## Summary

<2–4 sentences describing what happened and why it is worth recording.>

## Context / Payload

<Reproduce the alert, input, or triggering payload that started the session,
if one exists. Use a code block.>

## Timeline

| Time (UTC) | Event |
|---|---|
| HH:MM | <what happened> |
| ... | ... |

## Evidence Collected

<Bullet list of findings from tool calls, CLI output, or observations.
Be specific: device names, command output snippets, regex matches, etc.>

## Root Cause

<Why did the workflow end the way it did? What condition caused the
deviation or escalation?>

## Possible Causes

<Numbered list of hypotheses, most likely first.>

## Recommended Actions

<Numbered list of follow-up tasks — immediate, short-term, and process/docs.
Reference BACKLOG.md if an item should be tracked there.>

## Notifications Sent

<List any Webex or other external notifications sent during the session,
with message IDs if available.>
```

---

## Rules

1. **Always include the "AGENT BEHAVIOR NOTE" block** if the session involved
   agent misbehavior — even minor deviations. This is the primary value of the
   file for future training and debugging.

2. **Be specific in the note.** Name the exact tool calls made incorrectly,
   quote the reasoning that was wrong, and state the correct behavior
   unambiguously.

3. **Do not editorialize.** Write factually. The note is read by engineers
   improving the agent, not by end users.

4. **Use today's UTC date** for the filename and the `Date:` field.

5. **Do not omit sections.** If a section has no content (e.g., no Webex
   notifications were sent), write "none" — do not delete the heading.

6. **Update `docs/project-docs/issues/` only.** Do not write to `context/`,
   `output/`, or any other folder.

7. After writing the file, confirm the path to the user.

---

## Example Filenames

```
docs/project-docs/issues/2026-05-16-fault-2000002-device-not-found.md
docs/project-docs/issues/2026-05-16-raw-step3-unexpected-output.md
docs/project-docs/issues/2026-05-16-webex-approval-timeout.md
```
