# Research story: weather, vegetable prices and food-system vulnerability in Sri Lanka

**Central question.** Does observed rainfall improve one-month-ahead forecasts of selected Sri Lankan vegetable prices, does the improvement differ by commodity, and what do rice and import evidence add about food-system vulnerability?

This is a research study, not a prediction product. Forecasting models are instruments for testing whether rainfall adds information beyond past prices.

## Two connected layers
| Layer | Where | Role |
|---|---|---|
| Visual storyboard | `storyboard/NN_*/storyboard.png` (10 pages) | What the audience sees; understandable without paragraphs |
| Storytelling notes | `storyboard/NN_*/README.md` | Why the page exists, what I say, evidence, qualification, next page |

`STORY_MAP.md` gives the sequence and the argument. `app.py` is a Streamlit review and rehearsal tool that reads these files directly.

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
