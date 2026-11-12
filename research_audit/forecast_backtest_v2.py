"""S1+ forecasting backtest v2 -- does rainfall improve 1-month-ahead vegetable price forecasts?

Run:  uv run --with matplotlib python research_audit/forecast_backtest_v2.py
Read-only on raw/ and existing derived/ files.  New files written:
  derived/era5_regional_monthly.csv (cache), forecast_results_v2.csv, forecast_model_comparison_v2.csv,
  forecast_intervals_v2.csv, forecast_backtest_report_v2.md, forecast_charts_v2/*.png

FROZEN DESIGN (set before running v2; pilot results were already seen -> exploratory)
  Timing   origin month t (end of t): known = monthly mean prices up to t, rain up to and including t.
           target = monthly mean log price of t+1.  Rain of t+1 is never used.
  Price    y_t = ln(monthly mean of valid daily CBSL prices); a month needs >= MIN_OBS daily prices.
  AR       lag set chosen by AIC on the training window only from {y_t | y_t,y_t-1 | y_t,y_t-11 | y_t,y_t-1,y_t-11}.
  AR+rain  the SAME lag set + rain terms A0 (anomaly of month t) and A3 (mean anomaly of months t-2..t).
  Anomaly  primary: mm/100 vs mean of the same calendar month over ERA5 years STRICTLY BEFORE year(t) (past-only, 2010+).
           sensitivity: fixed 2010-2015 mm climatology; expanding z-score.
  Rain geo primary: national land mean.  secondary: Dambulla box, Nuwara Eliya box (hand-drawn +-0.3 deg, no polygons).
  Eval     expanding window, refit every origin; test origins 2021-08 .. last; warm-up origins (>=24 train rows) only feed
           the empirical error history used for prediction intervals.
  Tests    Clark-West (nested, one-sided, Newey-West lag 3), DM (NW lag 3), moving-block bootstrap of the loss
           differential (blocks 3/6/12); Holm across the 7 commodities for the PRIMARY spec only.
"""
import glob, math, os, sys, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "research_audit"); os.chdir(ROOT)
os.makedirs(f"{OUT}/forecast_charts_v2", exist_ok=True)

VEGS = ["Cabbage", "Brinjal", "Carrot", "Tomato", "Snake gourd", "Pumpkin", "Beans"]
MARKETS = ["dambulla", "pettah"]          # dambulla = primary, pettah = robustness (same weather, correlated prices; NOT independent)
MIN_OBS, TEST_START, WARM_ROWS, MIN_ERR_HIST = 10, pd.Timestamp("2021-08-01"), 24, 12
LAGSETS = {"y0": ["y0"], "y0,y1": ["y0", "y1"], "y0,y11": ["y0", "y11"], "y0,y1,y11": ["y0", "y1", "y11"]}
NW_LAG, B_BOOT, BLOCKS, PI = 3, 4000, (3, 6, 12), (0.10, 0.90)   # 80 % interval
rng = np.random.default_rng(20261112)

# ---------------------------------------------------------------- regional ERA5 (cached; raw .nc untouched)
BOXES = {"dam": (7.86, 80.65, 0.3), "nuw": (6.97, 80.77, 0.3)}   # lat, lon, half-width (deg)
def build_regional():
    f = f"{OUT}/derived/era5_regional_monthly.csv"
    if os.path.exists(f):
        return pd.read_csv(f, parse_dates=["month"]).set_index("month")
    import xarray as xr
    parts = {k: [] for k in ["nat", "dam", "nuw"]}; ncell = {}
    for fn in sorted(glob.glob("raw/EAR5/downloads/*.nc")):
        ds = xr.open_dataset(fn); land = ds.t2m.isel(valid_time=0).notnull()
        tp = ds.tp.where(land) * 1000; tp = tp.sel(valid_time=tp.valid_time.dt.hour == 0)
        w = np.cos(np.deg2rad(ds.latitude))
        for k in parts:
            if k == "nat": m = land
            else:
                la, lo, h = BOXES[k]
                m = land & (abs(ds.latitude - la) <= h + 1e-9) & (abs(ds.longitude - lo) <= h + 1e-9)
            ncell[k] = int(m.sum())
            x = tp.where(m); ww = w.broadcast_like(x).where(m.broadcast_like(x), 0)
            parts[k].append(x.weighted(ww).mean(["latitude", "longitude"], skipna=True).to_series())
    res = {}
    for k, v in parts.items():
        s = pd.concat(v).sort_index(); s = s[~s.index.duplicated(keep="last")]
        s.index = s.index.normalize() - pd.Timedelta(days=1)          # 00 UTC (D+1) accumulation = total of day D
        res["rain_" + k] = s.resample("MS").sum(min_count=1); res["n_" + k] = s.resample("MS").count()
    m = pd.DataFrame(res); m.index.name = "month"
    m["days_in_month"] = m.index.days_in_month
    for k in parts: m["cells_" + k] = ncell[k]
    m.to_csv(f); return m

