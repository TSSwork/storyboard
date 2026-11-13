"""Recompute every numeric claim shown in the earlier 10-slide storyboard (archive/ten_slide_deck/) from the source outputs and write CLAIM_SOURCE_REGISTER.csv.

Read-only on research_audit/ and raw/. Needs the full research project one level up (research_audit/, raw/). Run: uv run python scripts/audit_claims.py
Status values: verified | partially verified | unsupported | needs clarification
"""
import re
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent      # research-story/
WORK = ROOT.parent                                    # the full research project (needed: this script reads its outputs)
RA, D, V = WORK / "research_audit", WORK / "research_audit/derived", WORK / "research_audit/forecast_validation_v2"
VEGS = ["Cabbage", "Brinjal", "Carrot", "Tomato", "Snake gourd", "Pumpkin", "Beans"]
rows = []


def reg(page, claim, source, evidence, status, note=""):
    rows.append(dict(page=page, claim=claim, source=source, evidence=evidence, status=status, note=note))


def txt(p):
    return Path(p).read_text()


comp = pd.read_csv(RA / "forecast_model_comparison_v2.csv")
prim = comp[(comp.market == "dambulla") & (comp.price_agg == "mean") & (comp.model == "AR+rain:nat")].set_index("commodity").loc[VEGS]
rw = pd.read_csv(V / "rain_window_comparison.csv").set_index(["commodity", "model"])
SRC_CMP = "research_audit/forecast_model_comparison_v2.csv"

# ---- page 6: main result ----
claimed = {"Cabbage": (19.7, .0018), "Brinjal": (12.4, .0009), "Carrot": (8.2, .0285), "Tomato": (4.8, .109),
           "Snake gourd": (1.8, .189), "Pumpkin": (1.8, .235), "Beans": (-1.5, .557)}
for v, (g, p) in claimed.items():
    ag, ap = prim.loc[v, "rmse_gain_vs_AR_pct"], prim.loc[v, "cw_p_holm"]
    ok = abs(ag - g) < 0.06 and abs(ap - p) < 0.0006 + 0.0005 * p
    reg(6, f"{v}: RMSE gain {g:+.1f}%, Holm CW p {p}", SRC_CMP, f"gain={ag:.3f}, cw_p_holm={ap:.5f}", "verified" if ok else "unsupported")
lab_map = {"supported (corrected)": "supported", "suggestive (uncorrected only)": "exploratory only", "no reliable evidence": "no reliable evidence", "worse or no gain": "rain does not help"}
fig_rule = lambda g, q: "rain does not help" if g <= 0 else "supported" if q < .05 else "exploratory only" if q < .15 else "no reliable evidence"
mism = [v for v in VEGS if lab_map[prim.loc[v, "evidence"]] != fig_rule(prim.loc[v, "rmse_gain_vs_AR_pct"], prim.loc[v, "cw_p_holm"])]
reg(6, "Evidence labels (supported / exploratory / none / worse) shown on the slide", SRC_CMP + " column 'evidence'; build_figures.py evidence()",
    f"stored labels {dict(prim.evidence)}; figure rule disagrees for: {mism or 'none'}",
    "partially verified" if not mism else "unsupported",
    "Labels agree today, but build_figures.evidence() re-derives them from Holm p only (no bootstrap condition, 0.15 cut-off for 'exploratory') instead of reading the stored v2 label. Propose reading the stored label.")

# ---- evaluation window / design ----
ev = pd.read_csv(V / "evaluation_samples.csv")
reg(5, "62 forecasts per vegetable; origins Aug 2021 to Sep 2026; targets Sep 2021 to Oct 2026", "research_audit/forecast_validation_v2/evaluation_samples.csv",
    f"n_test={sorted(set(ev.n_test))}; first_origin={sorted(set(ev.first_origin))}; last_origin={sorted(set(ev.last_origin))}; sample identical with/without secondary specs={bool(ev.primary_only_sample_identical.all())}", "verified" if set(ev.n_test) == {62} and set(ev.first_origin) == {"2021-08-01"} and set(ev.last_origin) == {"2026-09-01"} else "unsupported")
