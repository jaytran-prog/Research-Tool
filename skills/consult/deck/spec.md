# Deck spec — `deck.json`

One format-free file describes the whole deck. The renderers (`scripts/render_deck.py`) turn it into a web deck, a PDF and an editable PowerPoint. Write valid JSON (UTF-8, no comments).

## Top level
```json
{
  "meta": {
    "title": "Intermittent fasting or calorie counting?",
    "subtitle": "What 99 trials say, and what to try for the next 3 months",
    "client": "Test client",
    "date": "2026-10-24",
    "prepared_by": "Research Tool",
    "evidence": "mixed",
    "note": "Test engagement: the client is fictional; the research is real."
  },
  "slides": [ ... ],
  "sources": [ { "n": 1, "label": "Semnani-Azad et al., BMJ 2025 (network meta-analysis, 99 RCTs)", "url": "https://doi.org/10.1136/bmj-2024-082007" } ]
}
```

## Slide
```json
{
  "id": "s4",
  "layout": "standard",
  "cuts": ["team", "investor", "client"],
  "section": "What the evidence shows",
  "title": "After six months, fasting and daily calorie cutting lose the same weight",
  "exhibit": { "kind": "dot_ci", "...": "..." },
  "takeaways": ["Short punchy line", "Short punchy line"],
  "so_what": "Pick the approach you can sustain, not the one with the best headline.",
  "evidence": "strong",
  "sources": [1, 2],
  "notes": "Speaker notes: caveats, exact wording, likely questions."
}
```
- `layout`: `cover` · `exec_summary` · `hero` · `section` · `standard` (exhibit + takeaways rail) · `full` (exhibit full width) · `sources`
- `cuts` optional (default: all). `takeaways` max 3, each ≤ 12 words. `so_what` ≤ 25 words.
- `evidence`: `strong` · `mixed` · `weak` (required on every content slide).
- `sources`: numbers from the top-level `sources` list (required whenever the slide shows a number or a factual claim).

### Special layouts
- `cover`: uses `title`, optional `subtitle`; meta fills the rest.
- `exec_summary`: `title` = the answer; `points`: 3–4 items `{ "headline": "...", "detail": "..." }`; `recommendation`: one sentence.
- `hero`: `exhibit` must be `hero_stat`; `title` explains why the number matters.
- `section`: `title` only.
- `sources`: no fields needed; renders the sources list.

## Exhibit library and data rules
A chart is only allowed when its data rule is met. Otherwise use the listed fallback — never invent or "fill in" data.

| kind | Use for | Data rule | Fallback |
|------|---------|-----------|----------|
| `bar` | comparing amounts | ≥ 2 values, all sourced; estimates flagged | `table` or `bullets` |
| `dot_ci` | effect sizes with uncertainty (forest plot) | each row has value + low + high from a source | `table` |
| `hero_stat` | one number that carries the story | sourced, or client-provided and labelled | `bullets` |
| `table` | structured comparisons | every cell sourced or "unknown" | — |
| `matrix_2x2` | positioning, prioritisation | `basis` states how positions were judged; qualitative positions allowed if the basis is stated | `table` |
| `options` | comparing options on criteria | each score explained in notes | `table` |
| `issue_tree` | breaking down the question / what was tested | statuses from the evidence | `bullets` |
| `roadmap` | phases, owners, gates over time | from the action plan | `table` |
| `kpi` | metrics, baseline, target, gate | baselines sourced or client-provided | `table` |
| `evidence_map` | what we know vs. assume vs. don't know | from the final critic review | — |
| `bullets` | text fallback | — | — |

### Exhibit shapes
```json
{ "kind": "bar", "orientation": "horizontal", "unit": "kg",
  "categories": ["4:3 fasting", "Daily restriction"],
  "series": [ { "name": "12-month weight change", "values": [-7.7, -4.8], "estimate": [false, false] } ],
  "highlight": [0], "value_format": "{:+.1f}" }

{ "kind": "dot_ci", "unit": "kg", "zero": 0, "left_label": "Favours fasting", "right_label": "Favours calorie restriction",
  "rows": [ { "label": "Alternate-day fasting (<24 wks)", "value": -1.29, "low": -1.99, "high": -0.59, "note": "BMJ 2025" } ],
  "highlight": [0] }

{ "kind": "hero_stat", "value": "2.9", "unit": "kg", "label": "more weight lost with 4:3 fasting over 12 months",
  "context": "One trial, 165 adults, intensive support in both arms (95% CI 0.1 to 5.7 kg)" }

{ "kind": "table", "columns": ["Competitor", "Where", "Price", "Strength"],
  "rows": [["The Workshop", "District 1", "40–160k VND", "Space and decor"]], "highlight_rows": [0] }

{ "kind": "matrix_2x2", "basis": "Positions judged from listings and 2025–26 reviews",
  "x": { "name": "Distance from you", "low": "Near", "high": "Far" },
  "y": { "name": "Fit for working", "low": "Low", "high": "High" },
  "quadrants": { "tl": "Direct threats", "tr": "Destination cafés", "bl": "Neighbours", "br": "Not competing" },
  "points": [ { "label": "Là Việt", "x": 0.2, "y": 0.75, "highlight": true } ] }

{ "kind": "options", "criteria": ["Weight loss", "Ease to sustain", "Evidence"],
  "options": [ { "name": "Time-restricted eating", "scores": [2, 4, 3], "verdict": "Recommended" } ],
  "recommended": 0 }

{ "kind": "issue_tree", "root": "Is fasting better than calorie counting?",
  "branches": [ { "label": "Loses more weight?", "status": "rejected", "children": ["Same after 6 months"] } ] }

{ "kind": "roadmap", "unit": "Week", "start": 1, "end": 12,
  "lanes": [ { "name": "Trial", "bars": [ { "label": "2-week test", "start": 1, "end": 2, "owner": "You" } ] } ],
  "gates": [ { "at": 6, "label": "Weight moved? Continue or switch" } ] }

{ "kind": "kpi", "rows": [ { "metric": "Weekly weight", "baseline": "Week 0 weigh-in", "target": "−0.5 kg/week avg", "gate": "Flat at week 6 → switch", "owner": "You" } ] }

{ "kind": "evidence_map", "rows": [ { "claim": "Same weight loss after 6 months", "strength": "strong", "status": "known", "close_by": "" } ] }

{ "kind": "bullets", "items": [ { "head": "Short bold lead", "text": "Supporting sentence." } ] }
```
- `matrix_2x2` `x`/`y` positions are 0–1 (0 = low end). `options` scores are 0–4 (drawn as Harvey balls).
- `issue_tree` / `evidence_map` statuses: `supported` · `rejected` · `open` and `known` · `assumed` · `unknown`.
- `estimate: true` values are drawn hatched or lighter and labelled "est.".

## Visual rules (the renderers enforce most of these)
- One accent colour for the point the title makes; everything else grey.
- Direct labels on charts instead of legends; no 3D, no pie charts, no gridline clutter.
- Max ~60 words of body text on a standard slide (excluding notes and footnotes).
- Every content slide footer: sources line, evidence badge, page number.
