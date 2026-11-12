# Data sources

Everything the app reads is in `data/` (a self-contained snapshot). This table says what each file is and where it comes from.

| File in `data/` | What it is | Original source | Used on pages |
|---|---|---|---|
| `cbsl_daily_prices.csv` | Daily wholesale and retail vegetable prices (Rs/kg), including Dambulla and Pettah wholesale | Central Bank of Sri Lanka (CBSL) via Macro Lab (stated in the file header) | 1, 3, 5, 8 |
| `era5_regional_monthly.csv` | Monthly rainfall: national land mean and two regional boxes, with days observed per month | ERA5-Land reanalysis (Copernicus), processed with the corrected accumulation method (see `07_data_quality_report.md` in the full project) | 1, 3, 5 |
| `era5_monthly.csv` | Monthly national weather summary (used here for Yala-season rainfall) | ERA5-Land, same processing | 9 |
| `dcs_national_yala.csv` | National Yala-season paddy sown area, harvested area, yield and production | Department of Census and Statistics, Sri Lanka | 9 |
| `rice_annual_balance.csv` | Annual paddy production, rice-equivalent production, and rice imports and exports | Production from DCS; trade from FAOSTAT and UN Comtrade; rice-equivalent uses an assumed 0.67 milling factor (an assumption, not data) | 9 |
| `usd_lkr_spot_rate.csv` | Daily indicative USD/LKR spot exchange rate | Central Bank of Sri Lanka | 9 |
| `forecast_model_comparison_v2.csv` | Forecast accuracy and tests per vegetable, market and model (RMSE gain, Clark-West, bootstrap, Holm, evidence label) | Output of the project's `forecast_backtest_v2.py` (not included here) | 6, 7, 8 |
| `forecast_results_v2.csv` | Every individual forecast: origin, target month, actual, predicted, 80% band | Same | 5, 8 |
| `rain_window_comparison.csv` | Validation results for the non-overlapping rainfall window and the regional rainfall specifications | Output of the project's `validate_v2.py` (not included here) | 6, 7 |
| `interval_coverage.csv` | Coverage and width of the 80% bands | Same | 8 |
| `lag_correlations.csv` | Exploratory correlations of price changes with rainfall anomalies at lags 0 to 3 | Project exploratory audit (`research_audit/_profiles/prices_out.txt`, section D) | 3 |
| `sri_lanka_boundary.geojson` | Sri Lanka outline, used only to draw the map | Country-boundary file held in the full project (only the Sri Lanka feature is kept) | 2 |

## Notes
- Prices are nominal (not adjusted for inflation). No CPI deflator has been collected.
- The forecasting files are results, not raw data: the full analysis code lives in the parent research project.
- To refresh `data/` from the full project, run `uv run python scripts/sync_data.py` (only works when this folder sits inside it).
- Data-quality findings (ERA5 correction, CBSL gaps, trade-data gaps) are documented in `07_data_quality_report.md` in the full project.
