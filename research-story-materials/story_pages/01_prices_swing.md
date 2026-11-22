# 01 - Vegetable prices swing wildly

**Act:** The problem · **Time:** about 1½ minutes

## What to do on this page
1. Leave **Cabbage** selected and let the audience read the four KPI cards.
2. Click **Beans**, then **Tomato**. The cards and chart change. Point out that every vegetable swings, by different amounts.
3. Turn **Show rainfall underneath** off and on so people see the two series line up in time.
4. On the **rain map** at the right, drag the month slider. Then switch to **Long-term monthly average** and slide from May to October. The south-west turns dark blue in the May–September monsoon, and the north and east get their rain later in the year.
5. End on the coral line under the chart: the question for the whole talk.

## What to say
"This is the wholesale price of cabbage at Dambulla, a major vegetable wholesale market, every month since 2016. Look at the cards. In its cheapest month cabbage sold for about 16 rupees a kilo, and in its dearest month about 452 rupees. That is roughly a 28-times gap. In six months out of ten the price moves by more than a fifth from one month to the next.

Farmers, traders and households all live with this. On the right is where the rain falls. Darker blue means more rain. It is not spread evenly: the south-west is soaked in the May monsoon, and the dry zone around Dambulla gets much less. The two dotted squares are the areas whose rain we also tested. So we asked a simple question. Underneath the price I've put the rain that fell across the island. Can last month's rain warn us about next month's price? Let's look for a pattern."

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
- **Rain map:** monthly totals for every ERA5-Land cell over Sri Lanka (0.1°, 541 land cells), built from the raw hourly files with the same corrected rule as the national series. The total for day D is the accumulated precipitation at 00 UTC on day D+1, and only complete months are kept. A test checks that the cell-weighted average reproduces the national and Dambulla-box series to within 0.5 mm. "Long-term monthly average" is the average of that calendar month over all years, 2010–2026. A few coastal cells, for example around the Puttalam lagoon, extend past the outline because ERA5-Land's land mask is coarser than the coastline.
- **Why monthly?** Daily prices are noisy and rain acts on crops over weeks.

## What not to claim
- That rain *causes* these swings. The chart puts the two side by side; it does not show cause.
- That the 28× gap is a "real" price rise. Prices are nominal, and the period includes the 2022 crisis.
