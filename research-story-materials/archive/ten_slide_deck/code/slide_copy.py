"""Slide text, shared by the live Streamlit slides (slides.py) and the PNG export (build_figures.py).

One source for every headline, subtitle, source line and text block, so the two renderings cannot drift apart.
"\\n" inside a string is a manual line break used only by the PNG export; the live slides join the lines.
"""

ACTS = {**{i: "Act I · Understanding the problem" for i in (1, 2, 3)},
        **{i: "Act II · Testing the idea" for i in (4, 5, 6, 7, 8)},
        **{i: "Act III · The wider picture" for i in (9, 10)}}

# page -> (headline, source, subtitle)
HEAD = {
    1: ("Can rainfall help anticipate vegetable prices?",
        "CBSL daily wholesale prices (Dambulla); ERA5-Land corrected national rainfall",
        "Vegetable prices swing sharply. Does last month's rain tell us anything about next month's price?"),
    2: ("One market, seven vegetables, two data sources",
        "CBSL daily prices; ERA5-Land (corrected accumulation); research_audit/07_data_quality_report.md",
        "Daily prices and hourly rainfall become monthly variables with explicit missing-data rules."),
    3: ("Prices have their own dynamics — and some follow last month's rain",
        "CBSL Dambulla wholesale; ERA5-Land; lag correlations from research_audit/_profiles/prices_out.txt (section D)",
        "Descriptive only: 10 of 28 correlation tests were p<0.05 (about 1.4 expected by chance)."),
    4: ("The test: does rainfall improve a model that already knows past prices?",
        "forecast_backtest_v2.py; forecast_validation_v2/predictor_overlap.csv",
        "At the end of month t, two models forecast the price of month t+1."),
    5: ("How we judge it: 62 real forecasts, three layers of scrutiny",
        "forecast_validation_v2/evaluation_samples.csv; forecast_backtest_report_v2.md",
        "Technical detail lives in the README and report; the slide shows the logic."),
    6: ("Rainfall helps some vegetables far more than others",
        "forecast_model_comparison_v2.csv · Dambulla wholesale, national ERA5 rain, 62 forecasts each",
        "Bar = size of improvement. Colour and label = strength of evidence (Holm-adjusted Clark–West p)."),
    7: ("The ranking holds up under alternative specifications",
        "forecast_validation_v2/rain_window_comparison.csv; forecast_model_comparison_v2.csv",
        "Each dot is one specification's RMSE gain vs price-only AR. Cabbage, brinjal, carrot stay clear of zero; beans stay at or below it."),
    8: ("Better does not mean accurate: errors stay large, bands under-cover",
        "forecast_results_v2.csv; forecast_validation_v2/interval_coverage.csv",
        "Cabbage, Dambulla. Empirical 80% bands from past out-of-sample errors."),
    9: ("Beyond vegetables: three separate sources of food-system vulnerability",
        "ERA5-Land; DCS paddy; FAOSTAT; CBSL exchange rates. Context analyses; none feeds the forecasting model.",
        "Weather, import exposure and exchange rates are shown side by side — never combined into one score."),
    10: ("Rainfall helps some vegetable forecasts — not all, and not precisely",
         "Synthesis of pages 1–9",
         None),
}

# ---- page 2 ----
P02_ITEMS = [("Main market", "CBSL Dambulla wholesale (Pettah = robustness check)"),
             ("Vegetables", "cabbage · brinjal · carrot · tomato · snake gourd · pumpkin · beans"),
             ("Target", "log monthly mean price, one month ahead"),
             ("Price rule", "monthly mean needs ≥10 valid daily prices; nominal LKR/kg"),
             ("Rain rule", "hourly ERA5 → daily → monthly; incomplete months set to missing")]
P02_FLOW = ["CBSL daily prices", "ERA5-Land hourly rain", "monthly variables"]
P02_NOTE = "An earlier ERA5 precipitation bug (overstated totals) is fixed; only corrected series are used."
P02_MAPNOTE = "dashed boxes = rainfall proxies, not growing areas"

# ---- page 4 ----
P04_A = "Price-only AR\nlags of the log price\n(lag set chosen by AIC, training window only)"
P04_B = "AR + rainfall\nthe SAME price lags\n+ A0 (rain in month t)\n+ A3 (3-month rain window)"
P04_FORECAST = "Forecast of\nprice in t+1"
P04_COMPARE = "Compare\nout-of-sample\nerrors"
P04_WINDOW = "A0 = month t · A3 (primary) = mean of t−2…t, overlaps A0 (corr 0.57)\nA3 (check) = mean of t−3…t−1, no overlap (corr −0.05)\nBoth use only rain already observed at t."
P04_BULLETS = ["Expanding window, refit at every origin", "Naive and seasonal-naive benchmarks scored too",
               "FX excluded: it worsened pilot RMSE for all seven vegetables", "No machine learning, no future rainfall"]

# ---- page 5 ----
P05_CARDS = [("1  Score", "RMSE of the log price, AR+rain\nvs price-only AR, same dates.\nGain = % reduction.\n62 forecasts per vegetable."),
             ("2  Test", "Clark–West (nested models,\nNewey–West lag 3), one-sided.\nDiebold–Mariano as supplement.\nMoving-block bootstrap (3/6/12)."),
             ("3  Correct", "Holm correction across the seven\nvegetables. Evidence label needs\nHolm p < 0.05 and every\nbootstrap p < 0.10.")]
P05_TL1 = "Origins Aug 2021 → Sep 2026\nTargets Sep 2021 → Oct 2026\nAIC lag choice: training rows only"
P05_TL2 = "Test window was seen in the pilot →\nexploratory. Errors are serially dependent."

# ---- page 9 ----  (title, caption, caveat); caption of the first has {r} and {n}
P09 = [("Weather and paddy", "Yala rain vs harvested/sown, r = {r:+.2f}, n = {n}", "Short series, policy shocks: association only."),
       ("Rice imports", "Apparent import share of supply", "Not self-sufficiency. Paddy→rice factor\n0.67 is an assumption, not data."),
       ("Exchange rate", "USD/LKR monthly mean (2022 shaded)", "Descriptive co-movement only; no pass-through\nestimate (needs a CPI/NCPI deflator).")]

# ---- page 10 ----  (heading, items)
P10 = [("Findings", ["Adding observed rain improves one-month-ahead forecasts for cabbage, brinjal and carrot beyond past prices.",
                     "The benefit is commodity-specific: snake gourd, pumpkin, beans show little or none; tomato is exploratory.",
                     "Paddy, imports and exchange rates are distinct, context-setting dimensions of vulnerability."]),
       ("Limitations", ["The test window was seen in the pilot: exploratory, not independent confirmation.",
                        "Rain series are proxies, not growing-area rainfall; 62 forecast errors are dependent.",
                        "Context analyses: short series, crisis confounding, incomplete trade data, no deflator yet."]),
       ("Implications and next steps", ["A research finding on where rainfall adds information; not a deployable forecasting tool.",
                                        "Next: out-of-sample test on newly published months; growing-area rainfall; CPI/NCPI deflator.",
                                        "Longer horizons would need rainfall forecasts, a separate study."])]
