# Evidence and citation audit — 10-page storyboard

> Folder layout note: this audit was written before the folder was reorganised. "README" below means the page's speaking guide in `story_pages/`; `build_figures.py` is now `scripts/build_figures.py` (slide text is in `story/slide_copy.py`); the audit script is `scripts/audit_claims.py`.

Scope: the ten slides, their speaking guides (`story_pages/NN_*.md`; called "READMEs" below because that was their name when the audit was run), `docs/references/`, and every number or claim in them. Register: `docs/CLAIM_SOURCE_REGISTER.csv` (55 rows). Reproduce with `uv run python scripts/audit_claims.py` (run from `research-story/`; it needs the full research project one level up, because it recomputes numbers from `research_audit/` and `raw/`), which recomputes values from `research_audit/` and `raw/` (read-only; it re-runs `forecast_pilot.py` without changing it).

## Result
| Status | Count |
|---|---|
| Verified | 48 |
| Partially verified | 5 |
| Needs clarification | 2 |
| Unsupported | 0 |

No claim contradicts its source. Every issue below is a missing qualifier or loose wording. This is the **initial audit**; the corrections you approved are listed in the next section.

## Corrections applied after approval (M1-M6, L1, L4)
Rerunning `audit_claims.py` after the corrections gives **55 verified, 0 partially verified, 0 needs clarification, 0 unsupported**. The seven rows that changed now include a text check on the slide or README wording. Analysis outputs and statistical values are unchanged.

| Item | What changed |
|---|---|
| M1 | Page 9 README: import share "peaks in low-production years (2014, 2017) and in 2022" |
| M2 | Page 9 README: Pearson r on detrended paddy production vs FAO rice imports; -0.46 has n = 13 and single detrending; the all-years Spearman -0.59 is stated |
| M3 | Page 9 slide caption and README: "Descriptive co-movement only; no pass-through estimate" |
| M4 | Page 9 slide and README: the paddy-to-rice factor 0.67 is shown as an **assumption**. **Correction to this audit:** the project already documents it as an assumption (`research_audit/02_variable_catalogue.md` line 22, `feasibility_tests.py:30`). The initial audit's statement that no source appears anywhere was wrong; the gap was only that the slide and README did not say so. No external source for 0.67 has been found, and none is claimed. |
| M5 | Page 3 slide footnote and README: the heat map uses a z-score anomaly, the strip the mm/100 forecasting anomaly |
| M6 | `build_figures.py` now reads the stored v2 `evidence` column; the independent rule is removed. Page 6 renders identically |
| L1 | Page 4 slide and README: "worsened pilot RMSE for all seven vegetables" |
| L4 | `references/research_references.md`: accents restored, DOIs added, obsolete caveat replaced by an accurate verification note |

Not applied (low priority, optional): L2 (quote the stored bootstrap p values on page 7), L3 ("point estimates" wording on page 7). L5 needed no change.

## Issues by severity (initial audit)

### Medium — fix before publication
| # | Where | Issue | Proposed correction |
|---|---|---|---|
| M1 | Page 9 README, Explanation: "import share spikes in crisis years" (register 42) | The three peaks are 2017 (29.6%), 2022 (25.6%) and 2014 (20.1%). Only 2022 is a crisis year; 2014 and 2017 are low-production years (rice-equivalent production 2,265 and 1,597 kt). | "Import share peaks in low-production years (2014, 2017) and in 2022." |
| M2 | Page 9 README, Evidence: "r = -0.79 (n = 15), -0.46 without 2017 and 2022" (40, 41) | Both numbers reproduce, but they are Pearson r between detrended paddy production and FAO rice imports (2010-2024), the second with 2017 and 2022 dropped after detrending on all 15 years (n = 13). The same source line also prints an all-years Spearman of -0.59. The README states none of this. | Add: "Pearson r, detrended paddy production vs FAO rice imports, same year; second figure n = 13." |
| M3 | Page 9 slide and README, exchange-rate panel (46) | No pass-through claim is made. But the text says only "Provisional: needs CPI/NCPI deflator". It never says the panel is descriptive. | Add "Descriptive co-movement only; no pass-through estimate" to the panel caption and the README Limitations. |
| M4 | Page 9 README, "conversion assumed" (43) | `rice_annual_balance.csv` uses a constant rice/paddy factor of 0.67. No source for the factor appears anywhere in the project. | Cite the source for 0.67 (DCS or FAO documentation), or state it as an assumption with the value. |
| M5 | Page 3 slide (31) | The anomaly strip is the v2 past-only mm/100 anomaly. The heat-map correlations come from `prices_out.txt` section D, which uses a z-score anomaly and de-seasonalised price changes. The slide does not say they differ. | Footnote: "Correlations use a z-score rain anomaly; the strip shows the mm/100 forecasting predictor." |
| M6 | Page 6 slide: evidence colours and labels (8) | `build_figures.py evidence()` re-derives the label from Holm p alone (0.05 and 0.15 cut-offs) rather than reading the stored v2 `evidence` column. Results agree for all seven vegetables today, but the rule is not the v2 rule (no bootstrap condition). | Read `evidence` from `forecast_model_comparison_v2.csv` and map it to the slide labels. |

