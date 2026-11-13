# Data sources

Everything the app reads is in `data/` (a self-contained snapshot). This table says what each file is and where it comes from.

| File in `data/` | What it is | Original source | Used on pages (4-page dashboard) |
|---|---|---|---|
| `cbsl_daily_prices.csv` | Daily wholesale and retail vegetable prices (Rs/kg), including Dambulla and Pettah wholesale | Central Bank of Sri Lanka (CBSL) via Macro Lab (stated in the file header) | 1, 2 |
| `era5_regional_monthly.csv` | Monthly rainfall: national land mean and two regional boxes, with days observed per month | ERA5-Land reanalysis (Copernicus), processed with the corrected accumulation method (see `07_data_quality_report.md` in the full project) | 1 |
| `era5_monthly.csv` | Monthly national weather summary (used here for Yala-season rainfall) | ERA5-Land, same processing | 3 |
| `dcs_national_yala.csv` | National Yala-season paddy sown area, harvested area, yield and production | Department of Census and Statistics, Sri Lanka | 3 |
| `rice_annual_balance.csv` | Annual paddy production, rice-equivalent production, and rice imports and exports | Production from DCS; trade from FAOSTAT and UN Comtrade; rice-equivalent uses an assumed 0.67 milling factor (an assumption, not data) | 3 |
| `usd_lkr_spot_rate.csv` | Daily indicative USD/LKR spot exchange rate | Central Bank of Sri Lanka | 3 |
| `forecast_model_comparison_v2.csv` | Forecast accuracy and tests per vegetable, market and model (RMSE gain, Clark-West, bootstrap, Holm, evidence label) | Output of the project's `forecast_backtest_v2.py` (not included here) | 2, 4 |
| `forecast_results_v2.csv` | Every individual forecast: origin, target month, actual, predicted, 80% band | Same | 2 |
| `rain_window_comparison.csv` | Validation results for the non-overlapping rainfall window and the regional rainfall specifications | Output of the project's `validate_v2.py` (not included here) | none (kept for the speaking guide and audit) |
| `interval_coverage.csv` | Coverage and width of the 80% bands | Same | none (page 2 computes coverage from the forecasts; kept for checking) |
| `lag_correlations.csv` | Exploratory correlations of price changes with rainfall anomalies at lags 0 to 3 | Project exploratory audit (`research_audit/_profiles/prices_out.txt`, section D) | none (kept from the earlier deck) |
| `era5_rain_grid.csv` | Monthly rainfall (mm) for each of the 541 ERA5-Land cells over Sri Lanka, complete months only | ERA5-Land raw hourly files in the full project, same corrected accumulation rule; built by `scripts/build_rain_grid.py`. Tested to reproduce the national and Dambulla-box series within 0.5 mm | 1 |
| `sri_lanka_boundary.geojson` | Sri Lanka outline, used only to draw the map | Country-boundary file held in the full project (only the Sri Lanka feature is kept) | 1 |

## Notes
- Prices are nominal (not adjusted for inflation). No CPI deflator has been collected.
- The forecasting files are results, not raw data: the full analysis code lives in the parent research project.
- To refresh `data/` from the full project, run `uv run python scripts/sync_data.py` (only works when this folder sits inside it).
- Data-quality findings (ERA5 correction, CBSL gaps, trade-data gaps) are documented in `07_data_quality_report.md` in the full project.
