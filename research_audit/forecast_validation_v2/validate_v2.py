"""Validation + rain-window sensitivity for forecast_backtest_v2.py  (EXPLORATORY: the test window was already seen).
Run from anywhere:  uv run --with matplotlib python research_audit/forecast_validation_v2/validate_v2.py
Self-contained re-implementation of the v2 pipeline (v2 script/outputs are NOT imported, modified or overwritten).
It first REPRODUCES the v2 primary results as a check, then adds the non-overlapping rain window and runtime timing assertions.

Specs (all Dambulla wholesale, monthly mean, 7 vegetables, same expanding window / origins / AIC lag selection):
  *_incl  : A0 = anomaly(t),  A3 = mean anomaly(t-2,t-1,t)    <- v2 PRIMARY definition (overlaps A0), kept unchanged
  *_prior : A0 = anomaly(t),  A3p = mean anomaly(t-3,t-2,t-1) <- non-overlapping sensitivity
  (mean vs sum of three months differs only by a factor 3 in the coefficient; OLS predictions are identical.)
  geographies: nat (national), dam (Dambulla box), nuw (Nuwara Eliya box); regional specs use COMPLETE months only.
Changes vs v2 (stated): bootstrap p = (count+1)/(B+1); same seed/blocks; ridge on intercept kept to reproduce v2 (effect measured below).
"""
import math, os, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", "..")); RA = f"{ROOT}/research_audit"
os.chdir(ROOT)
VEGS = ["Cabbage", "Brinjal", "Carrot", "Tomato", "Snake gourd", "Pumpkin", "Beans"]
MIN_OBS, TEST_START, WARM_ROWS, MIN_ERR_HIST = 10, pd.Timestamp("2021-08-01"), 24, 12
LAGSETS = {"y0": ["y0"], "y0,y1": ["y0", "y1"], "y0,y11": ["y0", "y11"], "y0,y1,y11": ["y0", "y1", "y11"]}
NW_LAG, B_BOOT, BLOCKS, PI = 3, 4000, (3, 6, 12), (0.10, 0.90)
rng = np.random.default_rng(20261112)

# ------------------------------------------------ rainfall completeness (national / Dambulla box / Nuwara Eliya box)
reg = pd.read_csv(f"{RA}/derived/era5_regional_monthly.csv", parse_dates=["month"]).set_index("month")
comp = pd.DataFrame({"days_in_month": reg.days_in_month})
for g in ["nat", "dam", "nuw"]:
    comp[f"days_obs_{g}"] = reg[f"n_{g}"]; comp[f"complete_{g}"] = reg[f"n_{g}"] == reg.days_in_month
    comp[f"cells_{g}"] = reg[f"cells_{g}"]
comp.index.name = "month"; comp.to_csv(f"{HERE}/rainfall_completeness.csv")
print("months in cache:", len(comp), "| incomplete months per geography:", {g: int((~comp[f'complete_{g}']).sum()) for g in ['nat', 'dam', 'nuw']},
      "| last month:", comp.index.max().date(), "days", int(comp.days_obs_nat.iloc[-1]))
RAIN = {g: reg[f"rain_{g}"].where(comp[f"complete_{g}"]) for g in ["nat", "dam", "nuw"]}   # incomplete months -> NaN, never partial totals

def anomaly(rain):
    """past-only: same calendar month, years strictly before year(t), >= 3 prior years; unit = mm/100"""
    out = pd.Series(np.nan, index=rain.index)
    for t in rain.index:
        if np.isnan(rain[t]): continue
        ref = rain[(rain.index.month == t.month) & (rain.index.year < t.year)].dropna()
        if len(ref) >= 3: out[t] = (rain[t] - ref.mean()) / 100.0
    return out
SPECS = {}
for geo in ["nat", "dam", "nuw"]:
    a = anomaly(RAIN[geo])
    SPECS[f"{geo}_incl"] = dict(geo=geo, kind="incl", a=a, F=pd.DataFrame({"A0": a, "A3": a.rolling(3).mean()}))                 # months t-2..t
    SPECS[f"{geo}_prior"] = dict(geo=geo, kind="prior", a=a, F=pd.DataFrame({"A0": a, "A3": a.shift(1).rolling(3).mean()}))      # months t-3..t-1
PRIMARY = "nat_incl"

