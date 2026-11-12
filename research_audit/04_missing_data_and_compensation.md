# 04 — Missing Data and Compensation Strategies

Priority: **P1** = changes what can be claimed and is cheap; **P2** = useful, moderate effort; **P3** = optional.

| # | Missing item | Why needed | Question affected | Proxy in hand | Official alternative source | Narrow the question instead? | Collect? |
|---|---|---|---|---|---|---|---|
| M1 | **CPI / CCPI (monthly)** | separate imported-food inflation from general inflation; real prices | Q7, Q8 | CBSL food-and-beverage imports (LKR) is not a price index; a domestic price-basket (e.g. HARTI rice+veg) could proxy but is circular | CBSL / DCS CCPI & NCPI (publicly downloadable) | Use *relative* prices (imported ÷ domestic item) which cancel general inflation | **P1 — yes, one small CSV**; the key to making the FX question defensible |
| M2 | **District boundaries** | map ERA5 grid cells to districts → district-level weather vs DCS district paddy (30 districts × 40+ seasons gives a real panel instead of n = 16) | Q1, Q12 | `chirp/boundaries/countries.geojson` is country-level only | GADM / OSM / Survey Dept district polygons | National analysis only (current) | **P1 — yes**; converts weakest result into strongest |
| M3 | Stocks, seed, feed, waste, non-food use (food balance sheet) | genuine self-sufficiency | Q4, Q14 | FAOSTAT apparent supply = prod + imports − exports | FAO Food Balance Sheets (national, annual) | Report "import share of apparent supply" and say so | P2 (small, annual) |
| M4 | Comtrade 2018 and complete 2025 | gap-free import series | Q5, Q3 | FAOSTAT trade 2018 (rice 163 kt); CBSL rice 2025 (185 kt) | Comtrade re-pull later in 2026-27; Sri Lanka Customs | Use FAOSTAT as primary quantity source 2010–2024, Comtrade for partner structure | P3 (retry API later) |
| M5 | Crop-specific seasonal production (vegetables, other crops) | link weather to non-paddy supply | Q13 | none | DCS/Dept of Agriculture crop statistics (the "difficult PDF") | Restrict production side to paddy; use *prices* as the supply signal for vegetables (Q9) | **No** — not worth the manual PDF extraction |
| M6 | Full-year ERA5 2026 / final ERA5 (non-ERA5T) | complete last year | Q1, Q9 | ERA5T 2026-09…11 usable with caveat | ERA5 final release (≈ 2–3 months lag) | Drop 2026 from annual analysis | P3 |
| M7 | World price benchmark (e.g. FAO Food Price Index, wheat/rice export prices) | external supply shocks | Q7 | Comtrade unit values (annual) | FAO FPI (public) | Use unit values + FX only | P2 |
| M8 | Monthly Comtrade (or CBSL monthly HS imports) | monthly import vs monthly price links | Q15 | CBSL monthly rice qty 2021+, vegetables USD, food LKR | CBSL external-sector tables | Annual only | P3 |
| M9 | Weather in growing areas (Nuwara Eliya/Dambulla basins) rather than national mean | vegetable-price link | Q9 | national mean rain | same ERA5 grid, sub-region means from existing `.nc` — no new download | Do after M2 (or with a hand-drawn box) | **P1 — free, from existing .nc** |
| M10 | Irrigation / water-release data (Mahaweli, reservoirs) | explain Yala outcomes | Q1 | DCS "Major/Minor/Rainfed" split | Irrigation Dept | Use irrigation share by district from DCS | P3 |
| M11 | ENSO / IOD indices | seasonal climate drivers | Q1 | ERA5 anomalies | NOAA ONI (one table) | skip | P3 |
| M12 | Extraction fix for HARTI `retail_subsidiary`, `wholesale_rice`, `wholesale_subsidiary` | onion/potato/dhal/chilli location-level prices, wholesale rice | Q7, Q10 | `summary_retail` / `summary_wholesale` already carry these for Colombo/Pettah (268 retail / 169 wholesale commodity keys) | re-run `extract.py` with leaf-label fixes | Use the summary tables | P2 (no new data needed) |

## Dataset-level verdicts
| Dataset | Verdict |
|---|---|
| ERA5-Land | **Keep**; replace `tp` with the corrected derived series; consider sub-regional means |
| DCS national + district | **Keep**; core supply data |
| FAOSTAT production | Keep for non-rice crops (annual); drop for rice (duplicate) |
| FAOSTAT trade | **Keep** — covers 2018, 1961–2024, filter aggregates |
| Comtrade | Keep for partners and HS6 detail; not for 2018/2025 totals |
| HARTI | **Keep** `summary_retail`, `summary_wholesale`, `retail_rice`, `retail_vegetables`, `farmgate`; park the rest |
| CBSL daily prices | **Keep** — cleaner than HARTI for vegetables |
| CBSL FX / imports | Keep (spot FX monthly; rice imports monthly 2021+) |
| World Bank RTFP | **Drop** from the core analysis (3 observed series; collapses 2018–2022); optional rice sanity check |
| CHIRPS | **Drop** (one day) unless re-downloaded; ERA5 suffices |
| DCS "difficult PDF" | **Do not pursue** |
| "SPOR" | Not present; confirm whether SPOT FX was meant |

**Recommendation:** Reopen acquisition only for M1 (CPI) and M2 (district polygons). Both are small, public, and decisive for a defensible FX and a district-level weather analysis. Everything else can be handled by narrowing the question.
