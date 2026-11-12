# Research story: weather, vegetable prices and food-system vulnerability in Sri Lanka

**Central question.** Does observed rainfall improve one-month-ahead forecasts of selected Sri Lankan vegetable prices, does the improvement differ by commodity, and what do rice and import evidence add about food-system vulnerability?

This is a research study, not a prediction product. Forecasting models are instruments for testing whether rainfall adds information beyond past prices.

## Two connected layers
| Layer | Where | Role |
|---|---|---|
| Visual storyboard | `storyboard/NN_*/storyboard.png` (10 pages) | What the audience sees; understandable without paragraphs |
| Storytelling notes | `storyboard/NN_*/README.md` | Why the page exists, what I say, evidence, qualification, next page |

`STORY_MAP.md` gives the sequence and the argument. `app.py` is the audience view; every slide is native (Plotly charts and HTML, vector, sharp at any size) in `slides.py`, with all slide text in `slide_copy.py`. The PNG files from `build_figures.py` are an export only and are no longer used by the app. In the app: all ten pages are listed in the sidebar (click to jump), with Previous and Next, the arrow keys or Page Up and Page Down to move, and a progress line. Pages 3, 5, 6, 7 and 8 also have selectors and sliders (`live_charts.py`: vegetable and specification selectors, a forecast-origin slider, a zoom slider) and every chart has hover values. Defaults show the primary specification; every other view is labelled exploratory. The page notes are not shown in the app; they live in each page's `README.md` as a speaking guide: what to say (a first-person script), key points to land, a plain-words and a technical version, likely questions with answers, evidence and sources, what not to claim, what to do on the slide, and the hand-over to the next page.

## Run
```
uv run python research-story/build_figures.py      # regenerate the 10 images from derived data
uv run streamlit run research-story/app.py         # author / presentation / story-flow views
```
Figures read `research_audit/` outputs only; raw data are never touched. Image text and README facts must match `research_audit/forecast_backtest_report_v2.md` and `forecast_validation_v2/`.

## Rules of the story
1. Ten pages: eight on the forecasting study, one wider context, one conclusion. Each page has one takeaway and one README.
2. Effect size and evidence strength are shown separately.
3. Exploratory is labelled exploratory; no causal claims; no composite vulnerability score.
4. The tomato result stays exploratory (the one corrected regional cell is not promoted).
5. The resolution is the empirical answer, not a product.

## Visual identity
Midnight navy `#002941` (ink and primary marks), soft blue `#b6dfed` (tints and the exploratory state), coral `#fd6e6e` (the single accent: the act marker, the "worse" state and caution callouts; never used for text). Type is Noto Sans in regular, medium and semibold. Evidence classes are always carried by a label as well as by colour.
