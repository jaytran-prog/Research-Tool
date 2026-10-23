# AI Consulting Firm for SMBs

## Problem Statement
How might we give SMB owners decision-ready answers on markets, competitors, products and tools — the output of a consulting team — without the cost, the wait, or the risk of confidently wrong AI research?

## Recommended Direction
One pipeline that copies how a real consulting firm works, built from three ideas:

1. **Diagnose before researching (Direction B).** An intake interview reframes the owner's question before any research starts. Owners often ask the wrong question; generic deep-research tools answer whatever is typed.
2. **Productized deliverables (Direction C).** A fixed menu — Competitor Teardown, Market Entry Check, Pricing Review, Tool/Vendor Shortlist — each with a fixed template, fixed workstreams and a capped research budget, so quality and cost are predictable.
3. **Analyst → Critic → Partner review chain (Direction A's quality layer).** Cheap analyst agents gather sourced evidence; a critic hunts for unsupported claims; a partner forces a clear recommendation. The sellable point is *trustworthy*, not just thorough.

All three directions run on the same parts and differ only in mode: `deep` (full interview, Direction B), `quick` (5-question form, Direction C), and the full menu with the review chain in both (Direction A). v1 runs as Claude Code skills and subagents, operated by the founder as a done-for-you service, before any app is built.

## Key Assumptions to Validate
- [ ] **Enough public data exists for SMB-scale questions** — run 3 real SMB questions; target ≥80% of claims in the memo backed by a source in the evidence ledger.
- [ ] **The critic catches real errors** — plant 3 false claims in an analyst draft; the critic must flag at least 2.
- [ ] **Owners finish the interview and value the reframe** — 5 owners; target ≥4 finish, ≥2 say the reframed question was better than theirs.
- [ ] **Output beats ChatGPT/Gemini Deep Research** — blind side-by-side with 5 owners; target ≥3 prefer ours to act on.
- [ ] **Cost per report stays under ~$5** — log tokens and searches per run; cap analyst search budgets.

## MVP Scope
**In:** `/consult` orchestrator skill; intake (deep + quick); 4 deliverable templates; analyst, critic and partner subagents; evidence ledger with sources; one revision loop; output saved per engagement as Markdown.
**Out:** UI, accounts, payments, scheduling, monitoring, white-labeling.

## Not Doing (and Why)
- **A web app / SaaS UI** — learn what to automate by running it as a service first.
- ~~**Open-ended "research anything" mode**~~ — **Revised in v0.3.0 (2026-10-24):** any-topic research is now supported through `custom-research`, but not as an open chat box. It keeps what differentiates the firm from generic deep research: intake that sharpens the question, a research plan the client confirms, critic fact-checking, gap tagging, and a short answer-first memo. The business deliverables stay as fast paths.
- **Competitor watch / recurring briefings** — good subscription idea, but it is a second product; revisit after 10 paid reports.
- **Selling to agencies (white-label)** — distribution play for later; first prove owners act on the memos.
- **Paid data sources (Similarweb, Ahrefs, etc.)** — budget constraint; test how far public data goes first.

## Open Questions
- Which industry or local market to aim at first? Generic SMB is hard to reach and data quality varies by market.
- Price point: per report ($X) or a done-for-you retainer?
- Language: should memos support Vietnamese as well as English?
