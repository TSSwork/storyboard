"""Pilot: does ERA5 rain improve 1-month-ahead vegetable price forecasts? Expanding-window, no look-ahead."""
import pandas as pd, numpy as np, os
os.chdir(os.path.join(os.path.dirname(__file__), ".."))
cb = pd.read_csv("raw/cbsl-daily-prices.csv", comment="#", parse_dates=["period"]).set_index("period")
mon = pd.read_csv("research_audit/derived/era5_monthly.csv", parse_dates=["month"]).set_index("month")
mon = mon[mon.days_in_month >= 28]; g = mon.groupby(mon.index.month).rain_mm
anom = ((mon.rain_mm - g.transform("mean")) / g.transform("std")).rename("a")   # NB: climatology uses full sample (slight look-ahead; flagged)
fx = pd.read_csv("raw/pdf/Indicative Rate of the USD_LKR SPOT Exchange Rate.csv", parse_dates=["Date"]).set_index("Date")["Exchange Rate"].resample("MS").mean()
dfx = np.log(fx).diff().rename("fx")
def fit_pred(X, y, xn, lam=1e-6):
    A = np.c_[np.ones(len(X)), X]; b = np.linalg.solve(A.T @ A + lam * np.eye(A.shape[1]), A.T @ y); return np.r_[1, xn] @ b
rows = []
for veg in ["Cabbage", "Carrot", "Brinjal", "Tomato", "Beans", "Pumpkin", "Snake gourd"]:
    col = [c for c in cb.columns if c.startswith(veg + " (wholesale, dambulla)")][0]
    y = np.log(cb[col].resample("MS").mean()).dropna()
    d = pd.concat([y.rename("y"), anom, dfx], axis=1).dropna(); d = d[d.index.isin(y.index)]
    d["y1"] = d.y.shift(1); d["y2"] = d.y.shift(2); d["y11"] = d.y.shift(11); d["a1"] = d.a.shift(1); d["a3"] = d.a.rolling(3).sum()
    d["target"] = d.y.shift(-1); d["nxt"] = d.index.to_series().shift(-1)
    d = d.dropna(subset=["target", "y11", "y2", "a1", "a3"]); n0 = 48
    cols = {"naive": None, "snaive": None, "AR": ["y", "y1", "y11"], "AR+rain": ["y", "y1", "y11", "a", "a1", "a3"], "AR+rain+fx": ["y", "y1", "y11", "a", "a1", "a3", "fx"]}
    err = {k: [] for k in cols}
    for i in range(n0, len(d)):
        tr, te = d.iloc[:i], d.iloc[i]
        for k, c in cols.items():
            if k == "naive": p = te.y
            elif k == "snaive": p = te.y11          # price 12 months before the target month
            else: p = fit_pred(tr[c].values, tr.target.values, te[c].values)
            err[k].append(te.target - p)
    r = {k: np.sqrt(np.mean(np.square(v))) for k, v in err.items()}
    # Diebold-Mariano-style: mean loss diff / se (naive se, no HAC) AR vs AR+rain
    dl = np.square(err["AR"]) - np.square(err["AR+rain"]); dm = dl.mean() / (dl.std(ddof=1) / np.sqrt(len(dl)))
    rows.append(dict(veg=veg, n_test=len(err["naive"]), **{k: round(v, 3) for k, v in r.items()}, rain_gain_pct=round(100 * (1 - r["AR+rain"] / r["AR"]), 1), fx_gain_pct=round(100 * (1 - r["AR+rain+fx"] / r["AR+rain"]), 1), DM_t=round(dm, 2)))
print(pd.DataFrame(rows).to_string(index=False))
