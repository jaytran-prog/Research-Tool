# Custom Research

**Answers:** any research question that doesn't fit a fixed deliverable — technology, science, health, policy, law, history, a personal or team decision, a market outside the menu.
**Best for:** questions where someone needs a sourced, honest answer they can act on or explain, not a pile of links.

Unlike the fixed deliverables, the engagement lead **designs the workstreams** for each question, and the client confirms the plan before research starts.

## Quick-form questions
1. **(required)** What's the question, in your own words?
2. **(required)** What will you do with the answer — a decision (what and by when), something to explain or write, or just to understand a topic?
3. What do you already know or believe? Anything you've read that you trust or distrust?
4. Scope: which country/region, time period, and depth (a quick overview or a thorough review)?
5. Memo language, and should research include non-English sources?
6. Optional: links, documents, or data you want the analysts to start from.

## Planning the research (engagement lead)
Before launching analysts, write `plan.md` and show it to the client in a few lines:
- **Topic type** (pick one or two from the table below) and what that means for sources.
- **3–4 workstreams.** Each is one sub-question that can be answered independently. Good splits: facts vs. opinions, for vs. against, options A/B/C, background vs. latest developments, cost vs. benefit. Avoid overlapping workstreams.
- **Per workstream:** id, the questions, source types, and budget.
- **What the answer will look like** (a recommendation, a comparison, an explanation, a timeline).

Ask the client to confirm or adjust in one message. If they don't respond to the plan, proceed with it.

**Base budget per workstream:** 6 searches · 8 fetches. Thorough depth: ×1.5. Max 4 workstreams.

### Source guide by topic type
| Topic type | Prefer | Treat with care | Staleness limit |
|---|---|---|---|
| Business / market | Company sites, filings, official statistics, review platforms, trade press | Vendor marketing, listicles | 24 months for prices and features |
| Technology / software | Official docs, changelogs, release notes, benchmarks with methods, GitHub issues | SEO comparison sites, affiliate reviews | 12 months |
| Science / health | Systematic reviews, meta-analyses, clinical guidelines (WHO, NICE, CDC, national bodies), peer-reviewed papers | Single small studies, preprints (label them), supplement or clinic sites | Prefer the latest guideline; flag anything superseded |
| Policy / law / regulation | Primary texts (laws, regulations, official gazettes), regulators, court decisions; state jurisdiction and effective date | Law-firm blogs (secondary), news summaries | Must be current law; note pending changes |
| Finance / economics | Central banks, statistics offices, filings, IMF/World Bank/OECD data | Promotional content, forecasts without method | 12 months for figures |
| History / culture / society | Academic sources, archives, reputable encyclopedias, major outlets with corrections policies | Unsourced blogs, viral posts | Not time-sensitive; note scholarly disagreement |
| Personal / consumer decision | Manufacturer specs, independent testing, long-term user reports | Sponsored reviews, affiliate lists | 12 months |

If a research or paper-search tool is available in the session (e.g., an academic search connector), analysts on science/health topics should use it.

## Critic checklist
- Each claim is supported by a source of the right type for the topic (see table); secondary sources don't stand in for primary ones on numbers or law.
- Scientific claims distinguish strong evidence (reviews, guidelines, replicated results) from weak (single studies, preprints, expert opinion).
- Where credible sources disagree, the disagreement is reported, not averaged away.
- Jurisdiction, dates and versions are stated where they matter (laws, software, prices, guidelines).
- Health, legal and financial findings are framed as research, not personal professional advice.

## Memo template
Hard limit: **900 words before Sources.**

```markdown
# <Short title of the question>
**Answer:** <the direct answer or recommendation, in 1–2 sentences>
**Evidence strength:** strong / mixed / weak — <why>

## What the evidence shows
<3 key findings, each with sources; label weak evidence as such>

## Where sources disagree
<the main disagreement and why — or "No significant disagreement found">

## What would change this answer
<2–3 assumptions and how to check each>

## Close the gaps yourself
<checklist of things only the client can find out: who to ask, what to check, what to measure>

## Next steps
<2–3 concrete actions>

## Sources
[1] …
```

For health, legal or financial topics, add one line under the Answer: "This is research, not professional advice — confirm with a qualified <doctor/lawyer/financial adviser> before acting."
