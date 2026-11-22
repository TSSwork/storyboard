// Summary: Can rainfall help anticipate vegetable prices?
// Same layout as the other team's summary, set in Manrope.
// Compile: typst compile summary.typ

#set document(title: "Summary: Can Rainfall Help Anticipate Vegetable Prices?")
#set page(paper: "a4", margin: (x: 2.5cm, top: 2.3cm, bottom: 2cm))
#set text(font: "Manrope", size: 10pt, weight: 450, fill: black, lang: "en", region: "gb")
#set par(justify: false, leading: 0.7em, spacing: 0.8em)
#show link: set text(fill: rgb("#1155cc"))
#show link: underline

#let section(title) = block(above: 1.15em, below: 0.6em, text(weight: 700)[#title:])

#text(weight: 700)[SUMMARY: CAN RAINFALL HELP ANTICIPATE VEGETABLE PRICES?]

#section[Concept]
We built an interactive dashboard that asks whether last month's rain tells us anything extra about next month's vegetable price, once we already know past prices. It has five pages: how much prices swing (with a rain map of the island), a page where the viewer looks for a pattern, the main forecasting test, the wider picture of rice, imports and the rupee, and a final page where the viewer guesses the answer before it is revealed.

#section[Data source]
Vegetable prices are the daily wholesale prices published by the Central Bank of Sri Lanka (CBSL) for the Dambulla market, collected through Macro Lab, from August 2016 to October 2026. We used seven vegetables (cabbage, brinjal, carrot, tomato, snake gourd, pumpkin and beans) and checked the results against Pettah prices. A month was kept only if it had at least 10 days of prices. Rainfall comes from ERA5-Land on the Copernicus Climate Data Store (#link("https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land")[https://cds.climate.copernicus.eu]), hourly from 2010 on a grid of 541 land cells over Sri Lanka, turned into monthly totals for the whole island and for areas around Dambulla and Nuwara Eliya. An early processing error was found and fixed, and only the corrected series are used. CHIRPS rainfall was considered as well, but only one day of it was available. For the context page we used paddy statistics from the Department of Census and Statistics, rice imports from FAOSTAT and UN Comtrade, and the USD/LKR rate from CBSL.

#section[Main message]
Vegetable prices in Sri Lanka move a lot. Cabbage at Dambulla has sold for about Rs 16 a kilo in its cheapest month and about Rs 452 in its dearest, and in six months out of ten the price changes by more than a fifth. Rain affects how crops grow and reach the market, so we asked whether it can give an early warning. The answer depends on the vegetable. Adding past rain clearly improved the forecast for cabbage (19.7% smaller error), brinjal (12.4%) and carrot (8.2%). Tomato showed only a hint (4.8%), snake gourd and pumpkin showed no clear effect, and beans got slightly worse. Even the better forecasts still miss by about a quarter of the price in a typical month, so this is a finding about where rain carries useful information, not a price prediction tool, and it does not show that rain causes the changes.

#section[Statistical methods used]
For each vegetable we compared two forecasts of next month's price: an autoregressive model using past prices only (number of past months chosen by AIC), and the same model with rain that had already fallen added, measured against the usual amount for that month in earlier years. Both were refitted every month from August 2021, giving 62 forecasts each, and compared using RMSE and MAE. To judge whether a gain was real we used the Clark and West test, supported by the Diebold and Mariano test and a moving block bootstrap, with a Holm correction because seven vegetables were tested. We also checked 80% prediction intervals, regional rain and the Pettah market. The results are exploratory: the test period was seen in an earlier pilot, rain is averaged over large areas rather than measured on farms, and prices are not adjusted for inflation.

#section[Platform]
The dashboard is built with Streamlit and Plotly, with KPI cards that change as the viewer picks a vegetable, a rain area or a market, a month by month rain map of Sri Lanka with a rain-area picker (whole island, Dambulla, Nuwara Eliya or Colombo, the last shown for comparison only), a bar chart comparing all seven vegetables, and charts that update with each choice.

#section[AI assistance]
All data comes from the official sources listed above. AI assistance was used to help write and debug the dashboard code and to check wording. The research question, the choice of models and tests, and the interpretation of the results are our own, and every number on the dashboard was checked against the analysis outputs.
