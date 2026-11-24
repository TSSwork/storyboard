// The full story of the project, from the first download to the gallery walk.
// Compile: typst compile full_story.typ   (needs the Manrope font; Newsreader is optional for headings)

#set document(title: "The Full Story: Rain and Vegetable Prices in Sri Lanka")
#set page(paper: "a4", margin: (x: 2.4cm, top: 2.3cm, bottom: 2.2cm), numbering: "1", number-align: center)
#set text(font: "Manrope", size: 10.5pt, weight: 450, lang: "en", region: "gb")
#set par(justify: false, leading: 0.72em, spacing: 1.05em)
#set heading(numbering: "1.")
#show heading: set text(font: ("Newsreader", "Newsreader 36pt", "Manrope"), weight: 600, fill: rgb("#002941"))
#show heading.where(level: 1): set text(size: 17pt)
#show heading.where(level: 1): set block(above: 1.8em, below: 0.9em)
#show heading.where(level: 2): set text(size: 13pt)
#show heading.where(level: 2): set block(above: 1.4em, below: 0.7em)
#show raw: set text(size: 8.8pt)
#show raw.where(block: true): block.with(fill: rgb("#f3f6f8"), inset: 9pt, radius: 4pt, width: 100%)
#set table(stroke: 0.5pt + rgb("#c9d6de"), inset: 6pt)
#show table.cell.where(y: 0): set text(weight: 700)
#show link: set text(fill: rgb("#1155cc"))

#let note(body) = block(fill: rgb("#fff4e5"), inset: 10pt, radius: 4pt, width: 100%, stroke: (left: 3pt + rgb("#f5a33b")), body)
#let key(body) = block(fill: rgb("#e8f3f8"), inset: 10pt, radius: 4pt, width: 100%, stroke: (left: 3pt + rgb("#2f7292")), body)

// ---------------------------------------------------------------- title
#align(left)[
  #text(font: ("Newsreader", "Newsreader 36pt", "Manrope"), size: 26pt, weight: 600, fill: rgb("#002941"))[The full story]
  #v(-0.4em)
  #text(size: 13pt, fill: rgb("#52707f"))[Can last month's rain help forecast next month's vegetable prices in Sri Lanka? What we did, from the first download to the gallery walk.]
]
#line(length: 100%, stroke: 0.6pt + rgb("#c9d6de"))

*Who this is for.* Anyone who was not part of the project and needs to understand it well enough to present it. Read this first. It tells the story in order and explains why each turn was taken. The other two documents go deeper: `analysis.typ` covers every analysis and its code, and `each_page_full_review.typ` walks through the dashboard page by page with what to say.

*How to read it.* Each section ends with a short box that says what to remember. Technical words are explained the first time they appear, and there is a plain glossary at the end.

#outline(title: [Contents], depth: 1, indent: 1em)

= The question in one paragraph

Vegetable prices in Sri Lanka jump around a lot. At the Dambulla wholesale market, cabbage has sold for about 16 rupees a kilo in its cheapest month and about 452 rupees in its dearest, a 28-fold gap. Farmers, traders and households all feel these swings. Rain affects how vegetables grow, how they are harvested and how they reach the market, so we asked a simple question: *if we already know past prices, does knowing last month's rain help us forecast next month's price any better?* We found that it does for some vegetables (cabbage, brinjal and carrot) and does not for others (snake gourd, pumpkin and beans), with tomato in between. Even the best forecasts still miss by about a quarter of the price, so this is a finding about where rain carries useful information, not a tool for predicting prices.

#key[*Remember:* the question is narrow on purpose. It is about one month ahead, using rain that has *already fallen*, and it asks whether rain adds anything *beyond* past prices.]

= Where the project started: a much bigger idea

The project did not start with vegetables. The first plan was an ambitious chain linking the whole food system:

#align(center)[weather #sym.arrow.r paddy (rice) production #sym.arrow.r rice imports #sym.arrow.r food prices]

The idea was to show how a bad season ripples through: poor rain lowers the rice harvest, the country imports more rice, and food becomes more expensive, made worse by a weak rupee. It is an attractive story, and it matches what many people believe about Sri Lanka's food system. But a story is only as strong as the data behind each link, so before building anything we collected every dataset we could find and checked what each one could really support.

= Collecting the data (10 to 12 November 2026)

Over three days we downloaded and organised data from nine sources. Here is what each one is, in plain words.

