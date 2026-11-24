// Every analysis in the project: what it was, why we did it, what it found, and whether it reached the dashboard.
// Compile: typst compile analysis.typ   (needs the Manrope font; Newsreader is optional for headings)

#set document(title: "Every Analysis We Did: Rain and Vegetable Prices in Sri Lanka")
#set page(paper: "a4", margin: (x: 2.3cm, top: 2.3cm, bottom: 2.2cm), numbering: "1", number-align: center)
#set text(font: "Manrope", size: 10.5pt, weight: 450, lang: "en", region: "gb")
#set par(justify: false, leading: 0.72em, spacing: 1.05em)
#set heading(numbering: "1.1")
#show heading: set text(font: ("Newsreader", "Newsreader 36pt", "Manrope"), weight: 600, fill: rgb("#002941"))
#show heading.where(level: 1): set text(size: 17pt)
#show heading.where(level: 1): set block(above: 1.8em, below: 0.9em)
#show heading.where(level: 2): set text(size: 13pt)
#show heading.where(level: 2): set block(above: 1.4em, below: 0.7em)
#show heading.where(level: 3): set text(size: 11.5pt)
#show raw: set text(size: 8.2pt)
#show raw.where(block: true): block.with(fill: rgb("#f3f6f8"), inset: 9pt, radius: 4pt, width: 100%)
#set table(stroke: 0.5pt + rgb("#c9d6de"), inset: 6pt)
#show table.cell.where(y: 0): set text(weight: 700)
#show link: set text(fill: rgb("#1155cc"))

#let note(body) = block(breakable: false, fill: rgb("#fff4e5"), inset: 10pt, radius: 4pt, width: 100%, stroke: (left: 3pt + rgb("#f5a33b")), body)
#let key(body) = block(breakable: false, fill: rgb("#e8f3f8"), inset: 10pt, radius: 4pt, width: 100%, stroke: (left: 3pt + rgb("#2f7292")), body)
#let why(body) = block(breakable: false, fill: rgb("#eef6f1"), inset: 10pt, radius: 4pt, width: 100%, stroke: (left: 3pt + rgb("#23936f")), [*Why this choice.* #body])
#let dash(body) = block(breakable: false, fill: rgb("#f4f0fb"), inset: 10pt, radius: 4pt, width: 100%, stroke: (left: 3pt + rgb("#8a63d2")), [*On the dashboard?* #body])

// ---------------------------------------------------------------- title
#text(font: ("Newsreader", "Newsreader 36pt", "Manrope"), size: 26pt, weight: 600, fill: rgb("#002941"))[Every analysis we did]
#v(-0.4em)
#text(size: 13pt, fill: rgb("#52707f"))[What each analysis was, why we chose it, what it found, and why only some of it reached the dashboard. With the real code and worked examples.]
#line(length: 100%, stroke: 0.6pt + rgb("#c9d6de"))

*Who this is for.* Someone who has read `full_story.typ` and now needs to answer a judge's question such as "why did you use that test?" or "why not machine learning?". Every analysis is explained from the ground up, without assuming a statistics background, but without skipping the detail either.

*How each section is built.* What we did, then a green box with *why this choice*, then the result, then a purple box saying whether it is *on the dashboard* and why. Code excerpts are copied from the project files and lightly trimmed; the file name is given above each one.

#outline(title: [Contents], depth: 2, indent: 1em)

= Preparing the data

Everything rests on two series: vegetable prices and rainfall. Getting these right took more care than any model.

== Vegetable prices

*Source.* The Central Bank of Sri Lanka (CBSL) publishes daily wholesale and retail prices, collected here through Macro Lab (the file header says so). The file `raw/cbsl-daily-prices.csv` has about 45 series covering three markets (Pettah in Colombo, Dambulla, and Narahenpita), from 1 August 2016 to November 2026. Prices are in rupees per kilogram, as published.

*Which vegetables.* Seven: cabbage, brinjal, carrot, tomato, snake gourd, pumpkin and beans. These have complete wholesale series at both Dambulla and Pettah. Narahenpita retail was not used because 38% to 79% of its days are missing.

*Which market.* Dambulla wholesale is the main market. It is a major collection point for vegetables from the growing regions, so its prices respond to supply quickly. Pettah wholesale is used only as a check.

*From daily to monthly.* For each vegetable and month, we took the average of the valid daily prices, but only if the month had at least 10 days of prices. Otherwise the month is left empty. Empty months are never filled in by guessing.

```python
# research_audit/forecast_backtest_v2.py
MIN_OBS = 10
def monthly_price(veg, market, agg):
    col = f"{veg} (wholesale, {market}) (Rs/kg)"
    s = cb[col].dropna(); s = s[s > 0]
    g = s.resample("MS"); p = getattr(g, agg)(); n = g.count()
    p[n < MIN_OBS] = np.nan                 # too few days: month is missing
    months = pd.date_range(p.index.min(), p.index.max(), freq="MS")
    return np.log(p.reindex(months)), n
```

#why[
- *Monthly, not daily.* Daily prices are noisy (a single truck arriving late can move a day's price), and rain affects crops over weeks, not hours. Monthly is also the natural step for rainfall totals.
- *At least 10 days.* A month with only two or three price days is not a reliable average. Ten days is about half the market days in a month. Months that fail are dropped rather than invented, because invented values would make the model look better than it is.
- *Mean, with the median as a check.* The mean uses every price. We re-ran the main test with the monthly median, which ignores extreme days, and the conclusions did not change (cabbage 21.8% instead of 19.7%).
- *The logarithm of the price.* Vegetable prices move in proportions: a jump from 100 to 200 rupees and from 200 to 400 rupees are the same kind of event (a doubling). Taking the logarithm turns proportional changes into equal steps, keeps big-price months from dominating, and means a forecast error of 0.1 in log terms is roughly a 10% miss.
]