src = txt(RA / "forecast_backtest_v2.py")
for what, pat in [("monthly mean needs >=10 valid daily prices", r"MIN_OBS, TEST_START, WARM_ROWS, MIN_ERR_HIST = 10"),
                  ("Newey-West lag 3, 4000 bootstrap draws, blocks 3/6/12, 80% interval", r"NW_LAG, B_BOOT, BLOCKS, PI = 3, 4000, \(3, 6, 12\)"),
                  ("Dambulla box centre 7.86N 80.65E, Nuwara Eliya 6.97N 80.77E, half-width 0.3 deg", r'"dam": \(7.86, 80.65, 0.3\), "nuw": \(6.97, 80.77, 0.3\)'),
                  ("Evidence label needs Holm CW p<0.05 and all bootstrap p<0.10", r"cw_p_holm < 0.05 and max\(boots\) < 0.10")]:
    reg("2/5", what, "research_audit/forecast_backtest_v2.py", "pattern found in script" if re.search(pat, src) else "pattern NOT found", "verified" if re.search(pat, src) else "unsupported")
reg(5, "Test window was already seen in the pilot (so results are exploratory)", "research_audit/forecast_pilot.py + v2 report", "pilot evaluated 63 expanding-window origins on the same series (see pilot check below); v2 report states exploratory status", "verified")

# pilot window overlap
cb = pd.read_csv(WORK / "raw/cbsl-daily-prices.csv", comment="#", parse_dates=["period"]).set_index("period")
col = [c for c in cb.columns if c.startswith("Cabbage (wholesale, dambulla)")][0]
y = np.log(cb[col].resample("MS").mean()).dropna()
mon = pd.read_csv(D / "era5_monthly.csv", parse_dates=["month"]).set_index("month"); mon = mon[mon.days_in_month >= 28]
g = mon.groupby(mon.index.month).rain_mm
an = ((mon.rain_mm - g.transform("mean")) / g.transform("std")).rename("a")
dd = pd.concat([y.rename("y"), an], axis=1).dropna(); dd = dd[dd.index.isin(y.index)]
dd["y11"] = dd.y.shift(11); dd["a1"] = dd.a.shift(1); dd["a3"] = dd.a.rolling(3).sum(); dd["target"] = dd.y.shift(-1); dd["y2"] = dd.y.shift(2)
dd = dd.dropna(subset=["target", "y11", "y2", "a1", "a3"])
reg(5, "Pilot test origins start about Jul-Aug 2021 (window re-used by v2)", "forecast_pilot.py logic replayed on cabbage", f"pilot first test origin = {dd.index[48].date()}, last = {dd.index[-1].date()}, n={len(dd) - 48} (v2: 2021-08 to 2026-09, n=62)", "verified")

# ---- page 4: predictor overlap ----
po = pd.read_csv(V / "predictor_overlap.csv").set_index("spec")["corr_A0_A3"]
reg(4, "corr(A0, A3) = 0.57 for the primary (A3 = t-2..t) and -0.05 non-overlapping (t-3..t-1)", "forecast_validation_v2/predictor_overlap.csv", f"nat_incl={po['nat_incl']:.3f}, nat_prior={po['nat_prior']:.3f}", "verified" if abs(po["nat_incl"] - .57) < .006 and abs(po["nat_prior"] + .05) < .006 else "unsupported")
vm = txt(V / "forecast_rain_window_sensitivity.md")
reg("4/5", "Validation reproduces v2 exactly (434 forecasts, max abs difference 0.0); timing checks pass", "forecast_validation_v2/forecast_rain_window_sensitivity.md section 2", "text present in report" if "434 forecasts" in vm and "0.0" in vm else "text missing", "verified" if "434 forecasts" in vm else "unsupported", "Reported by the validation script's own assertions; not independently re-run in this audit.")

