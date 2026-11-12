# 08 - Better does not mean accurate

![storyboard](storyboard.png)

**Demonstrates:** Understanding of uncertainty and model limitations

## What to say
I want to end the results section with a reality check, because a percentage improvement can sound more impressive than it is.

The chart shows cabbage. The dark line is the actual price, the grey line is the price-only forecast, and the dotted line is the rainfall forecast. The shaded band is an empirical 80 percent range, built from the model's own past errors.

You can see two things. The rainfall model does follow the movements, and it is better than the baseline. But it misses the size and the timing of sharp moves. The typical percentage error is between 23 and 40 percent depending on the vegetable.

Second, the bands are supposed to contain the actual price 80 percent of the time. Across the vegetables they contain it between 73 and 84 percent of the time. So they under-cover, and I will not call them calibrated intervals. With 62 points the uncertainty on those coverage numbers is itself about five percentage points.

So the right reading is this: rainfall adds information, and that is a research finding. It does not make these forecasts accurate enough to run a business on, and I am not claiming it does.

## Key points to land
- Typical forecast errors remain large: MAPE between 23 and 40 percent.
- The 80 percent bands cover 73 to 84 percent of outcomes, so they under-cover.
- A better forecast is not an accurate forecast; this is a research result, not a product.

## In plain words
Rain makes the forecast better than guessing from past prices alone, but it is still often wrong by a quarter or more. Both things are true.

## For the technical evaluator
Intervals are the forecast plus the 10th and 90th percentiles of the model's earlier out-of-sample errors (at least 12 needed), built in log space so they are asymmetric in rupees. A caveat from the validation: the fixed-climatology sensitivity uses warm-up errors computed with climatology that includes later years, so I do not treat those intervals as validly calibrated.

## If someone asks
**"So is the model useless?"**  
No, it shows rainfall carries real information for some vegetables. But the forecasts are not accurate enough to act on by themselves, and I never claimed otherwise.

**"Why do the bands under-cover?"**  
They are estimated from past errors and the price series has shocks bigger than earlier ones. With a short test, coverage estimates are also noisy.

**"What is MAPE?"**  
Mean absolute percentage error: the average size of the miss as a percentage of the actual price.

**"Could a better model fix this?"**  
Possibly, but that is a different study. This one deliberately uses a simple model to isolate the rainfall question.

## Evidence behind the slide
`forecast_results_v2.csv` and `forecast_validation_v2/interval_coverage.csv`. MAPE for AR plus rain ranges from 23.1 to 39.7 percent across the seven vegetables. Coverage of the nominal 80 percent band for AR plus rain (national, primary window) ranges from 0.73 to 0.84. Standard error of a coverage estimate with 62 points is about 0.05 (square root of 0.8 x 0.2 / 62).

## What not to claim
- Do not call the bands calibrated or the forecasts accurate.
- Do not present relative RMSE gains as practical accuracy.
- Do not use these forecasts to suggest prices for any real decision.

## On the slide
- Select Tomato to show its MAPE of about 40 percent.
- Drag the range slider below the chart to zoom into the 2023 spike.

## Hand-over to the next page
So far everything has been about vegetables. The last content slide steps back to the wider food system around them.
