Yes. Based on the research work we've discussed, your project is a study of Sri Lanka's food production, vegetable prices, rainfall, rice import dependency and exchange-rate movements, with a main forecasting experiment examining whether rainfall improves short-term vegetable-price forecasts.

I'll separate the data sources from the analysis we performed, so you can use this as a starting point for your report's Data Sources and Methodology section.

One important distinction: I can reconstruct the project structure and methods from our previous work, but I don't currently have the actual `CLAIM_SOURCE_REGISTER.csv` contents. The links below are the official source portals, not a claim that every individual downloaded file or observation has been rechecked.

# 1. Data sources and what we did with them

## A. Agricultural production and trade

| Source                                               | Official link                                                                                                             | How it was used                                                                                                                                                   |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| FAOSTAT – Food and Agriculture Organization          | [FAOSTAT](https://www.fao.org/faostat/en/?utm_source=chatgpt.com)                                                         | Agricultural production and trade statistics. Used to examine Sri Lanka's crop production and agricultural trade over time.                                       |
| UN Comtrade                                          | [UN Comtrade API and data](https://comtradeplus.un.org/?utm_source=chatgpt.com)                                           | International merchandise trade data. Used to examine rice imports, import quantities and values, and import dependency.                                          |
| Department of Census and Statistics (DCS), Sri Lanka | [Paddy Statistics](https://www.statistics.gov.lk/Agriculture/StaticalInformation/Paddy_Statistics?utm_source=chatgpt.com) | Domestic paddy production, harvested extent and yield by season and district. Used to compare domestic production with imports and examine production shortfalls. |

FAOSTAT provides internationally comparable agricultural statistics, while UN Comtrade provides detailed trade records. DCS provides Sri Lanka's official paddy statistics.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://www.fao.org\&sz=32)

FAOHome+2



What we derived from these sources:

- Domestic paddy production trends.
- Rice import trends and import-share calculations.
- Production and import relationships.
- Import-share spikes, including the peaks identified in 2014, 2017 and 2022.
- Paddy-production and rice-import correlations.

Important data caveats: The earlier audit identified a missing UN Comtrade observation for 2018 and incomplete 2025 data. Those should be acknowledged when discussing the relevant time series.

## B. Rainfall and climate data

| Source                                            | Official link                                                                                               | How it was used                                                                       |
| ------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| ERA5-Land – Copernicus Climate Change Service     | [ERA5-Land dataset](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land?utm_source=chatgpt.com) | Main rainfall source for the weather-informed vegetable-price forecasting experiment. |
| CHIRPS – Climate Hazards Center, UC Santa Barbara | [CHIRPS rainfall data](https://www.chc.ucsb.edu/data/chirps?utm_source=chatgpt.com)                         | Alternative rainfall dataset considered for comparison and validation.                |

ERA5-Land provides gridded land-surface climate estimates at approximately 0.1° resolution. CHIRPS combines satellite rainfall estimates and station observations at 0.05° resolution.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://cds.climate.copernicus.eu\&sz=32)

Climate Data Store+1



What we did with ERA5-Land:

- Extracted rainfall data for Sri Lanka.
- Created a national land-area rainfall average using cosine-latitude weighting.
- Created regional rainfall series for Dambulla and Nuwara Eliya.
- Calculated rainfall anomalies using historical monthly climatology.
- Tested whether past rainfall could improve one-month-ahead vegetable-price forecasting.

The forecasting experiment used:

- National rainfall as the primary specification, based on 541 land grid cells.
- Dambulla and Nuwara Eliya regional boxes as secondary specifications, each using 36 cells.
- A rainfall anomaly based on the same calendar month's mean over previous years.
- Additional sensitivity checks using a fixed 2010–2015 climatology and a z-score anomaly.

The regional boxes were hand-defined proxies, not official agricultural district boundaries.

Important caveat: Our earlier review identified problems with one processed ERA5 rainfall output, so that output should not be treated as validated merely because it came from ERA5-Land. CHIRPS coverage in the material we reviewed was also limited to one day, so it was not a full-period independent validation.

## C. Vegetable prices and food prices

| Source                                                              | Official link                                                                                        | How it was used                                                                                                                               |
| ------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| HARTI – Hector Kobbekaduwa Agrarian Research and Training Institute | [Daily Food Commodities Bulletin](https://www.harti.gov.lk/daily-price.php?utm_source=chatgpt.com)   | Daily wholesale food prices, including vegetables from markets such as Dambulla and Pettah. Main price data used in the forecasting research. |
| World Bank – Real Time Food Prices (RTFP)                           | [Sri Lanka RTFP dataset](https://microdata.worldbank.org/catalog/6169?utm_source=chatgpt.com)        | Monthly food-price estimates by product and market. Used as an additional source for historical food-price comparisons.                       |
| HARTI                                                               | [Weekly Food Commodities Bulletin](https://www.harti.gov.lk/weekly-price.php?utm_source=chatgpt.com) | Weekly price information for comparison with daily and monthly trends.                                                                        |

HARTI publishes daily wholesale price information for markets including Dambulla and Pettah. The World Bank RTFP dataset contains monthly estimates across Sri Lankan markets.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://www.harti.gov.lk\&sz=32)

Harti+2



What we did with these sources:

- Collected daily vegetable prices.
- Focused the forecasting experiment on seven vegetables from the Dambulla wholesale market.
- Aggregated valid daily observations into monthly mean prices.
- Required at least 10 valid daily observations for a month; missing months were not filled.
- Used monthly median prices as a sensitivity check.
- Used Pettah prices as an additional robustness comparison.

The seven vegetables were:

1. Cabbage
2. Brinjal
3. Carrot
4. Tomato
5. Snake gourd
6. Pumpkin
7. Beans

Important caveat: HARTI and World Bank price observations are not necessarily independent. The RTFP dataset uses a combination of directly observed prices and machine-learning estimates of missing prices, drawing on sources including WFP, FAO and national statistical offices. It should not be treated as entirely observed market data.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://microdata.worldbank.org\&sz=32)

Microdata World Bank+1



## D. Exchange rates and macroeconomic data

| Source                           | Official link                                                                                                                                            | How it was used                                                                                                      |
| -------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| Central Bank of Sri Lanka (CBSL) | [Daily Exchange Rates](https://www.cbsl.gov.lk/cbsl_custom/exrates/exrates.php?utm_source=chatgpt.com)                                                   | Exchange-rate information, particularly USD/LKR, for examining currency movements alongside food prices and imports. |
| CBSL                             | [Economic and Social Statistics – External Trade](https://www.cbsl.gov.lk/en/statistics/economic-and-social-statistics/chapter-4?utm_source=chatgpt.com) | External trade, imports and exchange-rate statistics.                                                                |
| CBSL                             | [Economic Data Library](https://www.cbsl.gov.lk/en/statistics/data?utm_source=chatgpt.com)                                                               | Economic data and statistical series.                                                                                |

CBSL provides daily indicative exchange rates and published external-trade statistics.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://www.cbsl.gov.lk\&sz=32)

Central Bank of Sri Lanka+2



What we did:

- Examined exchange-rate movements alongside rice imports and food prices.
- Produced the page 9 exchange-rate comparison.
- Used the exchange-rate panel descriptively.

The exchange-rate panel should be interpreted as descriptive co-movement only, not evidence that exchange-rate changes caused a particular change in rice prices or import prices.

## E. Inflation and consumer price information

| Source                              | Official link                                                                                                           | How it relates to the project                             |
| ----------------------------------- | ----------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------- |
| Department of Census and Statistics | [Monthly NCPI](https://www.statistics.gov.lk/InflationAndPrices/StaticalInformation/MonthlyNCPI?utm_source=chatgpt.com) | National consumer price index and inflation information.  |
| Department of Census and Statistics | [Inflation and Prices](https://www.statistics.gov.lk/InflationAndPrices/StaticalInformation?utm_source=chatgpt.com)     | CCPI, NCPI, producer prices and retail-price information. |

[image](https://www.google.com/s2/favicons?domain=https://www.statistics.gov.lk\&sz=32)

Department of Census and Statistics+1

This is relevant to interpreting nominal food prices: increases in LKR/kg do not necessarily represent increases in real prices.

However, based on our previous project review, CPI/NCPI data had not been fully integrated into the forecasting model. The model uses nominal prices, so inflation remains a limitation.

# 2. What we actually built and analysed

This is the important part if you need to explain the work in your research presentation.

Research work overview

1. Agricultural production and import analysis

   Used FAOSTAT, UN Comtrade and DCS data to examine Sri Lanka's domestic production and rice-import dependency.
2. Weather and production analysis

   Used rainfall information to investigate relationships between rainfall patterns, agricultural production and food supply.
3. Rice production and import relationships

   Examined import-share peaks and correlations between detrended paddy production and rice imports.
4. Vegetable-price analysis

   Used HARTI wholesale prices to analyse historical price patterns across seven vegetables.
5. Weather-informed price forecasting

   Compared price-only autoregressive models with models that also include past rainfall.
6. Statistical validation and robustness

   Compared forecast errors, performed statistical tests, checked alternative rainfall specifications and evaluated uncertainty intervals.

## 3. The main forecasting experiment

This was the most developed quantitative part of the work.

Research question:

Does adding historical rainfall information improve one-month-ahead vegetable-price forecasts compared with using historical prices alone?

The refined experiment used an expanding-window backtest with 62 forecast origins per vegetable, beginning in August 2021.

| Model          | Description                                                  |
| -------------- | ------------------------------------------------------------ |
| Naive          | Uses the latest observed price                               |
| Seasonal naive | Uses the price from the corresponding month one year earlier |
| Price-only AR  | Autoregressive model using historical prices                 |
| AR + rainfall  | Same price terms, with additional rainfall anomaly variables |

The AR lag structure was selected using AIC from a predefined set. The rainfall model included the current-month anomaly and a three-month rainfall-anomaly average.

We used:

- RMSE and MAE for forecast-error comparison.
- Clark–West tests for nested forecast models.
- Diebold–Mariano tests as supplementary evidence.
- Moving-block bootstrap tests with block lengths of 3, 6 and 12.
- Holm multiple-testing correction across the seven vegetables.
- 80% prediction intervals as an exploratory uncertainty measure.

The model specification and results are documented in the backtest material from our earlier work.&#x20;

Pasted text(7).txt

Pasted text(7).txt



### Main findings from the refined backtest

Exploratory results, not causal evidence

| Vegetable   | Approx. log-RMSE improvement from rainfall |
| ----------- | ------------------------------------------ |
| Cabbage     | 20%                                        |
| Brinjal     | 12%                                        |
| Carrot      | 8%                                         |
| Tomato      | 5%                                         |
| Snake gourd | 2%                                         |
| Pumpkin     | 2%                                         |
| Beans       | -1.5%                                      |

The statistical interpretation was:

- Cabbage and brinjal: Evidence supported after multiple-testing correction.
- Carrot: Supported, but borderline.
- Tomato: Exploratory evidence only.
- Snake gourd, pumpkin and beans: No reliable evidence of improvement.

These findings are limited by the relatively short test window, the earlier pilot-informed selection of test months and commodities, and the use of rainfall proxies rather than measured farm-level rainfall.&#x20;

Pasted text(7).txt



# 4. References and source records for the final report

For your bibliography, I would organize the references into these groups:

| Reference group          | What to cite                                                                                   |
| ------------------------ | ---------------------------------------------------------------------------------------------- |
| Agricultural statistics  | FAOSTAT database; DCS Paddy Statistics                                                         |
| International trade      | UN Comtrade database                                                                           |
| Rainfall                 | ERA5-Land dataset; CHIRPS dataset                                                              |
| Food prices              | HARTI Daily Food Commodities Bulletin; World Bank RTFP                                         |
| Macroeconomic statistics | CBSL exchange-rate and external-trade statistics                                               |
| Forecasting methodology  | The statistical methods and papers already listed in your project's six-reference bibliography |

One thing I don't want to invent: Our earlier audit said all six research citations were checked against publisher or repository records, but I don't have their exact titles and bibliographic entries in the retrieved project context. The audit also identified missing DOI information and author accents for Künsch and Muñoz-Sabater. Those exact references should be taken from your `CLAIM_SOURCE_REGISTER.csv` and existing bibliography rather than reconstructed from memory.

# 5. Where to find the exact record of what we used

These are the two files you mentioned in the completed audit:

- `research-story/AUDIT_REPORT.md` — claim verification results, explanations and proposed wording fixes.
- `research-story/CLAIM_SOURCE_REGISTER.csv` — the source mapping for individual claims.

The CSV is particularly important because it should let us connect each slide's claim to its exact source, rather than just citing a general data portal.

My recommendation: Use the tables above as your preliminary data-source and methodology reference, but use the source register to prepare the final bibliography. That will give you a defensible chain from each dataset, through the processing and analysis, to the result shown in the presentation.

If you upload `CLAIM_SOURCE_REGISTER.csv` and `AUDIT_REPORT.md`, I can turn them into a complete, properly formatted reference list with the exact dataset links, DOI links, and a source-by-source explanation of how each dataset was processed and used.