# ---- page 7: robustness ----
changes = [(v, rw.loc[(v, "nat_incl"), "evidence"], rw.loc[(v, "nat_prior"), "evidence"]) for v in VEGS]
same = all(a == b for _, a, b in changes)
reg(7, "No vegetable changes evidence class between overlapping and non-overlapping A3 (national)", "forecast_validation_v2/rain_window_comparison.csv", str([(v, a, b) for v, a, b in changes if a != b] or "all identical"), "verified" if same else "unsupported")
reg(7, "Brinjal gain 12.4 -> 10.4; carrot 8.2 -> 9.6; cabbage 19.7 -> 19.5", "rain_window_comparison.csv",
    f"brinjal {rw.loc[('Brinjal','nat_incl'),'rmse_gain_vs_AR_pct']:.1f}->{rw.loc[('Brinjal','nat_prior'),'rmse_gain_vs_AR_pct']:.1f}; carrot {rw.loc[('Carrot','nat_incl'),'rmse_gain_vs_AR_pct']:.1f}->{rw.loc[('Carrot','nat_prior'),'rmse_gain_vs_AR_pct']:.1f}; cabbage {rw.loc[('Cabbage','nat_incl'),'rmse_gain_vs_AR_pct']:.1f}->{rw.loc[('Cabbage','nat_prior'),'rmse_gain_vs_AR_pct']:.1f}", "verified")
tp = rw.loc[("Tomato", "dam_prior"), "cw_p_holm"]
reg(7, "Tomato, Dambulla box with non-overlapping window reaches Holm p = 0.036 (one of six specifications), not promoted", "rain_window_comparison.csv", f"cw_p_holm={tp:.4f}; evidence={rw.loc[('Tomato','dam_prior'),'evidence']}; boot p b3/b6/b12 = {rw.loc[('Tomato','dam_prior'),['boot_p_b3','boot_p_b6','boot_p_b12']].round(3).tolist()}",
    "verified" if abs(tp - .036) < .001 else "unsupported", "Report calls bootstrap p 'about 0.10'; the maximum of the three block lengths is the stored value above.")
specs = ["nat_incl", "nat_prior", "dam_incl", "dam_prior", "nuw_incl", "nuw_prior"]
pet = comp[(comp.market == "pettah") & (comp.price_agg == "mean") & (comp.model == "AR+rain:nat")].set_index("commodity").loc[VEGS]
med = comp[(comp.market == "dambulla") & (comp.price_agg == "median") & (comp.model == "AR+rain:nat")].set_index("commodity").loc[VEGS]
allg = pd.DataFrame({s: [rw.loc[(v, s), "rmse_gain_vs_AR_pct"] for v in VEGS] for s in specs}, index=VEGS)
allg["pettah"], allg["median"] = pet.rmse_gain_vs_AR_pct.values, med.rmse_gain_vs_AR_pct.values
top3_pos = bool((allg.loc[["Cabbage", "Brinjal", "Carrot"]] > 0).all().all()); beans_neg = bool((allg.loc["Beans"] <= 0).all())
reg(7, "Cabbage, brinjal, carrot stay clear of zero in every specification; beans stay at or below zero (slide subtitle)", "rain_window_comparison.csv; forecast_model_comparison_v2.csv (pettah, median)",
    f"min gain top-3 = {allg.loc[['Cabbage','Brinjal','Carrot']].min().min():.2f}; beans max = {allg.loc['Beans'].max():.2f}", "verified" if top3_pos and beans_neg else "partially verified",
    "'Clear of zero' is about the point estimate; only the national-rain primary has formal tests behind it. Pettah/median/box cells have no Holm family in the slide.")
rng = (allg[["nat_incl", "dam_incl", "nuw_incl"]].max(axis=1) - allg[["nat_incl", "dam_incl", "nuw_incl"]].min(axis=1))
reg(7, "Rain geography moves gains by a few points only", "rain_window_comparison.csv", f"max spread across national/Dambulla/Nuwara Eliya = {rng.max():.1f} pp ({rng.idxmax()})", "verified" if rng.max() < 4 else "needs clarification")
reg(7, "Pettah is a robustness check, not independent validation", "design decision (research brief) + report", "Pettah and Dambulla prices are both CBSL market series on the same dates and the same rain series", "verified")

