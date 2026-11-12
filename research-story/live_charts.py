"""Interactive versions of the key storyboard charts (Plotly + Streamlit widgets).

Same source files as the static slides (research_audit outputs). Defaults show the frozen primary
specification; every other view is labelled exploratory. Nothing here recomputes statistics.
"""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

import build_figures as bf

NAVY, SOFT, CORAL, MID, GRID, PAPER, MUTED = bf.NAVY, bf.SOFT, bf.CORAL, bf.MID, bf.GRID, bf.PAPER, bf.MUTED
FONT = "Noto Sans, DejaVu Sans, sans-serif"
VEGS = bf.VEGS
CLASS_LABEL = {"supported": "supported", "exploratory": "exploratory only", "no evidence": "no reliable evidence", "worse": "rain does not help"}


def style(fig, height=520, legend=True):
    fig.update_layout(height=height, paper_bgcolor=PAPER, plot_bgcolor=PAPER, font=dict(family=FONT, color=NAVY, size=13),
                      margin=dict(l=10, r=10, t=30, b=10), showlegend=legend, legend=dict(orientation="h", y=-0.15),
                      hoverlabel=dict(bgcolor="white", font=dict(family=FONT, color=NAVY)))
    fig.update_xaxes(gridcolor=GRID, zerolinecolor=NAVY, linecolor=GRID, tickfont=dict(color=MUTED))
    fig.update_yaxes(gridcolor=GRID, zerolinecolor=NAVY, linecolor=GRID, tickfont=dict(color=MUTED))
    return fig


@st.cache_data
def load():
    ra = bf.RA
    comp = pd.read_csv(ra / "forecast_model_comparison_v2.csv")
    res = pd.read_csv(ra / "forecast_results_v2.csv", parse_dates=["origin", "target_month"])
    rw = pd.read_csv(bf.V2 / "rain_window_comparison.csv")
    ic = pd.read_csv(bf.V2 / "interval_coverage.csv")
    return comp, res, rw, ic, bf.prices(), bf.national_rain()


# ---------------- page 3: prices and rain ----------------
LAG = pd.read_csv(bf.OUT / "03_prices_and_rain/assets/lag_correlations.csv", index_col=0)


def page3():
    _, _, _, _, pr, (rain, anom) = load()
    v = st.selectbox("Vegetable", VEGS, key="p3_veg")
    s = pr[v].dropna().loc["2016":]
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.62, 0.38], vertical_spacing=0.06)
    fig.add_vrect(x0="2022-01-01", x1="2022-12-31", fillcolor=SOFT, opacity=0.35, line_width=0)
    fig.add_trace(go.Scatter(x=s.index, y=s.values, mode="lines", line=dict(color=NAVY, width=2), name=f"{v} price", hovertemplate="%{x|%b %Y}: %{y:.0f} LKR/kg<extra></extra>"), 1, 1)
    a = anom.loc["2016":]
    fig.add_trace(go.Bar(x=a.index, y=a.values, marker_color=[MID if x >= 0 else CORAL for x in a.fillna(0)], name="Rain anomaly (×100 mm)", hovertemplate="%{x|%b %Y}: %{y:+.2f} (×100 mm)<extra></extra>"), 2, 1)
    fig.update_yaxes(title_text="LKR/kg (nominal)", row=1, col=1); fig.update_yaxes(title_text="rain anomaly (×100 mm)", row=2, col=1)
    style(fig, 560)
    left, right = st.columns([3, 1], gap="large")
    left.plotly_chart(fig, width="stretch")
    hm = go.Figure(go.Heatmap(z=LAG.values, x=[f"lag {k}" for k in LAG.columns], y=VEGS, zmin=-0.6, zmax=0.6,
                              colorscale=[[0, CORAL], [0.5, "#ffffff"], [0.72, "#8cc0d6"], [1, NAVY]], showscale=False,
                              text=[[f"{x:+.2f}" for x in row] for row in LAG.values], texttemplate="%{text}", textfont=dict(size=12),
                              hovertemplate="%{y}, %{x}: r = %{z:+.2f}<extra></extra>", xgap=2, ygap=2))
    k = VEGS.index(v)
    hm.add_shape(type="rect", x0=-0.5, x1=3.5, y0=k - 0.5, y1=k + 0.5, line=dict(color=NAVY, width=2.5))
    hm.update_yaxes(autorange="reversed"); hm.update_xaxes(side="top")
    style(hm, 400, legend=False)
    hm.update_layout(margin=dict(l=10, r=10, t=40, b=10))
    right.plotly_chart(hm, width="stretch")
    right.caption("Correlation of price change with rain k months earlier (z-score rain anomaly, de-seasonalised price change), all seven vegetables; the selected one is outlined. Exploratory. The strip uses the mm/100 forecasting anomaly. Shaded: 2022.")


