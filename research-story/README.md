# Weather, vegetable prices and food-system vulnerability in Sri Lanka

An interactive research dashboard in five pages. It asks one question: **can observed rainfall improve one-month-ahead forecasts of wholesale vegetable prices in Sri Lanka, and does the answer differ by vegetable?** Visitors answer it themselves: pick a vegetable, choose where rain is measured, and watch the KPI cards change. A context page looks at paddy, rice imports and exchange rates, kept separate from the forecasting work.

This folder is self-contained: copy it anywhere, install one tool, run one command.

---

## 1. Run it (about two minutes)

You need [uv](https://docs.astral.sh/uv/), a small tool that installs Python and the libraries for you. Install it once (see the uv documentation for your system), then:

```
cd research-story
uv run streamlit run app.py
```

Your browser opens at <http://localhost:8501>. The first run downloads the libraries (needs internet once); after that it works offline. Stop it with `Ctrl+C` in the terminal.

If the page does not open, go to the address above. If port 8501 is busy, run `uv run streamlit run app.py --server.port 8502`.

## 2. Using the app

- **Sidebar:** the five pages, grouped into three parts. Click any row to jump to it.
- **Bottom bar:** the current part on the left, `page / 5` in the middle, **Previous** and **Next** on the right.
- **Keyboard:** right arrow or Page Down = next, left arrow or Page Up = previous.
- **Presenting:** collapse the sidebar with the arrow at its top, then use the browser's full-screen mode (F11).
- **Hover** any chart for exact values.

| Page | What you can do |
|---|---|
| 1 Prices swing wildly | Pick a vegetable; the four KPI cards and the chart update. Toggle rainfall under the chart. On the rain map, slide through any month since 2010 or switch to a typical month |
| 2 Spot the pattern yourself | Pick a vegetable and how many months earlier the rain fell. Each dot is a month; the cards say how strong the link is in words, and a bar chart compares all seven vegetables |
| 3 Does rain help? Try it | Pick a vegetable, where rain is measured and the market. The cards show the typical miss with and without rain, a plain verdict ("Clear help", "A hint, not proven", "No clear effect", "No help") and how often the price fell inside the forecast range. A strip shows the verdict for all seven vegetables |
| 4 Rain is only one piece | Three context cards and charts: weather and paddy, rice imports, exchange rate |
| 5 What did we learn? | Guess which vegetable rain helps most, then click **Wanna see the conclusion?** to reveal the findings and whether the guess was right |

The default settings on page 3 (Whole island, Dambulla) are the main analysis. The other regions and Pettah are checks.

## 3. What the study found

- Adding observed rainfall to a price-only forecast model improves one-month-ahead forecasts for **cabbage (19.7%), brinjal (12.4%) and carrot (8.2%)**, and these gains survive correction for testing seven vegetables.
- Tomato (4.8%) is only suggestive. Snake gourd and pumpkin show no reliable gain (about 1.8%). Beans get slightly worse (-1.5%). **The value of rainfall depends on the vegetable.**
- The forecasts are still not accurate: typical errors are 23 to 40%, and the 80% bands cover 73 to 84% of outcomes.
- Everything here is **exploratory**: the test period was examined in an earlier pilot, the rainfall series are proxies, and nothing is claimed about causation.

## 4. What is in this folder

Only what the app needs to run:

```
research-story/
├── README.md          this file
├── app.py             the app shell: sidebar, bottom bar, keyboard, page transitions
├── story/             the code behind the pages
│   ├── pages.py         the five pages: controls, KPI cards, charts, conclusion reveal
│   ├── metrics.py       every number on the cards, read from data/
│   ├── rainmap.py       rainfall per map cell for the Sri Lanka rain map
│   ├── ui.py            KPI cards, icons, verdict strip, confetti (HTML/SVG/CSS)
│   └── common.py        colours, vegetable list, data loading
├── data/              every dataset the app reads
├── static/fonts/      Noto Sans, bundled so text looks the same everywhere
├── .streamlit/        theme and settings
├── pyproject.toml     libraries needed (uv reads this)
├── uv.lock            exact versions
└── .python-version    Python version for uv
```

## 5. Speaking guides, docs and tests

These live in the sibling folder **`../research-story-materials/`** and are not needed to run the app:
- `story_pages/`: what the presenter does and says on each page, what each card means, and the method under "If an evaluator asks". Start with `03_does_rain_help.md`.
- `docs/`: the story map, the claim audit (55 claims, all verified), data sources and method references.
- `tests/`: automated checks that the cards show the stored results and every page runs.
- `scripts/`: rebuild the rain map grid, refresh the data, re-run the claim audit.
- `archive/`: the earlier 10-slide version.

See `../research-story-materials/README.md` for how to run the tests and scripts.

## 6. Method in brief

- **Data:** CBSL daily wholesale prices (Dambulla main market, Pettah as a robustness check), turned into monthly means; ERA5-Land rainfall, corrected after an early processing error, turned into monthly anomalies using only earlier years.
- **Design:** two models forecast next month's price, one using past prices only and one using the same prices plus rainfall, both refit every month on data available at that time (62 forecasts per vegetable, August 2021 to September 2026).
- **Testing:** Clark-West test for nested models, Diebold-Mariano and block-bootstrap as supplements, Holm correction across the seven vegetables.
- **Not included:** no machine learning, no future rainfall, no causal claims. The exchange rate was left out because it worsened pilot forecasts.

**Main limitations:** the test window was seen in the pilot; rainfall is measured nationally or in rough regional boxes, not where crops grow; the 62 forecast errors are not independent; prices are nominal; the context analyses (paddy, imports, exchange rate) are short series and the exchange-rate panel is descriptive only.

## 7. Troubleshooting

| Problem | What to do |
|---|---|
| `uv: command not found` | Install uv first (link in section 1), then open a new terminal |
| Browser shows nothing | Open <http://localhost:8501> by hand, or use another port as shown above |
| The sidebar disappeared | Click the small arrow at the top left of the page |
| Text looks different from expected | The bundled font loads only when the app is started from this folder (`cd research-story` first) |

## 8. Credits

Data: Central Bank of Sri Lanka, Copernicus ERA5-Land, Department of Census and Statistics (Sri Lanka), FAOSTAT and UN Comtrade (see `../research-story-materials/docs/references/data_sources.md`). Font: Noto Sans by Google, under the SIL Open Font License 1.1. Libraries: Streamlit, Plotly, pandas, NumPy.