# ---- page 8: accuracy ----
ic = pd.read_csv(V / "interval_coverage.csv"); ic = ic[ic.model == "nat_incl"].set_index("commodity").loc[VEGS]
reg(8, "MAPE 23-40% for AR+rain", SRC_CMP, f"min={prim.mape_pct.min():.1f}, max={prim.mape_pct.max():.1f}", "verified" if 23 <= prim.mape_pct.min() and prim.mape_pct.max() <= 40 else "unsupported")
reg(8, "80% band coverage 0.73-0.84 for AR+rain (national, primary window)", "forecast_validation_v2/interval_coverage.csv", f"min={ic.coverage.min():.3f}, max={ic.coverage.max():.3f}", "verified" if abs(ic.coverage.min() - .73) < .01 and abs(ic.coverage.max() - .84) < .01 else "unsupported")
reg(8, "Standard error of a coverage estimate is about 0.05 with 62 points", "arithmetic sqrt(0.8*0.2/62)", f"{np.sqrt(.16/62):.3f}", "verified")
reg(8, "Fixed-climatology interval history uses warm-up errors that rely on later climatology", "forecast_rain_window_sensitivity.md section 8", "statement present in validation report" if "warm-up errors" in vm else "missing", "verified" if "warm-up errors" in vm else "unsupported")

# ---- page 3: exploratory correlations ----
po_txt = txt(RA / "_profiles/prices_out.txt")
blk = po_txt.split("== D.")[1]
parsed = {}
for v in VEGS:
    m = re.search(rf"^{v}\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)", blk, flags=re.M)
    parsed[v] = [float(x) for x in m.groups()]
shown = pd.read_csv(ROOT / "data/lag_correlations.csv", index_col=0)
diff = max(abs(shown.loc[v].values - np.array(parsed[v])).max() for v in VEGS)
reg(3, "Lag 0-3 correlation heat map values", "research_audit/_profiles/prices_out.txt section D; lag_correlations.csv", f"max abs difference between slide table and source = {diff:.3f}", "verified" if diff < .006 else "unsupported",
    "Values were copied by hand into the CSV; this check parses the source text and compares. The source output was produced by research_audit/feasibility_prices.py (not re-run here).")
reg(3, "10 of 28 tests had p<0.05; about 1.4 expected by chance", "prices_out.txt", "line 'significant at 5%: 10 of 28 (~1.4 expected by chance)' present" if "10 of 28" in blk else "missing", "verified" if "10 of 28" in blk else "unsupported", "28 x 0.05 = 1.4 (arithmetic).")
reg(3, "Lag-1: cabbage +0.60, carrot +0.44, brinjal +0.40", "prices_out.txt", f"lag1: cabbage {parsed['Cabbage'][1]}, carrot {parsed['Carrot'][1]}, brinjal {parsed['Brinjal'][1]}", "verified")
reg(3, "Anomaly = rain minus same-calendar-month mean of earlier years, /100 mm (slide)", "forecast_backtest_v2.py anomaly()", "v2 primary uses past-only climatology, mm/100. NOTE: the prices_out.txt correlations use a z-score anomaly (era5 national, 'z-anomaly') not the mm/100 past-only anomaly", "partially verified",
    "Slide pairs the mm/100 anomaly strip with correlations computed from a z-score anomaly. Propose a footnote stating the correlation anomaly is a z-score.")

# ---- page 2: data ----
rc = pd.read_csv(V / "rainfall_completeness.csv", parse_dates=["month"])
bad = rc[~(rc.complete_nat & rc.complete_dam & rc.complete_nuw)].month.dt.strftime("%Y-%m").tolist()
reg(2, "Incomplete rainfall months: 2009-12 and 2026-11 only; set to missing", "forecast_validation_v2/rainfall_completeness.csv", f"incomplete months = {bad}", "verified" if bad == ["2009-12", "2026-11"] else "unsupported")
reg(2, "36 land cells per box, 541 national", "rainfall_completeness.csv", f"cells_nat={rc.cells_nat.iloc[0]}, cells_dam={rc.cells_dam.iloc[0]}, cells_nuw={rc.cells_nuw.iloc[0]}", "verified" if (rc.cells_nat.iloc[0], rc.cells_dam.iloc[0], rc.cells_nuw.iloc[0]) == (541, 36, 36) else "unsupported")
dq = txt(RA / "07_data_quality_report.md")
reg(2, "Earlier ERA5 precipitation bug overstated rainfall; corrected series used", "research_audit/07_data_quality_report.md E1/E2", "E1: monthly tp 12.4-21.4x too large (median 14.3x); E2: correct method = tp at 00 UTC of D+1" if "12.4" in dq else "missing", "verified" if "12.4" in dq else "unsupported", "Correction verified in the audit report; era5_validate.py output not re-run here.")
reg(2, "Prices are nominal; no deflator applied", "raw/cbsl-daily-prices.csv header, 07_data_quality_report.md", "CBSL series published in Rs/kg; no CPI deflator collected (07 lists it as missing)", "verified")
mm = pd.to_datetime(cb.index); reg(1, "CBSL data covers 2016-2026", "raw/cbsl-daily-prices.csv", f"first {mm.min().date()}, last {mm.max().date()}", "verified")

