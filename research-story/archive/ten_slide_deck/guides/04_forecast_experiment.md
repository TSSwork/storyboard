# 04 - The test: does rainfall improve a model that already knows past prices?

![slide](../storyboard/04_forecast_experiment/storyboard.png)

**Demonstrates:** Model design and forecasting methodology

## What to say
This is the heart of the design, and I tried to keep it as simple as possible on purpose.

At the end of any month, call it month t, I build two forecasts of next month's price. The first model uses only past prices: this month's, last month's, and the price a year ago, whichever combination the data support best. The second model uses exactly the same price information and adds rainfall: this month's anomaly, and a three-month rainfall measure.

Because the price part is identical, any difference between the two forecasts can only come from rainfall. That is the whole point. I also score two naive benchmarks, repeating the last price and repeating last year's price, to make sure the models are beating something sensible.

The small boxes at the bottom show the three-month window. In my main version it covers months t minus 2 to t, which overlaps this month's rainfall. That is not cheating, since all of it was already observed, but the two predictors are correlated. So I also run a version using t minus 3 to t minus 1, where they are not.

Finally, what I left out. No machine learning, no future rainfall, and no exchange rate: in my pilot the exchange rate made the forecast worse for all seven vegetables, so it stays out. This is a research instrument, not a prediction product.

## Key points to land
- Same price lags in both models, so any gain is attributable to rain.
- Both rainfall measures use only rain observed by the end of month t.
- FX excluded because it worsened pilot RMSE for all seven vegetables; no machine learning.

## In plain words
Two forecasters see the same price history. One also sees the rainfall. If the second is more accurate, rain added something. If not, it did not.

## For the technical evaluator
The models are linear autoregressions on log monthly prices, with the price lag set chosen by AIC from four candidates using training data only, and shared by both models. The rain model adds A0 (anomaly in month t) and A3 (mean anomaly over three months). Because the AR model is nested in the AR-plus-rain model, the Clark-West test is the appropriate comparison.

## If someone asks
**"Why such a simple model?"**  
Because the question is whether rainfall adds information, and a simple, transparent baseline makes that attributable. A complex model could improve for reasons unrelated to rain. Machine learning was deliberately out of scope.

**"Isn't using the current month's rain in the three-month window double counting?"**  
It overlaps the first predictor, so the two are correlated (0.57 in the test period). It is not look-ahead. I ran the non-overlapping window as a check; the conclusions did not change.

**"Why not add the exchange rate or other variables?"**  
In the pilot, adding the exchange rate worsened RMSE for all seven vegetables, so it was excluded. More variables would also blur the question.

**"Could you not just use next month's rainfall forecast?"**  
That would be a different, longer-horizon study that needs a rainfall forecast model. This study only asks about observed rainfall.

## Evidence behind the slide
`forecast_backtest_v2.py` (lag sets y0 | y0,y1 | y0,y11 | y0,y1,y11 chosen by AIC on the training window, shared by both models; verified by assertion in the validation script). `forecast_validation_v2/predictor_overlap.csv`: correlation of A0 and A3 is 0.57 (primary) and -0.05 (non-overlapping). Pilot (`forecast_pilot.py`): adding FX reduced accuracy for all seven vegetables.

## What not to claim
- Do not call this a prediction tool or imply it is ready for use.
- Do not say the overlap is a leak; it uses only already-observed rain.
- Do not claim the exchange rate is irrelevant to food prices, only that it did not help these forecasts.

## On the slide
- This slide is a diagram: walk left to right with your hand rather than clicking.
- Point at the highlighted card to stress that the price lags are the same.

## Hand-over to the next page
A design is only as good as how it is judged. The next slide explains how I scored these forecasts and how I tested whether the difference is real.