# ---------------------------------------------------------------- data
reg = build_regional()
reg = reg[(reg.n_nat == reg.days_in_month)]                               # complete months only (drops partial 2026-11)
nat_chk = pd.read_csv(f"{OUT}/derived/era5_monthly.csv", parse_dates=["month"]).set_index("month").rain_mm
assert np.allclose(reg.rain_nat, nat_chk.reindex(reg.index), rtol=1e-3), "national series disagrees with era5_validate output"
RAIN = {"nat": reg.rain_nat, "dam": reg.rain_dam, "nuw": reg.rain_nuw}

def anomaly(rain, kind):
    """past-only anomaly per month. expanding: same-calendar-month years strictly before; fixed: 2010-2015."""
    out = pd.Series(np.nan, index=rain.index)
    for t in rain.index:
        same = rain[(rain.index.month == t.month)]
        if kind.startswith("exp"):
            ref = same[same.index.year < t.year]; need = 4 if kind.endswith("z") else 3
        else:
            ref = same[(same.index.year >= 2010) & (same.index.year <= 2015)]; need = 4
        if len(ref) < need: continue
        out[t] = (rain[t] - ref.mean()) / (ref.std(ddof=1) if kind.endswith("z") else 100.0)   # mm/100 or z
    return out
SPECS = {   # model name -> (geo, anomaly kind, group)
    "AR+rain:nat": ("nat", "exp_mm", "primary"),
    "AR+rain:dam": ("dam", "exp_mm", "secondary (geography)"),
    "AR+rain:nuw": ("nuw", "exp_mm", "secondary (geography)"),
    "AR+rain:nat_fixedclim": ("nat", "fix_mm", "sensitivity (climatology)"),
    "AR+rain:nat_z": ("nat", "exp_z", "sensitivity (z-score)"),
}
ANOM = {}
for name, (geo, kind, _) in SPECS.items():
    a = anomaly(RAIN[geo], kind)
    ANOM[name] = pd.DataFrame({"A0": a, "A3": a.rolling(3).mean()})

cb = pd.read_csv("raw/cbsl-daily-prices.csv", comment="#", parse_dates=["period"]).set_index("period")
def monthly_price(veg, market, agg):
    col = f"{veg} (wholesale, {market}) (Rs/kg)"
    s = cb[col].dropna(); s = s[s > 0]
    g = s.resample("MS"); p = getattr(g, agg)(); n = g.count()
    p[n < MIN_OBS] = np.nan
    return np.log(p.reindex(pd.date_range(p.index.min(), p.index.max(), freq="MS"))), n

# ---------------------------------------------------------------- model fitting
def ols_pred(X, y, xn, lam=1e-6):
    A = np.c_[np.ones(len(X)), X]; b = np.linalg.solve(A.T @ A + lam * np.eye(A.shape[1]), A.T @ y)
    return float(np.r_[1, xn] @ b), A, b
def aic(X, y):
    _, A, b = ols_pred(X, y, np.zeros(X.shape[1])); r = y - A @ b
    return len(y) * math.log(max(float(r @ r) / len(y), 1e-12)) + 2 * A.shape[1]