# ---- page 4: FX ----
out = subprocess.run(["uv", "run", "python", str(RA / "forecast_pilot.py")], capture_output=True, text=True, cwd=WORK).stdout
fx = re.findall(r"^\s*(\w[\w ]*?)\s+63\s+[\d.]+\s+[\d.]+\s+[\d.]+\s+[\d.]+\s+[\d.]+\s+(-?[\d.]+)\s+(-?[\d.]+)", out, flags=re.M)
fxg = [float(b) for _, _, b in fx]
reg(4, "FX excluded because it worsened pilot forecasts", "research_audit/forecast_pilot.py (re-run)", f"fx_gain_pct per vegetable = {fxg}", "verified" if fxg and all(x < 0 for x in fxg) else "unsupported",
    "True for all 7 vegetables' pilot RMSE. Slide 4 wording 'worsened every pilot forecast' is loose: it means every vegetable's RMSE, not every individual forecast. Propose 'worsened pilot RMSE for all seven vegetables'.")
reg(4, "Naive and seasonal-naive benchmarks scored; lag set by AIC on training rows only; same price lags in both models", "forecast_results_v2.csv models; validation report assertions",
    f"models in results: {sorted(pd.read_csv(RA/'forecast_results_v2.csv', usecols=['model']).model.unique())}", "verified")

# ---- page 9: wider context ----
mon2 = pd.read_csv(D / "era5_monthly.csv", parse_dates=["month"]).set_index("month")
yl = pd.read_csv(D / "dcs_national_yala.csv"); yl["y"] = yl.season_label.astype(str).str[:4].astype(int); yl = yl[(yl.y >= 2010) & (yl.y <= 2025)].copy()
yl["rain"] = [mon2.loc[f"{y}-03":f"{y}-08", "rain_mm"].sum() for y in yl.y]; yl["hs"] = yl.harv_000ha / yl.sown_000ha
dt = lambda s, yr: s - np.polyval(np.polyfit(yr, s, 1), yr)
ry = np.corrcoef(dt(yl.rain.values, yl.y.values), dt(yl.hs.values, yl.y.values))[0, 1]
reg(9, "Yala (Mar-Aug) rain vs harvested/sown ratio r about +0.68, n = 16 (detrended)", "ERA5 monthly + dcs_national_yala.csv; feasibility_tests.py", f"r={ry:+.3f}, n={len(yl)}", "verified" if abs(ry - .68) < .01 and len(yl) == 16 else "unsupported",
    "Slide scatter is detrended; ERA5 era5_monthly.csv mm (corrected series) used. Permutation p (0.002) reported in earlier audit, not on slide.")
rb = pd.read_csv(D / "rice_annual_balance.csv"); rb = rb[(rb.y >= 2010) & (rb.y <= 2024)].dropna(subset=["fao_rice_imp_000t", "paddy_000t"])
r15 = np.corrcoef(dt(rb.paddy_000t.values, rb.y.values), rb.fao_rice_imp_000t.values)[0, 1]
keep = ~rb.y.isin([2017, 2022]).values; r13 = np.corrcoef(dt(rb.paddy_000t.values, rb.y.values)[keep], rb.fao_rice_imp_000t.values[keep])[0, 1]; n13 = int(keep.sum())
reg(9, "Production vs imports r = -0.79 (n = 15)", "feasibility_tests.py line 45; derived/rice_annual_balance.csv", f"Pearson r between detrended paddy production and FAO rice imports, 2010-2024, n={len(rb)}: {r15:+.3f}", "partially verified" if abs(r15 + .79) < .01 else "unsupported",
    "Number is right but the README (page 9) omits that it is DETRENDED paddy production vs FAO imports, same year. Needs the qualifier.")