*Not adjusted for inflation.* All prices are nominal (as published). We had no consumer price index in the project. This does not change which forecasting model wins, because both models forecast the same nominal series; inflation sits inside the past-price terms of both.

== Rainfall from ERA5-Land

*Source.* ERA5-Land is a "reanalysis" from the Copernicus Climate Data Store: a weather model run over the past and continuously corrected with real observations, so it has no gaps. We downloaded hourly data from January 2010 on a grid of squares 0.1 degrees across (about 11 km), 203 monthly files with no missing hours.

*Which squares.* ERA5-Land marks each square as land or sea. Sri Lanka has 541 land squares. All rainfall series use these.

=== The rainfall bug, and the fix

The first processed file in the project said January 2010 had 1,256 mm of rain across the island, about nine times the normal January figure of roughly 143 mm. The cause: ERA5-Land stores rainfall as an *accumulation*. At 01:00 it holds the rain since midnight; at 02:00 the rain since midnight again (now two hours' worth); and so on, until it resets. The original script added up all 24 hourly values, counting early-morning rain up to 24 times. Monthly totals came out between 12.4 and 21.4 times too large (typically 14 times).

The fix is to read one value per day: the value at midnight (00:00 UTC) at the *start of the next day*, which holds the whole previous day's total.

```python
# research_audit/era5_validate.py
w = np.cos(np.deg2rad(ds.latitude))         # weight each square by its true area
land = ds.t2m.isel(valid_time=0).notnull()  # ERA5-Land leaves sea squares empty
...
tp0 = h.tp[h.index.hour == 0]               # keep only the 00 UTC accumulations
# the value at 00 UTC on day D+1 is the total of day D
tp0.index = tp0.index.normalize() - pd.Timedelta(days=1)
d["rain_mm"] = tp0
```

After the fix, yearly national rainfall is 1,370 to 2,323 mm (2010 to 2025), with the expected double peak: about 294 mm in October, 351 in November and 241 in December, and a low of about 82 mm in March. Only the corrected series are used in the project.

#why[
- *Weighting by the cosine of latitude.* On a map grid, squares further from the equator cover slightly less ground. Multiplying by the cosine of the latitude gives each square a weight equal to its real area, so the island average is a true area average. Over Sri Lanka the effect is small, but it is the correct method.
- *ERA5-Land and not station data.* Rain gauges are irregular and have gaps; a reanalysis covers every square every hour. CHIRPS, a satellite product, would have been a good independent check, but only one day of it had been downloaded, which cannot validate anything.
- *Complete months only.* A month with missing days is set to missing rather than counted as a partial total. Only two months fail: December 2009 (one leftover time step) and November 2026 (still in progress).
]

=== National rain and two regional boxes

The main rainfall series is the average over all 541 land squares. Two regional series were built as checks: a box 0.3 degrees each way around Dambulla (7.86 N, 80.65 E) and around Nuwara Eliya (6.97 N, 80.77 E), each 36 land squares.

#why[
Dambulla market receives vegetables from many regions: hill-country crops such as cabbage and carrot come from around Nuwara Eliya, while others are grown in the dry zone. We did not know in advance which area's rain matters most for each vegetable, and we had no district boundary file to build exact growing-area averages. So the national average was fixed in advance as the main series, and the two boxes are checks. The boxes are hand-drawn approximations, which we always say.
]

#dash[
Yes. Page 1 shows the national rain bars and a rain map of all 541 squares. The map file `era5_rain_grid.csv` was rebuilt from the raw hourly files with the same corrected rule, and an automated test checks that averaging it reproduces the national and Dambulla-box series to within 0.5 mm. Page 1 also has a rainfall-area picker (island, Dambulla, Nuwara Eliya, Colombo). The Colombo box was added later for display only; it was never part of the forecasting test.
]

== The other sources

#table(
  columns: (1.1fr, 2.2fr, 1.4fr),
  table.header([Source], [What we checked], [Decision]),
  [DCS paddy statistics], [National season totals since 1951 (complete); district workbooks with inconsistent headers and spelling variants.], [National Yala series used on page 4.],
  [FAOSTAT production and trade], [Rice production identical to DCS (correlation 1.000). Trade file mixes products with totals such as "Cereals", which must not be summed.], [Rice imports used on page 4.],
  [UN Comtrade], [2018 missing entirely; 2025 incomplete (rice 84 thousand tonnes against CBSL's 185); product codes change between classification revisions.], [Cross-check only; agrees with FAOSTAT (0.998).],
  [CBSL exchange rates], [Daily rupee to US dollar rate, May 2010 to November 2026, no duplicate dates.], [Monthly average used on page 4.],
  [HARTI weekly bulletins], [529 PDFs turned into tables. 38 gaps longer than a week; 2020 has 25 weeks; duplicate records; prices about 1.39 times CBSL for the same Dambulla carrot.], [Not used. Too patchy, and a different price definition.],
  [World Bank Real-Time Food Prices], [816 columns, 27 with data, most of those modelled estimates; observations collapse between 2018 and 2022.], [Not used.],
)

#key[*Independence matters.* FAOSTAT rice production is DCS; FAOSTAT and Comtrade rice imports are the same customs records; HARTI and CBSL at Dambulla move together (correlation 0.96). Treating these as separate confirmations would have inflated our confidence, so each group counts as one source.]

= The exploratory analyses: what could the data support?

Before choosing a main study, we ran a quick first test on every question the data might answer (`03_research_feasibility.md`, scripts `feasibility_tests.py` and `feasibility_prices.py`). These were deliberately simple: correlations, with significance judged by *permutation tests*.

#why[
A *permutation test* asks: if there were no real link, how often would shuffling one series at random produce a correlation this strong? We shuffled 3,000 to 5,000 times. If only 0.2% of shuffles beat the real correlation, the p-value is 0.002. This avoids relying on textbook assumptions (such as bell-shaped data), which are doubtful for short, irregular series. Where a series has a long-run trend (rice production rises over time, for example), we removed a straight-line trend first, so that two unrelated rising series do not look linked.
]