def run_series(y):
    """Expanding-window one-step backtest for one price series. Returns long DataFrame of forecasts."""
    d = pd.DataFrame({"y0": y, "y1": y.shift(1), "y11": y.shift(11), "target": y.shift(-1)})
    models = list(SPECS)
    for m in models:
        d[m + "|A0"] = ANOM[m].A0.reindex(d.index); d[m + "|A3"] = ANOM[m].A3.reindex(d.index)
    base = ["y0", "y1", "y11", "target"] + [c for m in models for c in (m + "|A0", m + "|A3")]
    usable = d.dropna(subset=base)
    recs, errhist = [], {k: [] for k in ["AR"] + models}
    idx = list(usable.index)
    for t in idx:
        tr = usable[usable.index < t]                                   # rows whose target month <= t  (known at origin t)
        tr = tr[tr.index + pd.DateOffset(months=1) <= t]
        if len(tr) < WARM_ROWS: continue
        te = usable.loc[t]
        best = min(LAGSETS, key=lambda k: aic(tr[LAGSETS[k]].values, tr.target.values))
        L = LAGSETS[best]; preds = {"naive": te.y0, "snaive": te.y11}
        preds["AR"] = ols_pred(tr[L].values, tr.target.values, te[L].values)[0]
        for m in models:
            c = L + [m + "|A0", m + "|A3"]
            preds[m] = ols_pred(tr[c].values, tr.target.values, te[c].values)[0]
        for mname, p in preds.items():
            lo = hi = np.nan
            if mname in errhist and len(errhist[mname]) >= MIN_ERR_HIST:
                q = np.quantile(errhist[mname], PI); lo, hi = p + q[0], p + q[1]   # empirical past out-of-sample errors only
            recs.append(dict(origin=t, target_month=t + pd.DateOffset(months=1), model=mname, actual_log=te.target, pred_log=p,
                             lo80_log=lo, hi80_log=hi, lagset=best, test=t >= TEST_START))
            if mname in errhist: errhist[mname].append(te.target - p)
    return pd.DataFrame(recs)

# ---------------------------------------------------------------- statistics
def nw_t(x, lag=NW_LAG):
    x = np.asarray(x, float); n = len(x); u = x - x.mean(); v = u @ u / n
    for k in range(1, lag + 1): v += 2 * (1 - k / (lag + 1)) * (u[k:] @ u[:-k]) / n
    return x.mean() / math.sqrt(max(v, 1e-18) / n)
def p_one(t): return 0.5 * math.erfc(t / math.sqrt(2))                       # P(Z >= t)
def p_two(t): return math.erfc(abs(t) / math.sqrt(2))
def boot_p(d, b):
    d = np.asarray(d, float); n = len(d); obs = d.mean(); c = d - obs; starts = n
    k = int(math.ceil(n / b)); idx = (rng.integers(0, n, size=(B_BOOT, k))[:, :, None] + np.arange(b)) % n
    m = c[idx.reshape(B_BOOT, -1)[:, :n]].mean(1)
    return float((m >= obs).mean())                                           # one-sided: H1 = rain model has lower loss
def holm(p):
    p = np.asarray(p, float); o = np.argsort(p); adj = np.empty_like(p); run = 0
    for r, i in enumerate(o):
        run = max(run, (len(p) - r) * p[i]); adj[i] = min(1, run)
    return adj
def bh(p):
    p = np.asarray(p, float); n = len(p); o = np.argsort(p)[::-1]; adj = np.empty(n); run = 1
    for r, i in enumerate(o):
        run = min(run, p[i] * n / (n - r)); adj[i] = run
    return adj

def metrics(g):
    a, p = g.actual_log.values, g.pred_log.values; A, P = np.exp(a), np.exp(p); e = a - p
    return dict(n=len(g), rmse_log=math.sqrt(np.mean(e ** 2)), mae_log=np.mean(np.abs(e)), mae_lkr=np.mean(np.abs(A - P)),
                rmse_lkr=math.sqrt(np.mean((A - P) ** 2)), mape_pct=100 * np.mean(np.abs(A - P) / A))

# ---------------------------------------------------------------- main
all_fc, cov_rows, cmp_rows = [], [], []
for market in MARKETS:
    for agg in ["mean", "median"]:
        for veg in VEGS:
            y, n = monthly_price(veg, market, agg)
            fc = run_series(y)
            fc.insert(0, "commodity", veg); fc.insert(0, "price_agg", agg); fc.insert(0, "market", market)
            all_fc.append(fc)
