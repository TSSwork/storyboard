# Forecast backtest v2 - validation and rain-window sensitivity

**Status: exploratory specification-sensitivity analysis.** The 62 test months were already examined in the pilot and in v2, so nothing here is independent confirmation. The v2 script, report and outputs are unchanged. The original primary specification stays primary; no specification below was promoted after seeing results.

Script: `validate_v2.py` (self-contained re-implementation; nothing imported from v2). Outputs in this folder: `rain_window_comparison.csv`, `rainfall_completeness.csv`, `evaluation_samples.csv`, `interval_coverage.csv`, `predictor_overlap.csv`, `rain_window_comparison.png`.

## 1. What the rainfall predictors actually are
At forecast origin t (last completed month; target = price of month t+1):

| Spec | A0 | A3 | Months in A3 |
|---|---|---|---|
| **v2 primary (`*_incl`)** | anomaly of month t | mean anomaly of t-2, t-1, t | **includes t**, so it overlaps A0 (test-period corr(A0, A3) = **0.57**) |
| Sensitivity (`*_prior`) | anomaly of month t | mean anomaly of t-3, t-2, t-1 | non-overlapping (corr = **-0.05**) |

Both use only rain observed by the end of t, so neither leaks future information. The v2 script defined A3 as the mean over t-2..t and the v2 report stated this correctly, but the overlap with A0 was not discussed; if a non-overlapping design was intended, v2 did not implement it. A mean and a sum of three months give identical OLS predictions (coefficient scale only). Anomaly = (rain - mean of the same calendar month over earlier years only) / 100 mm, as in v2.

## 2. Implementation checks (all pass; assertions are in the script)
| Check | Result |
|---|---|
| Reproduction of v2 | the primary AR+rain forecasts (434 forecasts) match `forecast_results_v2.csv` with max abs difference 0.0 |
| Rain features use data <= t only | each feature recomputed from rain truncated at t, for 570 spec-origin pairs (2019 on): identical |
| Price inputs and target | y_t, y_t-1, y_t-11, target = y_t+1 verified against the price series at every origin |
| Training targets known at origin | max training-row target month <= t asserted at every origin |
| AIC lag selection | uses training rows only; both AR and AR+rain use the same lag set (asserted `c[:len(L)] == L`) |
| Climatology | same calendar month, years strictly before year(t); features recomputed from truncated data match |
| Missing prices | not filled: each series has 123 monthly points and 1 missing month in its span; rows with missing inputs are dropped (111 usable rows) |
| Interval history | each error entering a quantile has its target month <= t (asserted) |
| Ridge on intercept | v2 penalises the intercept (lam = 1e-6). Leaving it unpenalised changes forecasts by at most 3.4e-6 in log price: immaterial; v2 behaviour kept so results reproduce |
| Bootstrap p | now (count + 1)/(4000 + 1); same seed and blocks 3/6/12. This only moved p-values slightly (e.g. cabbage b3 0.00625 -> 0.0057 because the resampling stream differs) and removes exact zeros |

## 3. Rainfall completeness
Report: `rainfall_completeness.csv` (days observed per month for national, Dambulla box, Nuwara Eliya box).
* National, Dambulla box and Nuwara Eliya box are complete for **all** months except two, identical for all three: 2009-12 (1 day, the leading accumulation timestep) and 2026-11 (5 of 30 days). Incomplete months are set to missing, never used as partial totals.
* Box sizes are 36 land cells each (national 541). v2 did not check box completeness explicitly; it is complete in practice, so v2 regional results are unaffected.

## 4. Evaluation samples
`evaluation_samples.csv`: for every vegetable the first origin is 2021-08, the last origin 2026-09 (target 2026-10), **n = 62**. Requiring all six rain specs to be present gives exactly the same dates as requiring only the primary one, so the secondary specs do not shape the primary evaluation window. The 2026-11 partial month is the only rain-driven exclusion. Binding constraints are the 24-row warm-up, the y(t-11) lag, and one missing price month.

## 5. Primary vs non-overlapping A3 (national rain, Dambulla wholesale, 62 forecasts)
RMSE gain = reduction of log RMSE vs the price-only AR on the same dates; CW p one-sided, Newey-West lag 3; Holm over the 7 commodities within each spec; bootstrap p unadjusted, corrected for finite simulations.