# ---------------- page 5: expanding-window forecasts ----------------
def page5():
    _, res, _, _, pr, _ = load()
    v = st.selectbox("Vegetable", VEGS, key="p5_veg")
    r = res[(res.market == "dambulla") & (res.price_agg == "mean") & (res.commodity == v)]
    ar, rn = r[r.model == "AR"].set_index("origin"), r[r.model == "AR+rain:nat"].set_index("origin")
    origins = list(ar.index)
    o = st.select_slider("Forecast origin (last month of data used)", options=origins, format_func=lambda d: d.strftime("%b %Y"), key="p5_origin")
    s = pr[v].dropna()
    t = ar.loc[o, "target_month"]
    fig = go.Figure()
    fig.add_vrect(x0=s.index[0], x1=o, fillcolor=SOFT, opacity=0.45, line_width=0, annotation_text="training window", annotation_position="top left")
    fig.add_trace(go.Scatter(x=s.index, y=s.values, mode="lines", line=dict(color=MUTED, width=1.6), name="Monthly mean price", hovertemplate="%{x|%b %Y}: %{y:.0f} LKR/kg<extra></extra>"))
    for name, row, col, sym in [("Actual", ar.loc[o], NAVY, "circle"), ("Price-only AR", ar.loc[o], "#8aa3b2", "diamond"), ("AR + rain", rn.loc[o], NAVY, "diamond-open")]:
        y = row["actual_lkr"] if name == "Actual" else row["pred_lkr"]
        fig.add_trace(go.Scatter(x=[t], y=[y], mode="markers", marker=dict(size=13, color=col, symbol=sym, line=dict(width=2, color=NAVY)), name=name, hovertemplate=f"{name}: %{{y:.0f}} LKR/kg<extra></extra>"))
    fig.update_xaxes(range=[s.index[0], pd.Timestamp("2026-12-01")]); fig.update_yaxes(title_text="LKR/kg (nominal)")
    style(fig, 460)
    st.plotly_chart(fig, width="stretch")
    a, b = ar.loc[o], rn.loc[o]
    c1, c2, c3 = st.columns(3)
    c1.metric(f"Actual, {t:%b %Y}", f"{a.actual_lkr:.0f} LKR/kg")
    c2.metric("Price-only AR forecast", f"{a.pred_lkr:.0f} LKR/kg"); c2.caption(f"error (forecast − actual): {a.pred_lkr - a.actual_lkr:+.0f}")
    c3.metric("AR + rain forecast", f"{b.pred_lkr:.0f} LKR/kg"); c3.caption(f"error (forecast − actual): {b.pred_lkr - b.actual_lkr:+.0f}")
    st.caption("Both models are refit at every origin using only data up to that month. One forecast says little; the evidence is the 62 forecasts together (page 6). Test window was seen in the pilot: exploratory.")


# ---------------- page 6: main result ----------------
SPECS = {"National rain, primary": "primary", "Non-overlapping window (check)": "nat_prior", "Dambulla rain box": "dam_incl", "Nuwara Eliya rain box": "nuw_incl"}