fc = pd.concat(all_fc, ignore_index=True)
fc["actual_lkr"] = np.exp(fc.actual_log); fc["pred_lkr"] = np.exp(fc.pred_log)
fc["lo80_lkr"] = np.exp(fc.lo80_log); fc["hi80_lkr"] = np.exp(fc.hi80_log)
fc["err_log"] = fc.actual_log - fc.pred_log
te = fc[fc.test]
te.drop(columns=["test"]).to_csv(f"{OUT}/forecast_results_v2.csv", index=False)

for (market, agg, veg), g in te.groupby(["market", "price_agg", "commodity"]):
    piv = g.pivot(index="origin", columns="model", values="pred_log"); act = g.drop_duplicates("origin").set_index("origin").actual_log
    ok = piv.dropna().index; piv, act = piv.loc[ok], act.loc[ok]
    e = {m: (act - piv[m]).values for m in piv.columns}
    ar_rmse = math.sqrt(np.mean(e["AR"] ** 2))
    for m in piv.columns:
        gm = g[(g.model == m) & g.origin.isin(ok)]
        row = dict(market=market, price_agg=agg, commodity=veg, model=m, group=("baseline" if m in ("naive", "snaive", "AR") else SPECS[m][2]),
                   **metrics(gm))
        row["rmse_gain_vs_AR_pct"] = 100 * (1 - row["rmse_log"] / ar_rmse) if m != "AR" else 0.0
        if m in SPECS:
            f = e["AR"] ** 2 - (e[m] ** 2 - (piv["AR"].values - piv[m].values) ** 2)      # Clark-West adjusted loss differential
            dl = e["AR"] ** 2 - e[m] ** 2
            row.update(cw_t=nw_t(f), cw_p_one=p_one(nw_t(f)), dm_t=nw_t(dl), dm_p_two=p_two(nw_t(dl)))
            for b in BLOCKS: row[f"boot_p_b{b}"] = boot_p(dl, b)
        row["lagsets_used"] = "; ".join(f"{k}:{v}" for k, v in gm.lagset.value_counts().items()) if m != "naive" and m != "snaive" else ""
        cmp_rows.append(row)
cmp = pd.DataFrame(cmp_rows)
for col in ["cw_p_one", "boot_p_b6"]:     # Holm / BH across the 7 commodities within (market, price_agg, model)
    cmp[col.replace("_p_one", "_p_holm").replace("boot_p_b6", "boot_b6_p_holm")] = np.nan
cmp["cw_p_bh"] = np.nan
for key, ix in cmp[cmp.model.isin(SPECS)].groupby(["market", "price_agg", "model"]).groups.items():
    cmp.loc[ix, "cw_p_holm"] = holm(cmp.loc[ix, "cw_p_one"].values)
    cmp.loc[ix, "boot_b6_p_holm"] = holm(cmp.loc[ix, "boot_p_b6"].values)
    cmp.loc[ix, "cw_p_bh"] = bh(cmp.loc[ix, "cw_p_one"].values)
def classify(r):
    if r.model not in SPECS: return ""
    if r.rmse_gain_vs_AR_pct <= 0: return "worse or no gain"
    boots = [r[f"boot_p_b{b}"] for b in BLOCKS]
    if r.cw_p_holm < 0.05 and max(boots) < 0.10: return "supported (corrected)"
    if r.cw_p_one < 0.05 or max(boots) < 0.05: return "suggestive (uncorrected only)"
    return "no reliable evidence"
cmp["evidence"] = cmp.apply(classify, axis=1)
cmp.to_csv(f"{OUT}/forecast_model_comparison_v2.csv", index=False, float_format="%.5g")

# intervals: coverage of the 80 % empirical-error interval on the test period
iv = te[te.model.isin(["AR"] + list(SPECS))].dropna(subset=["lo80_log"]).copy()
iv["covered"] = (iv.actual_log >= iv.lo80_log) & (iv.actual_log <= iv.hi80_log)
iv["width_lkr"] = iv.hi80_lkr - iv.lo80_lkr; iv["width_log"] = iv.hi80_log - iv.lo80_log
ivs = iv.groupby(["market", "price_agg", "commodity", "model"]).agg(n=("covered", "size"), nominal=("covered", lambda s: 0.8),
        coverage=("covered", "mean"), mean_width_log=("width_log", "mean"), mean_width_lkr=("width_lkr", "mean")).reset_index()