| Vegetable | Gain primary | Gain prior | Change (pp) | MAPE prim / prior (%) | CW Holm p prim / prior | Boot p (b3,b6,b12) primary | Boot p (b3,b6,b12) prior | Evidence prim -> prior |
|---|---|---|---|---|---|---|---|---|
| Cabbage | 19.7 | 19.5 | -0.2 | 24.0 / 24.6 | 0.0018 / 0.0010 | .006 .006 .001 | .005 .008 .003 | supported -> supported |
| Brinjal | 12.4 | 10.4 | -2.0 | 24.7 / 25.2 | 0.0009 / 0.0013 | .003 .003 .003 | .015 .014 .017 | supported -> supported |
| Carrot | 8.2 | 9.6 | +1.5 | 26.9 / 26.5 | 0.0285 / 0.0132 | .031 .028 .023 | .028 .023 .021 | supported -> supported |
| Tomato | 4.8 | 4.8 | +0.0 | 39.7 / 40.2 | 0.109 / 0.077 | .14 .16 .16 | .14 .16 .15 | suggestive -> suggestive |
| Snake gourd | 1.8 | 2.0 | +0.1 | 24.8 / 24.8 | 0.189 / 0.200 | .27 .27 .29 | .24 .24 .28 | none -> none |
| Pumpkin | 1.8 | 1.6 | -0.2 | 25.5 / 25.9 | 0.235 / 0.298 | .20 .20 .21 | .24 .24 .21 | none -> none |
| Beans | -1.5 | -2.5 | -1.0 | 23.1 / 23.4 | 0.557 / 0.776 | .78 .79 .82 | .89 .88 .89 | worse -> worse |

**Reading:** the direction and the commodity ranking do not depend on whether the current month is counted twice. Cabbage is unchanged; brinjal's gain shrinks by 2 pp (still corrected-significant, bootstrap p about 0.015); carrot's rises by 1.5 pp; the three weak vegetables and beans stay weak or negative. No vegetable changes evidence class in the national comparison. The MAE in LKR/kg changes by under 1-2 LKR in each case (full values in the CSV).

## 6. Regional rain, both windows (exploratory; gain % vs AR)
| Vegetable | nat incl | nat prior | Dambulla incl | Dambulla prior | Nuwara Eliya incl | Nuwara Eliya prior |
|---|---|---|---|---|---|---|
| Cabbage | 19.7 | 19.5 | 18.3 | 18.1 | 21.5 | 21.7 |
| Brinjal | 12.4 | 10.4 | 13.1 | 12.3 | 11.8 | 10.0 |
| Carrot | 8.2 | 9.6 | 8.2 | 9.3 | 8.0 | 8.6 |
| Tomato | 4.8 | 4.8 | 5.5 | 5.9 | 5.4 | 5.5 |
| Snake gourd | 1.8 | 2.0 | 2.8 | 2.9 | 2.7 | 3.2 |
| Pumpkin | 1.8 | 1.6 | 2.0 | 2.3 | 1.1 | 0.7 |
| Beans | -1.5 | -2.5 | -1.1 | -1.1 | -2.1 | -3.2 |

Caution on multiplicity: one cell reaches "supported (corrected)" for tomato (Dambulla box, non-overlapping window: Holm CW p = 0.036, but bootstrap p about 0.10). It is one of six specifications and the primary tomato result (Holm 0.109) is not significant. It must **not** be promoted to a tomato finding; Holm is applied within each spec, not across specs. Tomato remains exploratory.

## 7. Prediction intervals (80 %, national models)
`interval_coverage.csv`. Coverage for AR+rain (primary / prior): cabbage 0.77 / 0.79, brinjal 0.84 / 0.86, carrot 0.74 / 0.71, tomato 0.74 / 0.76, snake gourd 0.73 / 0.73, pumpkin 0.84 / 0.82, beans 0.77 / 0.71; price-only AR 0.69-0.84. The rain window does not materially change calibration. With 62 points the standard error of a coverage estimate is about 0.05, and the intervals use only 12+ past errors at the start. Present as empirical uncertainty bands with actual coverage printed, not as calibrated intervals. Intervals are built in log space, so they are asymmetric in LKR/kg.

## 8. Statistical notes to carry into the methodology
* Holm applies to the Clark-West p-values (7 tests per specification). Block-bootstrap p-values are reported separately and are **not** Holm-adjusted here (v2's CSV also has a Holm column for block length 6). The evidence label requires Holm CW p < 0.05 and every bootstrap p < 0.10.
* Newey-West t-statistics use a normal approximation; with about 62 forecasts the p-values are approximate.
* The fixed 2010-2015 climatology (v2 sensitivity) is only past-only for origins from 2016 on; warm-up errors before then would use "future" climatology relative to those origins, so those errors should not be used to claim historically valid interval calibration. Test-period forecasts (2021-08 on) are unaffected, but v2's fixed-climatology interval history includes warm-up errors. Treat v2 fixed-climatology interval results accordingly.

## 9. Conclusion
* The v2 primary result is reproduced exactly and passes the timing and training-only assertions.
* Removing the overlap between A0 and A3 does not change the conclusions: cabbage and brinjal are supported after correction in both versions, carrot is supported in both with a small shift in size, tomato stays exploratory, and snake gourd, pumpkin and beans show no evidence.
* Rain-window choice, rain geography and anomaly definition move the estimated gains by only a few percentage points, with brinjal the most sensitive. Remaining caveats are unchanged: the test window was examined before, 62 dependent forecasts limit power, and the rain series are geographic proxies.
* Recommendation: freeze the forecasting analysis with `*_incl` as the primary specification as run in v2, report the non-overlapping version as a robustness check, and move to the storyboard.
