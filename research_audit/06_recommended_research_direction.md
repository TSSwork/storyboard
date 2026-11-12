# 06 — Recommended Research Direction (revised: S1+ primary)

## Decision
**Primary chapter - S1+ Weather-informed vegetable price forecasting.**
**Supporting chapters** - paddy production and weather (S2), rice import dependency (S3) and FX exposure (S4), providing food-system context. They do not feed the forecasting model.

**Title:** *Weather Variability and Short-term Vegetable Price Forecasting in Sri Lanka: An Empirical Study Using Rainfall and Market Price Data*

**Central question:** Does incorporating rainfall information improve short-term forecasts of selected vegetable prices in Sri Lanka, and does the improvement differ between commodities?

The broader motivation (weather, food prices and import dependency) is unchanged. The forecasting experiment supplies the clearest empirical contribution because it is the only link with enough data (~120 monthly points) for an out-of-sample test.

## Why this changed from the earlier "three-module" plan
* The original integrated chain is only supportable for rice and only at n = 14-16.
* The pilot and `forecast_backtest_v2.py` show a clean, commodity-specific result on 62 out-of-sample months.
* FX did not improve forecasts, so it belongs to the supporting economic analysis, not the forecasting model.

## What the evidence currently says (v2, exploratory)
| Vegetable | RMSE gain vs price-only AR | Holm-adj. Clark-West p | Label |
|---|---|---|---|
| Cabbage | +19.7 % | 0.002 | supported (corrected) |
| Brinjal | +12.4 % | 0.001 | supported (corrected), gain concentrated in 2nd half |
| Carrot | +8.2 % | 0.029 | supported but borderline |
| Tomato | +4.8 % | 0.109 | exploratory only |
| Snake gourd | +1.8 % | 0.189 | no reliable evidence |
| Pumpkin | +1.8 % | 0.235 | no reliable evidence |
| Beans | -1.5 % | 0.557 | rain does not help |

Details, robustness (Dambulla/Nuwara Eliya boxes, monthly median, climatology variants, 2022 exclusion, Pettah) and caveats are in `forecast_backtest_report_v2.md`. The test window was already seen in the pilot, so this is not an independent confirmation.

## What can and cannot be concluded
| Supportable | Not supportable |
|---|---|
| Past rainfall adds out-of-sample 1-month-ahead information for Dambulla cabbage and brinjal (and modestly carrot) beyond past prices | That rain causes price changes |
| Benefit differs by vegetable; some show none | That results hold for other markets, vegetables or national consumers |
| Pettah shows the same pattern (consistency, not replication) | Skill at 2-3 month horizons (needs rainfall forecasts) |
| Forecast errors remain large (MAPE about 24-40 %) | Calibrated 80 % intervals (empirical coverage 0.69-0.84) |
| FX did not improve these forecasts | That FX is irrelevant to food prices |

## Supporting chapters (unchanged conclusions)
* **Paddy (S2):** season-level, n = 16; Yala rain vs harvested/sown ratio r = +0.68 is the most credible signal; district panel needs polygons.
* **Rice imports (S3):** production vs imports r = -0.79 (n = 15), -0.46 without 2017 and 2022; apparent import share only, not self-sufficiency.
* **FX (S4):** needs CPI/NCPI; rice and imported items co-move with LKR at 0-2 month lag; no pass-through magnitudes without a deflator.

## Next steps
1. Done: v2 backtest (`forecast_backtest_v2.py`) with outputs `forecast_results_v2.csv`, `forecast_model_comparison_v2.csv`, `forecast_intervals_v2.csv`, `forecast_backtest_report_v2.md`, `forecast_charts_v2/`.
2. Cheap, worthwhile: collect CPI/NCPI (for S4 and an optional real-price check) and district polygons (to replace hand-drawn rain boxes).
3. Optional sensitivities not yet run: other target markets, a fixed-lag-set variant matching the pilot, repeated-origin diagnostics on interval calibration.
4. Do not add machine learning or an application. Keep the model as a research instrument.
5. Wider-context chapters can be written from the existing 03 / 04 / 07 findings.

## Risks to manage
* Multiple-testing: the Holm family is the 7 primary tests only; secondary specs are exploratory.
* Pilot-selection caveat: the earlier look at the test window is not corrected for.
* Anomaly-definition sensitivity: gains shrink with a fixed 2010-2015 climatology or z-scores.
* ERA5 `tp` bug: only the corrected derived series are used.
* Data caveats (CBSL gaps, HARTI duplicates, Comtrade 2018/2025) remain as in `07_data_quality_report.md`.
