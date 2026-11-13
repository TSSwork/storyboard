// Summary: Can rainfall help anticipate vegetable prices?
// Compile: typst compile summary.typ

#let navy = rgb("#002941")
#let muted = rgb("#5a7482")
#let coral = rgb("#fd6e6e")
#let tint = rgb("#eef6fa")
#let rule-c = rgb("#dbe7ee")

#set document(title: "Summary: Can Rainfall Help Anticipate Vegetable Prices?")
#set page(paper: "a4", margin: (x: 2.4cm, top: 2.2cm, bottom: 2cm),
  footer: context [
    #set text(7.5pt, fill: muted)
    Weather and vegetable prices in Sri Lanka #h(1fr) #counter(page).display() of 2
  ])
#set text(font: "Manrope", size: 9.8pt, weight: 450, fill: navy, lang: "en", region: "gb")
#set par(justify: false, leading: 0.82em, spacing: 1.25em)

#show heading.where(level: 2): it => block(above: 2em, below: 0.9em, sticky: true)[
  #text(8pt, weight: 700, fill: coral, tracking: 0.12em)[#upper(it.body)]
]
#show link: set text(fill: rgb("#2f7292"))

#let stat(num, label) = box(width: 100%, inset: (y: 2pt))[
  #text(22pt, weight: 700)[#num] \
  #v(-2pt)
  #text(8.5pt, fill: muted)[#label]
]

// title
#text(8pt, weight: 700, fill: muted, tracking: 0.12em)[PROJECT SUMMARY]
#v(6pt)
#text(22pt, weight: 800)[Can rainfall help anticipate \ vegetable prices?]
#v(8pt)
#text(11pt, fill: muted)[An interactive research dashboard on weather and wholesale vegetable prices in Sri Lanka]
#v(18pt)

#grid(columns: (1fr, 1fr, 1fr), column-gutter: 18pt,
  stat[7][vegetables from the Dambulla market],
  stat[62][real monthly forecasts for each one],
  stat[3 of 7][where rain clearly helped],
)
#v(6pt)
#line(length: 100%, stroke: 0.5pt + rule-c)

== Concept

We wanted to know one thing. If we already know past vegetable prices, does last month's rain tell us anything extra about next month's price?

The dashboard has five pages. It starts with how much prices swing, next to a rain map of the island. Then the viewer looks for a pattern on their own, runs the main test, and sees the wider picture of rice, imports and the rupee. On the last page they guess the answer before it is revealed.

== Data sources

*Prices.* Daily wholesale prices published by the Central Bank of Sri Lanka (CBSL) for the Dambulla market, collected through Macro Lab, from August 2016 to October 2026. We used cabbage, brinjal, carrot, tomato, snake gourd, pumpkin and beans, and checked the results against Pettah prices. A month was kept only if it had at least 10 days of prices.

*Rain.* ERA5-Land from the Copernicus Climate Data Store (#link("https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land")[cds.climate.copernicus.eu]), hourly from 2010, on a grid of 541 land cells over Sri Lanka. We built monthly totals for the whole island and for areas around Dambulla and Nuwara Eliya. An early processing error was found and fixed, and only the corrected numbers are used. We looked at CHIRPS as well, but only one day of it was available.

*Context.* Paddy statistics from the Department of Census and Statistics, rice imports from FAOSTAT and UN Comtrade, and the USD/LKR rate from CBSL.

== Main message

Vegetable prices move a lot. Cabbage at Dambulla has sold for about Rs 16 a kilo in its cheapest month and about Rs 452 in its dearest. In six months out of ten the price moves by more than a fifth.

Adding past rain made the forecast clearly better for three vegetables. For the rest it did little or nothing.

#v(4pt)
#align(center, block(width: 88%, breakable: false, table(
  columns: (1.3fr, 1fr, 1.1fr),
  stroke: (x: none, y: 0.5pt + rule-c),
  inset: (x: 8pt, y: 6pt),
  align: (left, right, left),
  table.header(
    text(8pt, weight: 700, fill: muted)[VEGETABLE],
    text(8pt, weight: 700, fill: muted)[ERROR REDUCED BY],
    text(8pt, weight: 700, fill: muted)[VERDICT],
  ),
  [Cabbage], [19.7%], [Clear help],
  [Brinjal], [12.4%], [Clear help],
  [Carrot], [8.2%], [Clear help],
  [Tomato], [4.8%], [A hint, not proven],
  [Snake gourd, pumpkin], [about 1.8%], [No clear effect],
  [Beans], [slightly worse], [No help],
)))
#v(4pt)

Even the better forecasts still miss by about a quarter of the price in a typical month. So this tells us where rain carries useful information. It is not a price prediction tool, and it does not show that rain causes the changes.

== Statistical methods used

For each vegetable we compared two forecasts of next month's price. One used past prices only, through an autoregressive model with the number of past months chosen by AIC. The other used the same past prices plus rain that had already fallen, measured against the usual amount for that month in earlier years.

Both were refitted every month from August 2021, which gave 62 forecasts each. We compared errors with RMSE and MAE. To judge whether a gain was real we used the Clark and West test, backed up by the Diebold and Mariano test and a moving block bootstrap, with a Holm correction because seven vegetables were tested. We also checked 80% prediction intervals, regional rain and the Pettah market.

#v(6pt)
#block(fill: tint, inset: (x: 14pt, y: 11pt), radius: 8pt, width: 100%)[
  #text(8pt, weight: 700, fill: muted, tracking: 0.1em)[LIMITATIONS]
  #v(2pt)
  The test period was already seen in an earlier pilot, so the results are exploratory. Rain is averaged over large areas rather than measured on farms, the forecast errors are not independent, and prices are not adjusted for inflation.
]

== Platform

Built with Streamlit and Plotly in Python. The KPI cards change as the viewer picks a vegetable, a rain area or a market, and the rain map can be moved month by month. Automated tests check that every number on screen matches the stored results.

== AI assistance

All data comes from the official sources above. AI tools helped us write and debug the dashboard code and check our wording. The research question, the choice of models and tests, and the reading of the results are our own, and every number was checked against the analysis outputs.