#table(
  columns: (1.25fr, 2.6fr, 1fr),
  table.header([Source], [What it gives us], [Used in the end?]),
  [Central Bank of Sri Lanka (CBSL) daily prices, via Macro Lab], [Daily wholesale and retail prices for about 45 vegetable and food series at Pettah (Colombo), Dambulla and Narahenpita, August 2016 to November 2026.], [Yes, the heart of the study],
  [ERA5-Land (Copernicus Climate Data Store)], [Hourly rainfall and temperature on a grid of squares about 9 km across, covering all of Sri Lanka since January 2010. This is a "reanalysis": a computer model of the weather that is continuously corrected with real observations, so it has no gaps.], [Yes, all rainfall],
  [CHIRPS rainfall], [A satellite-based rainfall product. Only one day (1 January 2010) had been downloaded.], [No, one day cannot validate anything],
  [Department of Census and Statistics (DCS) paddy statistics], [Rice area sown, area harvested, yield and production for each season, nationally since 1951 and by district since 1978.], [Yes, page 4],
  [FAOSTAT (Food and Agriculture Organization) production and trade], [Yearly crop production and imports and exports for Sri Lanka since 1961.], [Yes, page 4 (rice imports)],
  [UN Comtrade], [Detailed yearly import and export records by product and partner country, 2010 to 2025 (2018 missing).], [Cross-check only],
  [CBSL exchange rates], [Daily rupee to US dollar rate since 2010.], [Yes, page 4],
  [HARTI weekly bulletins (Hector Kobbekaduwa Agrarian Research and Training Institute)], [Weekly retail prices from 529 PDF bulletins, 2015 to 2026, extracted into tables.], [No, too many gaps and duplicates],
  [World Bank Real-Time Food Prices], [Monthly food prices by market. Most columns turned out to be modelled estimates, not observed prices.], [No],
)

== The data audit: checking before trusting

Before any analysis, every file was profiled: how many rows, which years, how much is missing, whether the numbers look believable. This "data audit" (the files `01_data_inventory.md` and `07_data_quality_report.md` in `research_audit/`) changed the project in three important ways.

*1. The rainfall numbers were wrong, and we fixed them.* The first processed rainfall file said January 2010 had 1,256 mm of rain across the island. A normal January is about 143 mm. The cause was a technical detail of ERA5-Land: its rainfall value is a *running total* that builds up through each day and resets at midnight (UTC). The original script added up every hourly running total, which counts the same rain many times over. Monthly totals came out 12 to 21 times too large. The correct method is to take the value at midnight at the end of each day, which already holds that whole day's total. After the fix, yearly rainfall came out between 1,370 and 2,323 mm, which matches Sri Lanka's known climate, with the expected two rainy peaks (around May and around October to December). Only the corrected rainfall is used anywhere in the project.

*2. Some sources were the same data in disguise.* FAOSTAT's rice production is exactly the DCS figure (correlation 1.000). FAOSTAT rice imports and Comtrade rice imports agree almost perfectly (0.998), and CBSL rice imports equal Comtrade for 2021 to 2024. HARTI and CBSL prices at Dambulla move together very closely. Counting these as separate confirmations would have made the evidence look stronger than it is, so we treated each group as one source.

*3. Some sources were not usable.* CHIRPS had one day. HARTI had long gaps (2020 has only 25 weeks of bulletins), duplicate records, and price levels about 1.39 times higher than CBSL for the same carrot at the same market, because the definitions differ. The World Bank file had 816 columns, only 27 with data, and most of those were modelled. We set these aside.

#key[*Remember:* the rainfall bug is a good story to tell evaluators. It shows we checked our inputs instead of trusting them, and it explains why we never use the original processed weather file.]

= Testing what the data could support (12 November)

Next we listed fifteen possible research questions and, for each one, checked whether the data overlapped in time and place, and ran a quick first test where possible. This is in `03_research_feasibility.md`. The most important findings:

- *Rain and the rice harvest.* In the Yala season (March to August), wetter seasons went with a larger share of the sown rice land being harvested: correlation +0.68 over 16 seasons. That is a real-looking link, but 16 points is a small sample.
- *Rice production and imports.* Years with low rice production had higher imports: correlation −0.79 over 15 years. But most of that strength came from two unusual years, 2017 and 2022. Without them the correlation drops to −0.46.
- *Exchange rate and food prices.* Rice prices moved with the rupee in the same month and the next, but 2022 had very high general inflation as well, and we had no consumer price index to separate the two.
- *Rain and vegetable prices.* This was the surprise. With about 120 monthly points for each of seven vegetables, a wetter-than-usual month was followed a month later by a price rise for cabbage (correlation +0.60), carrot (+0.44) and brinjal (+0.40), while beans showed almost nothing (+0.08). Ten of the 28 tests were significant at the 5% level, when only about 1.4 would be expected by chance.

