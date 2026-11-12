# 07 — Data Quality Report

Severity: **HIGH** = invalidates a result if ignored; **MED** = needs handling; **LOW** = note.

## 1. ERA5-Land — validated (and an error found)
| # | Finding | Evidence | Sev. |
|---|---|---|---|
| E1 | **Precipitation was mis-aggregated.** `tp` in ERA5-Land is accumulated from 00 UTC each day (`GRIB_stepType=accum`). `extract.py` resamples to days with `.sum()` of hourly accumulations (and the "daily" CSV is in fact hourly). Monthly `tp` is therefore 12.4–21.4× too large (median 14.3×): e.g. Jan-2010 reported **1,256 mm** vs a realistic ≈143 mm January climatology. | Compared `EAR5/processed/sri_lanka_monthly_weather.csv` with `derived/era5_monthly.csv`; hourly pattern in `era5_2015_03.nc`: 1.09 mm at 00 UTC (prior-day total), 0.01…1.94 mm rising through the day | **HIGH** |
| E2 | Correct method: daily total of day D = `tp` at 00 UTC of D+1. Corrected national annual rain 1,370–2,323 mm (2010–2025), bimodal climatology (Oct 294, Nov 351, Dec 241 mm; Mar 82 mm min) — plausible. | `derived/era5_daily.csv`, `era5_monthly.csv` | – |
| E3 | Temperature/dewpoint fine: corrected daily means differ ≤ 0.144 °C from the original (averaging order). | | OK |
| E4 | Spatial: original polygon (18 vertices) selects 727 cells, of which 219 are sea (NaN, silently skipped) and **33 coastal land cells (6 %) fall outside the polygon**. ERA5-Land's own land mask gives 541 cells; I used those. | cell counts via shapely | MED |
| E5 | Temporal coverage: 203 monthly files, 147,693 hourly steps, **no gaps, no duplicate hours**; 2026-11 has 6 days. | `derived/era5_file_checks.csv` | OK |
| E6 | `expver`: 200 files 0001 (final), 2026-09/10 = 0005 (ERA5T preliminary), one file mixed. Last 2–3 months may be revised. | | LOW |
| E7 | 2026 is incomplete (Jan–Oct); 2026 annual rain (1,272 mm) must not be compared with full years. | | MED |
| E8 | National mean only — cannot be matched to district-level DCS data without district polygons (not in project). | | MED |
| E9 | CHIRPS holds one day (2010-01-01): mean 0.39 mm vs ERA5-Land 0.66 mm that day — same order, but a single day cannot validate anything. | | LOW |

## 2. DCS paddy
* National series complete (no missing); two unit systems.
* District workbooks: header layouts differ across 8 files; year labels `1978/1979` (Maha) vs `1979` (Yala); typo `198` for 1980 in Yala production header; 19.3 % of extent/yield cells are "-" (not applicable).
* District labels: `KILINOCHCHI/KILINOCHCHIYA/KILLINOCHCHI`, `MAHAWELI 'H'` ×3 spellings, plus aggregate rows `SRI LANKA`, `HIGHLAND PADDY`, and `UDAWALAWE` – double-counting risk if all rows are summed.
* Yala 2025 and Maha 2025/26 are the last seasons (preliminary).

## 3. FAOSTAT
* Production: no duplicate (Item, Element, Year); flags 64 % official (A), 19 % estimated (E), 13 % imputed (I), 2.8 % missing (X). Rice 2010–2024 all flag A (= DCS).
* Trade: no duplicate keys, but item list mixes commodities and **aggregates** ("Total Merchandise Trade" 18.3 bn USD in 2024, "Cereals", "Food Excluding Fish"); quantity units differ (t, An, 1000 An, No). Filter by Unit and exclude aggregates before summing.