def page6():
    comp, _, rw, _, _, _ = load()
    choice = st.radio("Rainfall specification", list(SPECS), horizontal=True, key="p6_spec")
    key = SPECS[choice]
    if key == "primary":
        d = comp[(comp.market == "dambulla") & (comp.price_agg == "mean") & (comp.model == "AR+rain:nat")].set_index("commodity").loc[VEGS]
        b = d[["boot_p_b3", "boot_p_b6", "boot_p_b12"]]
    else:
        d = rw[rw.model == key].set_index("commodity").loc[VEGS]
        b = d[["boot_p_b3", "boot_p_b6", "boot_p_b12"]]
    cls = [bf.EVID_LABEL[e] for e in d.evidence]
    gain, p = d.rmse_gain_vs_AR_pct.values, d.cw_p_holm.values
    text = [f"{g:+.1f}%   Holm p {(f'{q:.4f}' if q < 0.01 else f'{q:.3f}')}   {CLASS_LABEL[c]}" for g, q, c in zip(gain, p, cls)]
    hover = [f"<b>{v}</b><br>RMSE gain {g:+.1f}%<br>Holm CW p {q:.4f}<br>bootstrap p (blocks 3/6/12): {bb[0]:.3f} / {bb[1]:.3f} / {bb[2]:.3f}<br>MAPE {m:.1f}%<br>{CLASS_LABEL[c]}"
             for v, g, q, bb, m, c in zip(VEGS, gain, p, b.values, d.mape_pct.values, cls)]
    fig = go.Figure(go.Bar(y=VEGS, x=gain, orientation="h", marker=dict(color=[bf.EVID_COL[c] for c in cls], line=dict(color=NAVY, width=[2 if c == "exploratory" else 0 for c in cls])),
                           hovertext=hover, hoverinfo="text"))
    # labels sit to the right of zero or of the bar, so negative bars never collide with the axis labels
    fig.add_trace(go.Scatter(x=[max(g, 0) + 0.6 for g in gain], y=VEGS, mode="text", text=text, textposition="middle right", hoverinfo="skip", showlegend=False, textfont=dict(color=NAVY, size=13)))
    fig.update_yaxes(autorange="reversed", tickfont=dict(size=14, color=NAVY)); fig.update_xaxes(title_text="RMSE reduction vs price-only AR (%)", range=[-4, 42])
    style(fig, 500, legend=False)
    st.plotly_chart(fig, width="stretch")
    if key == "primary":
        st.caption("Primary specification: Dambulla wholesale, national ERA5 rain, 62 forecasts per vegetable, Holm correction across seven vegetables. Bar = size of improvement; colour and label = strength of evidence.")
    else:
        st.warning("Secondary specification: exploratory. Holm is applied within each specification, not across them, so a significant cell here does not replace the primary result (for example Dambulla-box tomato with the non-overlapping window).")


