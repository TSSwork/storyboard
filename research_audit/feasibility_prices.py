import pandas as pd, numpy as np, os
os.chdir(os.path.join(os.path.dirname(__file__), ".."))
D = "research_audit/derived/"; rng = np.random.default_rng(2)
def perm_r(x, y, n=3000):
    m = ~(np.isnan(x) | np.isnan(y)); x, y = x[m], y[m]; r = np.corrcoef(x, y)[0, 1]
    return r, (sum(abs(np.corrcoef(x, rng.permutation(y))[0, 1]) >= abs(r) for _ in range(n)) + 1) / (n + 1), len(x)
# --- balance robustness
b = pd.read_csv(D + "rice_annual_balance.csv", index_col=0).loc[2010:2024]
dp = b.paddy_000t - np.polyval(np.polyfit(b.index, b.paddy_000t, 1), b.index)
print("Spearman paddy(detr) vs FAO imports:", round(dp.rank().corr(b.fao_rice_imp_000t.rank()), 2),
      "| excl 2017 & 2022 r=", round(dp.drop([2017, 2022]).corr(b.fao_rice_imp_000t.drop([2017, 2022])), 2))
# --- exchange rate monthly
fx = pd.read_csv("raw/pdf/Indicative Rate of the USD_LKR SPOT Exchange Rate.csv", parse_dates=["Date"])
print("FX rows", len(fx), fx.Date.min().date(), fx.Date.max().date(), "dup dates", fx.Date.duplicated().sum(), "USDLKR range", fx["Exchange Rate"].min().round(1), fx["Exchange Rate"].max().round(1))
fxm = fx.set_index("Date")["Exchange Rate"].resample("MS").mean().rename("usdlkr")
# --- HARTI retail rice (weekly -> monthly)
r = pd.read_csv("raw/pdf/HARTI/tables/retail_rice.csv", parse_dates=["week_start"]); r["mid"] = (r["min"] + r["max"]) / 2
print("retail_rice locations per week (median):", r.groupby("week_start").row.nunique().median(), " | price mid range", r.mid.min(), r.mid.max())
def mon(df, col): return df.groupby([pd.Grouper(key="week_start", freq="MS"), col]).mid.mean().unstack()
rm = mon(r, "column"); 
col = r[r.row == "Colombo"]; rc = mon(col, "column")
print("monthly months:", len(rm), rm.index.min().date(), rm.index.max().date(), "| Colombo-only coverage:", rc.notna().sum().to_dict())
def xcorr(price, name, lags=range(0, 7)):
    lp = np.log(price).diff(); lf = np.log(fxm).diff(); out = []
    for L in lags:
        j = pd.concat([lp, lf.shift(L)], axis=1).dropna(); out.append(round(j.corr().iloc[0, 1], 2))
    print(f"  {name:28s} dlog(price) vs dlog(USDLKR) lag0..6:", out, "n=", len(j))
