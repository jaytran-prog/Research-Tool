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

Early prototype (v0.2.0). See the assumptions in [docs/ideas/ai-consulting-firm.md](docs/ideas/ai-consulting-firm.md).

**First test (Oct 2026):** a Competitor Teardown for a fictional specialty coffee shop in Ho Chi Minh City, researched against real competitors.
- The critic caught real errors without any being planted: a branch in the wrong district, two different shops with the same name merged into one, prices from 2016–2021 presented as current, and a competitor website that looked compromised.
- The weak point is data access, not the agents. Small local markets have little current public data, and the best sources (Facebook, Google Maps reviews, delivery apps) are hard for agents to reach.

**Changes in v0.2.0 based on that test:**
- Quick mode requires competitor links, and every engagement asks the owner for a 5-minute evidence pack (links, menu photos, known prices).
- Budgets are 1.5× for local markets, failed page loads don't count against the budget, and the revision round gets a full budget instead of half.
- Analysts prefer sources from the last 24 months, check each branch separately, never merge similarly named businesses, and drop sites that look compromised.
- The critic always produces "safe to use", "must not be used" and "open gaps" lists, and the partner writes only from those lists.
- Memos have a hard limit of 900 words before Sources, and the engagement lead checks every memo before it's delivered.
- The skill falls back to general-purpose agents when the plugin's own agents aren't available.

## License

MIT
