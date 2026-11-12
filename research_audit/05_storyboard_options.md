# 05 — Alternative Research Storyboards (ranked)

> **Update (S1+ decision).** After the pilot and the v2 backtest (`forecast_backtest_report_v2.md`), **S1+ is the primary chapter**. S2 (paddy) and S3/S4 (rice imports, FX exposure) are supporting chapters that give food-system context; they are not inputs to the forecasting model. S5 stays a descriptive synthesis table.

Ranking = feasibility x analytical strength, judged on the evidence in `03_research_feasibility.md`, not on resemblance to the original idea.

| Role | Storyboard | Feasibility | Analytical strength | Main reason |
|---|---|---|---|---|
| **Primary** | **S1+ Weather-informed vegetable price forecasting** | High | High | ~120 monthly obs, 7 commodities, clean CBSL series, out-of-sample test possible; rain gains survive correction for cabbage, brinjal (and carrot, borderline) |
| Supporting | S2 Rice food system: weather -> paddy -> imports -> price | Medium-high | Medium-high | Every link has data; n = 14-16, national only |
| Supporting | S3 Import dependency structure (Comtrade + FAOSTAT) | High | Medium | Descriptive; dependency is "apparent" |
| Supporting | S4 Exchange-rate exposure of food prices | Medium | Medium | Needs CPI to separate FX from inflation; FX did **not** improve vegetable forecasts, so it stays out of S1+ |
| Synthesis | S5 Food-system vulnerability profile | Medium-low alone | Low-medium | Descriptive table only, no composite weights |

---

## S1+ - Weather-informed Vegetable Price Forecasting (PRIMARY)
* **Central RQ:** Does adding rainfall information improve one-month-ahead forecasts of selected Sri Lankan vegetable prices, and does the improvement differ by commodity?
* **Role of the model:** a research instrument (AR vs AR + rain), not a product. The storyboard must still make sense with the model removed (S1 below is that descriptive story).
* **Data:** CBSL Dambulla wholesale daily prices -> monthly mean (>= 10 days) -> ln; corrected ERA5-Land rain (national primary; Dambulla and Nuwara Eliya boxes secondary); Pettah as a market robustness check.
* **Design (frozen):** origin month t uses prices and rain through t to forecast month t+1; expanding window; past-only climatology (anomaly in mm primary, z-score sensitivity); AIC-chosen lag set shared by both models; baselines naive, seasonal naive, AR; no FX; 1-month horizon primary (2-3 months would need rainfall forecasts).
* **Inference:** Clark-West (nested), HAC, moving-block bootstrap (3/6/12), Holm across 7 commodities for the primary spec; BH exploratory.
* **v2 result (exploratory, 62 forecasts):** RMSE reduction vs price-only AR: cabbage 19.7 %, brinjal 12.4 %, carrot 8.2 %, tomato 4.8 %, snake gourd 1.8 %, pumpkin 1.8 %, beans -1.5 %. Holm-corrected CW p: cabbage 0.002, brinjal 0.001, carrot 0.029, others >= 0.11. 80 % intervals under-cover (0.69-0.84).
* **Storyboard order:** problem -> data and quality -> price behaviour -> rain anomalies and regions -> exploratory rain-price association (S1 below) -> forecasting experiment -> which commodities benefit (with uncertainty) -> interpretation -> food-system context (S2-S4) -> limitations.
* **Not claimed:** causality; representativeness beyond Dambulla/Pettah; calibrated intervals; skill at 2-3 months.

## S1 — Rainfall Anomalies and Vegetable Price Dynamics in Sri Lanka (2016–2026) *(descriptive base of S1+)*
* **Main RQ:** Do monthly rainfall anomalies precede price movements of vegetables in Sri Lankan wholesale/retail markets, and which vegetables are most sensitive?
* **Supporting RQs:** (a) What are the lags (0–3 months, cumulative 3-month anomalies)? (b) Is the response stronger for up-country than low-country vegetables? (c) Do Pettah/Dambulla/Narahenpita and wholesale/retail respond differently? (d) Is the relationship stable before/after 2022?
* **Datasets / variables:** `derived/era5_monthly.csv` (rain, t2m); `raw/cbsl-daily-prices.csv` (Beans, Carrot, Cabbage, Tomato, Brinjal, Pumpkin, Snake gourd… ×4 market-types); HARTI `retail_vegetables`, `summary_retail`; (optional) sub-regional ERA5 means.
* **Methods:** monthly mean log price; seasonal demeaning; Δlog; rain z-anomaly vs month climatology; lagged correlation with permutation p-values; then distributed-lag regression with HAC errors, FDR correction across commodities; robustness: wholesale vs retail, drop 2022.
* **Visuals:** anomaly-vs-price heat map (commodity × lag), event plots (e.g. Nov-Dec heavy-rain months), scatter with lowess.
* **Data gaps:** growing-area rainfall (national mean now), production volumes, CPI.
* **Feasibility:** High. **First result:** lag-1 r = +0.60 cabbage, +0.44 carrot, +0.40 brinjal; 3-month cumulative anomaly +0.37 cabbage, +0.34 carrot (p ≤ 0.001); 10/28 tests p < 0.05 vs 1.4 expected.
* **Limitations:** correlation, national rain, autocorrelation, short series (118 months), many tests.
* **Contribution:** quantifies weather sensitivity of consumer vegetable prices — an under-documented link for Sri Lanka; identifies commodity-specific vulnerability.