print("\n== C1. HARTI rice (all-location mean) vs USD/LKR, monthly log-differences")
for c in ["Samba 1", "Nadu 1", "Raw Red", "Raw White", "Keeri Samba"]: xcorr(rm[c].dropna(), c)
ps = pd.concat([np.log(rm["Nadu 1"]).rename("rice"), np.log(fxm)], axis=1).dropna()
y21 = ps.loc["2021-12":"2022-12"]; print("  Dec-2021->Dec-2022: Nadu1 +%.0f%%  USDLKR +%.0f%%" % (100 * (np.exp(y21.rice.iloc[-1] - y21.rice.iloc[0]) - 1), 100 * (np.exp(y21.usdlkr.iloc[-1] - y21.usdlkr.iloc[0]) - 1)))
# --- imported vs local (HARTI summary_retail Colombo)
s = pd.read_csv("raw/pdf/HARTI/tables/summary_retail.csv", parse_dates=["week_start"]); s["mid"] = (s["min"] + s["max"]) / 2
s["k"] = s.section.fillna("") + " | " + s.commodity
sel = [k for k in s.k.unique() if any(t in k for t in ("Dried Chillies", "Big Onion", "Potato", "Red Onion", "Red Dhal", "Sugar", "Wheat", "Coconut | Large", "Rice"))]
cnt = s[s.k.isin(sel)].groupby("k").week_start.nunique(); print("\nsummary_retail candidate series (weeks):", cnt[cnt > 100].to_dict())
sm = s[s.k.isin(cnt[cnt > 100].index)].groupby([pd.Grouper(key="week_start", freq="MS"), "k"]).mid.mean().unstack()
print("== C2. 2021-12 -> 2022-12 change (%), imported vs local items, and corr of dlog with dlog(USDLKR) lag0..3")
for k in sm.columns:
    x = sm[k].dropna(); lp = np.log(sm[k]).diff(); lf = np.log(fxm).diff(); rr = [round(pd.concat([lp, lf.shift(L)], axis=1).dropna().corr().iloc[0, 1], 2) for L in range(4)]
    try: ch = 100 * (sm[k].loc["2022-12"].iloc[0] / sm[k].loc["2021-12"].iloc[0] - 1)
    except Exception: ch = np.nan
    print(f"  {k:36s} n_months={len(x):3d} chg2022={ch:6.0f}%  r_lag0..3={rr}")
# --- weather vs vegetable prices (CBSL daily, Dambulla wholesale)
cb = pd.read_csv("raw/cbsl-daily-prices.csv", comment="#", parse_dates=["period"]).set_index("period")
vcols = [c for c in cb.columns if "wholesale, dambulla" in c and any(v in c for v in ["Beans", "Carrot", "Cabbage", "Tomato", "Brinjal", "Pumpkin", "Snake"])]
vm = np.log(cb[vcols].resample("MS").mean()); vm.columns = [c.split(" (")[0] for c in vm.columns]
ncount = cb[vcols].resample("MS").count().min().min(); print("\nCBSL daily obs per month (min over series):", ncount, "| months", len(vm), vm.index.min().date(), vm.index.max().date())
mon = pd.read_csv(D + "era5_monthly.csv", parse_dates=["month"]).set_index("month")
mon = mon[mon.days_in_month >= 28]; clim = mon.groupby(mon.index.month).rain_mm.transform("mean"); anom = (mon.rain_mm - clim) / mon.groupby(mon.index.month).rain_mm.transform("std")
print("== D. dlog(veg price), de-seasonalised, vs ERA5 national rain z-anomaly (lag in months), perm p; n tests =", len(vm.columns) * 4)
sig = 0; rows = []
for c in vm.columns:
    dp = vm[c].diff(); dp = dp - dp.groupby(dp.index.month).transform("mean")
    for L in range(0, 4):
        j = pd.concat([dp, anom.shift(L)], axis=1).dropna(); r_, p_, n_ = perm_r(j.iloc[:, 0].values, j.iloc[:, 1].values)
        rows.append((c, L, r_, p_, n_)); sig += p_ < 0.05
t = pd.DataFrame(rows, columns=["veg", "lag", "r", "p", "n"]); print(t.pivot(index="veg", columns="lag", values="r").round(2).to_string()); print("significant at 5%%: %d of %d (≈%.1f expected by chance); min p=%.3f" % (sig, len(t), 0.05 * len(t), t.p.min()))
# cumulative 3-month rain anomaly
a3 = anom.rolling(3).sum()
rows = []
for c in vm.columns:
    dp = vm[c].diff(); dp = dp - dp.groupby(dp.index.month).transform("mean"); j = pd.concat([dp, a3.shift(1)], axis=1).dropna(); rows.append((c, *perm_r(j.iloc[:, 0].values, j.iloc[:, 1].values)))
print("3-mo cumulative anomaly lag1:", [(c, round(r_, 2), round(p_, 3)) for c, r_, p_, n_ in rows])
# HARTI veg vs rain: coverage of vegetables weekly
v = pd.read_csv("raw/pdf/HARTI/tables/retail_vegetables.csv", parse_dates=["week_start"]); print("\nHARTI retail_vegetables items:", sorted(v.column.dropna().unique())[:12], "weeks", v.week_start.nunique())
