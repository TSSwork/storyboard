# 02 — Variable Catalogue

Concept map used in the audit: **Weather → Production → Imports → Prices (+ FX)**. Each concept lists the variables that really exist, their unit/definition and the join key.

## Weather (ERA5-Land, `raw/EAR5/downloads`, derived in `derived/`)
| Variable | Raw definition | Unit | Treatment | Derived column |
|---|---|---|---|---|
| `t2m` | 2 m air temperature, instantaneous | K | −273.15; area-weighted (cos lat) mean over 541 land cells | `t2m_mean/max/min` (daily from 24 hourly values) |
| `d2m` | 2 m dewpoint, instantaneous | K | same | `d2m_mean` |
| `tp` | Total precipitation, **accumulated from 00 UTC** (GRIB `stepType=accum`) | m | ×1000 → mm; **daily total of day D = value at 00 UTC of D+1** (never sum the hourly values) | `rain_mm`; monthly sum = Σ daily |
Join keys: date / month → season windows (Maha = Oct–Feb, Yala = Mar–Aug, my operational definition). No district-level weather exists (national mean only).

## Domestic production
| Source | Variable | Unit | Notes |
|---|---|---|---|
| DCS national | Sown, Harvested | 000 ac & 000 ha | Maha label `2010/11`, Yala `2011` |
| DCS national | Average yield | bu/ac & kg/ha | paddy |
| DCS national | Production | 000 bu & 000 Mt | paddy (not milled rice) |
| DCS district | Production | 000 Mt | 30 labels incl. totals |
| DCS district | Sown / Harvested / Yield by Major, Minor, Rainfed, Total | ha, ha, kg/ha | "-" = not applicable/missing |
| FAOSTAT production | Area harvested / Production / Yield | ha / t / kg/ha | 120 items; FAO "Rice" = paddy, identical to DCS |
Calendar-year paddy used in tests = Maha(`Y−1/Y`) + Yala(`Y`). Rice-equivalent uses an assumed 0.67 milling factor (**assumption**, not in data).

## Trade
| Source | Variable | Unit | Notes |
|---|---|---|---|
| Comtrade | `primaryValue` | USD | CIF for imports; use `partnerCode=0` rows **or** partner rows, never both (identical totals: 2012 17.885 bn each) |
| Comtrade | `netWgt`, `qty` | kg | qty available for 83–100 % of value (lowest 2023, 2016) |
| Comtrade | `flowCode` | M / X / RX / RM / DX / FM | Imports = `M` only. `FM` mirrors `M` (81,454 = 81,454 rows in 2022); `DX`/`RX` are export sub-breakdowns |
| Comtrade | `cmdCode`, `aggrLevel` | HS 2/4/6 digit | levels 2/4/6 each sum to the same total — pick one level |
| Comtrade | `classificationCode` | H3 (2010–12), H4 (2013–16), H5 (2017–22), H6 (2023–25) | codes shift with HS revisions |
| FAOSTAT trade | Import/Export quantity | t (also 1000 An, An, No for animals) | filter Unit == t |
| FAOSTAT trade | Import/Export value | 1000 USD | |
| CBSL | rice import qty | '000 MT, monthly | 2021–2026 only |
| CBSL | vegetable imports | USD mn, monthly | |
| CBSL | food & beverage imports | LKR mn, monthly | |

## Prices
| Source | Variable | Unit | Level |
|---|---|---|---|
| HARTI `retail_rice`, `retail_vegetables`, `retail_fruits`, `retail_fish`, `retail_meat`, `annex_*` | `min`,`max` (weekly range quoted by market) | Rs/kg (Rs/egg, Rs/nut) | ≈30–73 markets; I use mid = (min+max)/2 |
| HARTI `summary_wholesale`/`summary_retail` | min, max, avg_this_week, avg_last_week, avg_last_year, % changes | Rs/kg | Pettah wholesale / Colombo retail; 169–268 commodity keys |
| HARTI `farmgate` | min/max/avg | Rs/kg | producing areas, paddy + vegetables |
| CBSL daily | Rs/kg by commodity × wholesale/retail × market | Rs/kg | Pettah, Dambulla, Narahenpita |
| World Bank | `rice_various`, `wheat_flour`, `rice_fao` | LKR/kg | observed; all other columns modelled |

## FX
USD/LKR spot (daily), indicative/buy-sell for AUD, EUR, JPY, CNH, XAU, annual CBSL matrix of 15 currencies.

## Cross-dataset keys
| Link | Key | Resolution after harmonisation |
|---|---|---|
| ERA5 ↔ DCS | season window | national, seasonal, 16 seasons (2010–2025) |
| DCS ↔ Comtrade/FAO | calendar year | national, annual, 15–16 points |
| Comtrade/FAO ↔ HARTI | commodity (HS 1006 ↔ rice varieties) | annual vs weekly → must aggregate prices to year |
| ERA5 ↔ CBSL/HARTI prices | month | national rain vs market prices, ≈120 months |
| FX ↔ prices | month | ≈131 months |
