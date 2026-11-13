// Summary: Can rainfall help anticipate vegetable prices?
// Compile: typst compile summary.typ

#let navy = rgb("#002941")
#let muted = rgb("#52707f")
#let coral = rgb("#fd6e6e")
#let tint = rgb("#e3f1f7")
#let rule-c = rgb("#d8e6ee")

#set document(title: "Summary: Can Rainfall Help Anticipate Vegetable Prices?")
#set page(paper: "a4", margin: (x: 1.8cm, top: 1.25cm, bottom: 1.3cm),
  footer: context [#set text(8pt, fill: muted); Weather, vegetable prices and food system vulnerability in Sri Lanka #h(1fr) #counter(page).display()])
#set text(font: "Manrope", size: 9pt, weight: 450, fill: navy, lang: "en", region: "gb")
#set par(justify: false, leading: 0.58em, spacing: 0.75em)

#show heading.where(level: 2): it => block(above: 0.95em, below: 0.45em)[
  #box(width: 6pt, height: 6pt, fill: coral, baseline: -1pt) #h(5pt)
  #text(10.5pt, weight: 700)[#it.body]
]

#let note(body) = block(fill: tint, inset: (x: 10pt, y: 7pt), radius: 6pt, width: 100%, body)

// title
#text(8.5pt, weight: 600, fill: muted, tracking: 0.04em)[SUMMARY]
#v(-4pt)
#text(19pt, weight: 800)[Can Rainfall Help Anticipate Vegetable Prices?]
#v(-6pt)
#text(10pt, fill: muted)[An interactive research dashboard on weather and wholesale vegetable prices in Sri Lanka]
#v(2pt)
#line(length: 100%, stroke: 0.6pt + rule-c)

== Concept

We built an interactive dashboard that asks one question: if we already know past vegetable prices, does last month's rain tell us anything extra about next month's price? Its five pages show how much prices swing (with a rain map of the island), let the viewer look for a pattern, run the main test, look at rice, imports and the rupee, and finally reveal the conclusion after the viewer makes a guess.

== Data sources

Vegetable prices are the daily wholesale prices published by the Central Bank of Sri Lanka (CBSL) for the Dambulla market, collected through Macro Lab. We used seven vegetables: cabbage, brinjal, carrot, tomato, snake gourd, pumpkin and beans, from August 2016 to October 2026. Pettah prices were used as a second market to check the results. Daily prices were turned into monthly averages, and a month was kept only if it had at least 10 valid days.

Rainfall comes from ERA5-Land, a reanalysis dataset from the Copernicus Climate Data Store (#link("https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land")[cds.climate.copernicus.eu]). We downloaded hourly data for 2010 to 2026 on a 0.1 degree grid, which gives 541 land cells over Sri Lanka, and built monthly totals for the whole island and for small areas around Dambulla and Nuwara Eliya. An early processing error that overstated rainfall was found and fixed, and only the corrected series are used. CHIRPS rainfall was considered too, but only one day of it was available, so it was not used.

For the context page we used paddy statistics from the Department of Census and Statistics (DCS), rice imports from FAOSTAT and UN Comtrade, and the USD/LKR exchange rate from CBSL.

== Main message

Vegetable prices in Sri Lanka move a lot. At Dambulla, cabbage has sold for about Rs 16 a kilo in its cheapest month and about Rs 452 in its dearest, and in six months out of ten the price changes by more than a fifth from one month to the next. Rain affects how crops grow and reach the market, so we asked whether it can warn us early.

The answer depends on the vegetable. Adding past rain made the forecast clearly better for three of the seven:

#align(center, table(
  columns: (auto, auto, auto),
  stroke: none, inset: (x: 10pt, y: 3.6pt), align: (left, center, left),
  fill: (_, y) => if y == 0 { tint } else if calc.odd(y) { white } else { rgb("#f6fafc") },
  table.header([*Vegetable*], [*Smaller forecast error*], [*Verdict*]),
  [Cabbage], [19.7%], [Clear help],
  [Brinjal], [12.4%], [Clear help],
  [Carrot], [8.2%], [Clear help],
  [Tomato], [4.8%], [A hint, not proven],
  [Snake gourd, pumpkin], [about 1.8%], [No clear effect],
  [Beans], [slightly worse (1.5%)], [No help],
))

Even the better forecasts still miss by about a quarter of the price on a typical month, so this is a research finding about where rain carries useful information. It is not a tool for predicting prices, and it does not show that rain causes the price changes.

== Statistical methods used

We compared two models for each vegetable. The first predicts next month's log price from past prices only (an autoregressive model, with the number of past months chosen by AIC). The second uses exactly the same past prices and adds rain. The rain is always rain that had already fallen, measured as the difference from the usual amount for that calendar month in earlier years.

Both models were refitted every month from August 2021 onwards, which gave 62 real one month ahead forecasts per vegetable. We compared their errors with RMSE and MAE. To decide whether the improvement was real we used the Clark and West test for nested models, with the Diebold and Mariano test and a moving block bootstrap as extra checks, and a Holm correction because seven vegetables were tested. We also checked 80% prediction intervals, regional rain instead of national rain, and the Pettah market.

#note[
  #text(weight: 700)[Limitations.] The test period was already looked at in an earlier pilot, so the results are exploratory. The rain series are national or regional averages, not rain measured on the farms. The 62 forecast errors are not independent, and prices are nominal because no inflation index was added yet.
]

== Platform

The dashboard is built with Streamlit and Plotly in Python, with KPI cards that change as the viewer picks a vegetable, a rain area or a market, plus a month by month rain map of Sri Lanka. Automated tests check that every number on screen matches the stored results.

== AI assistance

The datasets come from the official sources listed above. AI tools were used to help write and debug the dashboard code and to check wording. The research question, the choice of models and tests, and the interpretation of the results are our own, and every number on the dashboard was checked against the analysis outputs.