The big chain from weather to imports to prices turned out to be supportable *only for rice*, *only at the national level*, and *only with 14 to 16 yearly points*. You cannot run a convincing forecasting test on 15 numbers. The vegetable price link, on the other hand, had ten times more data and a pattern that differed clearly between vegetables.

= The decision that shaped everything

We changed direction. The vegetable question became the main study, and the rice, imports and exchange-rate findings became supporting context. The recorded decision (`06_recommended_research_direction.md`) gave the study a working title, *Weather Variability and Short-term Vegetable Price Forecasting in Sri Lanka*, and a central question:

#key[*Does adding rainfall information improve short-term forecasts of selected vegetable prices in Sri Lanka, and does the improvement differ between vegetables?*]

Why forecasting, and not just correlation? A correlation can look strong by accident, especially when you test many combinations. A forecasting test is harder to fool: you build the forecast using only information available at the time, then check it against what really happened in months the model had not seen. If rain genuinely carries information, forecasts that use it should miss by less.

= The pilot: a quick first attempt

Before the main test, we ran a quick, rough version (`forecast_pilot.py`). For each of the seven vegetables it compared four ways of forecasting next month's Dambulla price:

- *naive*: next month's price will be the same as this month's;
- *seasonal naive*: next month's price will be the same as that month last year;
- *prices only*: a simple model that predicts next month from the last few months' prices;
- *prices plus rain*: the same model with rainfall added.

The pilot also tried adding the exchange rate. The results were promising for rain (cabbage forecasts improved by 15%, brinjal by 14%, carrot by 5%) and clear for the exchange rate: *adding it made the forecasts worse for all seven vegetables*, by between 1.8% and 16.7%. So the exchange rate was dropped from the forecasting model.

But the pilot had flaws. Its definition of "wetter than usual" used the average of all years, including future years, which is a small form of cheating. Its statistical test ignored the fact that forecast errors in neighbouring months are related. We fixed all of this in the main version.

#note[*An honest caveat we always state:* because the pilot already looked at the same test months (July 2021 onwards), the main test is not a completely fresh confirmation. We call the results *exploratory* for this reason. The way to fix this in future is to test the method on months published after the study.]

= The main forecasting test (version 2)

The main test (`forecast_backtest_v2.py`) was designed in writing *before* it was run, so that we could not adjust it after seeing the results. The full design and code are in `analysis.typ`; here is the idea in plain words.

*Standing in the past.* Imagine it is the end of August 2021. We know every monthly price up to August and every month's rain up to August. We fit the model on that history and forecast September's price. Then we step forward to the end of September, refit with one more month of data, and forecast October. We repeat this until the last forecast, for October 2026. That gives 62 genuine forecasts per vegetable, each made without any knowledge of the future.

*Two forecasts every month.* At each step we make two forecasts. One uses only past prices. The other uses exactly the same past prices plus two rainfall numbers: how much wetter or drier than usual this month was, and the same over the last three months. "Usual" means the average for that calendar month in *earlier years only*, so no future information slips in.

*Which one missed by less?* After all 62 months, we compare the errors. For cabbage, the prices-only forecast missed by about 52 rupees a kilo on average; with rain, about 42. The overall error (measured in a way that weights large misses more heavily) was 19.7% smaller.

*Could that be luck?* With 62 forecasts, some difference will appear by chance. So we used tests designed for exactly this comparison, a bootstrap check that does not rely on textbook assumptions, and a correction for having tested seven vegetables at once. A vegetable was labelled *clear help* only if it passed all of these.

== The result

#table(
  columns: (0.9fr, 1fr, 1.1fr, 1.7fr),
  table.header([Vegetable], [Error reduction with rain], [Label (on the dashboard)], [What it means]),
  [Cabbage], [19.7%], [Clear help], [Survives every check.],
  [Brinjal], [12.4%], [Clear help], [Survives every check; the gain is larger in the second half of the test period.],
  [Carrot], [8.2%], [Clear help], [Passes, but closer to the line.],
  [Tomato], [4.8%], [A hint, not proven], [Significant before the correction for seven tests, not after.],
  [Snake gourd], [1.8%], [No clear effect], [Too small to trust.],
  [Pumpkin], [1.8%], [No clear effect], [Too small to trust.],
  [Beans], [−1.5%], [No help], [Rain made the forecast slightly worse.],
)

