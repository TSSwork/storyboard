# Story map (4 pages)

Audience: the general public, and industry professionals who may assess the work. The screen shows plain words, KPI cards and charts people can play with. The method is not on screen. It is in each page's speaking guide (`story_pages/`), under "If an evaluator asks".

| Act | Page | Title | What the viewer does | Demonstrates |
|---|---|---|---|---|
| The problem | 01 | Vegetable prices swing wildly | Picks a vegetable; KPI cards show cheapest, dearest, biggest move, how often prices swing | Problem framing, data processing |
| The test | 02 | Does rain help? Try it | Picks vegetable, rain region and market; cards show the miss with and without rain, the verdict and how often the range held | Model design, validation, honest interpretation |
| The bigger picture | 03 | Rain is only one piece | Reads three context cards; hovers three charts | Linking to a wider industry problem |
| | 04 | What did we learn? | Clicks "Wanna see the conclusion?" | Critical thinking and conclusions |

Narrative arc: a felt problem (1) → the viewer runs the experiment themselves (2) → zoom out (3) → a reveal that stays as cautious as the evidence (4).

## How this replaced the 10-page deck
- Old pages 1–3 (question, scope and data, prices and rain) became page 1.
- Old pages 4–8 (design, evaluation, main result, robustness, accuracy) became page 2. Design and evaluation moved to the speaking guide. The main result is the verdict card and strip, robustness is the region and market controls, and accuracy is the "inside our range" card.
- Old page 9 became page 3, and old page 10 became the reveal on page 4.
- The old deck (PNG images, speaking guides and slide code) is kept in `archive/ten_slide_deck/`.

## Honesty rules for the dashboard
- Every number is read from `data/` when the page runs, and evidence labels come from the stored column.
- Null and negative results look exactly like wins: the same cards, with a coral or grey tone.
- Regional and Pettah views are checks, labelled as such in the guide.

## Open items
- CPI/NCPI deflator for the exchange-rate panel.
- An out-of-sample test on newly published months.
