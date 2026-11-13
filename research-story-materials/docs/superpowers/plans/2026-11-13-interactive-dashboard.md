# Interactive Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the 10-slide storyboard with a 4-page interactive dashboard: reactive KPI cards, plain-language controls, a merged "Does rain help? Try it" page, and a confetti conclusion reveal.

**Architecture:** Pure data functions in `story/metrics.py` (unit-tested, no Streamlit). HTML/SVG card and icon builders in `story/ui.py`. Page bodies in `story/pages.py`. `app.py` keeps the sidebar/control-bar shell and wraps each page in a keyed container so a fade/slide animation plays on every page change.

**Tech Stack:** Streamlit ≥1.50, Plotly, pandas, numpy, pytest (dev), uv.

**Spec:** `docs/superpowers/specs/2026-11-13-interactive-dashboard-design.md`

## Global Constraints

- Every number shown comes from `data/` at runtime; no new models, commodities, horizons or claims.
- Do not modify anything in `data/`.
- Evidence labels are read from the stored `evidence` column, never re-derived.
- Plain-language evidence labels: `supported (corrected)` → "Clear help"; `suggestive (uncorrected only)` → "A hint, not proven"; `no reliable evidence` → "No clear effect"; `worse or no gain` → "No help".
- Palette: navy `#002941`, soft blue `#b6dfed`, coral `#fd6e6e` (accent / "worse" only), plus sage `#5e9e83` ("helped"), slate `#8aa3b2` ("no change"), paper `#f6fafc`. No gradient text, no glows.
- All motion wrapped in `@media (prefers-reduced-motion: no-preference)`.
- No external network at runtime: confetti is inline JS, icons are inline SVG.
- Folder stays standalone: `uv sync && uv run streamlit run app.py` from a fresh copy must work.
- Commit after every task; never push.

## Review Focus

- Switching market to Pettah: Pettah has 61 forecasts, not 62; KPIs must use the actual count, not a hard-coded 62.
- Vegetable with a negative gain (Beans): chip must read "worse" in coral, not show a green arrow with a minus sign.
- Leaving page 4 after revealing and coming back: page must render without re-firing confetti until the button is clicked again.
- Page 1 vegetable with gaps (months with <10 daily prices): month-to-month jump must compare consecutive *calendar* months only, not bridge gaps.
- Keyboard arrows while focus is in a select box or radio: must not change page (existing guard must still find the new control bar).

---

### Task 1: Data functions (`story/metrics.py`)

**Files:**
- Create: `story/metrics.py`, `tests/test_metrics.py`
- Modify: `pyproject.toml` (add `[dependency-groups] dev = ["pytest>=8"]`)

**Interfaces:**
- Consumes: `story.common.prices() -> DataFrame` (monthly, columns = VEGS), `story.common.DATA`, `VEGS`, `EVID_LABEL`.
- Produces:
  - `REGIONS = {"Whole island": "nat", "Around Dambulla": "dam", "Hill country (Nuwara Eliya)": "nuw"}`
  - `MARKETS = {"Dambulla": "dambulla", "Pettah (Colombo)": "pettah"}`
  - `PLAIN = {...}` (the four labels above) and `TONE = {"Clear help": "good", "A hint, not proven": "soft", "No clear effect": "flat", "No help": "bad"}`
  - `price_kpis(veg: str) -> dict` keys `low, low_month, high, high_month, jump_pct, jump_month, big_move_share, n_months`
  - `rain_kpis(veg: str, region: str, market: str) -> dict` keys `miss_without, miss_with` (mae_lkr, Rs/kg), `gain_pct` (rmse_gain_vs_AR_pct), `label` (plain), `tone`, `inside_without, inside_with` (0–10, one decimal), `n`
  - `forecast_path(veg, region, market) -> DataFrame` columns `target_month, actual, without, with, lo, hi` (LKR; lo/hi from the rain model)
  - `verdicts(region, market) -> list[tuple[str, str, str]]` = (veg, plain label, tone) in VEGS order
  - all `@functools.cache`'d file reads; `price_agg == "mean"` throughout.

- [ ] **Step 1: Write failing tests** in `tests/test_metrics.py`:

```python
from story import metrics as m

def test_cabbage_dambulla_national_matches_stored_result():
    k = m.rain_kpis("Cabbage", "nat", "dambulla")
    assert round(k["gain_pct"], 1) == 19.7
    assert k["label"] == "Clear help" and k["tone"] == "good"
    assert round(k["miss_without"]) == 52 and round(k["miss_with"]) == 42
    assert k["n"] == 62

def test_beans_is_no_help():
    k = m.rain_kpis("Beans", "nat", "dambulla")
    assert k["gain_pct"] < 0 and k["label"] == "No help" and k["tone"] == "bad"

def test_inside_range_is_out_of_ten_and_matches_coverage_file():
    k = m.rain_kpis("Cabbage", "nat", "dambulla")
    assert k["inside_without"] == round(0.6935 * 10, 1)
    assert 0 <= k["inside_with"] <= 10

def test_pettah_uses_actual_count():
    assert m.rain_kpis("Cabbage", "nat", "pettah")["n"] == 61

def test_verdicts_national_dambulla():
    v = {veg: lab for veg, lab, _ in m.verdicts("nat", "dambulla")}
    assert [x for x in v if v[x] == "Clear help"] == ["Cabbage", "Brinjal", "Carrot"]
    assert v["Tomato"] == "A hint, not proven"

def test_price_kpis_shape_and_gap_rule():
    k = m.price_kpis("Cabbage")
    assert k["high"] > k["low"] > 0 and 0 <= k["big_move_share"] <= 1
    assert k["jump_pct"] > 0

def test_forecast_path_lengths():
    f = m.forecast_path("Cabbage", "nat", "dambulla")
    assert len(f) == 62 and (f.lo <= f.hi).all()
```

(If the Pettah count turns out not to be 61 per vegetable, assert it equals the `n` column of the comparison file for that row instead; the point is no hard-coded 62.)

- [ ] **Step 2:** `uv run pytest tests -q` → FAIL (module missing).
- [ ] **Step 3: Implement `story/metrics.py`.** `inside_*` = share of forecasts with `lo80_log <= actual_log <= hi80_log` × 10, from `forecast_results_v2.csv`; `jump_pct` = max absolute % change between consecutive calendar months (use `.asfreq("MS")` then `pct_change(fill_method=None)` so gaps give NaN); `big_move_share` = share of those changes with |Δ| > 20%.
- [ ] **Step 4:** `uv run pytest tests -q` → all pass.
- [ ] **Step 5:** Commit `research-story: plain-language metrics for the dashboard, with tests`.

### Task 2: KPI cards, icons, confetti (`story/ui.py`) and global CSS

**Files:**
- Create: `story/ui.py`, `tests/test_ui.py`
- Modify: `app.py` (CSS block: add card, chip, verdict-strip, reveal and page-transition styles; remove `.s-*` rules no longer used after Task 3)

**Interfaces:**
- Produces:
  - `ICON: dict[str, str]` inline SVG strings (24×24, stroke 1.6, `currentColor`) for keys `tag, trend_up, bolt, wave, rain, target, check, shield, leaf, globe, coins, sparkle`
  - `kpi(icon: str, label: str, value: str, note: str = "", tone: str = "flat") -> str` — one card; tone ∈ `good|soft|flat|bad` sets the note chip colour (sage / soft blue / slate / coral)
  - `kpi_row(cards: list[str]) -> None` — renders a responsive grid (4 across, 2 under 900px, 1 under 560px)
  - `verdict_strip(items: list[tuple[str, str, str]], selected: str) -> None` — 7 pill tiles with leaf icon tinted by tone, selected one outlined navy
  - `confetti() -> None` — `st.iframe` with inline JS drawing ~120 soft-coloured (palette colours) paper pieces on a fixed canvas in `window.parent.document`, ~2.5 s, removed after; no-op when `matchMedia('(prefers-reduced-motion: reduce)')`.
- Card style: white, 1px `#d8e6ee` border, 14px radius, very soft navy shadow, icon in a 36px soft-blue circle, label muted 0.85rem, value 2rem semibold tabular numbers, `@keyframes rise` (opacity 0→1, translateY 6px→0, 350ms) staggered by `nth-child`.
- Page transition: `[class*="st-key-page_"] { animation: pagein .45s ease both }` (opacity + translateX 16px→0).

- [ ] **Step 1: Failing tests** `tests/test_ui.py`: `kpi("tag","Typical miss","Rs 42","↓ 19%","good")` contains `Rs 42`, `kpi-chip good`, and an `<svg`; `kpi` HTML-escapes its label (`"<b>"` → `&lt;b&gt;`); every `ICON` value starts with `<svg`.
- [ ] **Step 2:** run → FAIL. **Step 3:** implement. **Step 4:** run → PASS.
- [ ] **Step 5:** Commit `research-story: KPI cards, inline icons and confetti`.

### Task 3: The four pages and the app shell

**Files:**
- Create: `story/pages.py`, `tests/test_app.py`
- Modify: `app.py` (nav from `pages.PAGES`; wrap body in `st.container(key=f"page_{n}")`; keep control bar, progress, keyboard script)
- Delete (git rm; recoverable from commit 96e9909): `story/slides.py`, `story/live_charts.py`, `story/slide_copy.py`, `scripts/build_figures.py`
- Move: `storyboard/` → `archive/ten_slide_deck/png/`; old `story_pages/*.md` → `archive/ten_slide_deck/guides/`