### Low — wording and housekeeping
| # | Where | Issue | Proposed correction |
|---|---|---|---|
| L1 | Page 4 slide bullet: "FX excluded: it worsened every pilot forecast" | Verified for all seven vegetables' pilot RMSE (-1.8% to -16.7%). It is not true of every individual forecast. | "FX excluded: it worsened pilot RMSE for all seven vegetables." |
| L2 | Page 7 README: tomato Dambulla-box "bootstrap p about 0.10" | The validation report says "about 0.10". The stored values are in `rain_window_comparison.csv` (register 20: block-length values 0.097, 0.098, 0.074, so "about 0.10" is the upper end). | Quote the stored maximum rather than "about". |
| L3 | Page 7 subtitle: "stay clear of zero" | True for every point estimate (top three > 0, beans <= 0 in all eight variants). Only the national primary has formal tests behind it. | Say "point estimates" or footnote that only the primary is tested. |
| L4 | `references/research_references.md` | Diacritics are missing (Künsch, Muñoz-Sabater). The "should be verified" caveat is now out of date. | Restore diacritics, add DOIs, remove the caveat. |
| L5 | Page 5 and others: "exploratory because the window was seen in the pilot" | Verified by replaying the pilot logic: pilot origins run Jul 2021 to Sep 2026 (63 tests) against v2's Aug 2021 to Sep 2026 (62). The window is almost identical. | None. |

## Citations (all six verified against publisher or repository records)
| Reference | Verified details | Note |
|---|---|---|
| Clark & West (2007), J. Econometrics 138(1) 291-311 | RePEc, EconBiz | None |
| Diebold & Mariano (1995), JBES 13(3) 253-263 | RePEc; DOI 10.1080/07350015.1995.10524599 | An NBER working-paper version lists pages 253-265; use the journal pages |
| Newey & West (1987), Econometrica 55(3) 703-708 | Econometric Society page; DOI 10.2307/1913610 | None |
| Holm (1979), Scand. J. Statist. 6(2) 65-70 | DOI 10.2307/4615733 | None |
| Künsch (1989), Ann. Statist. 17(3) 1217-1241 | Project Euclid; DOI 10.1214/aos/1176347265 | None |
| Muñoz-Sabater et al. (2021), ESSD 13(9) 4349-4383 | ESSD page; DOI 10.5194/essd-13-4349-2021 | None |

Bibliographic details come from search-result records for each paper, not from reading the full text. Check page ranges against the published PDF if a reference list is formally submitted.

## What was verified directly against source (highlights)
- Page 6: all seven RMSE gains and Holm CW p-values match `forecast_model_comparison_v2.csv`.
- Pages 5 and 8: n = 62 and the origins Aug 2021 to Sep 2026 match `evaluation_samples.csv`. The sample is identical with or without the secondary specs. Constants (minimum 10 valid daily prices, Newey-West lag 3, B = 4000, blocks 3/6/12, 80% interval, evidence rule) match `forecast_backtest_v2.py`.
- Page 4: corr(A0, A3) = 0.57 and -0.05 match `predictor_overlap.csv`.
- Page 7: no evidence-class change between windows. Brinjal moves 12.4 to 10.4 and carrot 8.2 to 9.6. Tomato Dambulla-box prior has Holm p = 0.036. Geography spread is under 4 percentage points.
- Page 8: MAPE 23.1 to 39.7. Coverage 0.73 to 0.84.
- Page 3: the heat-map values equal the `prices_out.txt` section D table. "10 of 28" is present in the source.
- Page 2: only 2009-12 and 2026-11 are incomplete. Box cells are 36 and national 541. The ERA5 bug (monthly totals 12.4 to 21.4 times too large) and its correction are documented in `07_data_quality_report.md`.
- Page 9: Yala r = +0.68 (n = 16) reproduces. Comtrade has no 2018 row and 2025 is partial. USD/LKR rose by about 80% from Dec 2021 to Dec 2022 (about 363 in Dec 2022).

## Limits of this audit
- `feasibility_prices.py`, `feasibility_tests.py`, `era5_validate.py` and the v2/validation scripts were not re-run. The pilot was re-run. Their saved outputs were read.
- The audit checks that slide and README numbers match source outputs. It does not re-judge the statistical methodology.
- Source datasets were checked for the claims above, not for completeness against the original publishers.

## Constraints respected
`forecast_pilot.py`, `forecast_backtest_v2.py`, validation outputs and raw data are unchanged. Nothing was pushed. The ten-page structure is unchanged.