== Rain and the rice harvest

*What we did.* For each Yala season (March to August) and each Maha season (October to February), 2010 to 2025, we summed national rain and compared it with the share of sown rice land that was harvested, the yield and the production. Both sides had their trend removed. Sixteen seasons each.

*Result.* The clearest signal: in Yala, wetter seasons went with a higher share of sown land harvested, correlation +0.68 (permutation p = 0.002). The harvested share is a good drought indicator, because in a dry season farmers plant but some fields fail. Rain against yield was weak (−0.16). We ran 32 tests here, so about 1.6 false positives were expected by chance; we treat everything here as suggestive, with the Yala harvested share the most believable.

#dash[Yes, as the green card and left chart on page 4 ("Wetter growing seasons, better paddy harvests", r = +0.68, 16 seasons). It is labelled "a link, not proof", because 16 points with policy shocks (such as the 2021 fertiliser restrictions) cannot support more.]

== Rice production and imports

*What we did.* Yearly detrended paddy production against FAOSTAT rice imports, 2010 to 2024 (15 years).

*Result.* Correlation −0.79 (p = 0.002): low-production years had high imports. But most of the strength came from 2017 and 2022. Without those two years the correlation is −0.46 (13 years). The rank-based (Spearman) version over all years is −0.59. The direction is solid; the size depends on two events.

== How much rice is imported

*What we did.* For each year, the share of rice supply that came from abroad:

$ "import share" = "imports" / ("domestic rice" + "imports"), quad "domestic rice" = 0.67 times "paddy production" $

*Result.* Between 0.5% and 29.6% (2010 to 2024). The peaks are 2017 (29.5%), 2022 (25.6%) and 2014 (20.1%). 2014 and 2017 were low-production years; 2022 was the economic crisis.

#note[*Two honest caveats.* (1) The factor 0.67, which converts paddy (rice in the husk) to milled rice, is an assumption recorded in the project, not a measured figure. (2) This is an *apparent* share: stock changes, waste, seed and animal feed are not modelled, so it is not a self-sufficiency rate.]

#dash[Yes, as the orange card and middle chart on page 4 ("Rice bought from abroad, peak year", 30% in 2017, 4% in 2024). The production-versus-imports correlation itself is not shown; it is kept for questions.]

== The exchange rate and food prices

*What we did.* Monthly changes in rice and imported-food prices (from HARTI) against monthly changes in the rupee to dollar rate, with delays of 0 to 6 months.

*Result.* Rice prices moved with the rupee in the same month and the next (correlations 0.30 to 0.36), fading to nothing by three months. Imported dried chillies (0.32) and red dhal (0.38) moved with it too; imported big onion barely did (0.05). But between late 2021 and late 2022, local Nuwara Eliya potatoes rose 122% and local Nadu rice 81%, as much as imported goods. That is general inflation, not just the rupee. Without a consumer price index we cannot separate the two.

#dash[Only descriptively: the purple card and right chart on page 4 show the rupee's price (Rs 333 now, up 75% since January 2021, with the 2022 crisis shaded). The note says "No price pass-through is estimated", meaning we do not claim how much of the rupee's fall reached food prices.]

== Rain and vegetable prices: the pattern that changed the project

This is the analysis that turned the project towards vegetables.

*What we did.* For each of the seven vegetables at Dambulla:
+ *Price change.* The monthly change in the log of the average price, which is roughly the percentage change.
+ *Remove the normal seasonal change.* Prices tend to rise in some calendar months every year. We subtracted the average change for that calendar month, so what is left is how unusual the change was.
+ *Rain anomaly.* National rain for the month, expressed as a z-score: how many standard deviations wetter or drier than the average for that calendar month.
+ *Correlate* the price change with the rain anomaly from the same month and from one, two and three months earlier, with permutation p-values.

```python
# research-story/story/metrics.py (the dashboard reproduces the audit exactly)
mon = mon[mon.days_in_month >= 28]                  # complete months only
g = mon.groupby(mon.index.month).rain_mm
z = (mon.rain_mm - g.transform("mean")) / g.transform("std")   # rain z-score

def pattern(veg, lag):
    dp = logp[veg].diff()                           # monthly change in log price
    # minus the usual change for that calendar month
    dp = dp - dp.groupby(dp.index.month).transform("mean")
    return pd.concat([z.shift(lag).rename("rain_z"),
                      (dp * 100).rename("price_chg")], axis=1).dropna()
```

*Result.* Correlations (122 months each, September 2016 to October 2026):

#table(
  columns: (1.2fr, 1fr, 1fr, 1fr, 1fr),
  align: (left, center, center, center, center),
  table.header([Vegetable], [Same month], [1 month earlier], [2 months earlier], [3 months earlier]),
  [Cabbage], [+0.10], [*+0.60*], [+0.16], [−0.06],
  [Carrot], [−0.06], [*+0.44*], [+0.20], [0.00],
  [Brinjal], [+0.03], [*+0.40*], [−0.29], [+0.18],
  [Tomato], [+0.19], [+0.26], [+0.01], [−0.26],
  [Snake gourd], [+0.16], [+0.20], [−0.15], [−0.14],
  [Pumpkin], [+0.02], [+0.14], [+0.04], [−0.07],
  [Beans], [+0.21], [+0.08], [+0.03], [−0.09],
)

Ten of the 28 correlations were significant at the 5% level. If there were no real links at all, about 1.4 would be expected by chance. A wetter-than-usual month tended to be followed, one month later, by a price rise for cabbage, carrot and brinjal. One plausible explanation is that heavy rain damages crops and disrupts harvesting and transport, and the shortage reaches the market a few weeks later. That is a hypothesis; the study does not test it.

#why[
*Why this was not enough on its own.* With 28 tests, some will look strong by luck. The z-score uses the average of *all* years, including later ones, so it is descriptive, not something you could have known at the time. And a correlation does not show that rain helps *forecast* prices once you already know past prices. All three problems are addressed by the forecasting test in section 3.
]

