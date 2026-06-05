# Export OpenCode Sessions

Export OpenCode sessions to JSON and markdown. Use when: exporting sessions, saving chat history, archiving OpenCode conversations, dumping session logs.

## Step 1: Retrieve Sessions

Run `curl -s http://localhost:4096/session` to get the list of available sessions.

The response is a JSON array of session objects. For each session, extract:
- **Session ID**: `id` field (e.g. `ses_1d9901d18ffeGUOMscGXoZsk22`)
- **Title**: `title` field
- **Last updated**: `time.updated` field (epoch milliseconds — convert to human-readable)
- **Slug**: `slug` field (use as filename prefix)

## Step 2: Present Sessions to User

Display a numbered table of sessions showing ID, title, and last-updated time (formatted as human-readable date/time). Then use the ask-questions tool to ask the user which sessions they want to export. Allow multi-select. Present each session as an option with the title as the label and the ID + last-updated as the description.

## Step 3: Export Each Selected Session

For each selected session:

1. **Fetch messages**: Run `curl -s http://localhost:4096/session/<sessionID>/message` to get the full conversation.

   The response is a JSON array of message objects. Each message has:
   - `info.id` — message ID
   - `info.role` — `"user"` or `"assistant"`
   - `info.time.created` — epoch milliseconds
   - `info.agent` — which agent handled it
   - `parts[]` — array of content parts, each with a `type` field:
     - `"text"` → has `text` field with the content
     - `"tool"` → tool call/result (include in export)
     - `"reasoning"` → model reasoning (include in export)
     - `"step-start"` / `"step-finish"` → agent step boundaries (skip in markdown)

2. **Save pretty-print JSON**: Write the raw JSON response (pretty-printed with 2-space indent) to `sessions/<slug>_<sessionID>.json`.

3. **Generate markdown export**: Create `sessions/<slug>_<sessionID>.md` with the following structure:

   ### Markdown Structure

   ```markdown
   # Session: <title>

   **Session ID:** <id>
   **Slug:** <slug>
   **Agent:** <agent>
   **Model:** <model.id> via <model.providerID>
   **Created:** <time.created as human-readable>
   **Last Updated:** <time.updated as human-readable>
   **Exported:** <current datetime>

   ---

   ## Summary

   <AI-generated 3-5 sentence summary of the conversation: what was discussed, key decisions made, and outcomes>

   ---

   ## Conversation

   <For each message in chronological order:>

   ### <Role> — <timestamp as human-readable>

   <text parts rendered directly>

   <details>
   <summary>Tool: <tool name></summary>

   ```json
   <tool call/result content>
   ```

   </details>

   ---
   ```

   Rules for the markdown conversation section:
   - Role should be **User** or **Assistant**
   - Preserve all code blocks with original language annotations
   - Render `"tool"` parts as collapsed `<details>` blocks
   - Render `"reasoning"` parts as collapsed `<details>` blocks with summary "Reasoning"
   - Skip `"step-start"` and `"step-finish"` parts
   - The summary should capture the key topics, decisions, and outcomes

## Notes

- Create the `sessions/` directory if it doesn't exist
- If a session has already been exported (files exist), ask before overwriting
- Derive the filename slug from the session's `slug` field (e.g. `tidy-planet`)
