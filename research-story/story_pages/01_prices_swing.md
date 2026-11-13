# 01 - Vegetable prices swing wildly

**Act:** The problem · **Time:** about 1½ minutes

## What to do on this page
1. Leave **Cabbage** selected and let the audience read the four KPI cards.
2. Click **Beans**, then **Tomato**. The cards and chart change. Point out that every vegetable swings, by different amounts.
3. Turn **Show rainfall underneath** off and on so people see the two series line up in time.
4. End on the coral line under the chart: the question for the whole talk.

## What to say
"This is the wholesale price of cabbage at Dambulla, a major vegetable wholesale market, every month since 2016. Look at the cards. In its cheapest month cabbage sold for about 16 rupees a kilo, and in its dearest month about 452 rupees. That is roughly a 28-times gap. In six months out of ten the price moves by more than a fifth from one month to the next.

Farmers, traders and households all live with this. So we asked a simple question. Underneath the price I've put the rain that fell across the island. Can last month's rain warn us about next month's price?"

## Key points
- The swings are large, frequent and different for each vegetable. That makes forecasting worthwhile and hard.
- The question is about one month ahead, using rain that has **already fallen**.

## Reading the cards
| Card | Meaning |
|---|---|
| Cheapest / Most expensive month | Lowest and highest monthly average wholesale price, Rs per kg, nominal |
| Biggest one-month move | Largest percentage change between two consecutive calendar months (a missing month is never bridged) |
| Months with a swing over 20% | Share of month-to-month changes larger than 20% in either direction, out of 10 |

## If an evaluator asks
- **Data:** CBSL daily wholesale prices, Dambulla. A month's average is used only if it has at least 10 valid daily prices; otherwise the month is missing.
- **Rain:** ERA5-Land hourly precipitation, aggregated to daily and then monthly totals over Sri Lanka's land cells. Incomplete months are set to missing. An early accumulation bug that overstated totals was fixed, and only corrected series are used.
- **Why nominal prices?** No suitable CPI/NCPI deflator was in the project. All comparisons in the forecasting test are between two models on the same nominal series, so the deflator does not change which model wins.
- **Why monthly?** Daily prices are noisy and rain acts on crops over weeks.

## What not to claim
- That rain *causes* these swings. The chart puts the two side by side; it does not show cause.
- That the 28× gap is a "real" price rise. Prices are nominal, and the period includes the 2022 crisis.