# ------------------------------------------------ prices
cb = pd.read_csv("raw/cbsl-daily-prices.csv", comment="#", parse_dates=["period"]).set_index("period")
def monthly_price(veg):
    s = cb[f"{veg} (wholesale, dambulla) (Rs/kg)"].dropna(); s = s[s > 0]
    g = s.resample("MS"); p = g.mean(); n = g.count(); p[n < MIN_OBS] = np.nan        # no filling
    return np.log(p.reindex(pd.date_range(p.index.min(), p.index.max(), freq="MS")))

def ols_pred(X, y, xn, lam=1e-6, pen_intercept=True):
    A = np.c_[np.ones(len(X)), X]; P = lam * np.eye(A.shape[1])
    if not pen_intercept: P[0, 0] = 0.0
    b = np.linalg.solve(A.T @ A + P, A.T @ y); return float(np.r_[1, xn] @ b), A, b
def aic(X, y):
    _, A, b = ols_pred(X, y, np.zeros(X.shape[1])); r = y - A @ b
    return len(y) * math.log(max(float(r @ r) / len(y), 1e-12)) + 2 * A.shape[1]
MON = pd.DateOffset(months=1)

def run_series(y, specs, require):
    """require: spec names whose features must be non-NaN for a row to be used (defines the common sample)."""
    d = pd.DataFrame({"y0": y, "y1": y.shift(1), "y11": y.shift(11), "target": y.shift(-1)})
    for m, sp in specs.items():
        d[m + "|A0"] = sp["F"].A0.reindex(d.index); d[m + "|A3"] = sp["F"].A3.reindex(d.index)
    need = ["y0", "y1", "y11", "target"] + [c for m in require for c in (m + "|A0", m + "|A3")]
    usable = d.dropna(subset=need)
    recs, hist = [], {k: [] for k in ["AR"] + list(specs)}
    for t in usable.index:
        tr = usable[usable.index + MON <= t]                         # rows whose target month is known at origin t
        if len(tr) < WARM_ROWS: continue
        assert tr.index.max() + MON <= t                             # training targets available at origin
        te = usable.loc[t]
        # ---- timing assertions: every input equals the value recomputed from data <= t only
        for lag, col in [(0, "y0"), (1, "y1"), (11, "y11")]: assert te[col] == y[t - pd.DateOffset(months=lag)]
        assert te.target == y[t + MON]
        best = min(LAGSETS, key=lambda k: aic(tr[LAGSETS[k]].values, tr.target.values))   # training window only
        L = LAGSETS[best]; preds = {"naive": te.y0, "snaive": te.y11}
        preds["AR"] = ols_pred(tr[L].values, tr.target.values, te[L].values)[0]
        for m in specs:
            c = L + [m + "|A0", m + "|A3"]; assert c[:len(L)] == L        # identical price terms in AR and AR+rain
            preds[m] = ols_pred(tr[c].values, tr.target.values, te[c].values)[0]
        if "pen" not in locals() or True:
            lam0 = ols_pred(tr[L + [PRIMARY + "|A0", PRIMARY + "|A3"]].values, tr.target.values, te[L + [PRIMARY + "|A0", PRIMARY + "|A3"]].values, lam=1e-6, pen_intercept=False)[0]
        for name, p in preds.items():
            lo = hi = np.nan
            if name in hist and len(hist[name]) >= MIN_ERR_HIST:
                assert all(s + MON <= t for s, _ in hist[name])      # error history only from already-realised targets
                q = np.quantile([e for _, e in hist[name]], PI); lo, hi = p + q[0], p + q[1]
            recs.append(dict(origin=t, model=name, actual=te.target, pred=p, lo80=lo, hi80=hi, lagset=best, test=t >= TEST_START,
                             pred_nopen=lam0 if name == PRIMARY else np.nan))
            if name in hist: hist[name].append((t, te.target - p))
    return pd.DataFrame(recs), len(d.dropna(subset=["y0"])), len(usable)

# ------------------------------------------------ rain features use only data <= t  (recompute from truncated rain)
def feature_timing_check():
    n_chk = 0
    for name, sp in SPECS.items():
        for t in sp["F"].index[sp["F"].index >= pd.Timestamp("2019-01-01")]:
            a_t = anomaly(RAIN[sp["geo"]][:t]); i = a_t.index
            A0 = a_t.get(t, np.nan)
            A3 = a_t.iloc[-3:].mean(skipna=False) if sp["kind"] == "incl" else a_t.iloc[-4:-1].mean(skipna=False)
            for got, exp in [(sp["F"].A0[t], A0), (sp["F"].A3[t], A3)]:
                assert (np.isnan(got) and np.isnan(exp)) or abs(got - exp) < 1e-12, (name, t)
            n_chk += 1
    return n_chk

