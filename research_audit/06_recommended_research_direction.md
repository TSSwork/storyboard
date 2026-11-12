# 06 — Recommended Research Direction

## Verdict on the original idea
The original chain (weather → production → imports → prices, with FX) is **not achievable as one integrated model across all commodities**, but it **is achievable as a narrowed, two-track study** built on rice and a handful of vegetables. Of the four things you wanted to know:

| Question | Verdict |
|---|---|
| 1. Defensible weather–paddy production analysis? | **Yes, partly.** Season-level, national, n = 16 per season; one credible signal (Yala rain vs harvested/sown, r = +0.68). Strong enough for a descriptive/associational chapter; much stronger once ERA5 is mapped to districts (needs district polygons). |
| 2. Defensible agricultural import-dependency analysis? | **Yes.** FAOSTAT (1961–2024) + Comtrade (15 yrs, partners). Must be framed as *apparent* dependency. |
| 3. Defensible food-price and exchange-rate analysis? | **Partly.** Strong data (131 months) but needs a CPI deflator to separate FX from general inflation. |
| 4. Meaningful connection between the three? | **Yes for rice (annual, n ≈ 15) and for weather → vegetable prices (monthly, n ≈ 120).** A single model linking all links for all commodities is not supported. |

## Recommended project
**Title:** *Weather, Staple Supply and Food-Price Exposure in Sri Lanka: Evidence from Rice and Selected Vegetables, 2010–2026*

**Central question (narrowed):** How do seasonal weather conditions relate to rice production and vegetable prices, and how exposed are rice and other staples to import dependency and exchange-rate movements?

**Structure — three modules sharing one weather dataset:**
1. **Module R (Rice chain, annual/seasonal)** — S2: rain/temperature → Maha/Yala sown/harvested/yield/production → rice imports (FAO/Comtrade/CBSL) → retail rice price and FX. Includes the 2014, 2017, 2022 shock years as case studies.
2. **Module V (Vegetables, monthly)** — S1: rain anomalies → CBSL/HARTI vegetable prices, lag structure, commodity ranking.
3. **Module D (Dependency & FX)** — S3 + S4: apparent import share and partner concentration for ≈15 staples; FX pass-through for imported vs domestic items (with CPI).
A short synthesis table (S5) combines the three indicators per commodity descriptively.

## Why this rather than the original
* It uses each dataset where it is strongest (ERA5 + DCS for rice; ERA5 + CBSL for vegetables; Comtrade/FAOSTAT for dependency).
* It avoids the three weak spots: non-paddy production (no seasonal data), self-sufficiency (no food balance), and a single all-commodity regression.
* It keeps the integrated story where the data really do connect (rice).

## Do first (order of work)
1. **Adopt corrected ERA5**: use `derived/era5_*.csv`; never `raw/EAR5/processed` `tp`. Re-run the extraction (`extract.py`) with `tp` = 00 UTC(D+1) logic or keep derived files.
2. **Collect two small items (only reasons to reopen acquisition):** CPI/CCPI monthly (CBSL/DCS) and district boundaries (GADM). Also derive sub-regional ERA5 means (Nuwara Eliya/Dambulla/Anuradhapura/Polonnaruwa boxes) from the existing `.nc`.
3. Build the analysis dataset: monthly panel (weather, FX, CBSL/HARTI prices) and annual panel (production, imports, rain, rice price).
4. Stabilise the evidence: pre-register the lag set and number of tests; apply FDR across commodities; run leave-one-year-out for 2017/2022.
5. Fix HARTI extraction only if location-level imported-vs-local prices are needed (`retail_subsidiary` labels).

## What can be concluded vs not
| Supportable | Not supportable |
|---|---|
| Wetter-than-normal months are followed by higher cabbage/carrot/brinjal prices (association, lag ≈ 1 month, n ≈ 120) | That rain *causes* those price rises (national rainfall, unobserved supply) |
| Shortfall years in paddy coincide with large rice imports (r = −0.79; direction robust to dropping 2017/2022, r = −0.46) | That imports are *caused* by the shortfall (policy, prices, 2022 FX crisis) |
| Yala harvested/sown share is higher in wetter Yala seasons | Weather determines national paddy yield (yield r −0.16/−0.34, n.s.) |
| Rice and imported-item prices co-move with LKR depreciation at 0–2 month lag | Pass-through magnitudes without a deflator |
| Import structure and concentration by HS commodity and partner (2010–2025) | Self-sufficiency ratios or "food security" levels |
| Three major datasets duplicate each other (FAO rice = DCS; CBSL = Comtrade rice) so evidence is thinner than the file count suggests | Treating each file as an independent confirmation |

## Risks to manage
* ERA5 `tp` bug found — any earlier result using `raw/EAR5/processed` precipitation must be recomputed.
* Multiple-testing and trend: report the number of tests; always detrend or difference.
* Comtrade 2018/2025 gaps: use FAOSTAT 2018 and CBSL 2025 for rice.
* "SPOR" ambiguity: please confirm which file you meant (I found only the SPOT FX rate).

## Acquisition status
Provisionally **closed**. Reopen only for CPI (M1), district polygons (M2); optionally FAO Food Balance Sheets (M3). The "difficult DCS PDF" is not needed.