## 4. UN Comtrade
* Record counts match the API manifests for all 15 years.
* **2018 absent** from the annual API; monthly 2018 files are 2-byte stubs (only 2012 monthly was downloaded). FAOSTAT trade does cover 2018 (rice imports 163 kt) and can bridge it for annual commodity quantities.
* **2025 is incomplete**: rice 84.1 kt vs CBSL 184.7 kt; big onion 131 kt vs ~300 kt in 2021–23. Do not interpret 2025 as a fall.
* HS revision breaks (H3 2010–12, H4 2013–16, H5 2017–22, H6 2023–25). Sugar (HS 1701) net weight 30 t in 2023 vs ~450–570 kt other years; netWgt coverage 83 % in 2023 → probable classification/weight gap, unexplained.
* Flow structure: 2010–2016 only M, X, RX; from 2017 add DX, FM (and RM). `FM` (foreign import) rows are one-for-one duplicates of `M`. Never sum flow codes.
* Quantities: `qty` present for 83–100 % of value; netWgt ≈ qty for rice.

## 5. HARTI extracted tables
| # | Finding | Evidence | Sev. |
|---|---|---|---|
| H1 | Coverage 2015-06-12 → 2026-10-16, 516 weeks from 529 PDFs; **38 gaps > 7 days**; 2015 only 21 weeks, **2020 only 25**, 2021 41; longest gaps 112 days (mid-2020, early-2021). | weeks per year table | MED |
| H2 | Duplicate keys: e.g. `retail_rice` 1,356 rows in 4 weeks (2023-04-14 …) where two bulletins cover the same week with slightly different values (368 exact duplicates). | | MED |
| H3 | **`retail_subsidiary` – 33,817 rows share keys**: leaf column labels are ambiguous ("Imported", "Local" repeat under several groups). Not analysis-ready. Use `summary_retail` instead (Colombo series for chillies, onion, potato, dhal). | | HIGH (for that table) |
| H4 | **`wholesale_rice` has 1,283 distinct location labels and only 125 weeks** (table merges wholesale/retail layout in some years). `wholesale_subsidiary` exists for only 26 weeks (2026). Not usable. | | HIGH (for those tables) |
| H5 | min > max in 0.2 % of `summary_*` rows (106 + 49), 32 in `retail_vegetables`: column mis-assignment in a few pages. Filter or drop. | | LOW |
| H6 | Market composition changes (retail_rice: median 29 locations/week, 39 distinct overall; 73 in fruits) → the all-market mean is not a fixed basket. Use a fixed market (Colombo/Dambulla) for strict comparisons. | | MED |
| H7 | HARTI ≈ 1.39× CBSL for the same Dambulla retail carrot, though r = 0.96 → price definitions differ; never mix levels across sources. | | MED |
| H8 | Rice prices: Nadu 1 retail median 74 (2015) → 121 (2021) → 220 (2022) → 230 (2026) Rs/kg. 1 outlier > 5× median. | | LOW |

## 6. World Bank RTFP
816 columns but 27 populated. Only `rice_various`, `wheat_flour`, `rice_fao` are observed; every other populated column is a modelled index (open/high/low/close/trust/inflation). Observations by year for rice_various: 282 (2015), 279, 217, **27 (2018), 12, 32, 20, 6 (2022)**, 240, 416, 305. Rows per market-month are unique (0 duplicates) but 77 % of rice cells are empty. Several columns are in the file for other countries' commodities and are 100 % empty.

## 7. CBSL
* Daily prices: 2016 only 101 days (starts Aug), ≈235–242 per year after; Narahenpita retail 38–79 % missing, green chilli/lime ≈ 30 % missing. Units "as published".
* "Exchange-rate monthly" file is **annual** (40 rows).
* Rice imports begin Jan 2021; equals Comtrade exactly for 2021–24.
* `status = b` flag (break?) on 14 % of food/vegetable import rows — meaning not documented in the file.
* JPY sell rate up to 2,785.9 in `Buy and Sell Exchange Rates.csv` (probably quoted per different unit in some periods) — not used.

## 8. Cross-source independence
FAOSTAT rice production = DCS (r 1.000); FAOSTAT rice imports ≈ Comtrade (r 0.998); CBSL rice imports = Comtrade; HARTI ≈ CBSL (Dambulla). Counting these as separate observations would inflate confidence.

## 9. Gaps that cannot be repaired from the project data
District-level weather; CPI/CCPI deflator; stock changes and non-food use for rice; Comtrade 2018 and complete 2025; crop-specific (non-paddy) national production beyond FAOSTAT annual series; consumer expenditure weights.