# ------------------------------------------------ statistics (same as v2; bootstrap p now (count+1)/(B+1))
def nw_t(x, lag=NW_LAG):
    x = np.asarray(x, float); n = len(x); u = x - x.mean(); v = u @ u / n
    for k in range(1, lag + 1): v += 2 * (1 - k / (lag + 1)) * (u[k:] @ u[:-k]) / n
    return x.mean() / math.sqrt(max(v, 1e-18) / n)
p_one = lambda t: 0.5 * math.erfc(t / math.sqrt(2)); p_two = lambda t: math.erfc(abs(t) / math.sqrt(2))
def boot_p(d, b):
    d = np.asarray(d, float); n = len(d); obs = d.mean(); c = d - obs; k = int(math.ceil(n / b))
    idx = (rng.integers(0, n, size=(B_BOOT, k))[:, :, None] + np.arange(b)) % n
    m = c[idx.reshape(B_BOOT, -1)[:, :n]].mean(1)
    return float(((m >= obs).sum() + 1) / (B_BOOT + 1))
def holm(p):
    p = np.asarray(p, float); o = np.argsort(p); adj = np.empty_like(p); run = 0
    for r, i in enumerate(o): run = max(run, (len(p) - r) * p[i]); adj[i] = min(1, run)
    return adj

# ------------------------------------------------ run
print("feature timing check (rain features recomputed from truncated data):", feature_timing_check(), "feature-origins OK")
all_fc, samp = [], []
for veg in VEGS:
    y = monthly_price(veg)
    fc, n_y, n_use = run_series(y, SPECS, require=list(SPECS))              # common sample over all 6 specs (as in v2 logic)
    fc_p, _, n_use_p = run_series(y, {PRIMARY: SPECS[PRIMARY]}, require=[PRIMARY])      # primary-only sample, for comparison
    t1 = fc[fc.test]; t2 = fc_p[fc_p.test]
    same = (sorted(t1.origin.unique()) == sorted(t2.origin.unique()))
    samp.append(dict(commodity=veg, price_months=int(y.notna().sum()), missing_price_months_in_span=int(y.isna().sum()), rows_usable=n_use,
                     first_origin=t1.origin.min().date(), last_origin=t1.origin.max().date(), n_test=t1.origin.nunique(),
                     primary_only_sample_identical=same, n_test_primary_only=t2.origin.nunique()))
    fc.insert(0, "commodity", veg); all_fc.append(fc)
fc = pd.concat(all_fc, ignore_index=True); te = fc[fc.test].copy()
sampdf = pd.DataFrame(samp); sampdf.to_csv(f"{HERE}/evaluation_samples.csv", index=False)

# reproduction check against v2 outputs (v2 files read only)
v2 = pd.read_csv(f"{RA}/forecast_results_v2.csv", parse_dates=["origin"])
v2 = v2[(v2.market == "dambulla") & (v2.price_agg == "mean") & (v2.model == "AR+rain:nat")][["commodity", "origin", "pred_log"]]
m = te[te.model == PRIMARY].merge(v2, on=["commodity", "origin"])
repro = float(np.abs(m.pred - m.pred_log).max()); print("reproduction of v2 primary forecasts: n =", len(m), " max |diff| (log) =", repro)
assert len(m) == len(te[te.model == PRIMARY]) and repro < 1e-9, "validation pipeline does not reproduce v2 primary forecasts"
pen = float(np.abs(te[te.model == PRIMARY].pred - te[te.model == PRIMARY].pred_nopen).max()); print("max |pred diff| when intercept is NOT ridge-penalised:", pen)

rows = []
for veg, g in te.groupby("commodity"):
    piv = g.pivot(index="origin", columns="model", values="pred").dropna(); act = g.drop_duplicates("origin").set_index("origin").actual.loc[piv.index]
    e = {k: (act - piv[k]).values for k in piv.columns}; ar = math.sqrt(np.mean(e["AR"] ** 2))
    for k in piv.columns:
        A, P = np.exp(act.values), np.exp(piv[k].values)
        r = dict(commodity=veg, model=k, n=len(act), first_origin=piv.index.min().date(), last_origin=piv.index.max().date(),
                 rmse_log=math.sqrt(np.mean(e[k] ** 2)), mae_lkr=np.mean(np.abs(A - P)), mape_pct=100 * np.mean(np.abs(A - P) / A))
        r["rmse_gain_vs_AR_pct"] = 100 * (1 - r["rmse_log"] / ar)
        if k in SPECS:
            f = e["AR"] ** 2 - (e[k] ** 2 - (piv["AR"].values - piv[k].values) ** 2); dl = e["AR"] ** 2 - e[k] ** 2
            r.update(cw_t=nw_t(f), cw_p_one=p_one(nw_t(f)), dm_t=nw_t(dl), dm_p_two=p_two(nw_t(dl)))
            for b in BLOCKS: r[f"boot_p_b{b}"] = boot_p(dl, b)
        rows.append(r)