ivs.to_csv(f"{OUT}/forecast_intervals_v2.csv", index=False, float_format="%.4g")

# ---------------------------------------------------------------- charts
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
for veg in VEGS:
    g = te[(te.market == "dambulla") & (te.price_agg == "mean") & (te.commodity == veg)]
    fig, ax = plt.subplots(figsize=(9, 3.6)); a = g[g.model == "AR"].set_index("target_month"); r = g[g.model == "AR+rain:nat"].set_index("target_month")
    ax.plot(a.index, a.actual_lkr, "k-", lw=1.6, label="actual")
    ax.plot(a.index, a.pred_lkr, color="#888", lw=1.2, label="AR (price only)")
    ax.plot(r.index, r.pred_lkr, color="#1b7f5c", lw=1.4, label="AR + national rain")
    ax.fill_between(r.index, r.lo80_lkr, r.hi80_lkr, color="#1b7f5c", alpha=.15, label="80% interval (AR+rain)")
    ax.set_title(f"{veg} - Dambulla wholesale, 1-month-ahead forecasts (LKR/kg)", fontsize=10); ax.legend(fontsize=7, ncol=4, loc="upper left")
    ax.spines[["top", "right"]].set_visible(False); fig.tight_layout(); fig.savefig(f"{OUT}/forecast_charts_v2/{veg.replace(' ', '_').lower()}.png", dpi=130); plt.close(fig)
sel = [("dambulla", "AR+rain:nat", "Dambulla, national rain (primary)", "#1b7f5c"), ("dambulla", "AR+rain:dam", "Dambulla, Dambulla-box rain", "#7aa6c2"),
       ("dambulla", "AR+rain:nuw", "Dambulla, Nuwara Eliya-box rain", "#c2a37a"), ("pettah", "AR+rain:nat", "Pettah, national rain (robustness)", "#a05a8a")]
fig, ax = plt.subplots(figsize=(9, 4.2)); w = 0.2
for j, (mk, mo, lab, col) in enumerate(sel):
    s = cmp[(cmp.market == mk) & (cmp.price_agg == "mean") & (cmp.model == mo)].set_index("commodity").reindex(VEGS)
    xs = np.arange(len(VEGS)) + (j - 1.5) * w; ax.bar(xs, s.rmse_gain_vs_AR_pct, w, color=col, label=lab)
    if mo == "AR+rain:nat" and mk == "dambulla":
        for x, (v, h) in zip(xs, zip(s.rmse_gain_vs_AR_pct, s.cw_p_holm)):
            if h < 0.05: ax.text(x, v + .3, "*", ha="center", fontsize=12)
ax.axhline(0, color="k", lw=.8); ax.set_xticks(range(len(VEGS))); ax.set_xticklabels(VEGS, fontsize=8)
ax.set_ylabel("RMSE reduction vs price-only AR (%)"); ax.legend(fontsize=7); ax.spines[["top", "right"]].set_visible(False)
ax.set_title("Does rainfall improve 1-month-ahead forecasts?  (* = Holm-corrected Clark-West p<0.05)", fontsize=9)
fig.tight_layout(); fig.savefig(f"{OUT}/forecast_charts_v2/summary_rmse_gain.png", dpi=130); plt.close(fig)

# ---------------------------------------------------------------- report
def md(df, fmt=None):
    cols = list(df.columns); s = "| " + " | ".join(cols) + " |\n|" + "---|" * len(cols) + "\n"
    for _, r in df.iterrows():
        s += "| " + " | ".join((f"{r[c]:.3g}" if isinstance(r[c], (float, np.floating)) else str(r[c])) for c in cols) + " |\n"
    return s
def tab(market, model, agg="mean"):
    s = cmp[(cmp.market == market) & (cmp.price_agg == agg) & (cmp.model == model)].set_index("commodity").reindex(VEGS).reset_index()
    return s[["commodity", "n", "rmse_gain_vs_AR_pct", "cw_t", "cw_p_one", "cw_p_holm", "cw_p_bh", "boot_p_b3", "boot_p_b6", "boot_p_b12", "dm_p_two", "evidence"]]
