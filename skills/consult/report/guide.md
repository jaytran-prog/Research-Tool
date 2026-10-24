# Written report — guide and spec (`report.json`)

The written report is the long form of the engagement: a 1,800–3,000-word article in the style of a consulting insights piece, with numbered exhibits. It is for readers who will read rather than be presented to — a board pre-read, an investor memo, a client report, or the client's own reference. It shares the deck's honesty rules and exhibit library (`deck/spec.md`).

## What makes it good
1. **Insight headline.** The title states the finding, not the topic. ✅ "Fasting and calorie counting end up even — so choose the one you'll keep" · ❌ "A review of intermittent fasting".
2. **Lead with the complication.** The first paragraph says why the obvious answer is wrong or risky, then gives the answer. No warm-up paragraphs.
3. **"At a glance" box.** 3–5 bullets a busy reader can stop after.
4. **Section headings are conclusions.** Read the headings in order and you have the argument (horizontal logic, as in the deck).
5. **Every exhibit proves its section.** 4–7 exhibits, each with an action title, numbered automatically ("Exhibit 1"). One idea per exhibit; highlight the data point the title is about.
6. **Evidence in the prose, not just the charts.** Each claim carries a citation `[n]`. Say how strong the evidence is in words ("one trial", "pooled across 99 trials", "an unreviewed abstract").
7. **Disagreement is reported.** When credible sources disagree, a paragraph says so and why.
8. **From insight to action.** A section on what to do: the recommendation, the plan (roadmap or KPI exhibit from the action plan), decision gates, and "close the gaps yourself".
9. **Honest limits.** A section on what we don't know (from the critic's open gaps), and "About this research" (method, sources, evidence strength, test/professional-advice notes).
10. **Plain, confident prose.** Short paragraphs (2–4 sentences), active voice, no jargon, numbers with units and dates. Label client-provided facts and estimates.

## Standard structure
1. Title + dek (one-sentence standfirst) + at a glance
2. Introduction: the complication and the answer (1–2 paragraphs)
3. 3–5 insight sections (most important first), each with prose and usually one exhibit
4. Where the evidence disagrees (can be folded into a section)
5. What to do: recommendation, plan, gates, close the gaps yourself
6. What we don't know
7. About this research
8. Sources

## Spec
```json
{
  "meta": { "title": "…", "dek": "…", "client": "…", "date": "2026-10-24", "prepared_by": "Research Tool",
            "evidence": "mixed", "note": "Test engagement… This is research, not professional advice…" },
  "at_a_glance": ["…", "…", "…"],
  "sections": [
    { "heading": "Full-sentence conclusion",
      "blocks": [
        { "type": "p", "text": "Prose with citations like this [1] and this [2]." },
        { "type": "exhibit", "title": "Exhibit action title", "evidence": "strong", "sources": [1],
          "height": 340, "exhibit": { "kind": "dot_ci", "...": "same shapes as deck/spec.md" },
          "note": "Optional note under the chart (method, caveat)." },
        { "type": "callout", "label": "What this means for you", "text": "…" },
        { "type": "bullets", "items": ["…", "…"] }
      ] }
  ],
  "about": "Paragraph(s) on method, sources and evidence strength.",
  "sources": [ { "n": 1, "label": "…", "url": "…" } ]
}
```
- Block types: `p`, `exhibit`, `callout`, `bullets`.
- Exhibit kinds: any from `deck/spec.md` except `hero_stat`; the same data rules apply. `height` (px, 220–460) sets the chart height at a 650-px width; default 320.
- Citations `[n]` must match `sources`. Every exhibit with data lists `sources` and `evidence`.
