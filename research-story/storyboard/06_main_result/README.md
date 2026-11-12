# 06 - Rainfall helps some vegetables far more than others

![storyboard](storyboard.png)

**Demonstrates:** Results interpretation and visual communication

## What to say
This is the main result, and I want you to read it in two ways at once.

The length of each bar is how much better the rainfall model is, as the percentage reduction in forecast error. The marker and the label beside it say how strong the evidence is after all the corrections.

Cabbage improves by 19.7 percent, brinjal by 12.4 percent, carrot by 8.2 percent. All three pass the corrected test. Carrot has a smaller gain than brinjal, but it also passes, so size and strength are not the same thing. It is borderline, though: its corrected p-value is 0.029.

Tomato improves by 4.8 percent, which looks positive, but its corrected p-value is 0.109, so I treat it as exploratory only. Snake gourd and pumpkin improve by under two percent with no reliable evidence. And beans actually get slightly worse, minus 1.5 percent, when rainfall is added.

So the answer to my opening question is not yes or no. It is: for some vegetables, observed rainfall adds real information beyond past prices, and for others it does not. That variation is the finding.

You can switch the rainfall definition above the chart. Those are exploratory views, and the page tells you so.

## Key points to land
- Cabbage, brinjal and carrot: material gains that survive correction.
- Tomato is exploratory only; snake gourd and pumpkin show nothing reliable; beans get worse.
- Bar length is effect size; the marker and label are evidence strength.

## In plain words
Rain helps forecast cabbage, brinjal and carrot. It does not reliably help the others. Even where it helps, the gain is a reduction in error, not perfect accuracy.

## For the technical evaluator
RMSE gain is one minus the ratio of log-scale RMSE for AR plus rain versus AR on the same 62 origins. P-values are one-sided Clark-West with Newey-West variance, Holm adjusted within the seven primary tests: 0.0018, 0.0009, 0.0285, 0.109, 0.189, 0.235, 0.557 in the order shown.

## If someone asks
**"Why does carrot count when the gain is smaller than tomato's?"**  
Because the strength of evidence depends on how consistent the improvement is across the 62 forecasts, not just its size. Carrot's gain is smaller than brinjal's but consistent enough to pass; tomato's is not.

**"Why do beans get worse?"**  
Adding predictors that carry no useful signal can add noise and slightly hurt forecasts. I do not claim more than that.

**"Is 19.7 percent a big improvement?"**  
It is large relative to the price-only baseline, but the forecasts remain far from precise, which is the point of slide 8.

**"Does this prove rain affects these prices?"**  
No. It shows rainfall improves out-of-sample prediction for these vegetables in this window. Causation needs a different study.

**"What do the other options above the chart do?"**  
They swap the rainfall definition: the non-overlapping window, the Dambulla box or the Nuwara Eliya box. They are exploratory checks, and slide 7 summarises them.

## Evidence behind the slide
`forecast_model_comparison_v2.csv`, Dambulla, mean monthly price, national rainfall: gains +19.7, +12.4, +8.2, +4.8, +1.8, +1.8, -1.5 percent; Holm Clark-West p 0.0018, 0.0009, 0.0285, 0.109, 0.189, 0.235, 0.557 (cabbage, brinjal, carrot, tomato, snake gourd, pumpkin, beans). Evidence labels come from the stored v2 `evidence` column; the page does not re-derive them.

## What not to claim
- Do not say rain causes the price movements or that the model is accurate.
- Do not promote tomato; its corrected result is not significant.
- Do not present the secondary rainfall options as a second primary result.

## On the slide
- Hover each bar to show Holm p, the three bootstrap p-values and MAPE.
- Switch to the Dambulla box and read out that the warning appears: it is exploratory.

## Hand-over to the next page
A result that depends on one arbitrary choice is not worth much, so the next slide asks whether this survives other reasonable choices.