def base_tab(market):
    s = cmp[(cmp.market == market) & (cmp.price_agg == "mean") & cmp.model.isin(["naive", "snaive", "AR", "AR+rain:nat"])]
    s = s.assign(model=s.model.str.replace("AR+rain:nat", "AR+rain (nat)", regex=False))
    return s[["commodity", "model", "rmse_log", "mae_log", "mae_lkr", "rmse_lkr", "mape_pct"]]
def sec_tab(market="dambulla"):
    s = cmp[(cmp.market == market) & (cmp.price_agg == "mean") & cmp.model.isin(list(SPECS))].pivot(index="commodity", columns="model", values="rmse_gain_vs_AR_pct").reindex(VEGS).reset_index()
    return s
med = cmp[(cmp.market == "dambulla") & (cmp.price_agg == "median") & (cmp.model == "AR+rain:nat")].set_index("commodity").reindex(VEGS).reset_index()[["commodity", "rmse_gain_vs_AR_pct", "cw_p_one", "cw_p_holm"]]
def sub_gain(g, mask):
    out = {}
    for veg in VEGS:
        x = g[(g.commodity == veg) & mask(g)]
        a = x[x.model == "AR"].set_index("origin"); r = x[x.model == "AR+rain:nat"].set_index("origin")
        out[veg] = 100 * (1 - math.sqrt(np.mean(r.err_log ** 2)) / math.sqrt(np.mean(a.err_log.loc[r.index] ** 2)))
    return out
