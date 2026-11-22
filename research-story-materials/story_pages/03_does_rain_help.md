# 03 - Does rain help? Try it

**Act:** The test · **Time:** 3 to 4 minutes. This is the main page. Let the audience drive it if they want to.

## What to do on this page
1. Start on **Cabbage · Whole island · Dambulla**. Read the four cards from left to right.
2. Point at the chart: navy is what actually happened, the dotted grey line is the prices-only forecast, and green is the forecast that also knew the rain.
3. Click **Beans**. The verdict turns coral, "No help". Let that land: rain does not help every vegetable.
4. Click **Brinjal** and **Carrot** (both clear help), then **Tomato** ("A hint, not proven").
5. Switch **Where rain is measured** to *Hill country* and the **Market** to *Pettah*. The bar chart at the bottom ranks all seven vegetables by how much rain cut the error, and shows which verdicts hold up.
6. Finish on the last card: even the better forecast misses often, and the price lands inside the range only 7 or 8 times in 10.

## What to say
"Every month from August 2021 we stood at the end of the month and made two forecasts of next month's price. One used only past prices. The other used the same past prices plus the rain that had already fallen. Then we waited and saw which forecast missed by less. That gives 62 real forecasts per vegetable.

For cabbage the prices-only forecast missed by about 52 rupees a kilo on a typical month. Adding rain brought that down to about 42, a fifth smaller overall error. That gain survives strict checks.

Now try beans. Adding rain makes nothing better; it is slightly worse. Pumpkin and snake gourd: no clear effect. Tomato looks a bit better, but not enough to trust.

So rain carries useful information for some vegetables, mostly cabbage, brinjal and carrot, and not for others. The last card is the honest part: even the better forecast is often off, and the real price falls inside our 80 percent range only about seven or eight times in ten."

## Key points
- Fair test: both forecasts see the same past prices, the same months and only information available at the time.
- Clear help: **cabbage (19.7% smaller error), brinjal (12.4%), carrot (8.2%)**. Hint only: tomato (4.8%). No clear effect: snake gourd, pumpkin (about 1.8%). No help: beans (−1.5%). Figures are for Dambulla and rain across the whole island.
- Better is not the same as accurate.

## Reading the controls and cards
| Item | Meaning |
|---|---|
| Where rain is measured | Whole island (main analysis), or a box around Dambulla, or around Nuwara Eliya (regional checks) |
| Market | Dambulla (main analysis) or Pettah, Colombo (consistency check, 61 forecasts) |
| Typical miss | Average absolute error in Rs per kg over all forecasts |
| "x% smaller overall error" | Percentage reduction in root-mean-square error of the log price, rain model vs prices-only |
| Verdict | The stored evidence label, put into plain words (table below) |
| Price landed inside our range | How often the actual price fell inside the 80% range, out of 10. A well-calibrated 80% range would score 8 |

| Verdict on screen | Stored label | Rule |
|---|---|---|
| Clear help | supported (corrected) | Holm-adjusted Clark–West p < 0.05 **and** all three bootstrap p < 0.10 |
| A hint, not proven | suggestive (uncorrected only) | Positive gain, significant only before correction |
| No clear effect | no reliable evidence | Positive gain, not significant |
| No help | worse or no gain | Gain ≤ 0 |

## If an evaluator asks
- **Models:** autoregressive model of the log monthly price (AR). The rain model is the *same* AR with two rain terms added: rain in month *t* and a 3-month rain window. The lag set is chosen by AIC on the training window only and shared by both models, so the only difference is rain.
- **Rain variable:** a past-only anomaly, i.e. rain minus the average of the same calendar month in *earlier* years only. No future information enters.
- **Backtest:** expanding window, refit at every origin; 62 one-month-ahead forecasts per vegetable, origins Aug 2021 to Sep 2026.
- **Tests:** Clark–West for nested models (one-sided, Newey–West variance, lag 3), Diebold–Mariano as a supplement, moving-block bootstrap with blocks of 3, 6 and 12 months, and Holm correction across the seven vegetables. Holm Clark–West p in the order cabbage, brinjal, carrot, tomato, snake gourd, pumpkin, beans: 0.0018, 0.0009, 0.0285, 0.109, 0.189, 0.235, 0.557.
- **Ranges:** empirical 80% intervals built from past out-of-sample errors. Their coverage of about 70–85% shows the intervals are too narrow.
- **Robustness:** a non-overlapping rain window, regional rain boxes and the Pettah market keep cabbage, brinjal and carrot clear of zero, and beans at or below it. Pettah is a consistency check, not an independent replication: same weather, linked supply chains.
- **Why exploratory?** The 2021–2026 test window was already looked at during the pilot, so this is not a clean out-of-sample confirmation.
- **Why no machine learning or exchange rate?** The question is whether rain adds information beyond past prices, which a nested linear comparison answers directly. The exchange rate worsened pilot errors for all seven vegetables.

## What not to claim
- That rain *causes* the price changes. The test shows only that past rain improves forecasts.
- That this is a working price-prediction tool.
- That the regional or Pettah views are new findings. They are checks on the main result. Do not promote the tomato Dambulla-box result.
