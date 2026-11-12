# 07 - The ranking holds up under alternative specifications

![storyboard](storyboard.png)

**Demonstrates:** Robustness testing and research judgement

## Purpose
Show the result is not a product of one arbitrary choice.

## Story
Across overlapping and non-overlapping windows, regional rainfall, the Pettah market and median prices, the same vegetables benefit and the same ones do not.

## Visual
Dot plot: one row per vegetable, one marker per specification, zero line. A dot plot shows spread across specifications at a glance, which grouped bars would bury.

## Evidence
`forecast_validation_v2/rain_window_comparison.csv`; `forecast_model_comparison_v2.csv` (Pettah, median price). No vegetable changes evidence class between overlapping and non-overlapping A3; brinjal is most sensitive (12.4 to 10.4).

## Explanation
One tomato cell (Dambulla box, non-overlapping) reaches Holm p = 0.036. I do not promote it: it is one of six specifications, Holm is applied within each specification, and the primary tomato result is not significant. Rain geography moves gains by a few points only.

## Interpretation
The commodity pattern is stable; individual percentages are not precise.

## Limitations
Secondary specifications are exploratory and not a pre-registered family. Pettah shows consistency, not replication. Rain boxes are proxies.

## Transition
Page 8 asks how accurate the forecasts really are.
