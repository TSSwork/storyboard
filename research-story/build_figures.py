"""Build the 18 storyboard images (storyboard/NN_slug/storyboard.png) from existing derived data.

Reads only; never modifies raw or research_audit files.
Run:  uv run python research-story/build_figures.py [page numbers...]
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

import slide_copy as SC
from matplotlib import font_manager
for _w in ("Regular", "Medium", "SemiBold"):          # static Noto Sans cuts, when installed (falls back to DejaVu Sans)
    _f = Path(f"/usr/share/fonts/google-noto/NotoSans-{_w}.ttf")
    if _f.exists():
        font_manager.fontManager.addfont(str(_f))

ROOT = Path(__file__).resolve().parent
WORK = ROOT.parent
RA = WORK / "research_audit"
D = RA / "derived"
V2 = RA / "forecast_validation_v2"
OUT = ROOT / "storyboard"

# ---- design tokens (one accent; evidence class carried by colour AND label) ----
# Palette: midnight navy (ink + primary), soft blue (tint), coral (the one accent: marks and caution only, never text)
NAVY, SOFT, CORAL = "#002941", "#b6dfed", "#fd6e6e"
PAPER, INK, MUTED, GRID = "#f6fafc", NAVY, "#52707f", "#d8e6ee"
TINT, RAIN, MID, BASE = "#e3f1f7", "#8cc0d6", "#2f7292", "#8aa3b2"
ACC, EXPL, BAD = NAVY, MID, CORAL
EVID_COL = {"supported": NAVY, "exploratory": SOFT, "no evidence": "#a9bcc7", "worse": CORAL}
plt.rcParams.update({"font.family": ["Noto Sans", "DejaVu Sans"], "axes.edgecolor": GRID, "axes.labelcolor": MUTED,
                     "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.facecolor": PAPER,
                     "figure.facecolor": PAPER, "axes.grid": False})

VEGS = ["Cabbage", "Brinjal", "Carrot", "Tomato", "Snake gourd", "Pumpkin", "Beans"]
SLUGS = {1: "opening", 2: "scope_and_data", 3: "prices_and_rain", 4: "forecast_experiment", 5: "evaluation",
         6: "main_result", 7: "robustness", 8: "accuracy", 9: "wider_context", 10: "conclusions"}
ACTS = SC.ACTS


# Stored v2 evidence label -> slide label (read from forecast_model_comparison_v2.csv, never re-derived)
EVID_LABEL = {"supported (corrected)": "supported", "suggestive (uncorrected only)": "exploratory",
              "no reliable evidence": "no evidence", "worse or no gain": "worse"}


def frame(n):
    headline, source, sub = SC.HEAD[n]
    fig = plt.figure(figsize=(16, 9), dpi=100)
    fig.add_artist(Line2D([0.0535], [0.9475], marker="s", color=CORAL, markersize=6, linestyle="none", transform=fig.transFigure))
    fig.text(0.064, 0.945, f"{n:02d}  ·  {ACTS[n]}", fontsize=11, color=MUTED, fontweight="medium")
    fig.text(0.05, 0.885, headline, fontsize=23, fontweight="semibold", va="center")
    if sub:
        fig.text(0.05, 0.835, sub, fontsize=12.5, color=MUTED, va="center")
    fig.text(0.05, 0.035, "Source: " + source, fontsize=9.5, color=MUTED)
    fig.text(0.95, 0.035, "Exploratory · not causal", fontsize=9.5, color=MUTED, ha="right")
    return fig


def save(fig, n):
    d = OUT / f"{n:02d}_{SLUGS[n]}"
    (d / "assets").mkdir(parents=True, exist_ok=True)
    fig.savefig(d / "storyboard.png", dpi=100, facecolor=PAPER)
    plt.close(fig)
    print("wrote", d / "storyboard.png")


def box(ax, xy, w, h, text, fc="white", ec=GRID, tc=INK, fs=12, bold=False, lw=1.4):
    ax.add_patch(FancyBboxPatch(xy, w, h, boxstyle="round,pad=0.01,rounding_size=0.015", fc=fc, ec=ec, lw=lw))
    ax.text(xy[0] + w / 2, xy[1] + h / 2, text, ha="center", va="center", fontsize=fs, color=tc,
            fontweight="semibold" if bold else "normal", linespacing=1.4)


def arrow(ax, a, b, col=MUTED):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=16, lw=1.6, color=col))


def blank(fig, rect=(0.05, 0.08, 0.9, 0.7)):
    ax = fig.add_axes(rect)
    ax.set_xlim(-0.01, 1.01); ax.set_ylim(-0.02, 1.02); ax.axis("off")
    return ax


# ---- data ----
def prices():
    cb = pd.read_csv(WORK / "raw/cbsl-daily-prices.csv", comment="#", parse_dates=["period"]).set_index("period")
    out = {}
    for v in VEGS:
        col = [c for c in cb.columns if c.startswith(v + " (wholesale, dambulla)")][0]
        s = cb[col].dropna()
        cnt = s.resample("MS").count()
        m = s.resample("MS").mean()[cnt >= 10]
        out[v] = m
    return pd.DataFrame(out)


def national_rain():
    m = pd.read_csv(D / "era5_regional_monthly.csv", parse_dates=["month"]).set_index("month")
    r = m.rain_nat.where(m.n_nat == m.days_in_month)
    clim = []
    for t in r.index:
        past = r[(r.index.month == t.month) & (r.index.year < t.year)].dropna()
        clim.append(past.mean() if len(past) else np.nan)
    return r, (r - pd.Series(clim, index=r.index)) / 100


def comp():
    c = pd.read_csv(RA / "forecast_model_comparison_v2.csv")
    c = c[(c.market == "dambulla") & (c.price_agg == "mean") & (c.model == "AR+rain:nat")].set_index("commodity")
    return c.loc[VEGS]


def style_axes(ax, grid_y=True):
    ax.tick_params(length=0, labelsize=10)
    if grid_y:
        ax.grid(axis="y", color=GRID, lw=0.8)
        ax.set_axisbelow(True)


# ---------------- pages ----------------
def mc(market="dambulla", agg="mean", model="AR+rain:nat"):
    c = pd.read_csv(RA / "forecast_model_comparison_v2.csv")
    c = c[(c.market == market) & (c.price_agg == agg) & (c.model == model)].set_index("commodity")
    return c.loc[VEGS]


def p01():
    fig = frame(1)
    pr = prices()["Cabbage"].loc["2016":]
    a = fig.add_axes([0.06, 0.45, 0.88, 0.27])
    a.plot(pr.index, pr.values, color=ACC, lw=2)
    a.set_ylabel("Cabbage, LKR/kg (nominal)", fontsize=10); style_axes(a); a.set_xticklabels([])
    r, _ = national_rain(); r = r.loc["2016":]
    b = fig.add_axes([0.06, 0.13, 0.88, 0.22])
    b.bar(r.index, r.values, width=24, color=RAIN)
    b.set_ylabel("National rain, mm/month", fontsize=10); style_axes(b)
    fig.text(0.5, 0.775, "Dambulla wholesale price and observed national rainfall, 2016–2026", ha="center", fontsize=11, color=MUTED)
    fig.text(0.5, 0.045 + 0.0, "", fontsize=1)
    save(fig, 1)


def p02():
    fig = frame(2)
    g = json.load(open(WORK / "raw/chirp/boundaries/countries.geojson"))
    f = [x for x in g["features"] if x["properties"].get("ISO3166-1-Alpha-3") == "LKA"][0]
    ax = fig.add_axes([0.04, 0.08, 0.28, 0.7])
    for poly in f["geometry"]["coordinates"]:
        for ring in poly:
            xs, ys = zip(*ring); ax.fill(xs, ys, fc=TINT, ec=BASE, lw=1)
    for nme, (x, y, c) in {"Dambulla": (80.65, 7.86, ACC), "Nuwara Eliya": (80.77, 6.97, EXPL)}.items():
        ax.add_patch(Rectangle((x - 0.3, y - 0.3), 0.6, 0.6, fc="none", ec=c, ls="--", lw=1.6))
        ax.plot(x, y, "o", color=c, ms=7); ax.annotate(nme, (x + 0.34, y + 0.12), fontsize=10, color=c)
    ax.plot(79.85, 6.94, "s", color=INK, ms=7); ax.text(79.95, 6.94, "Pettah", fontsize=10, va="center")
    ax.set_aspect(1); ax.axis("off")
    ax.text(0.5, -0.02, SC.P02_MAPNOTE, transform=ax.transAxes, ha="center", fontsize=9, color=MUTED)
    r = blank(fig, (0.36, 0.1, 0.6, 0.68))
    for i, (k, v) in enumerate(SC.P02_ITEMS):
        y = 0.96 - i * 0.135
        r.text(0, y, k, fontsize=10.5, color=MUTED, fontweight="medium", va="top")
        r.text(0, y - 0.04, v, fontsize=12.5, va="top")
    box(r, (0.0, 0.1), 0.28, 0.14, SC.P02_FLOW[0], fs=10.5); box(r, (0.33, 0.1), 0.28, 0.14, SC.P02_FLOW[1], fs=10.5)
    box(r, (0.69, 0.1), 0.3, 0.14, SC.P02_FLOW[2], fc=ACC, ec=ACC, tc="white", fs=10.5, bold=True)
    arrow(r, (0.28, 0.17), (0.33, 0.17)); arrow(r, (0.61, 0.17), (0.69, 0.17))
    r.text(0.0, 0.01, SC.P02_NOTE, fontsize=10, color=INK)
    save(fig, 2)


def p03():
    lag = pd.DataFrame({0: [0.10, 0.03, -0.06, 0.19, 0.16, 0.02, 0.21], 1: [0.60, 0.40, 0.44, 0.26, 0.20, 0.14, 0.08],
                        2: [0.16, -0.29, 0.20, 0.01, -0.15, 0.04, 0.03], 3: [-0.06, 0.18, 0.00, -0.26, -0.14, -0.07, -0.09]}, index=VEGS)
    (OUT / "03_prices_and_rain/assets").mkdir(parents=True, exist_ok=True)
    lag.to_csv(OUT / "03_prices_and_rain/assets/lag_correlations.csv")
    fig = frame(3)
    pr = prices()
    gs = fig.add_gridspec(2, 4, left=0.05, right=0.60, bottom=0.36, top=0.78, hspace=0.5, wspace=0.3)
    for i, v in enumerate(VEGS):
        ax = fig.add_subplot(gs[i // 4, i % 4]); s = pr[v].dropna()
        ax.axvspan(pd.Timestamp("2022-01-01"), pd.Timestamp("2022-12-31"), color=GRID, lw=0)
        ax.plot(s.index, s.values, color=ACC, lw=1.3); ax.set_title(v, fontsize=10.5, loc="left", fontweight="semibold")
        style_axes(ax); ax.tick_params(labelsize=7.5)
    n = fig.add_subplot(gs[1, 3]); n.axis("off")
    n.text(0, 0.9, "LKR/kg, nominal\nshaded = 2022", fontsize=9.5, color=MUTED, va="top", linespacing=1.5)
    h = fig.add_axes([0.70, 0.36, 0.26, 0.42])
    h.imshow(lag.values, cmap=LinearSegmentedColormap.from_list("rain", [(0, CORAL), (0.5, "#ffffff"), (0.72, "#8cc0d6"), (1, NAVY)]), vmin=-0.6, vmax=0.6, aspect="auto")
    h.set_xticks(range(4)); h.set_xticklabels([f"lag {k}" for k in range(4)], fontsize=9.5); h.xaxis.tick_top()
    h.set_yticks(range(7)); h.set_yticklabels(VEGS, fontsize=10); h.tick_params(length=0)
    for i in range(7):
        for j in range(4):
            h.text(j, i, f"{lag.values[i, j]:+.2f}", ha="center", va="center", fontsize=9, color="white" if abs(lag.values[i, j]) > 0.35 else INK)
    for sp in h.spines.values(): sp.set_visible(False)
    h.add_patch(Rectangle((0.5, -0.5), 1, 3, fill=False, ec=INK, lw=2))
    fig.text(0.70, 0.325, "Corr. of de-seasonalised price change with a\nz-score rain anomaly k months earlier", fontsize=9, color=MUTED, va="top", linespacing=1.4)
    _, an = national_rain(); an = an.loc["2016":]
    b = fig.add_axes([0.05, 0.08, 0.55, 0.15])
    b.bar(an.index, an.values, width=24, color=[MID if v >= 0 else CORAL for v in an.fillna(0)]); b.axhline(0, color=INK, lw=0.8)
    b.set_ylabel("rain anomaly\n(×100 mm)", fontsize=9); style_axes(b); b.tick_params(labelsize=8)
    fig.text(0.70, 0.215, "Strip: forecasting anomaly = rain minus the mean of\nthe same calendar month in earlier years, ÷ 100 mm.\nHeat map: z-score anomaly, a different construction.\nCorrelation motivates the test; it is not the finding.", fontsize=9.5, va="top", linespacing=1.45)
    save(fig, 3)


def p04():
    fig = frame(4)
    ax = blank(fig, (0.05, 0.42, 0.9, 0.38))
    box(ax, (0.02, 0.58), 0.33, 0.38, SC.P04_A, fs=11.5, bold=True)
    box(ax, (0.02, 0.04), 0.33, 0.46, SC.P04_B, fc=TINT, ec=ACC, fs=11.5, bold=True)
    box(ax, (0.5, 0.35), 0.2, 0.3, SC.P04_FORECAST, fs=13, bold=True)
    arrow(ax, (0.35, 0.77), (0.5, 0.55)); arrow(ax, (0.35, 0.27), (0.5, 0.45))
    box(ax, (0.79, 0.35), 0.19, 0.3, SC.P04_COMPARE, fs=12); arrow(ax, (0.7, 0.5), (0.8, 0.5))
    w = blank(fig, (0.05, 0.08, 0.9, 0.28))
    for i, lab in enumerate(["t−3", "t−2", "t−1", "t"]):
        fc = TINT if i == 3 else "white"
        w.add_patch(Rectangle((i * 0.075, 0.45), 0.07, 0.35, fc=fc, ec=ACC if i == 3 else GRID, lw=2 if i == 3 else 1))
        w.text(i * 0.075 + 0.035, 0.625, lab, ha="center", va="center", fontsize=11)
    w.text(0.0, 0.3, SC.P04_WINDOW, fontsize=10.5, va="top", linespacing=1.5)
    for i, t in enumerate(SC.P04_BULLETS):
        w.text(0.42, 0.9 - i * 0.2, "•  " + t, fontsize=12, va="top")
    save(fig, 4)


def p05():
    fig = frame(5)
    ax = blank(fig, (0.05, 0.47, 0.9, 0.33))
    cards = [(h, ACC, t) for h, t in SC.P05_CARDS]
    for i, (h, c, t) in enumerate(cards):
        x0 = i * 0.34
        ax.add_patch(Rectangle((x0, 0.0), 0.31, 1.0, fc="white", ec=GRID)); ax.add_patch(Rectangle((x0, 0.985), 0.31, 0.015, fc=c, ec="none"))
        ax.text(x0 + 0.015, 0.84, h, fontsize=13, fontweight="semibold", color=INK, va="center")
        ax.text(x0 + 0.015, 0.68, t, fontsize=11.5, va="top", linespacing=1.5)
    tl = blank(fig, (0.05, 0.08, 0.9, 0.3))
    for k, y in enumerate([0.78, 0.5, 0.22]):
        w = 0.4 + k * 0.07
        tl.add_patch(Rectangle((0.0, y), w, 0.17, fc=TINT, ec="none")); tl.add_patch(Rectangle((w, y), 0.03, 0.17, fc=ACC, ec="none"))
        tl.text(w / 2, y + 0.085, "training window (grows)", ha="center", va="center", fontsize=10)
        tl.text(w + 0.045, y + 0.085, "forecast t+1", va="center", fontsize=10, color=ACC)
    tl.text(0.66, 0.85, SC.P05_TL1, fontsize=11.5, va="top", linespacing=1.5)
    tl.text(0.66, 0.35, SC.P05_TL2, fontsize=10.5, color=EXPL, va="top", linespacing=1.5)
    save(fig, 5)


def p06():
    c = mc(); gain, p = c.rmse_gain_vs_AR_pct.values, c.cw_p_holm.values
    ev = [EVID_LABEL[e] for e in c.evidence]
    fig = frame(6)
    a = fig.add_axes([0.14, 0.15, 0.5, 0.6]); y = np.arange(7)[::-1]
    a.barh(y, gain, color=[EVID_COL[e] for e in ev], height=0.62, edgecolor=[NAVY if e == "exploratory" else "none" for e in ev], linewidth=1.6); a.axvline(0, color=INK, lw=1)
    a.set_yticks(y); a.set_yticklabels(VEGS, fontsize=13); a.set_xlabel("RMSE reduction vs price-only AR (%)", fontsize=11); a.tick_params(length=0, labelsize=10)
    for yy, g in zip(y, gain):
        a.text(g + (0.5 if g >= 0 else -0.5), yy, f"{g:+.1f}%", va="center", ha="left" if g >= 0 else "right", fontsize=12, fontweight="semibold")
    a.set_xlim(-4, 24)
    t = fig.add_axes([0.68, 0.1, 0.28, 0.64]); t.axis("off"); t.set_ylim(-0.5, 6.5); t.set_xlim(0, 1)
    t.text(0, 6.75, "Holm p", fontsize=10.5, color=MUTED, fontweight="semibold"); t.text(0.4, 6.75, "Evidence", fontsize=10.5, color=MUTED, fontweight="semibold")
    lab = {"supported": "supported", "exploratory": "exploratory only", "no evidence": "no reliable evidence", "worse": "rain does not help"}
    for yy, q, e in zip(y, p, ev):
        t.text(0, yy, f"{q:.4f}" if q < 0.01 else f"{q:.3f}", va="center", fontsize=12)
        t.scatter(0.405, yy, s=70, color=EVID_COL[e], edgecolor=NAVY if e == "exploratory" else "none", linewidth=1.4, zorder=3); t.text(0.46, yy, lab[e], va="center", fontsize=11.5, color=INK, fontweight="medium")
    save(fig, 6)


def p07():
    rw = pd.read_csv(V2 / "rain_window_comparison.csv").set_index(["commodity", "model"])
    pet, med = mc("pettah"), mc("dambulla", "median")
    marks = [("Primary: national rain, A3 = t−2…t", NAVY, "o", 110, [rw.loc[(v, "nat_incl"), "rmse_gain_vs_AR_pct"] for v in VEGS]),
             ("Non-overlapping A3 = t−3…t−1", "#5b9ab7", "o", 60, [rw.loc[(v, "nat_prior"), "rmse_gain_vs_AR_pct"] for v in VEGS]),
             ("Dambulla rain box", MID, "s", 55, [rw.loc[(v, "dam_incl"), "rmse_gain_vs_AR_pct"] for v in VEGS]),
             ("Nuwara Eliya rain box", "#7a8f9c", "^", 60, [rw.loc[(v, "nuw_incl"), "rmse_gain_vs_AR_pct"] for v in VEGS]),
             ("Pettah market", "#1d5878", "D", 45, list(pet.rmse_gain_vs_AR_pct.values)),
             ("Monthly median price", BASE, "X", 55, list(med.rmse_gain_vs_AR_pct.values))]
    fig = frame(7)
    a = fig.add_axes([0.12, 0.17, 0.56, 0.56]); y = np.arange(7)[::-1]
    a.axvline(0, color=INK, lw=1); a.grid(axis="y", color=GRID); a.set_axisbelow(True)
    for lab, c, m, s, vals in marks:
        a.scatter(vals, y, s=s, color=c, marker=m, label=lab, zorder=3, edgecolor="white", linewidth=0.8)
    a.set_yticks(y); a.set_yticklabels(VEGS, fontsize=12); a.set_xlabel("RMSE reduction vs AR (%)", fontsize=11); a.tick_params(length=0, labelsize=10)
    for sp in a.spines.values(): sp.set_visible(False)
    a.legend(frameon=False, fontsize=10, loc="center left", bbox_to_anchor=(1.03, 0.5))
    fig.text(0.05, 0.075, "Multiplicity: one tomato cell (Dambulla box, non-overlapping window) reaches Holm p = 0.036. It is one of six specifications and the primary tomato result is not significant, so it is NOT promoted.",
             fontsize=10.5, color=EXPL)
    save(fig, 7)


def p08():
    r = pd.read_csv(RA / "forecast_results_v2.csv", parse_dates=["origin", "target_month"])
    r = r[(r.market == "dambulla") & (r.price_agg == "mean") & (r.commodity == "Cabbage")]
    ar = r[r.model == "AR"].set_index("target_month"); rn = r[r.model == "AR+rain:nat"].set_index("target_month")
    m = mc(); ic = pd.read_csv(V2 / "interval_coverage.csv"); ic = ic[ic.model == "nat_incl"].set_index("commodity").loc[VEGS]
    fig = frame(8)
    a = fig.add_axes([0.06, 0.1, 0.56, 0.64])
    a.fill_between(rn.index, rn.lo80_lkr, rn.hi80_lkr, color=ACC, alpha=0.14, lw=0, label="AR+rain 80% band")
    a.plot(ar.index, ar.actual_lkr, color=INK, lw=2, label="Actual"); a.plot(ar.index, ar.pred_lkr, color=BASE, lw=1.6, label="Price-only AR")
    a.plot(rn.index, rn.pred_lkr, color=ACC, lw=2, label="AR + rain")
    a.set_ylabel("LKR/kg", fontsize=10); style_axes(a); a.legend(frameon=False, fontsize=10, loc="upper left")
    t = fig.add_axes([0.67, 0.1, 0.29, 0.64]); t.axis("off"); t.set_xlim(0, 1); t.set_ylim(-0.5, 7.5)
    t.text(0.38, 7.2, "MAPE %", fontsize=10, color=MUTED, fontweight="semibold"); t.text(0.72, 7.2, "80% cover", fontsize=10, color=MUTED, fontweight="semibold")
    for i, v in enumerate(VEGS):
        yy = 6.4 - i; t.text(0, yy, v, fontsize=11.5, va="center"); t.text(0.4, yy, f"{m.loc[v, 'mape_pct']:.1f}", fontsize=11.5, va="center")
        cov = ic.loc[v, "coverage"]; t.text(0.74, yy, f"{cov:.2f}", fontsize=11.5, va="center", color=INK)
        if cov < 0.75: t.scatter(0.70, yy, s=36, color=CORAL, zorder=3)
    t.text(0, -0.4, "Nominal coverage 0.80; coral dot = below 0.75.", fontsize=9.5, color=MUTED)
    save(fig, 8)


def p09():
    mon = pd.read_csv(D / "era5_monthly.csv", parse_dates=["month"]).set_index("month")
    yl = pd.read_csv(D / "dcs_national_yala.csv"); yl["y"] = yl.season_label.astype(str).str[:4].astype(int); yl = yl[(yl.y >= 2010) & (yl.y <= 2025)].copy()
    yl["rain"] = [mon.loc[f"{y}-03":f"{y}-08", "rain_mm"].sum() for y in yl.y]; yl["hs"] = yl.harv_000ha / yl.sown_000ha
    dt = lambda s, yr: s - np.polyval(np.polyfit(yr, s, 1), yr)
    x, yv = dt(yl.rain.values, yl.y.values), dt(yl.hs.values, yl.y.values); r = np.corrcoef(x, yv)[0, 1]
    rb = pd.read_csv(D / "rice_annual_balance.csv"); rb = rb[(rb.y >= 2010) & (rb.y <= 2025)]
    fx = pd.read_csv(WORK / "raw/pdf/Indicative Rate of the USD_LKR SPOT Exchange Rate.csv", parse_dates=["Date"]).set_index("Date")["Exchange Rate"].resample("MS").mean()
    fig = frame(9)
    cols = [(0.05, NAVY, SC.P09[0][0], SC.P09[0][1].format(r=r, n=len(yl)), SC.P09[0][2]),
            (0.37, MID, *SC.P09[1]), (0.69, BASE, *SC.P09[2])]
    for x0, c, h, cap, cav in cols:
        fig.add_artist(Rectangle((x0 - 0.005, 0.07), 0.29, 0.7, fc="white", ec=GRID, transform=fig.transFigure, zorder=0))
        fig.add_artist(Rectangle((x0 - 0.005, 0.764), 0.29, 0.006, fc=c, ec="none", transform=fig.transFigure))
        fig.text(x0 + 0.01, 0.725, h, fontsize=12, fontweight="semibold", color=INK, va="center")
        fig.text(x0 + 0.01, 0.17, cap, fontsize=10.5, va="center"); fig.text(x0 + 0.01, 0.105, cav, fontsize=9.5, color=MUTED, va="center")
    a = fig.add_axes([0.10, 0.26, 0.20, 0.4]); a.scatter(x, yv, s=36, color=ACC, zorder=3)
    b = np.polyfit(x, yv, 1); xs = np.linspace(x.min(), x.max(), 5); a.plot(xs, np.polyval(b, xs), color=BASE, lw=1.4)
    a.set_xlabel("Yala rain, detrended (mm)", fontsize=9); a.set_ylabel("harvested/sown, detrended", fontsize=9); style_axes(a); a.tick_params(labelsize=8)
    share = rb.fao_rice_imp_000t / (rb.rice_eq_000t + rb.fao_rice_imp_000t) * 100
    c2 = fig.add_axes([0.40, 0.26, 0.22, 0.4]); c2.bar(rb.y, share, color=EXPL, width=0.7); c2.set_ylabel("import share, %", fontsize=9); style_axes(c2); c2.tick_params(labelsize=8)
    d = fig.add_axes([0.72, 0.26, 0.22, 0.4]); d.plot(fx.index, fx.values, color=EXPL, lw=1.8); d.axvspan(pd.Timestamp("2022-01-01"), pd.Timestamp("2022-12-31"), color=GRID, lw=0)
    d.set_ylabel("USD/LKR", fontsize=9); style_axes(d); d.tick_params(labelsize=8)
    save(fig, 9)


def p10():
    import textwrap
    fig = frame(10)
    ax = blank(fig, (0.05, 0.1, 0.9, 0.72))
    cols = [(h, c, items) for (h, items), c in zip(SC.P10, (NAVY, CORAL, MID))]
    for i, (h, c, items) in enumerate(cols):
        x0 = i * 0.34
        ax.add_patch(Rectangle((x0, 0.0), 0.31, 1.0, fc="white", ec=GRID)); ax.add_patch(Rectangle((x0, 0.985), 0.31, 0.015, fc=c, ec="none"))
        ax.text(x0 + 0.015, 0.89, h, fontsize=13, fontweight="semibold", color=INK, va="center")
        y = 0.79
        for k, it in enumerate(items):
            t = "\n".join(textwrap.wrap(it, 36)); ax.text(x0 + 0.015, y, f"{k + 1}  " + t.replace("\n", "\n    "), fontsize=12, va="top", linespacing=1.4)
            y -= 0.05 + 0.052 * (t.count("\n") + 1)
    save(fig, 10)


PAGES = {i: globals()[f"p{i:02d}"] for i in range(1, 11)}

if __name__ == "__main__":
    for d in [OUT / f"{n:02d}_{s}" for n, s in SLUGS.items()]:
        (d / "assets").mkdir(parents=True, exist_ok=True)
    todo = [int(a) for a in sys.argv[1:]] or list(PAGES)
    for n in todo:
        PAGES[n]()
