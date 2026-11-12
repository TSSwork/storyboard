# Data sources
| Use | Source | File / location | Notes |
|---|---|---|---|
| Vegetable prices | CBSL via Macro Lab | `raw/cbsl-daily-prices.csv` | Dambulla and Pettah wholesale; nominal; monthly mean needs >=10 valid days |
| Rainfall | ERA5-Land | `research_audit/derived/era5_*.csv` | Corrected accumulation; incomplete months missing |
| Paddy | Dept. of Census and Statistics | `research_audit/derived/dcs_national_*.csv` | Seasonal, 2010-2025 used |
| Rice production and trade | FAOSTAT; UN Comtrade; CBSL | `derived/rice_annual_balance.csv` | Comtrade gaps 2018, partial 2025 |
| Exchange rate | CBSL | `raw/pdf/Indicative Rate...csv` | USD/LKR |
| Weekly prices | HARTI bulletins | `raw/pdf/HARTI/` | Retail rice and imported items |
| Inflation | CBSL CPI/NCPI | not yet collected | Needed for page 16 |
Quality notes: `research_audit/07_data_quality_report.md`.