**Interfaces:**
- Consumes: Task 1 and Task 2 interfaces.
- Produces: `PAGES: list[tuple[str, str, str, Callable[[], None]]]` = (nav title, material icon, act, render fn), 4 entries; `ACTS` derived from it.

Page contents (copy in plain words; no p-values, no model names on screen):
1. **"Vegetable prices swing wildly"** (act "The problem", icon `:material/show_chart:`). Segmented control of 7 vegetables. KPIs: Cheapest month (Rs, month), Most expensive month, Biggest one-month jump (%), "Months with a >20% swing" (x of 10). Plotly price line (navy) over rain bars (soft blue), toggle "Show rainfall". One-line hook below: "So, can last month's rain warn us about next month's price?"
2. **"Does rain help? Try it"** (act "The test", icon `:material/science:`). Controls row: vegetable (segmented), where rain is measured (radio of `REGIONS`), market (radio of `MARKETS`). KPIs: "Typical miss, prices only" (Rs/kg), "Typical miss, adding rain" (Rs/kg, chip "x% smaller/larger overall error" tone from label), "Verdict" (plain label, tone), "Price landed inside our range" (x of 10, note "without rain: y"). Plotly: actual (navy line), prices-only forecast (slate dashed), with-rain forecast (sage), shaded with-rain range (soft blue, 0.35 alpha). Then `verdict_strip`. Small muted line: "62 real month-ahead forecasts, Aug 2021 – Sep 2026. Exploratory, not proof of cause." (use actual `n`).
3. **"Rain is only one piece"** (act "The bigger picture", icon `:material/public:`). Three KPI cards (rain–harvest link r, import share latest year %, USD/LKR rise since 2021 %) above the three existing page-9 charts (port `p9_data` from old `slides.py` into `pages.py`).
4. **"What did we learn?"** (act "The bigger picture", icon `:material/flag:`). Centered card with sparkle icon and a primary button "Wanna see the conclusion?". On click: `st.session_state.revealed = True`, call `ui.confetti()` once (flag `st.session_state.confetti_pending` cleared after render), then three staggered cards: "Rain helps some vegetables" (cabbage, brinjal, carrot: errors 8–20% smaller), "…but not all, and not precisely" (others no clear gain; typical miss still ~a quarter of the price), "What it means" (a research finding, not an app; next: test on new months, farm-area rain). Numbers from `metrics`, not typed. A quiet "Hide again" tertiary button resets.

- [ ] **Step 1: Failing test** `tests/test_app.py` using `streamlit.testing.v1.AppTest.from_file("app.py")`: for each page index 0–3 set `session_state.page` and `run()`, assert `not at.exception`; on page 1 (index 1) set radio market to Pettah and rerun → no exception; on page 3 click the "Wanna see the conclusion?" button → markdown contains "Rain helps some vegetables"; switch to page 0 and back → no exception.
- [ ] **Step 2:** run → FAIL. **Step 3:** implement pages and shell, do the moves/deletes. **Step 4:** `uv run pytest tests -q` → PASS.
- [ ] **Step 5:** Visual check in a browser (Playwright screenshot of each page at 1440×900 and 390×844); fix overlap/overflow.
- [ ] **Step 6:** Commit `research-story: four-page interactive dashboard with conclusion reveal`.

### Task 4: Speaking guides, README, audit script, standalone check

**Files:**
- Create: `story_pages/01_prices_swing.md`, `02_does_rain_help.md`, `03_bigger_picture.md`, `04_conclusion.md` (format `# NN - Title`; sections: What to do on this page, What to say, Key points, If an evaluator asks (carries the theory: AR vs AR+rain, Clark–West, Holm, bootstrap, past-only rain, exploratory test window), What not to claim)
- Modify: `README.md` (4 pages, new tree, `archive/` explained, pytest command), `docs/STORY_MAP.md` (4-page map), `scripts/audit_claims.py` (read guides from `archive/ten_slide_deck/guides/` for old-page text checks; add checks that page-4 conclusion figures come from `metrics`)

- [ ] **Step 1:** Write the guides and docs; `app.py` titles parse from the new md files.
- [ ] **Step 2:** `uv run pytest tests -q` → PASS.
- [ ] **Step 3:** Copy folder to scratchpad, `uv sync`, run the AppTest suite there → PASS.
- [ ] **Step 4:** Commit `research-story: speaking guides and docs for the four-page dashboard`.
