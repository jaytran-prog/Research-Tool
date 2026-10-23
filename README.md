# Research Tool — an AI consulting firm for SMBs

A Claude Code plugin that works like a small consulting firm. It interviews the business owner, picks a fixed-scope deliverable, sends analyst agents to research in parallel, has a critic fact-check every source, and has a partner write a short decision memo.

Unlike a generic deep-research tool, it **questions your question first** and **won't put a number in the memo without a checked source**.

## Install

In Claude Code:

```
/plugin marketplace add jaytran-prog/Research-Tool
/plugin install consult@research-tool
```

Restart Claude Code if the skill doesn't appear right away.

## Use

| Command | What happens |
|---------|--------------|
| `/consult` | **Deep mode:** a short diagnostic interview, a reframed question, then the firm recommends a deliverable |
| `/consult quick competitor-teardown` | **Quick mode:** 5 questions and straight to research |

Depending on your Claude Code version, the command may appear as `/consult:consult`.

### Deliverables
| id | Answers |
|----|---------|
| `competitor-teardown` | Who do I really compete with, how do they win, and where can I beat them? |
| `market-entry-check` | Should I enter this market, location, segment or product line: go, no-go, or test first? |
| `pricing-review` | Are my prices and packages right? |
| `vendor-shortlist` | Which tool or vendor should I pick, and what will it really cost? |

## How it works

```
Owner ─▶ Intake (deep interview or quick form) ─▶ Deliverable template
      ─▶ Analysts in parallel (haiku, web research, sourced evidence ledgers)
      ─▶ Critic (sonnet, opens sources to check claims, ≤1 revision round)
      ─▶ Partner (opus, 2-page decision memo)
      ─▶ engagements/<date>-<slug>/memo.md
```

Each engagement saves its brief, evidence ledgers, critic review and memo in `engagements/` in your working directory, and logs a line to `engagements/log.md` (verdict, evidence strength, searches used) so you can track quality and cost over time.

> **Privacy:** `engagements/` holds real business details. Keep it out of version control. This repo's `.gitignore` already excludes it.

## Repository layout

| Path | Role |
|------|------|
| `.claude-plugin/plugin.json` | Plugin manifest |
| `.claude-plugin/marketplace.json` | Lets others install the plugin from this repo |
| `skills/consult/SKILL.md` | Orchestrator: stages, modes, revision loop |
| `skills/consult/intake.md` | Diagnostic interview guide |
| `skills/consult/deliverables/*.md` | Quick-form questions, workstreams, research budgets, critic checklist, memo template |
| `agents/consult-analyst.md` | Researches one workstream and writes a sourced ledger |
| `agents/consult-critic.md` | Fact-checks ledgers and returns PASS or REVISE |
| `agents/consult-partner.md` | Writes the decision memo |
| `docs/ideas/ai-consulting-firm.md` | Product one-pager: assumptions, MVP scope, what we're not doing |

## Develop locally

Clone the repo and load it as a local plugin:

```
claude --plugin-dir ./Research-Tool
```

### Add a deliverable
Copy a file in `skills/consult/deliverables/`, change its questions, workstreams, budgets, checklist and template, then add its id to the list in `skills/consult/SKILL.md`. Bump `version` in `.claude-plugin/plugin.json` and `marketplace.json` so users get the update.

## Status

Early prototype (v0.1.0). Not yet validated on real engagements. See the assumptions in [docs/ideas/ai-consulting-firm.md](docs/ideas/ai-consulting-firm.md).

## License

MIT