#dash[Yes, as page 2, "Spot the pattern yourself". The viewer picks a vegetable and the delay, and sees each month as a dot. An automated test checks that the page reproduces all 28 values of the audit table to within 0.01. The page says on screen: "A pattern is a clue, not proof."]

== Questions we considered and did not pursue

#table(
  columns: (1.3fr, 2fr),
  table.header([Question], [Why it was dropped]),
  [District-level rain and rice], [Needs district boundary files to map weather squares onto districts. Not in the project; cheap to add later.],
  [Self-sufficiency ratios], [Needs stock changes, seed, feed and waste. Only the apparent import share is possible.],
  [Import partner concentration and import values by product group], [Feasible and descriptive, but it does not connect to the vegetable question and would overload a public dashboard.],
  [Monthly import prices against import costs], [Comtrade monthly data exist only for 2012.],
  [Temperature], [Available, but the question was about rain, and adding more weather variables to a 62-forecast test increases the risk of finding something by chance.],
  [The full weather to rice to imports to prices chain], [Every link exists, but only for rice, only nationally, and only with 14 to 16 yearly points. Too thin for a convincing test. It became context instead (page 4).],
)

= The forecasting study

== Why a forecasting test

The pattern on page 2 is a correlation. The forecasting test asks a harder and more useful question: *if you already use past prices, does adding rain make next month's forecast miss by less, on months the model has never seen?*

#why[
A forecasting test, also called an *out-of-sample* test or *backtest*, protects against the main weakness of correlations. Each forecast is made using only what was known at the time and then checked against the real outcome. If rain only looked useful by chance in the past, it will not keep improving forecasts month after month. And by comparing a model *with* rain against the same model *without* rain, the only difference is the rain, so any improvement can be credited to it.
]

== The pilot

The pilot (`forecast_pilot.py`) was a quick first version. For each vegetable it forecast Dambulla's next-month log price from month 49 onwards (63 test months, July 2021 to September 2026) with:

- *naive*: next month equals this month;
- *seasonal naive*: next month equals the same month last year;
- *AR* (autoregressive, meaning "predicts a series from its own past"): next month from this month, last month and the month eleven months back;
- *AR plus rain*: the same, plus three rain anomaly terms;
- *AR plus rain plus exchange rate*: the same, plus the monthly change in the rupee.

#table(
  columns: (1.2fr, 1fr, 1.4fr),
  align: (left, center, center),
  table.header([Vegetable], [Gain from rain], [Effect of adding the exchange rate]),
  [Cabbage], [+15.3%], [−9.4% (worse)],
  [Brinjal], [+13.8%], [−16.7% (worse)],
  [Carrot], [+5.4%], [−5.4% (worse)],
  [Tomato], [+2.1%], [−2.8% (worse)],
  [Snake gourd], [+1.3%], [−4.2% (worse)],
  [Pumpkin], [−2.8%], [−1.8% (worse)],
  [Beans], [−4.1%], [−2.6% (worse)],
)

*What it told us.* Rain looked useful for the same three vegetables the correlations pointed to. The exchange rate made forecasts worse for every vegetable, so it was left out of the main study (and kept only as context on page 4).

*What was wrong with it.* (1) "Usual rain" was the average over all years including future ones, a small leak of future information. (2) The price lags were fixed rather than chosen from the training data. (3) The significance test treated forecast errors as independent, although neighbouring months are related. (4) There was no correction for testing seven vegetables. Version 2 fixed all four.

#note[*The pilot caveat.* The pilot looked at almost exactly the same test months as version 2 (July 2021 onwards against August 2021 onwards), and the choice of vegetables and of rain came after seeing it. So even version 2's corrected p-values do not account for that first look. This is why every result is called *exploratory*.]

== The main test: version 2 design

The design was written down at the top of `forecast_backtest_v2.py` *before* the script was run, and not changed afterwards.

=== What is being forecast

The log of the monthly average Dambulla wholesale price in month $t+1$, standing at the end of month $t$. At that moment we know prices up to month $t$ and rain up to the end of month $t$. Rain in month $t+1$ is never used.

=== The prices-only model (AR)

$ y_(t+1) = alpha + beta_1 y_t + beta_2 y_(t-1) + beta_3 y_(t-11) + "error" $

Here $y_t$ is this month's log price, $y_(t-1)$ last month's, and $y_(t-11)$ the price eleven months back, which is the same calendar month as the target one year earlier. That last term lets the model learn seasonal patterns.

At every forecast date the model chooses which of four lag sets to use: $\{y_t\}$, $\{y_t, y_(t-1)\}$, $\{y_t, y_(t-11)\}$ or all three. It picks the set with the lowest *AIC* (Akaike information criterion) on the training data only.

#why[
- *An autoregressive model* is the standard, honest benchmark for a price series: prices this month are the best single guide to prices next month. Beating it is meaningful.
- *AIC* balances fit against complexity: adding a term always fits the past better, and AIC charges a penalty for each extra term so the model does not chase noise. Choosing on training data only means the choice never peeks at the test month.
- *The coefficients are fitted by ordinary least squares* (the line that minimises squared errors), refitted at every forecast date. A tiny ridge penalty (one millionth) is added purely for numerical stability; it changes forecasts by less than 0.00001.
]

=== The rain model (AR plus rain)

$ y_(t+1) = alpha + beta_1 y_t + beta_2 y_(t-1) + beta_3 y_(t-11) + gamma_1 "A0"_t + gamma_2 "A3"_t + "error" $

Exactly the *same* price terms as the prices-only model at that date, plus two rain terms:

- $"A0"_t$: the rain anomaly of month $t$;
- $"A3"_t$: the average rain anomaly over months $t-2$, $t-1$ and $t$.

The rain anomaly is how much wetter than usual the month was, in units of 100 mm, where "usual" is the average rain for that calendar month in *earlier years only*:

