# 03 - Prices have their own dynamics, and some follow last month's rain

![slide](../storyboard/03_prices_and_rain/storyboard.png)

**Demonstrates:** Data processing and exploratory analysis

## What to say
This slide is where the idea first looks promising, and also where I need to be most careful.

The big chart is the selected vegetable's monthly price, with the rainfall anomaly underneath. An anomaly is simply how much wetter or drier a month was than the usual rainfall for that calendar month, using only earlier years so that nothing from the future leaks in. The shaded band is 2022, when the economic crisis pushed nearly every price up.

Now look at the table on the right. Each cell is a correlation between a vegetable's price change and the rainfall anomaly a given number of months earlier. The column that stands out is lag one, rain from last month. Cabbage is plus 0.60, carrot plus 0.44, brinjal plus 0.40. That is why these three vegetables caught my attention.

But I want to say clearly what this is not. I ran 28 of these tests, and ten came out nominally significant. With 28 tests, you would expect about 1.4 by chance. So this table is a reason to look closer, not a finding. It is descriptive and motivating only.

The other important point from the price charts is that prices have strong patterns of their own: trends, seasons and shocks. A fair test must therefore give the baseline model all of that, which is exactly what the next slide does.

## Key points to land
- Lag one, last month's rain, is where the correlation sits for cabbage, carrot and brinjal.
- 10 of 28 significant against about 1.4 expected by chance: exploratory only.
- Prices have their own structure, so the comparison must be against a model that uses it.

## In plain words
The table asks: when it rained more than usual last month, did this vegetable's price tend to rise this month? For some vegetables, yes. But with many comparisons on a short history, some of that can be chance.

## For the technical evaluator
The heat-map correlations use a z-score rain anomaly against de-seasonalised price changes (from the earlier exploratory audit), while the strip below the chart and the forecasting models use the past-only mm/100 anomaly. They are different constructions and I say so on the slide.

## If someone asks
**"Isn't a correlation of 0.60 strong?"**  
It is large for monthly data, which is why I looked further. But it comes from one of 28 tests on a short series, with no correction for multiple testing and no out-of-sample check. The forecasting test on the following slides is the real evidence.

**"Why do different vegetables behave differently?"**  
This study does not test mechanisms, so I would not offer an explanation as a finding. It only shows where rainfall adds forecasting information.

**"What is the pink and blue in the table?"**  
Blue is a positive correlation, coral a negative one. The outlined row is the vegetable you selected above the chart.

**"Why does the strip use a different anomaly from the table?"**  
The table comes from the original exploratory analysis; the forecasting models use the stricter past-only version. I keep both and label them so nobody mixes them up.

## Evidence behind the slide
`research_audit/_profiles/prices_out.txt` section D (values copied to `03_prices_and_rain/assets/lag_correlations.csv`; the audit script re-parses the source and matches them). The correlations use a z-score rain anomaly against de-seasonalised price changes; the strip shows the mm/100 forecasting anomaly. CBSL Dambulla monthly means; ERA5 anomaly = rain minus the mean of the same calendar month in earlier years, divided by 100 mm.

## What not to claim
- Do not present the heat map as a result or as evidence that rain predicts prices.
- Do not claim a mechanism for why some vegetables respond.
- Do not mix the z-score heat map with the mm/100 anomaly strip as if they were one measure.

## On the slide
- Select Cabbage, then Tomato: the outlined row moves and the chart changes.
- Point to the lag-1 column and the three strongest cells, then to the 10-of-28 line in the subtitle.

## Hand-over to the next page
A promising correlation is not enough. The next slide turns the hint into a fair test: a model that already knows past prices against the same model with rainfall added.