gd = te[(te.market == "dambulla") & (te.price_agg == "mean")]
mid = gd.target_month.sort_values().unique()[len(gd.target_month.unique()) // 2]
sub = pd.DataFrame({"all": sub_gain(gd, lambda g: g.target_month == g.target_month),
                    "excl_2022_targets": sub_gain(gd, lambda g: g.target_month.dt.year != 2022),
                    "first_half": sub_gain(gd, lambda g: g.target_month < mid),
                    "second_half": sub_gain(gd, lambda g: g.target_month >= mid)}).reindex(VEGS).reset_index().rename(columns={"index": "commodity"})
ivp = ivs[(ivs.market == "dambulla") & (ivs.price_agg == "mean") & ivs.model.isin(["AR", "AR+rain:nat"])].pivot(index="commodity", columns="model", values=["coverage", "mean_width_lkr"])
ivp.columns = [f"{a}_{b}" for a, b in ivp.columns]; ivp = ivp.reindex(VEGS).reset_index()
nt = cmp[(cmp.market == "dambulla") & (cmp.model == "AR") & (cmp.price_agg == "mean")].n.tolist()
INTERP = """## 8. Interpretation (written after inspecting the results)
**Descriptive history (separate from forecasting).** Earlier lagged correlations (03 audit) already pointed to cabbage, carrot and brinjal. They are associations with national rain and say nothing about forecast skill.

**Out-of-sample forecast performance.** Over 62 one-month-ahead forecasts per vegetable, adding past rain to the price-only AR lowered log RMSE by about 20 % (cabbage), 12 % (brinjal), 8 % (carrot), 5 % (tomato) and 2 % (snake gourd, pumpkin); beans were 1.5 % worse. In LKR/kg the cabbage MAE fell from about 52 to 42 and brinjal from about 62 to 53. Naive was hard to beat for beans and pumpkin. Seasonal naive was the worst baseline everywhere because prices trended up strongly (2022).

**Statistical significance (primary spec only, Holm over 7).** Cabbage (Holm p = 0.002), brinjal (0.001) and carrot (0.029) pass the Clark-West test after correction, and their block-bootstrap p-values are below 0.05 at blocks 3/6/12. Tomato is uncorrected-only (CW p = 0.027, Holm 0.11, bootstrap about 0.15). Snake gourd, pumpkin and beans show no reliable evidence. Treat the corrected result as **supported for cabbage and brinjal, weaker for carrot** (Holm 0.029 sits close to the line and its DM p is 0.033), **exploratory for tomato**, and as a clear negative for the other three.

**Robustness.** The conclusion survives Dambulla-box and Nuwara Eliya-box rain (similar or larger gains, Nuwara Eliya best for cabbage), the monthly median, and the Pettah market (agreement, not independence). Gains for cabbage and carrot are essentially unchanged when 2022 targets are removed and positive in both halves of the test window. Brinjal's gain is concentrated in the second half (6 % vs 17 %); tomato's gain disappears in the second half. The fixed 2010-2015 climatology and the z-score version give smaller gains (cabbage 17 % and 16 %, carrot 5 % and 6 %), so the anomaly definition matters; the sign pattern across vegetables does not change.

**Predictive uncertainty.** The 80 % intervals under-cover for most series (empirical coverage 0.69-0.84, mostly 0.70-0.78), so they are too narrow, mainly because early error history is short and 2022 errors are large. Do not present them as calibrated; they are a first, honest approximation. Interval width in LKR/kg is large (cabbage about 125-140, carrot about 206), which matches the large point errors: even the best model misses by roughly 24-40 % (MAPE; about 24-27 % for cabbage, brinjal and carrot).

**What is sufficiently supported for the chapter.**
* Cabbage and brinjal: rain adds out-of-sample information at a 1-month horizon beyond past prices (supported after multiple-testing correction, robust to geography, aggregation and the 2022 episode for cabbage).
* Carrot: modest and borderline; report as supported with a caution.
* Tomato: exploratory. Snake gourd, pumpkin, beans: no evidence; report as negative results.
* Not supported: any causal claim, any claim for markets beyond Dambulla/Pettah, any claim at 2-3 month horizons, calibrated intervals.

**Caveats that remain.** These test months were seen in the pilot, so even the corrected p-values do not account for that earlier look; ~62 dependent forecasts limit power; boxes are proxies; the fitted AR+rain price lag set (AIC-chosen) differs from the pilot's fixed lags, which is why the gains are not identical to the pilot.
"""
rep = f"""# Forecast Backtest v2 - Weather-informed vegetable price forecasting (S1+)

*Generated by `research_audit/forecast_backtest_v2.py`. Pilot (`forecast_pilot.py`) is unchanged. Raw and existing derived files untouched; one new cache file `derived/era5_regional_monthly.csv`.*

**Status: refined EXPLORATORY backtest.** The pilot had already shown us these test months, and the commodity list and rain idea came from it, so nothing below is an independent confirmation.

## 1. Question and design (frozen before the run)
Does adding past rainfall to a price-only autoregression reduce one-month-ahead forecast error for seven Dambulla wholesale vegetables? Rain is the only extra information; FX is excluded.

| Item | Decision |
|---|---|
| Target | ln(monthly mean wholesale price, LKR/kg) of month t+1 |
| Information at origin t | monthly prices through t; ERA5 rain through the end of t. Rain of t+1 is never used |
| Price aggregation | mean of valid daily prices; a month needs >= {MIN_OBS} daily prices else it is missing (no filling). Monthly median is a sensitivity check |
| Baselines | naive (y_t); seasonal naive (y_t-11, the same calendar month as the target one year earlier); price-only AR |
| AR | lag set chosen by AIC on the training window from {{y_t}}, {{y_t,y_t-1}}, {{y_t,y_t-11}}, {{y_t,y_t-1,y_t-11}}; OLS, refit each origin |
| AR+rain | the same lag set + A0 (anomaly of month t) + A3 (mean anomaly of months t-2, t-1, t). Lag set is chosen on the price-only model so both have identical price terms |
| Anomaly (primary) | (rain_t - mean of the same calendar month over ERA5 years strictly before year(t)) / 100 mm; ERA5 starts 2010 so the first test year has 6+ reference years |
| Anomaly (sensitivity) | fixed 2010-2015 climatology (mm); expanding-climatology z-score |
| Rain geography | **primary: national** land mean (cos-lat weighted, {int(reg.cells_nat.iloc[0])} land cells). **Secondary:** Dambulla box ({int(reg.cells_dam.iloc[0])} cells) and Nuwara Eliya box ({int(reg.cells_nuw.iloc[0])} cells), +-0.3 deg around 7.86N 80.65E and 6.97N 80.77E. Hand-drawn, no district polygons; they are proxies, not the growers' rain |
| Evaluation | expanding window; test origins {TEST_START:%Y-%m} onward (n = {max(nt)} per commodity); earlier origins with >= {WARM_ROWS} training rows only build error history |
| Intervals | 80 % = forecast + 10th/90th percentile of the model's own past out-of-sample errors (>= {MIN_ERR_HIST} errors needed) |
| Tests | Clark-West (nested models, one-sided, Newey-West lag {NW_LAG}); DM (NW lag {NW_LAG}, two-sided, supplementary); moving-block bootstrap of the squared-error differential (blocks 3/6/12, {B_BOOT} draws); Holm (and BH, exploratory) across the 7 commodities, **primary specification only** |
| Evidence label | *supported (corrected)*: RMSE gain > 0, Holm CW p < 0.05 and all bootstrap p < 0.10. *suggestive*: uncorrected CW p < 0.05 or all-block bootstrap p < 0.05 but not the above. Otherwise *no reliable evidence* / *worse or no gain* |

Forecast prices in LKR are exp(forecast of log price) (median-type forecast, no retransformation bias correction). Log RMSE is **not** a percentage error; MAE/RMSE in LKR/kg and MAPE are given beside it.

## 2. Out-of-sample forecast performance (Dambulla wholesale, primary)
{md(base_tab("dambulla"))}
*Per-commodity forecast charts: `forecast_charts_v2/<commodity>.png`.*

## 3. Does rain help? (Dambulla, national rain = PRIMARY)
RMSE gain = reduction in log RMSE relative to the price-only AR on the same forecast dates.

{md(tab("dambulla", "AR+rain:nat"))}
![summary](forecast_charts_v2/summary_rmse_gain.png)

## 4. Secondary and sensitivity specifications (exploratory; no family-wise claim)
RMSE gain (%) vs price-only AR, Dambulla wholesale:

{md(sec_tab())}
Monthly **median** instead of mean (national rain):

{md(med)}
Corrected p-values for each secondary specification are in `forecast_model_comparison_v2.csv` (Holm within spec). Choosing the best of these specs per commodity would be a forking-paths search; the primary specification was fixed in advance.

## 4b. Is the gain driven by the 2022 crisis or one half of the sample?
RMSE gain (%) of AR+rain (national) over AR, Dambulla, on sub-samples of the same forecasts (not re-fitted):

{md(sub)}
## 5. Pettah robustness (same frozen model; NOT independent validation)
Pettah and Dambulla prices are strongly related and share the same weather, so agreement is consistency, not replication. Nothing was tuned on Pettah.

{md(tab("pettah", "AR+rain:nat"))}
## 6. Predictive uncertainty (Dambulla, 80 % intervals)
Nominal coverage 0.80. With ~{min(nt)}-{max(nt)} test points the coverage estimate itself has a standard error of about 0.05.

{md(ivp)}
## 7. Limitations
* ~{max(nt)} forecast months, serially dependent; Clark-West/bootstrap have limited power and the normal approximation is rough.
* Pilot leakage of *selection*: commodities and the rain idea came after seeing the pilot test window. Holm covers only the 7-test family, not the earlier search.
* National and box rainfall are proxies for growing-area weather. Dambulla supplies come from several regions; boxes are hand-drawn; ERA5-Land at 0.1 deg smooths hill rain.
* Weather enters only as past rainfall; transport, policy, import controls, the 2022 crisis and inflation are not modelled. Prices are nominal, so inflation trends sit inside the AR terms.
* Coefficients are associations, not causal effects. Rain may proxy for harvest timing or demand.
* Horizons beyond one month would need rainfall forecasts and are not tested.
* Monthly mean of daily prices with a {MIN_OBS}-day minimum; prices as published, units not independently verified.
* Interval coverage is estimated with few points and uses error history that is itself short.

{INTERP}"""
open(f"{OUT}/forecast_backtest_report_v2.md", "w").write(rep)
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
print(tab("dambulla", "AR+rain:nat").to_string(index=False)); print(); print(tab("pettah", "AR+rain:nat").to_string(index=False))
print(); print(sec_tab().to_string(index=False)); print(); print(med.to_string(index=False)); print(); print(sub.to_string(index=False)); print(); print(ivp.to_string(index=False))
print(); print(base_tab("dambulla").to_string(index=False))
