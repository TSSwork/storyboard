# 03 — Research Feasibility

Method: for each question I located the required variables, checked temporal/commodity/geographic overlap, and ran a first-pass, *associational* test where one is possible (`feasibility_tests.py`, `feasibility_prices.py`). Permutation p-values (5,000 shuffles; no scipy); linear trend removed before correlating series with a trend. **None of these results is causal.**

## Overlap actually available
| Pair | Overlap | Resolution | Usable n |
|---|---|---|---|
| ERA5 × DCS national paddy | 2010–2025 | seasonal, national | 16 Maha + 16 Yala |
| ERA5 × DCS district | 2010–2025 | needs district weather — **absent** | – |
| DCS/FAO production × Comtrade/FAO imports (rice) | 2010–2024 | annual, national | 15 (Comtrade 14, 2018 missing) |
| Comtrade/FAO imports × HARTI prices | 2015-06–2025 | annual vs weekly | ≈10 annual points, or monthly price vs annual quantity (weak) |
| FX × HARTI rice/commodity prices | 2015-06–2026-10 | monthly | ≈131 |
| ERA5 × CBSL veg prices | 2016-08–2026-10 | monthly | ≈118 |
| ERA5 × HARTI prices | 2015-06–2026-10 | weekly/monthly | ≈130 months |

