# Weather, vegetable prices and food-system vulnerability in Sri Lanka

An interactive research storyboard in ten pages. It asks one question: **can observed rainfall improve one-month-ahead forecasts of wholesale vegetable prices in Sri Lanka, and does the answer differ by vegetable?** A final context page looks at paddy, rice imports and exchange rates, kept separate from the forecasting work.

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

- **Sidebar:** the ten pages, grouped into three acts. Click any row to jump to it. "Start from page 1" appears on every page except the first.
- **Bottom bar:** the current act on the left, `page / 10` in the middle, **Previous** and **Next** on the right.
- **Keyboard:** right arrow or Page Down = next, left arrow or Page Up = previous.
- **Presenting:** collapse the sidebar with the arrow at its top, then use the browser's full-screen mode (F11).
- **Hover** any chart for exact values. Some pages have controls:

| Page | What you can do |
|---|---|
| 3 Prices and rain | Pick a vegetable; the outlined row in the correlation table follows it |
| 5 Evaluation | Pick a vegetable and drag the forecast-origin slider to watch the training window grow |
| 6 Main result | Switch the rainfall definition (primary, non-overlapping window, two regional boxes) |
| 7 Robustness | Tick specifications on and off |
| 8 Accuracy | Pick a vegetable, zoom with the range slider under the chart |

The default view on every page is the primary analysis. Other views are labelled exploratory on the page.

## 3. What the study found

- Adding observed rainfall to a price-only forecast model improves one-month-ahead forecasts for **cabbage (19.7%), brinjal (12.4%) and carrot (8.2%)**, and these gains survive correction for testing seven vegetables.
- Tomato (4.8%) is only suggestive. Snake gourd and pumpkin show no reliable gain (about 1.8%). Beans get slightly worse (-1.5%). **The value of rainfall depends on the vegetable.**
- The forecasts are still not accurate: typical errors are 23 to 40%, and the 80% bands cover 73 to 84% of outcomes.
- Everything here is **exploratory**: the test period was examined in an earlier pilot, the rainfall series are proxies, and nothing is claimed about causation.

## 4. What is in this folder

```
research-story/
├── README.md              this file
├── app.py                 the app: sidebar, bottom bar, keyboard
├── pyproject.toml         the libraries needed (uv reads this)
├── uv.lock                exact versions, so it runs the same everywhere
├── .python-version        Python version for uv
├── .streamlit/            colour theme and settings for the app
├── story/                 the code behind the slides
│   ├── slide_copy.py        every headline, subtitle and text block on the slides
│   ├── slides.py            the ten slides, built from native charts and HTML
│   ├── live_charts.py       the interactive charts with selectors and sliders
│   └── common.py            colours, vegetable list and data loading
├── data/                  every dataset the app reads (one common folder)
├── story_pages/           one speaking guide per page (10 Markdown files)
├── storyboard/            optional PNG exports of the slides (one folder per page)
├── docs/                  background documents
│   ├── STORY_MAP.md         how the ten pages build one argument
│   ├── AUDIT_REPORT.md      check of every claim against its source
│   ├── CLAIM_SOURCE_REGISTER.csv   55 claims, each with its source and status
│   └── references/
│       ├── data_sources.md      where each data file comes from
│       └── research_references.md   statistical-method references
├── scripts/               optional tools (not needed to run the app)
│   ├── build_figures.py     export the slides as PNG images
│   ├── sync_data.py         refresh data/ from the full research project
│   └── audit_claims.py      re-run the claim audit (needs the full project)
└── static/fonts/          Noto Sans, bundled so text looks the same on every computer
```

## 5. For evaluators: where to look

1. **Run the app** and read the ten pages in order. They stand on their own.
2. **`story_pages/`** holds what the presenter says on each page: a spoken script, key points, a plain-words and a technical explanation, likely questions with answers, the evidence behind the slide and what must not be claimed. Open `06_main_result.md` first for the central result.
3. **`docs/AUDIT_REPORT.md`** shows that the numbers were checked against the analysis outputs (55 claims, all verified) and lists what was corrected. The register is in `docs/CLAIM_SOURCE_REGISTER.csv`.
4. **`data/`** has every dataset; `docs/references/data_sources.md` explains each file.
5. **`story/`** is the code. `slide_copy.py` is the easiest file to read: it contains all of the slide text.

## 6. Method in brief

- **Data:** CBSL daily wholesale prices (Dambulla main market, Pettah as a robustness check), turned into monthly means; ERA5-Land rainfall, corrected after an early processing error, turned into monthly anomalies using only earlier years.
- **Design:** two models forecast next month's price, one using past prices only and one using the same prices plus rainfall, both refit every month on data available at that time (62 forecasts per vegetable, August 2021 to September 2026).
- **Testing:** Clark-West test for nested models, Diebold-Mariano and block-bootstrap as supplements, Holm correction across the seven vegetables.
- **Not included:** no machine learning, no future rainfall, no causal claims. The exchange rate was left out because it worsened pilot forecasts.

**Main limitations:** the test window was seen in the pilot; rainfall is measured nationally or in rough regional boxes, not where crops grow; the 62 forecast errors are not independent; prices are nominal; the context analyses (paddy, imports, exchange rate) are short series and the exchange-rate panel is descriptive only.

## 7. Optional tools

Run these from inside `research-story/`.

```
uv run --extra export python scripts/build_figures.py     # PNG copies of the slides into storyboard/
uv run python scripts/sync_data.py                         # refresh data/ (only when this folder sits inside the full project)
uv run python scripts/audit_claims.py                      # re-run the claim audit (needs the full project one level up)
```

## 8. Troubleshooting

| Problem | What to do |
|---|---|
| `uv: command not found` | Install uv first (link in section 1), then open a new terminal |
| Browser shows nothing | Open <http://localhost:8501> by hand, or use another port as shown above |
| The sidebar disappeared | Click the small arrow at the top left of the page |
| Text looks different from the screenshots | The bundled font loads only when the app is started from this folder (`cd research-story` first) |

## 9. Credits

Data: Central Bank of Sri Lanka, Copernicus ERA5-Land, Department of Census and Statistics (Sri Lanka), FAOSTAT and UN Comtrade (see `docs/references/data_sources.md`). Font: Noto Sans by Google, under the SIL Open Font License 1.1. Libraries: Streamlit, Plotly, pandas, NumPy.
