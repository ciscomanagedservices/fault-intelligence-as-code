# Best Practices

## General

- Start with a clear RG before generating FS and RAW.
- Keep linked-set IDs aligned: `AD000010`, `FS000010`, `RG000010`, `RAW000010`.
- Use semantic versions on YAML artifacts.
- Keep tags lowercase and hyphenated.
- Capture assumptions and review items in companion `.analysis.md` files.

## Remediation Guides

- Write for a network engineer first: plain English, concrete commands, realistic examples.
- Include one Triggering Event subsection per unique message ID or event source.
- Use placeholders such as `{{ neighbor_ip }}` for values that vary by fault instance.
- Include escalation criteria and evidence to collect.
- Include post-repair verification so the RAW can derive a final success check.

## Fault Signatures

- Anchor regex patterns to the exact mnemonic and important structure.
- Avoid broad patterns that match unrelated operational messages.
- Extract variables rather than hardcoding device-specific values.
- Include platform-specific variants when syslog formats differ.
- Include `clear_event` when a fault can self-clear.

## Repair Action Workflows

- Keep validation actions in `validation`; do not hide checks inside repair actions.
- Include default branches in `action_select` for unexpected outputs.
- Use `escalate` for permanent handoff and `custom_action` for external work after which the workflow resumes.
- Do not use `exec_cli` for `show` commands. Use `eval_cli` for evaluated checks and `escalate.data.commands` for evidence collection.
- Do not include `configure terminal`, `commit`, `end`, or `write memory` in `config_cli.commands[]`; the executor handles mode bookends.

## Publishing

- Publish from `ia-drafts/` through `ia-publish`; do not hand-copy individual files unless repairing a failed publish.
- Publish Markdown RG files with the linked YAML artifacts.
- Regenerate `intelligence-artifacts/index.json` after publishing so readers and explorer views stay current.