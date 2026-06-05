# Quickstart

Start here when you want to run, adapt, or extend the demo. The quickstarts are separated by job so the first path stays simple and the lab/authoring paths do not distract from it.

## Before You Begin

This project is documented as an OpenCode-first workflow:

1. Install OpenCode.
2. Fork this repository so you can keep your own changes.
3. Clone your fork to your workstation or lab host.
4. Open a terminal in the cloned folder.
5. Start OpenCode with `opencode web` for the browser UI or `opencode` for the terminal UI.
6. Use the prompt shown in the quickstart with the specified agent.

Use **Builder** when a quickstart asks you to change files, customize settings, or run setup checks. Use the named project agents for specialized workflows: `network-troubleshooter`, `ia-curator`, and `kb-curator`.

| Goal | Quickstart |
|------|------------|
| Run the easiest local agent test with simulated device responses | [Local Agent Prompt Test](local-agent-test.md) |
| Connect OpenCode, RADKit MCP, Splunk, Webex, and lab devices | [Lab Environment](lab-environment.md) |
| Create FS, RAW, RG, and RAW test artifacts | [Artifact Authoring](artifact-authoring.md) |
| Query, ingest, save, and lint KB vault content | [Knowledge Base Curator](kb-curator.md) |

Use [Local Agent Prompt Test](local-agent-test.md) first. It only needs OpenCode and the checked-in test bundles.