cmp = pd.DataFrame(rows); cmp["cw_p_holm"] = np.nan
for k in SPECS: ix = cmp.index[cmp.model == k]; cmp.loc[ix, "cw_p_holm"] = holm(cmp.loc[ix, "cw_p_one"].values)   # Holm over 7 commodities within each spec
def ev(r):
    if r.model not in SPECS: return ""
    if r.rmse_gain_vs_AR_pct <= 0: return "worse or no gain"
    bp = [r[f"boot_p_b{b}"] for b in BLOCKS]
    if r.cw_p_holm < 0.05 and max(bp) < 0.10: return "supported (corrected)"
    if r.cw_p_one < 0.05 or max(bp) < 0.05: return "suggestive (uncorrected only)"
    return "no reliable evidence"
cmp["evidence"] = cmp.apply(ev, axis=1)
prim = cmp[cmp.model == PRIMARY].set_index("commodity")
cmp["gain_change_vs_primary_pp"] = [r.rmse_gain_vs_AR_pct - prim.loc[r.commodity, "rmse_gain_vs_AR_pct"] if r.model in SPECS else np.nan for r in cmp.itertuples()]
cmp.to_csv(f"{HERE}/rain_window_comparison.csv", index=False, float_format="%.5g")

# intervals for primary vs prior (national)
iv = te[te.model.isin(["AR", PRIMARY, "nat_prior"])].dropna(subset=["lo80"]).copy(); iv["cov"] = (iv.actual >= iv.lo80) & (iv.actual <= iv.hi80)
iv["w"] = np.exp(iv.hi80) - np.exp(iv.lo80)
ivs = iv.groupby(["commodity", "model"]).agg(n=("cov", "size"), coverage=("cov", "mean"), mean_width_lkr=("w", "mean")).reset_index(); ivs.to_csv(f"{HERE}/interval_coverage.csv", index=False, float_format="%.4g")

# predictor overlap (A0 vs A3) over the test origins
ov = []
for k in ["nat_incl", "nat_prior"]:
    F = SPECS[k]["F"]; F = F[F.index >= TEST_START]; ov.append(dict(spec=k, corr_A0_A3=float(F.A0.corr(F.A3))))
ov = pd.DataFrame(ov); ov.to_csv(f"{HERE}/predictor_overlap.csv", index=False)

# chart
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(9, 3.9)); w = 0.38
for j, (k, lab, col) in enumerate([("nat_incl", "primary: A3 = mean(t-2..t)", "#1b7f5c"), ("nat_prior", "sensitivity: A3 = mean(t-3..t-1)", "#c27a3c")]):
    s = cmp[cmp.model == k].set_index("commodity").reindex(VEGS); xs = np.arange(7) + (j - .5) * w
    ax.bar(xs, s.rmse_gain_vs_AR_pct, w, color=col, label=lab)
    for x, v, h in zip(xs, s.rmse_gain_vs_AR_pct, s.cw_p_holm):
        if h < 0.05: ax.text(x, v + .3, "*", ha="center", fontsize=12)
ax.axhline(0, color="k", lw=.8); ax.set_xticks(range(7)); ax.set_xticklabels(VEGS, fontsize=8); ax.legend(fontsize=8)
ax.set_ylabel("RMSE reduction vs AR (%)"); ax.spines[["top", "right"]].set_visible(False)
ax.set_title("Rain-window sensitivity, Dambulla, national rain (* Holm CW p<0.05; exploratory)", fontsize=9)
fig.tight_layout(); fig.savefig(f"{HERE}/rain_window_comparison.png", dpi=130); plt.close(fig)

pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
cols = ["commodity", "model", "n", "rmse_gain_vs_AR_pct", "gain_change_vs_primary_pp", "mae_lkr", "mape_pct", "cw_p_one", "cw_p_holm", "boot_p_b3", "boot_p_b6", "boot_p_b12", "evidence"]
for k in SPECS: print(f"\n== {k}"); print(cmp[cmp.model == k][cols].round(4).to_string(index=False))
print("\n", sampdf.to_string(index=False)); print("\n", ov.to_string(index=False)); print("\n", ivs.round(3).to_string(index=False))
