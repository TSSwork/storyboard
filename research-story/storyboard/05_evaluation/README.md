# 05 - How we judge it: 62 real forecasts, three layers of scrutiny

![storyboard](storyboard.png)

**Demonstrates:** Statistical reasoning and validation

## Purpose
Show evaluation rigour without turning the slide into a statistics lecture.

## Story
Score the forecasts, test whether the gain is real, then correct for testing seven vegetables.

## Visual
Three cards (score, test, correct) above an expanding-window timeline with origins and targets. Cards give the logic; the timeline shows no look-ahead.

## Evidence
`forecast_validation_v2/evaluation_samples.csv`: origins Aug 2021 to Sep 2026, targets Sep 2021 to Oct 2026, n = 62 per vegetable. Clark-West (nested, one-sided, Newey-West lag 3), Diebold-Mariano (supplementary), moving-block bootstrap (3/6/12, 4000 draws), Holm across seven vegetables.

## Explanation
Models are refit at every origin using only data known then. RMSE gain is the percentage reduction of log-price RMSE versus the baseline on the same dates. The evidence label needs Holm p < 0.05 and all bootstrap p < 0.10. The validation script reproduces v2 exactly (434 forecasts, max difference 0.0) and passes timing assertions.

## Interpretation
The label 'supported' is a statement about this test window and these tests.

## Limitations
The pilot already looked at this window, so results are exploratory. The 62 errors are serially dependent; Newey-West p-values are approximate.

## Transition
With the method clear, page 6 shows what it found.