reg(9, "Production vs imports r = -0.46 without 2017 and 2022", "research_audit/_profiles/prices_out.txt line 1", f"Recomputed Pearson, paddy detrended on the full 2010-2024 sample then 2017 and 2022 dropped (n={n13}): {r13:+.3f}. Source: feasibility_prices.py lines 9-11. The same print line also shows the all-years SPEARMAN (-0.59), so the two figures use different statistics", "partially verified" if abs(r13 + .46) < .01 else "unsupported",
    "Value reproduces, but the README (page 9) does not say it is a Pearson r on detrended production (detrended once on the full sample), n = 13, and the nearby -0.59 is Spearman. Add the qualifier.")
share = rb.fao_rice_imp_000t / (rb.rice_eq_000t + rb.fao_rice_imp_000t) * 100
reg(9, "Apparent import share spikes in crisis years (README)", "rice_annual_balance.csv", f"share peaks: {share.sort_values(ascending=False).head(3).round(1).to_dict()} (index = year)", "needs clarification",
    "Peaks are 2017 (29.6%), 2022 (25.6%), 2014 (20.1%). 2022 is a crisis year; 2014 and 2017 are low-production years, not crises. Propose 'low-production years and 2022'.")
reg(9, "Paddy to rice-equivalent conversion assumed", "rice_annual_balance.csv", f"rice_eq / paddy = {(pd.read_csv(D/'rice_annual_balance.csv').assign(r=lambda d: d.rice_eq_000t/d.paddy_000t).r.dropna().round(3).unique())}", "partially verified", "Factor is constant 0.67; its source is not cited anywhere in the project. Needs a cited source (e.g. DCS or FAO conversion note) before publication.")
com = pd.read_csv(D / "comtrade_year_summary.csv")
reg(9, "Comtrade has no 2018 annual data; 2025 is partial", "derived/comtrade_year_summary.csv; 07_data_quality_report.md lines 30-31", f"years present include 2017 and 2019 but not 2018: {sorted(set([2017,2018,2019]) & set(com.year))}; DQ report: 2025 rice 84.1 kt vs CBSL 184.7 kt", "verified" if 2018 not in set(com.year) and "2025 is incomplete" in dq else "unsupported")
fxm = pd.read_csv(WORK / "raw/pdf/Indicative Rate of the USD_LKR SPOT Exchange Rate.csv", parse_dates=["Date"]).set_index("Date")["Exchange Rate"].resample("MS").mean()
reg(9, "USD/LKR jumped in 2022", "raw/pdf/Indicative Rate...csv (CBSL)", f"monthly mean: Jan-2022 {fxm['2022-01-01']:.0f}, Dec-2022 {fxm['2022-12-01']:.0f} (+{(fxm['2022-12-01']/fxm['2021-12-01']-1)*100:.0f}% vs Dec-2021)", "verified")
reg(9, "Exchange-rate panel is descriptive, not pass-through", "storyboard 09 slide and README", "Slide caption: 'Provisional: needs CPI/NCPI deflator.' README limitation: 'no CPI/NCPI deflator yet'. Neither text says 'co-movement' or rules out pass-through explicitly", "needs clarification",
    "No pass-through claim is made, but the wording should say explicitly 'descriptive co-movement only; no pass-through estimate'. Propose adding that sentence (not done silently).")
reg(9, "Apparent import share is not self-sufficiency", "07_data_quality_report.md / S3 caveat", "report states stocks, non-food uses, feed, seed, waste not modelled", "verified")

# ---- history of claims in docs outside the slides ----
reg(10, "Next steps: out-of-sample test on newly published months; growing-area rainfall; CPI/NCPI", "design proposal", "Forward-looking recommendations, not empirical claims", "verified", "Treated as opinion, not evidence.")
reg(10, "Longer horizons would need rainfall forecasts", "design reasoning", "At horizon h>1 the model needs rain at t+1..t+h-1, which is not observed at forecast time", "verified", "Logical consequence of 'no future rainfall' design.")