$ "anomaly"_t = ("rain"_t - "average rain in the same calendar month, earlier years") / (100 "mm") $

```python
# research_audit/forecast_backtest_v2.py
def anomaly(rain, kind):
    """past-only anomaly per month: same calendar month, years strictly before"""
    out = pd.Series(np.nan, index=rain.index)
    for t in rain.index:
        same = rain[(rain.index.month == t.month)]
        ref = same[same.index.year < t.year]    # earlier years only
        if len(ref) < 3: continue
        out[t] = (rain[t] - ref.mean()) / 100.0 # in units of 100 mm
    return out

ANOM[name] = pd.DataFrame({"A0": a, "A3": a.rolling(3).mean()})
```

#why[
- *An anomaly, not raw rain.* Rain is hugely seasonal (October is always wetter than March), and prices already carry their own seasonal pattern through $y_(t-11)$. What could add information is rain that is *unusual* for the time of year.
- *Earlier years only.* If "usual" included later years, the model would be using information from the future. ERA5-Land starts in 2010, so the first test year (2021) already has eleven earlier years of reference.
- *Two rain terms.* A single very wet month (A0) and a run of wet months (A3) can affect crops differently, for example a short storm versus waterlogged fields.
- *Units of 100 mm.* Only a scaling choice so the coefficients are readable; it does not change any forecast.
- *The same price terms in both models.* The lag set is chosen on the prices-only model and reused, so the *only* difference between the two forecasts is rain. That makes the comparison fair.
]

#note[*A later finding about A3.* A follow-up check (`forecast_rain_window_sensitivity.md`) noted that A3 includes month $t$, so it overlaps A0 (they are correlated 0.57). We re-ran everything with A3 over $t-3$ to $t-1$ instead. Nothing important changed: cabbage 19.5% instead of 19.7%, brinjal 10.4% instead of 12.4%, carrot 9.6% instead of 8.2%, and no vegetable changed label. The original version stays the main one because it was fixed in advance.]

=== Standing in the past: the expanding window

```python
# research_audit/forecast_backtest_v2.py  (core loop, trimmed)
for t in idx:                                  # each forecast origin, in time order
    tr = usable[usable.index < t]
    tr = tr[tr.index + pd.DateOffset(months=1) <= t]   # outcome known at t
    if len(tr) < WARM_ROWS: continue           # need at least 24 training rows
    te = usable.loc[t]
    best = min(LAGSETS,
               key=lambda k: aic(tr[LAGSETS[k]].values, tr.target.values))
    L = LAGSETS[best]
    preds = {"naive": te.y0, "snaive": te.y11}
    preds["AR"] = ols_pred(tr[L].values, tr.target.values, te[L].values)[0]
    for m in models:                           # rain models: same lags + A0, A3
        c = L + [m + "|A0", m + "|A3"]
        preds[m] = ols_pred(tr[c].values, tr.target.values, te[c].values)[0]
```

At every month, the model is refitted on all history up to that month (the window *expands* by one month each step) and forecasts one month ahead. Forecasts made from August 2021 onwards (targets September 2021 to October 2026) are the *test* forecasts: 62 per vegetable. Earlier forecasts, from the first month with 24 training rows, only build up a history of errors used for the uncertainty ranges.

#why[
- *Expanding window.* This is what a real forecaster would do: use everything known so far. Refitting every month means the model never uses a coefficient estimated with future data.
- *Test start August 2021.* Prices start in August 2016, the $y_(t-11)$ term needs a year of history, and the model needs at least 24 training rows, plus some earlier forecasts to build an error history for the ranges. August 2021 leaves about five years of genuine test forecasts.
]

=== Uncertainty ranges

Each forecast comes with an 80% range: the forecast plus the 10th and 90th percentiles of the model's *own past* forecast errors (at least 12 needed).

```python
q = np.quantile(errhist[mname], (0.10, 0.90))   # past errors only
lo, hi = p + q[0], p + q[1]
```

#why[This makes no assumption about the shape of errors (they need not be bell-shaped), and uses only errors the model really made before that date. Ranges are built in log terms, so in rupees they are lopsided: more room above than below, which suits prices that spike upwards.]

== How we measured error

For each vegetable, over the 62 test months, with $P_t$ the real price and $hat(P)_t$ the forecast (in rupees), and $e_t$ the error in log terms:

#table(
  columns: (1.3fr, 1.7fr, 2fr),
  table.header([Measure], [Formula], [Plain meaning]),
  [Mean absolute error, in rupees], [$1/n sum abs(P_t - hat(P)_t)$], [The typical miss in rupees per kilo. This is the "typical miss" card on page 3.],
  [Root mean square error, log], [$sqrt(1/n sum e_t^2)$], [An overall error that weights big misses more. The basis of the "% smaller overall error" figure.],
  [Mean absolute percentage error], [$100/n sum abs(P_t - hat(P)_t) / P_t$], [The typical miss as a share of the price. The "about a quarter" on page 5 is the median of this across the seven vegetables (24.8%).],
)

The gain from rain is

$ "gain" = 100 times (1 - "RMSE"_"rain" / "RMSE"_"prices only") $

For cabbage: $100 times (1 - 0.326 \/ 0.406) = 19.7%$.

#why[
- *Root mean square error as the main yardstick.* A forecast that is usually close but occasionally misses by 300 rupees is worse for a trader than one that misses a little more often but never wildly. Squaring the errors captures that. Using the log price keeps a 50-rupee miss on a 100-rupee vegetable from counting the same as on a 500-rupee one.
- *Mean absolute error in rupees for the public.* "Missed by about 52 rupees a kilo" is something anyone understands. That is why page 3 shows rupees, while the verdict is based on the root mean square error.
- *Why the two numbers differ.* For cabbage, the typical miss falls from about 52 to 42 rupees (about 18%), while the overall error falls 19.7%. They measure different things, so they need not match.
]

