# kb-wiki

A collection of agent skills for building and maintaining a persistent, compounding knowledge base inside an [Obsidian](https://obsidian.md) vault. Designed to work with GitHub Copilot, OpenCode, or any other AI coding assistant.

**You don't need to know how to code.** You just need to be able to open a chat with your AI assistant and type a sentence. The agent handles everything else.

The wiki is the product. Chat is just the interface. Knowledge compounds like interest.

---

## Getting Started

> This guide assumes you are comfortable using agent harnesses such as OpenCode or GitHub Copilot.

You only need to do this once.

### Step 1 — Get the files onto your computer

Open a chat with your AI assistant (GitHub Copilot, OpenCode, etc.) and say:

> **"Clone or copy the kb-wiki skill package to a folder of my choice and ask me where I want it."**

The agent will ask you where you'd like the folder, then download everything automatically. No git knowledge needed.

### Step 2 — Set up your wiki

Once the files are on your computer, open that folder in your editor and say:

> **"set up a wiki"**

The agent will ask you a few questions about your project and then build out your personal knowledge base — folder structure, index, and everything else.

That's it. You're ready to go.

### Step 3 — Open your project in Obsidian (optional but recommended)

Obsidian gives you a visual interface for your wiki — graph view, backlinks, search, and rich formatting. It's free.

1. Download and install [Obsidian](https://obsidian.md)
2. Open Obsidian and click **Open folder as vault**
3. Navigate to your project folder and select it
4. Obsidian will open your project as a vault, with your knowledge base available inside the `wiki/` folder with full graph view, search, and backlink support

> **Note:** Do not configure Obsidian Sync or any other synchronization service for this vault. Doing so will copy your wiki data to a cloud service that may not be authorized for this content.

You can keep Obsidian open alongside your chat — as the agent adds and updates pages, they appear in Obsidian automatically.

---

## How to Use the Skills

All of these work by just typing a phrase in the chat with your AI assistant. You don't run commands or install anything manually.

| What you want to do | What to say |
|---|---|
| Set up a new wiki | **"set up a wiki"** |
| Add a document, file, or URL to the wiki | **"ingest"** (processes everything in `kb/.raw/`) or **"ingest [filename or URL]"** |
| Ask a question using your wiki | **"wiki query: [your question]"** |
| Build something from wiki knowledge | **"use wiki query to [create a report / draft meeting notes / analyze X]"** |
| Save the current conversation as a wiki page | **"save this"** |
| Check the wiki for broken links or problems | **"lint the wiki"** |

---

## What Each Skill Does

| Skill | What it does |
|-------|-------------|
| `wiki` | Sets up your vault, scaffolds the structure, and routes to other skills |
| `wiki-ingest` | Reads files, URLs, or images and turns them into wiki pages. Drop files into `kb/.raw/` and say **"ingest"** to process them all, or say **"ingest [specific file or URL]"** to target one source. |
| `wiki-query` | Searches the wiki to answer questions or build new things from your accumulated knowledge. Use it to analyze information, generate reports, draft meeting agendas, create summaries, or produce any output grounded in what's in your wiki. |
| `wiki-lint` | Checks the wiki for orphan pages, dead links, and other issues |
| `save` | Files the current chat or insight as a permanent wiki page |
| `obsidian-markdown` | Reference for Obsidian formatting syntax (the agent uses this automatically) |

---

## What Your Wiki Will Look Like

After setup, your project folder will contain:

```
your-project/
├── .raw/               # Drop immutable source documents here to ingest
├── wiki/               # Your AI-generated knowledge base lives here
│   ├── index.md        # Master catalog of all pages
│   ├── hot.md          # Recent context (used automatically by the agent)
│   └── log.md          # Log of all operations
└── AGENTS.md           # Instructions the agent reads automatically
```

Open your project folder in [Obsidian](https://obsidian.md) for a visual graph view of your knowledge base (see Step 3 above), or just work through chat — everything works either way.

**Tip:** Drop files into `.raw/` at any time. When you're ready, say **"ingest"** and the agent will pull everything in that folder into the wiki automatically.

---

## Inspirations

**kb-wiki** was adapted from the [claude-obsidian](https://github.com/agriidaniel/claude-obsidian) project by agricidaniel, which pioneered the concept of using Claude Code as a persistent Obsidian knowledge companion.

The underlying philosophy of using an LLM to build a compounding, cross-referenced knowledge base was inspired by [Andrej Karpathy's LLM KB gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).
