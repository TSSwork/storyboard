# 02 - One market, seven vegetables, two data sources

![slide](../storyboard/02_scope_and_data/storyboard.png)

**Demonstrates:** Research scope and data-source understanding

## What to say
Before any result, I want to be exact about what this study covers, because the biggest risk with a topic like this is claiming too much.

The main market is Dambulla wholesale, from the Central Bank of Sri Lanka's daily price series. Pettah wholesale is used only as a robustness check, and I will not call it independent validation. There are seven vegetables: cabbage, brinjal, carrot, tomato, snake gourd, pumpkin and beans. I forecast one month ahead, and I turn the daily prices into a monthly mean, but only when a month has at least ten valid daily prices. If it does not, that month is simply missing. I do not fill gaps.

The second source is ERA5-Land, a reanalysis dataset of weather. I take hourly precipitation, turn it into daily totals, then monthly totals. The map shows the two regional boxes I use as secondary checks, around Dambulla and around Nuwara Eliya. They are rough boxes, not the areas where the crops are actually grown, and I say so on the slide.

One thing I want to be open about: my first rainfall extraction had a bug. Monthly totals were between 12 and 21 times too large because I summed an accumulating variable. I found it in my own audit, corrected it, and every number you see here uses the corrected series.

## Key points to land
- One market, seven vegetables, one month ahead; this is deliberately narrow.
- Missing data are left missing, never filled.
- The ERA5 error was found and corrected; only corrected rainfall is used.

## In plain words
Prices come from a market's daily records. Rain comes from a weather dataset on a grid over the island. Both are turned into one number per month so they can be compared.

## For the technical evaluator
ERA5-Land precipitation is an accumulation from 00 UTC each day, so the daily total for day D is the value at 00 UTC of D+1. Summing the hourly accumulations, as I first did, overstates the total. National rainfall is a cosine-latitude-weighted mean over 541 land cells; each box is 36 cells.

## If someone asks
**"Why Dambulla?"**  
It was the primary market in the pilot and in the frozen design, and Pettah, the second market in the same CBSL data, is used as a check. I do not claim Dambulla represents every market.

**"Why national rainfall rather than rainfall where the vegetables grow?"**  
I do not have growing-area boundaries, so national rainfall is the primary measure and the two boxes are exploratory alternatives. I state plainly that all of them are proxies.

**"What happens to months with missing data?"**  
A price month needs at least ten valid daily prices. A rainfall month must be complete. Only two rainfall months are incomplete, December 2009 and November 2026, and both are set to missing rather than used as partial totals.

**"How do you know the bug is fixed?"**  
The corrected annual national rainfall is plausible for the island, and the audit report documents the comparison. I would not claim more than that.

## Evidence behind the slide
`research_audit/07_data_quality_report.md` (finding E1: monthly totals 12.4 to 21.4 times too large, median 14.3 times; E2: the correct method). Box centres: Dambulla 7.86N 80.65E, Nuwara Eliya 6.97N 80.77E, plus or minus 0.3 degrees, 36 land cells each; national 541 cells. `forecast_validation_v2/rainfall_completeness.csv` shows only 2009-12 and 2026-11 incomplete.

## What not to claim
- Do not call Pettah an independent replication.
- Do not describe the boxes as the growing regions.
- Do not imply prices are real (inflation-adjusted); they are nominal and no deflator is applied.

## On the slide
- Hover the dashed boxes on the map to show they are 36-cell proxies.
- Point out Pettah's position as a market on the coast, not a rainfall box.

## Hand-over to the next page
Now that the data are defined, let me show you what the prices and the rainfall actually look like, and why the obvious comparison is not enough.
