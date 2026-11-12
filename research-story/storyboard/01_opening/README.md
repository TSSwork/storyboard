# 01 - Can rainfall help anticipate vegetable prices?

![storyboard](storyboard.png)

**Demonstrates:** Problem framing and communication

## What to say
Good morning. I want to start with a question that sounds simple: can last month's rain tell us anything about next month's vegetable prices?

Look at the top chart. That is the wholesale price of cabbage at Dambulla since 2016, in rupees per kilogram. It rises, collapses, spikes. Anyone who buys or sells vegetables knows how unpredictable this is. Underneath is the rainfall for the whole country, month by month.

It is tempting to look at these two charts and say "wet months, high prices". I am not going to say that, and the rest of this presentation is about why. Instead I am asking a narrower question that can actually be tested: if I already know every past price, does adding observed rainfall make my forecast of next month's price better? That is a question with an answer, and the answer turns out to depend on the vegetable.

So over the next ten slides I will show you how I set the test up, how I checked it was fair, what it found, how far it can be trusted, and where the wider food system fits in.

## Key points to land
- The question is about forecasting, not about cause and effect.
- The comparison that matters is against a model that already knows past prices.
- The answer will differ by vegetable: that is the finding to hold on to.

## In plain words
Think of two forecasters. One looks only at the price history. The other looks at the price history and the weather report. The study asks whether the second one is actually better, and for which vegetables.

## For the technical evaluator
This is an out-of-sample predictive-ability question for nested models: the price-only model is a special case of the price-plus-rain model, which matters later for which statistical test is valid.

## If someone asks
**"Isn't it obvious that rain affects vegetable prices?"**  
It is plausible that rainfall affects supply, but plausible is not the same as useful. The useful question is whether rainfall adds information that past prices do not already contain. Prices already reflect some weather effects, so the extra value can be small or zero. That is exactly what the test measures.

**"Are you saying rain causes the price changes?"**  
No. This study can only say whether rainfall helps predict. A predictive gain is consistent with a causal link but does not prove one, and I make no causal claim anywhere.

**"Why cabbage in the chart?"**  
It is the vegetable with the strongest result, so it makes the picture easiest to read. The same data exist for all seven vegetables and every one is shown later.

## Evidence behind the slide
CBSL daily wholesale prices (`raw/cbsl-daily-prices.csv`), Dambulla, monthly mean of valid daily prices, nominal LKR/kg, series spanning August 2016 to November 2026. ERA5-Land corrected national monthly rainfall (`research_audit/derived/era5_regional_monthly.csv`). The chart is descriptive and contains no result.

## What not to claim
- Do not say rain drives prices or that wet months cause price rises.
- Do not read patterns off this chart as evidence; it is only the motivation.
- Prices are nominal: do not describe the upward drift as real-price inflation.

## On the slide
- Hover the price line to read a month's value.
- Point to a high-price period, then say you will not draw a conclusion from it yet.

## Hand-over to the next page
To test the question properly I first need to be clear about exactly which market, which vegetables and which data I am using. That is the next slide.
