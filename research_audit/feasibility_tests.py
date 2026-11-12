"""Evidence-gathering tests for the feasibility assessment (descriptive / associational only)."""
import pandas as pd, numpy as np, os, sys
os.chdir(os.path.join(os.path.dirname(__file__), ".."))
D = "research_audit/derived/"; rng = np.random.default_rng(1)
def perm_p(x, y, n=5000):
    x, y = np.asarray(x, float), np.asarray(y, float); m = ~(np.isnan(x) | np.isnan(y)); x, y = x[m], y[m]
    r = np.corrcoef(x, y)[0, 1]; c = sum(abs(np.corrcoef(x, rng.permutation(y))[0, 1]) >= abs(r) for _ in range(n))
    return r, (c + 1) / (n + 1), len(x)
def detr(s, yrs):
    ok = s.notna(); b = np.polyfit(yrs[ok], s[ok], 1); return s - np.polyval(b, yrs)
mon = pd.read_csv(D + "era5_monthly.csv", parse_dates=["month"]).set_index("month")
def win(y0, m0, y1, m1, col):  # inclusive month window
    s = mon.loc[f"{y0}-{m0:02d}":f"{y1}-{m1:02d}", col]; return s.sum() if col == "rain_mm" else s.mean()
print("=== A. Weather vs national paddy (ERA5 national mean vs DCS), detrended ===")
for s in ("maha", "yala"):
    d = pd.read_csv(D + f"dcs_national_{s}.csv"); d["y"] = d.season_label.astype(str).str[:4].astype(int)
    d = d[(d.y >= 2010) & (d.y <= 2025)].copy()
    d["rain"] = [win(y, 10, y + 1, 2, "rain_mm") if s == "maha" else win(y, 3, y, 8, "rain_mm") for y in d.y]
    d["t2m"] = [win(y, 10, y + 1, 2, "t2m_mean") if s == "maha" else win(y, 3, y, 8, "t2m_mean") for y in d.y]
    d["harv_sown"] = d.harv_000ha / d.sown_000ha
    print(f"\n{s}: seasons {d.y.min()}-{d.y.max()} n={len(d)}  mean rain {d.rain.mean():.0f} mm (sd {d.rain.std():.0f})")
    print(d[["y","rain","sown_000ha","harv_000ha","yield_kg_ha","prod_000mt"]].round(0).to_string(index=False, header=False).replace("\n"," | ")[:700])
    for tgt in ("prod_000mt", "yield_kg_ha", "harv_000ha", "harv_sown"):
        for w in ("rain", "t2m"):
            r, p, n = perm_p(detr(d[w], d.y.values), detr(d[tgt], d.y.values)); print(f"  detrended {w:4s} vs {tgt:12s} r={r:+.2f} perm_p={p:.3f} n={n}")
print("\n=== B. Rice: domestic production vs imports (annual) ===")
mh = pd.read_csv(D + "dcs_national_maha.csv"); yl = pd.read_csv(D + "dcs_national_yala.csv")
mh["y"] = mh.season_label.astype(str).str[:4].astype(int) + 1; yl["y"] = yl.season_label.astype(int)   # calendar year of harvest
cal = (mh.set_index("y").prod_000mt + yl.set_index("y").prod_000mt).rename("paddy_000t").to_frame()
cal["rice_eq_000t"] = cal.paddy_000t * 0.67
ct = pd.read_csv(D + "comtrade_year_summary.csv").set_index("year")
cal["comtrade_rice_imp_000t"] = ct.rice_t / 1000
ft = pd.read_csv("raw/FAOSTAT_TRADE/extracted/sri_lanka_agricultural_trade.csv")
fm = ft[(ft.Item == "Rice, milled") & (ft.Element == "Import quantity")].set_index("Year").Value / 1000
fe = ft[(ft.Item == "Rice, milled") & (ft.Element == "Export quantity")].set_index("Year").Value / 1000
cal["fao_rice_imp_000t"] = fm; cal["fao_rice_exp_000t"] = fe
fp = pd.read_csv("raw/FAOSTAT/extracted/sri_lanka_crop_production.csv")
fpp = fp[(fp.Item == "Rice") & (fp.Element == "Production")].set_index("Year").Value / 1000
cal["fao_paddy_000t"] = fpp
c = cal.loc[2010:2025]; print(c.round(0).to_string())
print("DCS vs FAO paddy production 2010-2024 r=%.3f, mean ratio %.3f" % (c.paddy_000t.corr(c.fao_paddy_000t), (c.paddy_000t / c.fao_paddy_000t).mean()))
print("Comtrade vs FAO rice import qty r=%.3f; ratio median %.2f" % (c.comtrade_rice_imp_000t.corr(c.fao_rice_imp_000t), (c.comtrade_rice_imp_000t / c.fao_rice_imp_000t).median()))
c = c.assign(imp_share=c.fao_rice_imp_000t / (c.rice_eq_000t + c.fao_rice_imp_000t - c.fao_rice_exp_000t.fillna(0)))
print("import share of apparent supply (supply = prod_eq + imports - exports; no stocks/seed/feed/waste): min %.3f max %.3f" % (c.imp_share.min(), c.imp_share.max()))
dp = detr(c.paddy_000t, c.index.values); print("detrended paddy prod vs FAO rice import same yr: r,p,n =", perm_p(dp, c.fao_rice_imp_000t), "| next yr:", perm_p(dp.iloc[:-1], c.fao_rice_imp_000t.shift(-1).iloc[:-1]))
print("detrended paddy prod vs Comtrade rice import same yr:", perm_p(dp[c.index != 2018], c.comtrade_rice_imp_000t[c.index != 2018]))
cal.to_csv(D + "rice_annual_balance.csv")
print("\n=== E. CBSL monthly rice imports vs Comtrade ===")
cb = pd.read_csv("raw/CBSL-rice-imports-quanitties.csv", comment="#"); cb["y"] = cb.period.str[:4].astype(int)
a = cb.groupby("y").agg(cbsl_000t=("value", "sum"), months=("value", "size")); a["comtrade_000t"] = ct.rice_t / 1000; print(a.round(1).to_string())
