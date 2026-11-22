# Story map (5 pages)

Audience: the general public, and industry professionals who may assess the work. The screen shows plain words, solid-colour KPI cards and charts people can play with. The method is not on screen. It is in each page's speaking guide (`story_pages/`), under "If an evaluator asks".

| Act | Page | Title | What the viewer does | Demonstrates |
|---|---|---|---|---|
| The problem | 01 | Vegetable prices swing wildly | Picks a vegetable; the cards show cheapest, dearest, biggest move and how often prices swing. Slides the rain map through months | Problem framing, data processing, spatial data |
| | 02 | Spot the pattern yourself | Picks a vegetable and the rain delay; sees each month as a dot and the strength of the link in words | Exploratory analysis, caution about chance patterns |
| The test | 03 | Does rain help? Try it | Picks vegetable, rain region and market; cards show the miss with and without rain, the verdict and how often the range held | Model design, validation, honest interpretation |
| The bigger picture | 04 | Rain is only one piece | Reads three context cards; hovers three charts | Linking to a wider industry problem |
| | 05 | What did we learn? | Guesses which vegetable rain helps most, then clicks "Wanna see the conclusion?" | Critical thinking and conclusions |

Narrative arc: a felt problem (1) → the viewer finds a clue (2) → the viewer tests the clue (3) → zoom out (4) → the viewer's guess meets the answer (5).

## How this replaced the 10-page deck
- Old pages 1–2 became page 1, and old page 3 (the lag correlations) became page 2.
- Old pages 4–8 became page 3. Design and evaluation moved to the speaking guide. The main result is the verdict card and strip, robustness is the region and market controls, and accuracy is the "inside our range" card.
- Old page 9 became page 4, and old page 10 became the reveal on page 5.
- The old deck is kept in `archive/ten_slide_deck/`.

## Honesty rules for the dashboard
- Every number is read from `data/` when the page runs, and evidence labels come from the stored column.
- Null and negative results look like wins: the same cards, coloured slate or pink instead of green.
- Page 2 is labelled as a clue, not proof, and the forecasting test on page 3 is the evidence.
- Regional and Pettah views are checks, labelled as such in the guide.

## Open items
- CPI/NCPI deflator for the exchange-rate panel.
- An out-of-sample test on newly published months.