## S2 — From Rain to Rice: Weather, Paddy Production and Import Response in Sri Lanka
* **Main RQ:** How do Maha and Yala seasonal weather conditions relate to paddy production, and do production shortfalls translate into rice imports and retail price pressure?
* **Supporting RQs:** (a) Rain/temperature vs sown, harvested, harvested/sown ratio, yield by season. (b) Do shortfalls (2014, 2017, 2022 episodes) coincide with import surges? (c) How do imports and FX relate to retail rice prices? (d) Are district patterns consistent (needs M2)?
* **Datasets:** ERA5 corrected; DCS national + district; FAOSTAT/Comtrade/CBSL rice imports; HARTI `retail_rice` / `summary_retail`; USD/LKR spot.
* **Methods:** season windows (Oct–Feb, Mar–Aug), detrended correlation, harvested/sown ratio as drought indicator; case-study timeline of the 3 shock years; annual production-vs-import scatter (Spearman and leave-two-out); local projection / lag correlation for price; optional district panel with fixed effects once weather is mapped to districts.
* **Visuals:** season rain vs ratio scatter; dual-axis production/imports 2010–2025; event timeline; district choropleth.
* **Gaps:** district weather, stocks, CPI.
* **Feasibility:** Medium-high. **First results:** Yala rain vs harvested/sown r = +0.68 (p = 0.002, n = 16); production vs imports r = −0.79 (p = 0.002, n = 15; excluding 2017 & 2022 r = −0.46); Δlog rice price vs ΔFX r ≈ 0.35 at lag 0–1.
* **Limitations:** n ≤ 16, national averages, technology/policy trends (e.g. 2021–22 fertiliser restrictions, not in the data), imports driven by policy, and the 2022 import surge is confounded with the economic and FX crisis.
* **Contribution:** a coherent causal-chain *description* for the country's staple, joined across four independent-ish sources, with explicit evidence strength at each link.

## S3 — Sri Lanka's Agricultural Import Dependency and Its Structural Change, 2010–2025
* **Main RQ:** How concentrated and how dependent is Sri Lanka's agri-food import structure, and how has it changed?
* **Supporting RQs:** which HS chapters/commodities dominate; partner concentration (HHI) per commodity; apparent import share (FAOSTAT) for ≈15 staples; HS-revision-safe trends; response to 2022 crisis.
* **Datasets:** Comtrade (partnerCode ≠ 0 for partners, `M` flow, HS 01–24), FAOSTAT trade + production, CBSL import series.
* **Methods:** shares, HHI, CAGR, concordance across H3→H6 at HS4 level, unit values, Lorenz/Treemap of partners.
* **Visuals:** stream chart of import value by chapter; partner network/heat map; dependency scatter (import share vs concentration).
* **Gaps:** 2018, 2025, stocks/non-food use.
* **Feasibility:** High. **Limitations:** apparent-supply caveat; unit values ≠ prices; 2025 partial.
* **Contribution:** descriptive atlas of vulnerability; foundation for S5.

## S4 — Exchange-Rate Exposure of Food Prices
* **Main RQ:** How strongly and with what lag do LKR depreciations pass through to retail food prices, and do imported items differ from domestic ones?
* **Datasets:** USD/LKR spot; HARTI `summary_retail` (imported vs local chillies, onion, potato, dhal, rice); CBSL daily; **CPI (to collect, M1)**; Comtrade unit values.
* **Methods:** Δlog pass-through with lags 0–6; relative-price (imported ÷ domestic) to cancel inflation; Mar-2022 event study; local projections.
* **First result:** rice Δlog vs ΔFX r = 0.30–0.36 (lag 0–1), fading by lag 3; imported chillies 0.32, dhal 0.38, big onion ≈ 0.05; Q4-21→Q4-22 imported chillies +184 % but domestic N'Eliya potato +122 % (inflation confound).
* **Feasibility:** Medium (high after M1). **Limitations:** policy shocks (import controls, taxes) not in data; one big regime change dominates.
* **Contribution:** pass-through estimates by commodity type.

## S5 — A Food-System Vulnerability Profile (synthesis)
* **Main RQ:** Which commodities are simultaneously import-dependent, weather-sensitive and FX-exposed?
* **Method:** one table, three indicators (S3 dependence, S1/S2 weather sensitivity, S4 pass-through), ranked descriptively — **no composite weights**.
* **Feasibility:** depends on S1–S4; **use as discussion chapter**, not as a standalone model.