# ---------------- page 7: robustness ----------------
def page7():
    comp, _, rw, _, _, _ = load()
    rwi = rw.set_index(["commodity", "model"])
    pet = comp[(comp.market == "pettah") & (comp.price_agg == "mean") & (comp.model == "AR+rain:nat")].set_index("commodity").loc[VEGS]
    med = comp[(comp.market == "dambulla") & (comp.price_agg == "median") & (comp.model == "AR+rain:nat")].set_index("commodity").loc[VEGS]
    g = lambda m: [rwi.loc[(v, m), "rmse_gain_vs_AR_pct"] for v in VEGS]
    marks = {"Primary: national rain, A3 = t−2…t": (g("nat_incl"), NAVY, "circle", 15), "Non-overlapping A3 = t−3…t−1": (g("nat_prior"), "#5b9ab7", "circle", 10),
             "Dambulla rain box": (g("dam_incl"), MID, "square", 10), "Nuwara Eliya rain box": (g("nuw_incl"), "#7a8f9c", "triangle-up", 11),
             "Pettah market": (list(pet.rmse_gain_vs_AR_pct.values), "#1d5878", "diamond", 10), "Monthly median price": (list(med.rmse_gain_vs_AR_pct.values), "#8aa3b2", "x", 10)}
    pick = st.multiselect("Specifications shown", list(marks), default=list(marks), key="p7_specs")
    fig = go.Figure()
    for name in pick:
        vals, col, sym, size = marks[name]
        fig.add_trace(go.Scatter(x=vals, y=VEGS, mode="markers", name=name, marker=dict(color=col, symbol=sym, size=size, line=dict(color="white", width=1)),
                                 hovertemplate="%{y}: %{x:+.1f}%<extra>" + name + "</extra>"))
    fig.update_yaxes(autorange="reversed", tickfont=dict(size=14, color=NAVY)); fig.update_xaxes(title_text="RMSE reduction vs price-only AR (%)", range=[-5, 25])
    fig.add_vline(x=0, line_color=NAVY)
    style(fig, 520)
    st.plotly_chart(fig, width="stretch")
    st.caption("Each marker is one specification's point estimate. Only the national primary has a Holm family of seven tests behind it. One tomato cell (Dambulla box, non-overlapping window) reaches Holm p = 0.036; it is one of six specifications and is not promoted.")


# ---------------- page 8: accuracy ----------------
def page8():
    comp, res, _, ic, _, _ = load()
    v = st.selectbox("Vegetable", VEGS, key="p8_veg")
    r = res[(res.market == "dambulla") & (res.price_agg == "mean") & (res.commodity == v)]
    ar, rn = r[r.model == "AR"].set_index("target_month"), r[r.model == "AR+rain:nat"].set_index("target_month")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=rn.index, y=rn.hi80_lkr, line=dict(width=0), showlegend=False, hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=rn.index, y=rn.lo80_lkr, fill="tonexty", fillcolor="rgba(182,223,237,0.55)", line=dict(width=0), name="AR+rain 80% band", hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=ar.index, y=ar.actual_lkr, line=dict(color=NAVY, width=2.4), name="Actual", hovertemplate="%{x|%b %Y}: %{y:.0f}<extra>Actual</extra>"))
    fig.add_trace(go.Scatter(x=ar.index, y=ar.pred_lkr, line=dict(color="#8aa3b2", width=1.8), name="Price-only AR", hovertemplate="%{x|%b %Y}: %{y:.0f}<extra>AR</extra>"))
    fig.add_trace(go.Scatter(x=rn.index, y=rn.pred_lkr, line=dict(color=MID, width=2.2, dash="dot"), name="AR + rain", hovertemplate="%{x|%b %Y}: %{y:.0f}<extra>AR + rain</extra>"))
    fig.update_yaxes(title_text="LKR/kg"); fig.update_xaxes(rangeslider=dict(visible=True, thickness=0.08))
    style(fig, 540)
    st.plotly_chart(fig, width="stretch")
    m = comp[(comp.market == "dambulla") & (comp.price_agg == "mean") & (comp.model == "AR+rain:nat") & (comp.commodity == v)].iloc[0]
    cov = ic[(ic.model == "nat_incl") & (ic.commodity == v)].iloc[0].coverage
    c1, c2, c3 = st.columns(3)
    c1.metric("MAPE, AR + rain", f"{m.mape_pct:.1f}%"); c2.metric("80% band coverage", f"{cov:.2f}"); c2.caption("nominal 0.80"); c3.metric("RMSE gain vs AR", f"{m.rmse_gain_vs_AR_pct:+.1f}%")
    st.caption("Better relative RMSE does not mean accurate forecasts: errors stay large and the empirical bands under-cover. Drag the slider under the chart to zoom.")


LIVE = {3: page3, 5: page5, 6: page6, 7: page7, 8: page8}