== Is the improvement real? The statistical tests

A difference in error over 62 months could be luck. Four tools were used together.

=== Why not a simple comparison

The usual test for comparing two forecasts is the *Diebold–Mariano test*: it checks whether the average difference in squared errors is far enough from zero. But when one model is the other plus extra terms (the rain model *contains* the prices-only model, so the models are *nested*), this test is unfair to the bigger model. Even if rain has a real effect, estimating its two extra coefficients adds a little noise to every forecast, which makes the bigger model look worse than it really is. So Diebold–Mariano is reported only as a supplement.

=== The Clark–West test (the main test)

Clark and West (2007) proposed a correction for nested models. For each test month:

$ f_t = e_("AR",t)^2 - [e_("rain",t)^2 - (hat(y)_("AR",t) - hat(y)_("rain",t))^2] $

The last term adds back the noise caused by estimating the extra coefficients. If rain is useless, $f_t$ averages zero; if rain helps, it is positive. The test statistic is the average of $f_t$ divided by its standard error, and the p-value is one-sided (we only ask whether rain *helps*).

```python
# research_audit/forecast_backtest_v2.py
# Clark-West adjusted loss differential
f  = e["AR"] ** 2 - (e[m] ** 2 - (piv["AR"].values - piv[m].values) ** 2)
# plain Diebold-Mariano loss differential
dl = e["AR"] ** 2 - e[m] ** 2
row.update(cw_t=nw_t(f), cw_p_one=p_one(nw_t(f)),
           dm_t=nw_t(dl), dm_p_two=p_two(nw_t(dl)))
```

=== Newey–West standard errors

Forecast errors in neighbouring months are related: if the model under-forecast in January, it often under-forecasts in February too. Ordinary standard errors assume independence and would be too small, making results look more certain. The *Newey–West* method (1987) widens the standard error to allow for this relation up to three months apart.

```python
def nw_t(x, lag=3):
    x = np.asarray(x, float); n = len(x); u = x - x.mean(); v = u @ u / n
    for k in range(1, lag + 1):             # add back neighbour covariances
        v += 2 * (1 - k / (lag + 1)) * (u[k:] @ u[:-k]) / n
    return x.mean() / math.sqrt(max(v, 1e-18) / n)
```

=== The moving-block bootstrap

A check that does not rely on any formula. We take the 62 monthly differences in squared error, cut them into blocks of consecutive months (3, 6 or 12 months long), and rebuild many new samples by drawing blocks at random, 4,000 times. If rain's advantage is real, the rebuilt samples should rarely show no advantage. Drawing *blocks* rather than single months keeps neighbouring months together, so their relation is preserved (Künsch, 1989).

=== Holm's correction for testing seven vegetables

Testing seven vegetables at the 5% level gives each one a 5% chance of a false alarm, and a much higher chance that *at least one* is a false alarm. Holm's method (1979) fixes this. Sort the seven p-values from smallest to largest; multiply the smallest by 7, the next by 6, and so on down to 1; and never let an adjusted value be smaller than the one before it.

#table(
  columns: (1.2fr, 1.2fr, 0.8fr, 1.2fr),
  align: (left, center, center, center),
  table.header([Vegetable], [Clark–West p], [Multiply by], [Holm-adjusted p]),
  [Brinjal], [0.000132], [7], [0.0009],
  [Cabbage], [0.000292], [6], [0.0018],
  [Carrot], [0.0057], [5], [0.0285],
  [Tomato], [0.0273], [4], [0.109],
  [Snake gourd], [0.0631], [3], [0.189],
  [Pumpkin], [0.1174], [2], [0.235],
  [Beans], [0.557], [1], [0.557],
)

Tomato is the instructive case: on its own, 0.027 is below 0.05, but after the correction it is 0.109. That is why tomato is "a hint, not proven".

=== The evidence label

The label shown on the dashboard comes straight from a rule written into the script:

```python
def classify(r):
    if r.rmse_gain_vs_AR_pct <= 0:
        return "worse or no gain"                # shown as "No help"
    boots = [r[f"boot_p_b{b}"] for b in (3, 6, 12)]
    if r.cw_p_holm < 0.05 and max(boots) < 0.10:
        return "supported (corrected)"           # shown as "Clear help"
    if r.cw_p_one < 0.05 or max(boots) < 0.05:
        return "suggestive (uncorrected only)"   # shown as "A hint, not proven"
    return "no reliable evidence"                # shown as "No clear effect"
```

#why[
- *Clark–West* because the models are nested; it is the standard test for exactly this situation.
- *Newey–West* because errors in neighbouring months are related.
- *The bootstrap* as a second opinion that does not depend on the normal-distribution approximation, which is rough with only 62 points.
- *Holm* because we tested seven vegetables and want the chance of even one false "clear help" to stay at 5%. Holm is less conservative than the simpler Bonferroni correction while still controlling that risk.
- *Requiring both* a corrected Clark–West result and every bootstrap check means "clear help" is a high bar on purpose.
]

== The results

Dambulla wholesale, national rain, 62 one-month-ahead forecasts per vegetable (September 2021 to October 2026):

#table(
  columns: (1.05fr, 0.95fr, 0.95fr, 0.8fr, 0.85fr, 0.9fr, 1.2fr),
  align: (left, center, center, center, center, center, left),
  table.header([Vegetable], [Typical miss, prices only (Rs/kg)], [Typical miss, with rain (Rs/kg)], [Gain], [Holm Clark–West p], [Bootstrap p (largest)], [Label]),
  [Cabbage], [52], [42], [19.7%], [0.002], [0.006], [Clear help],
  [Brinjal], [62], [53], [12.4%], [0.001], [0.004], [Clear help],
  [Carrot], [85], [81], [8.2%], [0.029], [0.033], [Clear help],
  [Tomato], [95], [90], [4.8%], [0.109], [0.16], [A hint, not proven],
  [Snake gourd], [42], [41], [1.8%], [0.189], [0.28], [No clear effect],
  [Pumpkin], [28], [27], [1.8%], [0.235], [0.20], [No clear effect],
  [Beans], [79], [79], [−1.5%], [0.557], [0.81], [No help],
)

