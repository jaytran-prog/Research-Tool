# Research Tool — an AI research firm you can run in Claude Code

A Claude Code plugin that works like a small consulting firm, on **any topic**. It sharpens your question first, plans the research, sends analyst agents out in parallel, has a critic fact-check every source, and has a partner write a short, answer-first memo that is honest about what it doesn't know.

How it differs from a generic deep-research tool:
- **It questions your question first.** A short intake turns "tell me about X" into the decision or need behind it.
- **No number reaches the memo without a checked source.** A separate critic opens the sources and throws out what doesn't hold up.
- **It knows when to stop searching.** Gaps that only you can close (a store visit, a call, your own data) become a checklist instead of more wasted searches.
- **One page, answer first.** Hard limit of 900 words before sources.

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
| `/consult` | **Deep mode:** a short interview sharpens your question, then the firm picks a deliverable |
| `/consult quick custom-research Is intermittent fasting better than calorie counting for weight loss?` | **Quick mode, any topic:** a few questions, a research plan to confirm, then research |
| `/consult quick competitor-teardown` | **Quick mode, business fast path** |

Depending on your Claude Code version, the command may appear as `/consult:consult`.

### Deliverables
| id | Answers |
|----|---------|
| `custom-research` | **Any question on any topic**: technology, science, health, policy, law, finance, history, or a personal decision. The firm designs 3–4 research workstreams for your question. |
| `competitor-teardown` | Who do I really compete with, how do they win, and where can I beat them? |
| `market-entry-check` | Should I enter this market, location, segment or product line: go, no-go, or test first? |
| `pricing-review` | Are my prices and packages right? |
| `vendor-shortlist` | Which tool or vendor should I pick, and what will it really cost? |

## How it works

```
You ─▶ Intake (deep interview or quick form) + your evidence pack
    ─▶ Deliverable, or a custom research plan you confirm
    ─▶ Analysts in parallel (haiku, web research, sourced evidence ledgers)
    ─▶ Critic (sonnet): checks sources, tags each gap "researchable" or "only you can close it"
    ─▶ One revision round, only for researchable gaps
    ─▶ Partner (opus): ≤900-word memo + "close the gaps yourself" checklist
    ─▶ engagements/<date>-<slug>/memo.md
```

Each engagement saves its brief, research plan, evidence ledgers, critic reviews and memo in `engagements/` in your working directory, and logs a row to `engagements/log.md` so you can track quality and cost over time.

> **Privacy:** `engagements/` holds your questions and any details you share. Keep it out of version control; this repo's `.gitignore` already excludes it.

> **Health, legal and financial topics:** memos are research, not professional advice, and say so.

## Repository layout

| Path | Role |
|------|------|
| `.claude-plugin/plugin.json` | Plugin manifest |
| `.claude-plugin/marketplace.json` | Lets others install the plugin from this repo |
| `skills/consult/SKILL.md` | Orchestrator: stages, modes, budgets, revision rules |
| `skills/consult/intake.md` | Diagnostic interview guide (business and general probes) |
| `skills/consult/deliverables/custom-research.md` | Any-topic deliverable: planning rules, source guide by topic type, critic checklist, memo template |
| `skills/consult/deliverables/*.md` | Business fast paths: questions, workstreams, budgets, checklist, memo template |
| `agents/consult-analyst.md` | Researches one workstream and writes a sourced ledger |
| `agents/consult-critic.md` | Fact-checks ledgers, tags gaps, returns PASS or REVISE |
| `agents/consult-partner.md` | Writes the memo |
| `docs/ideas/ai-consulting-firm.md` | Product one-pager: assumptions, scope, what we're not doing |

## Develop locally

Clone the repo and load it as a local plugin:

```
claude --plugin-dir ./Research-Tool
```

### Add a fast-path deliverable
Copy a file in `skills/consult/deliverables/`, change its questions, workstreams, budgets, checklist and template, then add it to the Deliverables table in `skills/consult/SKILL.md`. Bump `version` in `.claude-plugin/plugin.json` and `marketplace.json` so users get the update.

## Status and test history

Prototype, v0.3.1.

| Version | Test | What we learned |
|---------|------|-----------------|
| v0.1.0 | Competitor Teardown for a fictional coffee shop in Ho Chi Minh City, against real competitors | The critic caught real errors (wrong district, two shops merged, stale prices, a compromised website). Memo too long (1,595 words). Local data thin. |
| v0.2.0 | Same test, with a client evidence pack and bigger budgets | Memo 891 words; nearby competitors found on the first pass; the client's own numbers made the advice concrete. But about 2× the searches, mostly spent proving current prices aren't online. |
| v0.3.0 | Custom Research on a health question: intermittent fasting vs calorie counting | Strong sources (BMJ 2025 review of 99 trials, Cochrane 2026, a 12-month *Annals* trial). The critic caught a missed key trial, misread figures and an invented "client-named" trial; an analyst corrected the critic's p-value. Memo 883 words, mixed evidence, with a professional-advice line and a do-it-yourself checklist. Problems: fallback agents used the browser, about 12 fetches blocked by journal and guideline sites, one analyst gave up early. |

**v0.3.0 changes:**
- **Any topic:** new `custom-research` deliverable with a confirmed research plan and a source guide per topic type (business, technology, science/health, policy/law, finance, history, personal decisions). Intake, agents and memo are topic-neutral.
- **Stop searching for what isn't online:** the critic tags each gap as researchable or client/field-only, and the revision round only chases researchable gaps (or is skipped).
- **"Close the gaps yourself"** checklist in every memo.
- **Competitor Teardown** now requires competitor prices or menu photos (or an explicit "I don't know") and asks for the client's address.
- Professional-advice line for health, legal and financial memos.

**v0.3.1 changes (from the health test):**
- Fallback agents are told to use only search, fetch, read and write (plus paper search if available), never a browser or terminal.
- Analysts try open copies of blocked pages (PubMed Central, Europe PMC, DOI, PubMed abstract, repositories; guideline PDFs and journal summaries) before giving up, then hand the link to the client.
- Analysts must make at least two attempts before calling something "not found", and can't leave half their budget unused with questions open.
- Nothing may be attributed to the client unless it's in the brief; full text beats abstracts when they disagree.
- The critic checks effort, attribution and version mismatches, and runs a quick check for key studies the analysts missed.
- The lead check counts words with a real tool and checks client-provided labels.

## License

MIT
