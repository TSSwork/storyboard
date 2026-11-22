# 02 - Spot the pattern yourself

**Act:** The problem · **Time:** about 2 minutes. A good page to hand the mouse to someone in the audience.

## What to do on this page
1. Start on **Cabbage** with **Rain from: 1 month earlier**. The blue card says **Strong**, and the dots climb from bottom-left to top-right.
2. Slide to **Same month**. The link drops to "Barely any". Then slide to **2 months earlier**. Ask: "So when does rain show up in the price?" Answer: about a month later.
3. Look at the bar chart on the right. At a one-month delay, cabbage, carrot and brinjal lead, and beans is near zero.
4. Click **Beans** to show what "barely any link" looks like: a shapeless cloud of dots.
5. End on the coral line: "A pattern is a clue, not proof." This sets up the next page.

## What to say
"Every dot here is one month. Left to right is how much wetter or drier than usual that month was across the island. Up and down is how much the cabbage price changed compared with a normal month for that time of year.

When I use the rain from one month earlier, the dots line up: a wet month tends to come before a price rise. The card says the link is strong, about 0.6 on a scale where 1 is a perfect line.

Now watch what happens when I use the rain from the same month: the pattern disappears. And across the seven vegetables, cabbage, carrot and brinjal show the clearest links at a one-month delay. Beans shows almost nothing.

But be careful. With seven vegetables and four delays we are looking at 28 links, and a few can look strong just by chance. So this is a clue. On the next page we put it to a proper test."

## Key points
- The clearest links appear with a **one-month delay**: cabbage +0.60, carrot +0.44, brinjal +0.40. Beans is +0.08.
- This page only *describes* patterns. The forecasting test on the next page is the real evidence.
- The same three vegetables come out on top on both pages. That agreement is worth pointing out, but it is still not proof of cause.

## Reading the cards
| Card | Meaning |
|---|---|
| Link between rain and price | The correlation (r), shown as a word: Strong (0.55 or more), Moderate (0.35 or more), Weak (0.15 or more), otherwise Barely any |
| Direction | Whether wetter months come before higher or lower prices |
| Strongest delay | The delay (0 to 3 months) with the largest link for this vegetable |
| Months compared | Months where both the price change and the rain are available (122 for each vegetable, Sep 2016 – Oct 2026) |

## If an evaluator asks
- **Construction:** this is exactly the project's exploratory table, `lag_correlations.csv`, from `research_audit/feasibility_prices.py` section D. Price change = the monthly change in the log of the Dambulla monthly mean price, minus the average change for that calendar month (de-seasonalised). Rain = the national ERA5 monthly total as a z-score against all years' mean and standard deviation for that calendar month. A test checks that the page reproduces all 28 table values to within 0.01.
- **Significance:** permutation tests in the audit found 10 of 28 links at p < 0.05, against about 1.4 expected by chance. No multiple-testing correction is applied to this exploratory table.
- **Why this differs from the forecasting test:** this z-score uses every year, including later ones, so it is descriptive only. The forecasting test uses a past-only anomaly and an out-of-sample comparison.
- **Why a one-month delay?** One plausible reason is that heavy rain damages crops and disrupts harvest and transport, so the supply effect reaches the market a few weeks later. That is a hypothesis, not something this study tests.

## What not to claim
- That rain *causes* price rises.
- That a "Strong" link means you can forecast prices. That question is answered on the next page, and the answer is more modest.