== Checking that the result is not fragile

We then asked whether the result depended on our particular choices. It did not, in any way that changes the story:

- *Rain measured in different places.* Using rain from a box around Dambulla, or around Nuwara Eliya in the hill country, instead of the whole island, gave similar gains (cabbage 18% and 22%).
- *A different market.* Running the same frozen model on Pettah (Colombo) prices gave the same pattern (cabbage 23%). Pettah is not truly independent, since it shares the weather and much of the supply, so we call this a consistency check, not a replication.
- *The 2022 crisis.* Removing the 2022 months barely changed cabbage or carrot.
- *A different definition of "usual" rain, or the monthly median price instead of the mean.* Gains moved by a few points; the ranking of vegetables did not change.
- *Overlap in the rain measures.* A later check found the three-month rain measure included the current month, overlapping the one-month measure. Re-running without the overlap changed nothing important (`forecast_rain_window_sensitivity.md`).

We also checked the uncertainty ranges. Each forecast comes with a range meant to contain the real price 8 times in 10. In practice it did so about 7 to 8 times in 10, so the ranges are a little too narrow. We say this openly.

#key[*Remember the three findings:* (1) rain helps some vegetables, clearly for cabbage, brinjal and carrot; (2) not all, and not precisely: even the best forecasts miss by about a quarter; (3) it is a research finding, not a price-prediction app, and it does not show that rain *causes* price changes.]

= From research to a story people can see

== First attempt: a ten-slide deck (12 to 13 November)

The first presentation was a ten-page storyboard in a Streamlit app: opening, scope and data, prices and rain, the forecasting experiment, how we evaluated it, the main result, robustness, accuracy, the wider context, and conclusions. Each page had a speaking guide.

We then audited every number in it. Fifty-five claims were checked against the analysis outputs and the raw data. None was wrong, but eight needed clearer wording (for example, that the 0.67 factor converting paddy to rice is an assumption, and that the exchange-rate chart shows the rupee's fall without estimating its effect on prices). After the corrections, all 55 were verified.

== Rethinking the audience

The dashboard is shown at the DST Data Gallery Walk to the general public and to judges. A ten-slide lecture on Clark–West tests is the wrong format for someone walking past a screen. So we rebuilt it around one principle: *let people discover the finding by playing with it, and keep the theory for when someone asks.* Pages 4 to 8 of the old deck (design, evaluation, result, robustness and accuracy) were merged into one interactive page where the viewer picks a vegetable and sees the verdict change. The method moved from the screen into the speaking guides.

== The five pages

#table(
  columns: (auto, auto, 1fr),
  table.header([Page], [Title], [Role in the story]),
  [1], [Vegetable prices swing wildly], [The problem: show how much prices move, and where rain falls.],
  [2], [Spot the pattern yourself], [The clue: the viewer finds that wet months come before price rises for some vegetables. Labelled clearly as a clue, not proof.],
  [3], [Does rain help? Try it], [The test: the viewer runs the forecasting comparison and sees the verdict for each vegetable.],
  [4], [Rain is only one piece], [The bigger picture: rice harvest, rice imports and the exchange rate, shown separately.],
  [5], [What did we learn?], [The ending: the viewer guesses which vegetable rain helps most, then reveals the three findings.],
)

The narrative arc is: a felt problem, a clue the viewer finds, a test the viewer runs, a step back, and the viewer's guess meeting the answer.

== Honesty rules for the dashboard

We set a few rules and kept to them:
- Every number on screen is read from the stored analysis results when the page loads. Nothing is typed in by hand, and nothing is re-estimated.
- Negative results look like positive ones: the same cards, just coloured grey or coral instead of green. Beans "No help" is shown as plainly as cabbage "Clear help".
- Page 2 says, on screen, that a pattern is a clue, not proof.
- The regional and Pettah views are checks, and the speaking guide says so.

= The final stretch (22 November)

== A colleague's improvement

A colleague added a rainfall-area picker to page 1. The rain bars under the price chart can now show rain for the whole island, around Dambulla, around Nuwara Eliya or around Colombo, and the chosen area is outlined on the map. Colombo was not one of the areas tested in the forecasting study, so it is there for comparison only, and the guides say so.