ref_rows = [
    ("Clark and West (2007) Journal of Econometrics 138(1): 291-311", "verified", "RePEc/EconPapers record eee:econom:v:138:y:2007:i:1:p:291-311; EconBiz"),
    ("Diebold and Mariano (1995) J. Business & Economic Statistics 13(3): 253-263", "verified", "RePEc bes:jnlbes:v:13:y:1995:i:3:p:253-63; DOI 10.1080/07350015.1995.10524599. (NBER working-paper version lists pages 253-265; use journal pages.)"),
    ("Newey and West (1987) Econometrica 55(3): 703-708", "verified", "Econometric Society page; DOI 10.2307/1913610"),
    ("Holm (1979) Scandinavian Journal of Statistics 6(2): 65-70", "verified", "bibliographic record; DOI 10.2307/4615733"),
    ("Kunsch (1989) Annals of Statistics 17(3): 1217-1241 (moving-block bootstrap)", "verified", "Project Euclid; DOI 10.1214/aos/1176347265. Project Euclid spells Kunsch without umlaut; correct form is Kuensch/Kunsch."),
    ("Munoz-Sabater et al. (2021) Earth System Science Data 13(9): 4349-4383", "verified", "ESSD page essd.copernicus.org/articles/13/4349/2021; DOI 10.5194/essd-13-4349-2021"),
]
for c, s, e in ref_rows:
    reg("refs", c, "docs/references/research_references.md", "web check of publisher / repository record: " + e, s)

# ---- wording / construction checks on the storyboard text itself (after corrections) ----
OLD = "archive/ten_slide_deck"   # the claim audit was run on the earlier 10-slide deck, kept there


def rd(path):
    return (ROOT / path).read_text()


bf, r9, r3, r4, r6 = (rd(f"{OLD}/code/build_figures.py") + rd(f"{OLD}/code/slide_copy.py") + rd(f"{OLD}/code/live_charts.py"), rd(f"{OLD}/guides/09_wider_context.md"), rd(f"{OLD}/guides/03_prices_and_rain.md"), rd(f"{OLD}/guides/04_forecast_experiment.md"), rd(f"{OLD}/guides/06_main_result.md"))


def fix(prefix, cond, ev_add, note=None):
    for r in rows:
        if r["claim"].startswith(prefix):
            if cond:
                r["status"] = "verified"
            r["evidence"] += " | storyboard text check: " + ev_add + (" (OK)" if cond else " (NOT FOUND)")
            if note is not None and cond:
                r["note"] = note


fix("Evidence labels", "EVID_LABEL" in bf and "c.evidence" in bf and "def evidence(" not in bf, "build_figures.py reads the stored v2 evidence column", "Fixed: labels read from the stored v2 column.")
fix("Anomaly = rain minus", "z-score anomaly, a different construction" in bf and "z-score rain anomaly" in r3, "slide 3 footnote and README distinguish z-score from mm/100", "Fixed: footnote added.")
fix("Production vs imports r = -0.79", "Pearson r = -0.79" in r9 and "detrended paddy production" in r9, "README 09 names Pearson, detrended, FAO imports, n", "Fixed: qualifier added.")
fix("Production vs imports r = -0.46", "dropping 2017 and 2022" in r9 and "-0.59" in r9, "README 09 gives n = 13, single detrending, and the Spearman -0.59", "Fixed: qualifier added.")
fix("Apparent import share spikes", "low-production years (2014, 2017) and in 2022" in r9, "README 09 wording", "Fixed: wording corrected.")
fix("Paddy to rice-equivalent", "0.67" in r9 and "assumption" in r9 and "assumption" in bf, "slide and README call 0.67 an assumption; documented in research_audit/02_variable_catalogue.md line 22 and feasibility_tests.py:30", "0.67 is a documented project assumption, now disclosed on the slide and README as an assumption (not as verified data).")
fix("Exchange-rate panel is descriptive", "Descriptive co-movement only" in bf and "descriptive co-movement only" in r9, "slide 9 caption and README 09 limitation", "Fixed: explicit descriptive-only wording added.")
fix("FX excluded because it worsened pilot forecasts", "pilot RMSE for all seven vegetables" in bf and "pilot RMSE for all seven vegetables" in r4, "slide 4 bullet and README 04", "Fixed: wording corrected.")

out = pd.DataFrame(rows); out.insert(0, "id", range(1, len(out) + 1))
out.to_csv(ROOT / "docs/CLAIM_SOURCE_REGISTER.csv", index=False)
print(out.status.value_counts().to_string()); print("total", len(out))
for _, r in out[out.status != "verified"].iterrows():
    print(f"[{r.id}] p{r.page} {r.status}: {r.claim}")