*Reading the table.* Cabbage and brinjal are the strongest results. Carrot passes, but its Holm p-value of 0.029 is close to the 0.05 line, so we call it modest. Tomato would pass without the correction for seven tests but not with it. Beans got slightly worse with rain.

*Against the simple benchmarks.* The prices-only model beat the naive forecast for every vegetable, though only just for pumpkin (overall error 0.403 against 0.404) and beans. The seasonal naive forecast ("same as last year") was worst everywhere, because prices rose strongly over the period, especially in 2022.

=== A worked example: cabbage, January 2024

January 2024 was cabbage's most expensive month, Rs 452 a kilo. Standing at the end of December 2023 (price about Rs 323):

#table(
  columns: (1.6fr, 1fr, 1.6fr),
  table.header([Forecast for January 2024], [Rupees per kilo], [80% range]),
  [Naive (same as December)], [323], [],
  [Seasonal naive (same as January 2023)], [52], [],
  [Prices only], [237], [183 to 416],
  [Prices plus rain], [399], [320 to 670],
  [*Actual*], [*452*], [],
)

October, November and December 2023 were all much wetter than usual across the island (November by about 220 mm, December by about 70 mm). The rain model's two rain terms picked this up and it raised its forecast; the prices-only model did not see the jump coming. To be fair, the rain model is not always right: for December 2023 itself it forecast Rs 527 when the price was Rs 323, an overshoot. Over all 62 months the misses balance out in rain's favour for cabbage, which is what the 19.7% measures.

== Robustness: does the result depend on our choices?

These checks were run *after* the main result and are exploratory. None was used to choose the main specification.

#table(
  columns: (1.6fr, 0.8fr, 0.8fr, 0.8fr, 0.8fr, 0.8fr, 0.8fr, 0.8fr),
  align: (left, center, center, center, center, center, center, center),
  table.header([Gain from rain (%)], [Cab.], [Brin.], [Carr.], [Tom.], [Snake], [Pump.], [Beans]),
  [Main: national rain], [19.7], [12.4], [8.2], [4.8], [1.8], [1.8], [−1.5],
  [Rain around Dambulla], [18.3], [13.1], [8.2], [5.5], [2.8], [2.0], [−1.1],
  [Rain around Nuwara Eliya], [21.5], [11.8], [8.0], [5.4], [2.7], [1.1], [−2.1],
  [Fixed 2010–2015 "usual" rain], [16.8], [10.6], [4.9], [3.2], [0.9], [1.1], [−3.0],
  [Rain as a z-score], [15.9], [13.0], [5.9], [1.7], [2.2], [−0.1], [−1.4],
  [Monthly median price], [21.8], [10.9], [8.7], [4.3], [2.9], [2.5], [−1.2],
  [Without 2022 months], [20.4], [12.3], [8.5], [4.2], [1.2], [2.7], [−0.9],
  [First half of test period], [17.7], [6.3], [7.7], [8.3], [0.9], [3.3], [−1.3],
  [Second half of test period], [22.5], [16.7], [8.6], [0.0], [3.2], [−0.2], [−1.8],
  [Pettah market], [22.7], [9.7], [8.9], [7.2], [2.0], [2.2], [−2.9],
)

*What this shows.* Cabbage, brinjal and carrot stay clearly positive in every version and beans stays at or below zero. The ranking barely moves. Brinjal's gain is concentrated in the second half of the test period. Tomato's gain disappears in the second half, another reason it is only a hint. Defining "usual" rain differently shrinks the gains by a few points, so that choice matters somewhat, but the pattern across vegetables does not change.

#note[*Do not promote tomato.* One secondary version (rain around Dambulla, non-overlapping window) gives tomato a corrected p-value of 0.036. It is one of many versions, its bootstrap p-value is about 0.10, and the main tomato result (0.109) is not significant. Picking the best of many versions would be a "forking paths" search, so tomato stays a hint. On the dashboard, choosing *Around Dambulla* with *Pettah* also shows tomato as "Clear help"; that is the same kind of secondary result, and the speaking guide says to treat it as a check, not a finding.]

== How honest are the uncertainty ranges?

An 80% range should contain the real price in 8 of every 10 months.

#table(
  columns: (1.2fr, 1fr, 1fr),
  align: (left, center, center),
  table.header([Vegetable], [Prices only], [With rain]),
  [Cabbage], [0.69], [0.77],
  [Brinjal], [0.71], [0.84],
  [Carrot], [0.73], [0.74],
  [Tomato], [0.69], [0.74],
  [Snake gourd], [0.77], [0.73],
  [Pumpkin], [0.84], [0.84],
  [Beans], [0.69], [0.77],
)

Most are below 0.80, so the ranges are somewhat too narrow, mainly because the error history was short at the start and the 2022 errors were large. With 62 points, each coverage figure is itself uncertain by about 0.05. We present them as honest first approximations, not as calibrated ranges. Page 3 shows them as "Price landed inside our range: 8 in 10 (prices only: 7 in 10, aim: 8)" for cabbage.

= From analysis to dashboard

== What went in, and why

#table(
  columns: (1.4fr, 0.6fr, 2fr),
  table.header([Analysis], [Page], [Why it earned a place]),
  [Price swings (cheapest, dearest, biggest move, share of big moves)], [1], [It makes the problem felt in ten seconds, with numbers anyone understands.],
  [National rain and the rain map], [1], [It shows where rain falls and that it is uneven, and sets up the question.],
  [Lagged correlations of rain and price changes], [2], [It lets the viewer discover the clue themselves, which is more convincing than being told.],
  [The forecasting test: typical miss, gain, verdict, ranges], [3], [It is the actual evidence and answers the research question.],
  [Regional rain and the Pettah market as controls], [3], [It lets anyone see that the result holds up, without a robustness table.],
  [All seven vegetables in one bar chart], [3], [It shows at a glance that the effect differs by vegetable, which is the finding.],
  [Rain and rice harvest, rice import share, exchange rate], [4], [It connects the study to the wider food system, honestly separated.],
  [The three findings, with a guess first], [5], [A clear ending; the guess makes people pay attention to the answer.],
)