== Feedback from the organisers

The organisers asked every team to check seven things: data sources acknowledged; visualisations accurate and supported by data; every feature working and visible; consistent formatting; concise text; a justified method; and a clear story. In response we:
- replaced the font with Manrope for text and Newsreader for headings, and removed the old font files;
- redesigned the footer on every page so the data source stands out, with a clear "Source" label, and removed internal file names from it;
- removed rain map squares that sat over the sea (a quirk of how ERA5-Land marks land along the coast), so the map is accurate;
- fixed spacing on page 4 so notes no longer touch the card borders;
- replaced a row of pill-shaped labels on page 3, which looked like buttons, with a bar chart that ranks all seven vegetables by how much rain cut the forecast error.

The method explanation stays off the screen by design. The dashboard is for the public; the method is explained verbally when a judge asks, using the speaking guides and these documents.

= What we can and cannot claim

#table(
  columns: (1fr, 1fr),
  table.header([We can say], [We must not say]),
  [For cabbage, brinjal and carrot, past rain improves one-month-ahead forecasts beyond past prices.], [Rain causes price changes.],
  [The benefit differs by vegetable; for some it is zero or negative.], [Rain predicts vegetable prices (in general).],
  [The pattern holds with regional rain and at Pettah.], [The results hold for other markets or for consumers nationally.],
  [Forecast errors remain large, about 24% to 40% of the price.], [This is an accurate price-forecasting tool.],
  [The exchange rate did not improve these forecasts.], [The exchange rate does not matter for food prices.],
  [Rain, rice imports and the rupee are separate pressures on food.], [Any combined "vulnerability score".],
)

== Limitations, in plain words

- *The test months were seen before.* The pilot looked at the same period, so the result is exploratory, not a fresh confirmation.
- *Rain is measured broadly.* We use rain averaged over the island or over hand-drawn boxes, not on the farms that actually supply Dambulla.
- *Small sample.* 62 forecasts per vegetable, and neighbouring months are related, so the tests have limited power.
- *Prices are not adjusted for inflation.* We had no consumer price index. This does not change which model wins, because both forecast the same series.
- *Only rain is modelled.* Transport, policy, import controls and the 2022 crisis are not.
- *One month ahead only.* Going further ahead would need rainfall *forecasts*, which is a different study.

== What we would do next

Test the method on months published after the study (a truly fresh test); use rainfall from the actual growing areas; add a consumer price index; and, if rainfall forecasts become available, look at longer horizons.

= Where everything lives

#table(
  columns: (auto, 1fr),
  table.header([Folder or file], [What it holds]),
  [`raw/`], [The original downloaded data, never modified.],
  [`research_audit/`], [The data audit (files 01 to 07), the pilot, the main forecasting test and its report (`forecast_backtest_report_v2.md`), and the robustness checks (`forecast_validation_v2/`).],
  [`research-story/`], [The dashboard app itself. Run it with `uv run streamlit run app.py`.],
  [`research-story-materials/`], [Speaking guides per page (`story_pages/`), the claim audit, data source notes, tests, and the old ten-slide deck (`archive/`).],
  [`research-story-materials/summary.typ`], [The two-page project summary submitted with the dashboard.],
  [`reading/`], [These three documents.],
)

= Glossary

/ Wholesale price: the price traders pay at a bulk market such as Dambulla, before retail mark-up. Shown in rupees per kilogram.
/ Monthly average price: the mean of a month's daily prices. A month is only used if it has at least 10 days of prices.
/ Reanalysis: a weather dataset made by running a weather model and constantly correcting it with real observations, giving complete coverage with no gaps.
/ Rain anomaly: how much wetter or drier a month was than the usual amount for that calendar month.
/ Correlation (r): a number from −1 to +1 measuring how closely two things move together in a straight line. 0 means no straight-line link.
/ Forecast error: the gap between the forecast and the real price.
/ Backtest: testing a forecasting method by pretending to stand at each past month and forecasting the next, using only what was known then.
/ Clear help: our plain-language label for a vegetable where adding rain reduced forecast error and that reduction passed all statistical checks, including the correction for testing seven vegetables.
/ Exploratory: a result worth taking seriously but not yet confirmed on fresh data.
/ Paddy: rice still in its husk, as harvested. Milled rice is about two thirds of the paddy weight (we assume 0.67).
/ Yala and Maha: Sri Lanka's two rice-growing seasons. Yala runs roughly March to August, Maha roughly October to February.
