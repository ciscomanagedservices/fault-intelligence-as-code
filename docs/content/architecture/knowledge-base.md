# Knowledge and Artifacts

The runtime uses two repository-backed knowledge sources: published intelligence artifacts and the KB wiki vault. Both are read-only during live remediation.

## Intelligence Artifacts

Published fault intelligence lives under `intelligence-artifacts/` and is grouped by alert definition:

```text
intelligence-artifacts/
  AD000002-bgp-neighbor-admin-shutdown-xr/
    FS000002-BGP_NEIGHBOR_ADMIN_SHUTDOWN.yml
    RAW000002-BGP_NEIGHBOR_ADMIN_SHUTDOWN_REPAIR.yml
    RG000002-BGP_NEIGHBOR_ADMIN_SHUTDOWN_GUIDE.md
  AD000003-bgp-max-prefix-adjchange-xr/
    FS000003-BGP_NEIGHBOR_MAX_PREFIX_LIMIT_EXCEEDED.yml
    RAW000003-BGP_NEIGHBOR_MAX_PREFIX_LIMIT_EXCEEDED_REPAIR.yml
    RG000003-bgp-max-prefix-adjchange-guide.md
```

Each artifact group contains a triad:

| Artifact | Purpose |
|----------|---------|
| Fault Signature (FS) | Detection logic and metadata for a fault, including syslog patterns and extracted variables. |
| Repair Action Workflow (RAW) | Machine-consumable validation and remediation steps executed by the `fault-remediation` skill. |
| Remediation Guide (RG) | Human-readable guide that explains symptoms, diagnosis, repair steps, escalation, and post-repair verification. |

`ia-reader` is the live-session access path for these artifacts. It returns the matching FS and RAW content, plus paths to the associated RG, to `network-troubleshooter`.

## Current Published Scenarios

| Alert definition | Scenario | Primary use |
|------------------|----------|-------------|
| `AD000002` | BGP neighbor administrative shutdown on IOS XR | Current simulator default and primary walkthrough scenario. |
| `AD000003` | BGP neighbor maximum-prefix limit exceeded on IOS XR | Additional published scenario for IA authoring and RAW testing. |

The generated artifact index lives at `intelligence-artifacts/index.md` and `intelligence-artifacts/index.json`.

## KB Wiki Vault

The project knowledge base is a wiki vault rooted at `kb/wiki/`, not a flat folder of YAML KB articles. It is organized for operational context and retrieval:

```text
kb/wiki/
  hot.md
  index.md
  overview.md
  business-rules/
  runbooks/
  incidents/
  known-issues/
  concepts/
  entities/
  questions/
  sources/
```

During a live session, `kb-reader` invokes the `wiki-query` skill with a fault-specific question and one of three modes:

| Mode | Use |
|------|-----|
| `quick` | Fast lookup from hot/index pages for low-latency context. |
| `standard` | Default retrieval depth for normal troubleshooting. |
| `deep` | Broader wiki traversal when extra context is worth the cost. |

The KB response supplies business rules and operational constraints, such as whether change approval is required, the response SLA, escalation path, known related incidents, and which pages were read.

## Why a Compiled Markdown KB?

RAG often means chunking raw documents into a vector database and retrieving the top semantic matches. That pattern is useful for large or messy corpora, but it also introduces design and operations choices: chunk size, overlap, embedding model, ranking, filtering, storage, and refresh strategy.

This prototype uses a compiled Markdown KB because the runtime knowledge need is focused. The heavy technical fault logic already lives in intelligence artifacts, so the KB can concentrate on operational context: business rules, escalation paths, maintenance windows, known issues, entities, relationships, and incident history.

The Markdown wiki has several practical advantages for this workflow:

| Advantage | Why it matters |
|-----------|----------------|
| Reviewable | Humans can inspect pages, edit them in Obsidian or a text editor, and review diffs in Git. |
| Versioned | Operational knowledge changes have history, authorship, and rollback paths. |
| Linkable | Wiki links create a lightweight knowledge graph that agents can traverse deliberately. |
| Curated | Agents compile durable facts from source documents instead of treating every source as an independent chunk. |
| Purpose-scoped | The KB stays focused on organizational context while FS/RAW/RG artifacts carry fault-specific technical logic. |

This is still RAG in the broader agentic sense: the agent retrieves external information to improve its context. The retrieval mechanism is simpler because the knowledge has already been curated into a shape the agent can use.

## Author-Time Maintenance

Two curator agents maintain the knowledge sources outside the live fault path:

| Agent | Maintains | Notes |
|-------|-----------|-------|
| `ia-curator` | `ia-drafts/`, `intelligence-artifacts/` | Uses the `ia-*` skill family to research, create, optimize, and publish artifacts. |
| `kb-curator` | `kb/` | Uses wiki skills to ingest sources, save insights, lint links, and maintain indexes. |

Live troubleshooting agents can read from these stores, but they cannot modify them.