## Feasibility matrix
| # | Research question | Required variables | Available datasets | Missing | Feasibility | Recommended approach | First evidence |
|---|---|---|---|---|---|---|---|
| Q1 | Do rainfall / temperature relate to paddy production? | season rain, temp; production, yield, harvested/sown | ERA5 (corrected), DCS national | district weather, irrigation share (partly in DCS district), radiation, ENSO index | **PARTIALLY FEASIBLE** | Season-level descriptive + detrended correlation, Maha and Yala separately; n = 16 each; add district panel only if district boundaries are obtained | Detrended, n = 16. Yala: rain vs harvested/sown ratio r = +0.68 (p = 0.002), rain vs harvested extent +0.43 (0.09), temp vs harvested extent −0.50 (0.05); rain vs yield −0.16 (0.56), vs production +0.32 (0.23). Maha: rain vs harvested extent +0.50 (0.054), yield −0.34 (0.20), production +0.26 (0.32). 32 tests, so ≈1.6 false positives are expected at 5 % — treat as hypothesis-generating; the Yala harvested/sown signal (drought-driven crop loss) is the most credible |
| Q2 | Can Maha and Yala be analysed separately? | seasons | DCS national & district, ERA5 | – | **FEASIBLE** | Yes; Maha window Oct–Feb, Yala Mar–Aug (state as assumption; check sensitivity to ±1 month) | rain mean 1,123 mm (Maha), 684 mm (Yala) |
| Q3 | Do production shortfalls coincide with higher imports (rice)? | production, imports | DCS, FAO, Comtrade, CBSL | stocks, consumption | **FEASIBLE (rice); not for other commodities** | Annual detrended production vs imports; show 2014, 2017, 2022 episodes | r = −0.79 (perm p = 0.002, n = 15, FAO); Comtrade −0.82; Spearman −0.59; excluding 2017 & 2022 r = −0.46 (n = 13) — direction robust, size driven by two events; next-year lag +0.30 (n.s.) |
| Q4 | Which commodities have highest import dependency? | production, imports, exports per commodity | FAOSTAT (prod + trade), Comtrade | stock changes, feed/seed/waste, non-food use | **PARTIALLY FEASIBLE** | *Apparent* dependency = imports / (production + imports − exports), reported as "import share of apparent supply" for ≈10–20 commodities where FAOSTAT item names match (rice, wheat — no domestic production, maize, onion, potato, pulses, sugar, chillies…); **not** self-sufficiency | Rice import share of apparent supply 0.5 %–29.6 % (2010–2024; no stock/seed/feed adjustment) |
| Q5 | How do import values and quantities change over time? | HS6 qty/value | Comtrade, FAOSTAT, CBSL | 2018 (Comtrade), 2025 completeness | **FEASIBLE** | HS chapters 01–24 by year; HS-revision concordance for H3→H6; use FAOSTAT for 2018 and CBSL for 2025 rice | Agri imports (HS 01–24) $1.9 bn (2010) → $3.1 bn (2025, partial); total M $12.4–21.5 bn |
| Q6 | Is import partner concentration changing? | partner × HS | Comtrade | – | **FEASIBLE** | HHI by commodity/year using partnerCode ≠ 0 rows only | Data present for all 15 years |
| Q7 | Are exchange-rate movements associated with imported food costs? | USD/LKR, import unit values, domestic prices, CPI | Spot FX (daily 2010–2026), HARTI/CBSL prices, Comtrade unit values | **CPI/CCPI deflator**, world food price index | **PARTIALLY FEASIBLE** | Monthly Δlog(price) vs Δlog(USD/LKR), lags 0–6; compare imported vs domestic items; event study around Mar-2022 float | Rice (all-market mean): r(lag0) 0.30–0.36, r(lag1) 0.27–0.35, ≈0 by lag 3, negative at 4–5 (n = 131). Imported items: dried chillies 0.32, red dhal 0.38; big onion 0.05, imported potato 0.13. Q4-2021→Q4-2022: imported chillies +184 %, imported potato +54 %, big onion +31 % but domestic Nadu rice +81 % and N'Eliya potato +122 % → **general inflation confounds**; imported vs domestic comparison needs a deflator |
| Q8 | Are domestic prices associated with domestic production? | production, prices | DCS seasonal, HARTI farmgate/retail rice | – | **PARTIALLY FEASIBLE** | Annual/seasonal; ≤ 12 yrs; descriptive only | Not yet run: only ≈10 annual points overlap |
| Q9 | Are prices associated with weather (vegetables)? | rain anomalies, prices | ERA5, CBSL daily, HARTI veg | district weather; production volumes | **FEASIBLE (associational)** | Monthly: Δlog price (seasonally demeaned) vs national rain z-anomaly, lags 0–3, and 3-month cumulative anomaly | Lag-1 r: cabbage +0.60, carrot +0.44, brinjal +0.40, tomato +0.26, snake gourd +0.20, pumpkin +0.14, beans +0.08 (n ≈ 120). 10 of 28 lag-tests p < 0.05 (1.4 expected by chance). 3-month cumulative anomaly lag 1: cabbage +0.37, carrot +0.34 (p ≤ 0.001). Wetter-than-normal months precede price rises for leafy/up-country crops — consistent with supply disruption but national rainfall is not the growing-area rainfall |
| Q10 | Which commodities are most weather-vulnerable? | as Q9 across commodities | CBSL + HARTI (≈45 + 268 series) | commodity-level production | **PARTIALLY FEASIBLE** | Rank commodities by lag-1/3-mo anomaly effect with FDR correction | Strong heterogeneity already visible (cabbage/carrot vs beans/tomato) |
| Q11 | Integrated chain weather → production → imports → prices | all | all | district resolution, deflator, other crops | **PARTIALLY FEASIBLE (rice only)** | Rice-only chain on annual/seasonal scale as a *case study* inside a wider study | Links individually exist: drought→harvested/sown (Yala), production→imports (r −0.79), imports/FX→rice price (r 0.3 monthly); sample sizes 14–16 |
| Q12 | District-level weather–paddy | district weather | DCS district | district boundaries + gridded weather aggregation | **NOT FEASIBLE now** (cheap to fix) | Needs a district shapefile (GADM/OSM) — then ERA5 grid cells can be mapped | – |
| Q13 | Non-paddy crop production vs weather | crop production by season | FAOSTAT (annual national only) | seasonal, regional | **NOT FEASIBLE** beyond annual national | Optionally annual FAOSTAT yields vs annual rain (n = 15) | – |
| Q14 | Self-sufficiency ratios | full supply-utilisation accounts | – | stocks, seed, feed, waste, food balance | **NOT FEASIBLE** | Report apparent import share only | – |
| Q15 | Imported-commodity price vs import unit value | monthly import value+qty by HS | Comtrade annual only (monthly 2012 only) | monthly Comtrade | **NOT FEASIBLE** monthly; annual only (n ≈ 10) | Use annual unit values as context | – |

## Temporal alignment rules
1. Seasons: Maha year `Y/Y+1` ↔ Oct Y … Feb Y+1; Yala `Y` ↔ Mar–Aug Y; harvest lands in Q1/Q3 of the following calendar months.
2. Calendar-year paddy = Maha(`Y−1/Y`) + Yala(`Y`).
3. Prices to monthly means; weather to monthly sums (rain) / means (temperature); imports annual (CBSL monthly 2021+).
4. Use first differences or deviations from trend / month-of-year for any price series.

## What the evidence does **not** support
* Any claim that rain "causes" yield changes (n = 16, no district resolution, trend and technology change).
* Self-sufficiency or "food security" claims from import ratios.
* Attributing 2022 price rises to FX alone (general inflation not controlled).
* Using World Bank RTFP or FAOSTAT rice as independent confirmation of DCS/HARTI/Comtrade.