== What stayed out, and why

#table(
  columns: (1.5fr, 2fr),
  table.header([Analysis], [Why it is not on screen]),
  [Naive and seasonal naive benchmarks], [Useful for us, but a third and fourth forecast line would confuse the public. Explained verbally if asked.],
  [The p-values, test names and bootstrap], [The dashboard is for the general public. The tests are turned into one plain verdict; the detail is for judges' questions.],
  [Fixed-climatology, z-score and median versions; half-sample splits; 2022 exclusion; non-overlapping rain window], [These are checks on the main result. Showing them all would invite viewers to pick the version they like. They stay in the speaking guides.],
  [Production against imports correlation], [Driven by two years; the import share chart tells the same story more honestly.],
  [Exchange rate to price pass-through], [We could not estimate it without a consumer price index, so we do not show a number.],
  [Temperature, district analysis, trade partners, HARTI, World Bank data], [Not used in the final study for the reasons in sections 1 and 2.],
)

== How the dashboard reads the results

The dashboard re-estimates nothing. It reads the stored outputs of the forecasting test from `research-story/data/` and turns them into plain words.

```python
# research-story/story/metrics.py
PLAIN = {"supported (corrected)": "Clear help",
         "suggestive (uncorrected only)": "A hint, not proven",
         "no reliable evidence": "No clear effect",
         "worse or no gain": "No help"}

def rain_kpis(veg, region, market):
    model = f"AR+rain:{region}"
    base, rain = _row(veg, "AR", market), _row(veg, model, market)
    label = PLAIN[rain.evidence]               # the label stored by the backtest
    return dict(miss_without=float(base.mae_lkr), miss_with=float(rain.mae_lkr),
                gain_pct=float(rain.rmse_gain_vs_AR_pct), label=label, ...)
```

Page 1's "biggest one-month move" never jumps over a missing month, so a gap in the data cannot create a fake swing:

```python
def month_changes(s):
    """Percent change between consecutive calendar months; a missing month gives NaN."""
    return s.asfreq("MS").pct_change(fill_method=None).dropna(how="all") * 100
```

The rain map hides squares that sit wholly over the sea (ERA5-Land's land mask is coarser than the coastline), but only for drawing. All rainfall numbers still use every land square.

== Automated checks

The folder `research-story-materials/tests/` holds 28 automated tests. They check, among other things, that the cards show the stored results (cabbage 19.7%, "Clear help"; beans "No help"), that the rain map reproduces the national and Dambulla series, that page 2 reproduces the audited correlation table, and that every page runs without error. Separately, a claim audit checked all 55 numbers in the earlier ten-slide version against the analysis outputs; all were verified after wording fixes.

= Glossary

/ Autoregressive (AR) model: a model that forecasts a series from its own past values.
/ Nested models: two models where one is the other plus extra terms. The rain model is nested in the prices-only model.
/ Out-of-sample forecast: a forecast checked against data the model was not fitted on.
/ Expanding window: refitting the model at each step on all data up to that point.
/ Lag: a value from an earlier month. "Lag 1" means one month earlier.
/ Anomaly: how far a value is from its usual level for the time of year.
/ z-score: an anomaly divided by the usual spread (standard deviation), so it is measured in "standard deviations".
/ Detrending: removing a straight-line trend so that two series that both rise over time do not look linked for that reason alone.
/ Correlation (r): from −1 to +1, how closely two series move together in a straight line.
/ p-value: if there were no real effect, the chance of seeing a result at least this strong. Small means "unlikely to be luck".
/ Permutation test: computing a p-value by shuffling the data many times.
/ AIC (Akaike information criterion): a score that rewards fit and penalises extra terms, used to choose the lag set.
/ Root mean square error (RMSE): the square root of the average squared error; weights large misses heavily.
/ Mean absolute error (MAE): the average size of the miss.
/ Mean absolute percentage error (MAPE): the average miss as a percentage of the real value.
/ Clark–West test: a test of whether a larger nested model forecasts better, corrected for the noise from its extra terms.
/ Diebold–Mariano test: a general test comparing two sets of forecast errors.
/ Newey–West standard error: a standard error that allows for related errors in neighbouring months.
/ Block bootstrap: rebuilding many samples from blocks of consecutive data to judge how much a result could vary by chance.
/ Holm correction: adjusting p-values when several tests are run, so the chance of any false alarm stays at the chosen level.
/ Coverage: the share of times the real value fell inside the forecast range.
/ Reanalysis: a complete weather record made by a model corrected with observations.

= References

- Clark, T. E. and West, K. D. (2007). Approximately normal tests for equal predictive accuracy in nested models. _Journal of Econometrics_, 138(1), 291–311.
- Diebold, F. X. and Mariano, R. S. (1995). Comparing predictive accuracy. _Journal of Business & Economic Statistics_, 13(3), 253–263.
- Holm, S. (1979). A simple sequentially rejective multiple test procedure. _Scandinavian Journal of Statistics_, 6(2), 65–70.
- Künsch, H. R. (1989). The jackknife and the bootstrap for general stationary observations. _Annals of Statistics_, 17(3), 1217–1241.
- Muñoz-Sabater, J. et al. (2021). ERA5-Land: a state-of-the-art global reanalysis dataset for land applications. _Earth System Science Data_, 13(9), 4349–4383.
- Newey, W. K. and West, K. D. (1987). A simple, positive semi-definite, heteroskedasticity and autocorrelation consistent covariance matrix. _Econometrica_, 55(3), 703–708.
