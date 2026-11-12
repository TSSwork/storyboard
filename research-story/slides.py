"""The ten storyboard slides as native Streamlit + Plotly + HTML (vector, sharp at any size).

Text comes from slide_copy.py (shared with the PNG export). Data comes from research_audit/ outputs.
"""
import html
import json

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

import build_figures as bf
import live_charts as lc
import slide_copy as SC

NAVY, SOFT, CORAL, MID, BASE, TINT, GRID, MUTED, RAIN = bf.NAVY, bf.SOFT, bf.CORAL, bf.MID, bf.BASE, bf.TINT, bf.GRID, bf.MUTED, bf.RAIN
esc = html.escape


def lines(t):
    """First line of a text block bold, the rest below it."""
    parts = t.split("\n")
    return f"<b>{esc(parts[0])}</b>" + ("<br>" + " ".join(esc(x) for x in parts[1:]) if len(parts) > 1 else "")


def flat(t):
    return " ".join(esc(x) for x in t.split("\n"))


def header(n):
    headline, _, sub = SC.HEAD[n]
    st.markdown(
        f'<div class="s-label"><span class="sq"></span>{n:02d} · {esc(SC.ACTS[n])}</div>'
        f'<h1 class="s-h1">{esc(headline)}</h1>' + (f'<p class="s-sub">{esc(sub)}</p>' if sub else ""),
        unsafe_allow_html=True,
    )


def footer(n):
    st.markdown(f'<div class="s-foot"><span>Source: {esc(SC.HEAD[n][1])}</span><span>Exploratory · not causal</span></div>', unsafe_allow_html=True)


def cards(items, colors):
    """Equal-height cards in one grid, each with a thin colour rule, heading and body. items = [(heading, body_html)]."""
    inner = "".join(f'<div class="s-card" style="border-top:3px solid {c}"><div class="s-card-h">{esc(h)}</div>{body}</div>' for (h, body), c in zip(items, colors))
    st.markdown(f'<div class="s-cards" style="grid-template-columns:repeat({len(items)},1fr)">{inner}</div>', unsafe_allow_html=True)


# ---------------- 1 ----------------
def s1():
    _, _, _, _, pr, (rain, _) = lc.load()
    p = pr["Cabbage"].dropna().loc["2016":]; r = rain.loc["2016":].dropna()
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.6, 0.4], vertical_spacing=0.07)
    fig.add_trace(go.Scatter(x=p.index, y=p.values, mode="lines", line=dict(color=NAVY, width=2.4), name="Cabbage price", hovertemplate="%{x|%b %Y}: %{y:.0f} LKR/kg<extra></extra>"), 1, 1)
    fig.add_trace(go.Bar(x=r.index, y=r.values, marker_color=RAIN, name="National rain", hovertemplate="%{x|%b %Y}: %{y:.0f} mm<extra></extra>"), 2, 1)
    fig.update_yaxes(title_text="Cabbage, LKR/kg (nominal)", row=1, col=1); fig.update_yaxes(title_text="National rain, mm/month", row=2, col=1)
    lc.style(fig, 560)
    st.plotly_chart(fig, width="stretch")
    st.caption("Dambulla wholesale price and observed national rainfall, 2016–2026")


# ---------------- 2 ----------------
def s2():
    g = json.load(open(bf.WORK / "raw/chirp/boundaries/countries.geojson"))
    f = [x for x in g["features"] if x["properties"].get("ISO3166-1-Alpha-3") == "LKA"][0]
    fig = go.Figure()
    for poly in f["geometry"]["coordinates"]:
        for ring in poly:
            xs, ys = zip(*ring)
            fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", fill="toself", fillcolor=TINT, line=dict(color=BASE, width=1), hoverinfo="skip", showlegend=False))
    for name, (x, y, c) in {"Dambulla": (80.65, 7.86, NAVY), "Nuwara Eliya": (80.77, 6.97, MID)}.items():
        fig.add_shape(type="rect", x0=x - 0.3, x1=x + 0.3, y0=y - 0.3, y1=y + 0.3, line=dict(color=c, width=2, dash="dash"))
        fig.add_trace(go.Scatter(x=[x], y=[y], mode="markers+text", text=[f"  {name}"], textposition="middle right", marker=dict(color=c, size=10),
                                 textfont=dict(color=c, size=13), hovertemplate=f"{name} rainfall box (±0.3°, 36 land cells)<extra></extra>", showlegend=False))
    fig.add_trace(go.Scatter(x=[79.85], y=[6.94], mode="markers+text", text=["  Pettah"], textposition="middle right", marker=dict(color=NAVY, size=10, symbol="square"),
                             textfont=dict(color=NAVY, size=13), hovertemplate="Pettah wholesale market (robustness check)<extra></extra>", showlegend=False))
    fig.update_xaxes(visible=False); fig.update_yaxes(visible=False, scaleanchor="x", scaleratio=1)
    lc.style(fig, 600, legend=False)
    left, right = st.columns([2, 3], gap="large")
    left.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    left.caption(SC.P02_MAPNOTE)
    rows = "".join(f'<div class="s-k">{esc(k)}</div><div class="s-v">{esc(v)}</div>' for k, v in SC.P02_ITEMS)
    flow = "".join(
        [f'<div class="s-box">{esc(SC.P02_FLOW[0])}</div><div class="s-arr">→</div><div class="s-box">{esc(SC.P02_FLOW[1])}</div><div class="s-arr">→</div><div class="s-box dark">{esc(SC.P02_FLOW[2])}</div>'])
    right.markdown(f'<div class="s-facts">{rows}</div><div class="s-flow">{flow}</div><p class="s-note">{esc(SC.P02_NOTE)}</p>', unsafe_allow_html=True)


# ---------------- 4 ----------------
def s4():
    chips = "".join(f'<span class="s-chip{" on" if l == "t" else ""}">{l}</span>' for l in ["t−3", "t−2", "t−1", "t"])
    bullets = "".join(f"<li>{esc(b)}</li>" for b in SC.P04_BULLETS)
    st.markdown(
        f'<div class="s-diagram"><div class="s-stack"><div class="s-mc">{lines(SC.P04_A)}</div><div class="s-mc hi">{lines(SC.P04_B)}</div></div>'
        f'<div class="s-arr big">→</div><div class="s-mc mid">{lines(SC.P04_FORECAST)}</div><div class="s-arr big">→</div><div class="s-mc">{lines(SC.P04_COMPARE)}</div></div>'
        f'<div class="s-two"><div><div class="s-chips">{chips}</div><p class="s-note">{"<br>".join(esc(x) for x in SC.P04_WINDOW.split(chr(10)))}</p></div>'
        f'<ul class="s-list">{bullets}</ul></div>',
        unsafe_allow_html=True,
    )


# ---------------- 5 ----------------
def s5():
    cards([(h, f"<p>{flat(t)}</p>") for h, t in SC.P05_CARDS], [NAVY] * 3)
    lc.page5()
    a, b = st.columns(2)
    a.caption(SC.P05_TL1.replace("\n", " · ")); b.caption(SC.P05_TL2.replace("\n", " "))


# ---------------- 9 ----------------
@st.cache_data
def p9_data():
    mon = pd.read_csv(bf.D / "era5_monthly.csv", parse_dates=["month"]).set_index("month")
    yl = pd.read_csv(bf.D / "dcs_national_yala.csv"); yl["y"] = yl.season_label.astype(str).str[:4].astype(int); yl = yl[(yl.y >= 2010) & (yl.y <= 2025)].copy()
    yl["rain"] = [mon.loc[f"{y}-03":f"{y}-08", "rain_mm"].sum() for y in yl.y]; yl["hs"] = yl.harv_000ha / yl.sown_000ha
    dt = lambda s, yr: s - np.polyval(np.polyfit(yr, s, 1), yr)
    x, y = dt(yl.rain.values, yl.y.values), dt(yl.hs.values, yl.y.values)
    rb = pd.read_csv(bf.D / "rice_annual_balance.csv"); rb = rb[(rb.y >= 2010) & (rb.y <= 2025)]
    share = (rb.fao_rice_imp_000t / (rb.rice_eq_000t + rb.fao_rice_imp_000t) * 100)
    fx = pd.read_csv(bf.WORK / "raw/pdf/Indicative Rate of the USD_LKR SPOT Exchange Rate.csv", parse_dates=["Date"]).set_index("Date")["Exchange Rate"].resample("MS").mean()
    return x, y, float(np.corrcoef(x, y)[0, 1]), len(yl), rb.y.values, share.values, fx


def s9():
    x, y, r, n, yrs, share, fx = p9_data()
    cols = st.columns(3, gap="medium")
    colors = [NAVY, MID, BASE]
    figs = []
    f1 = go.Figure(go.Scatter(x=x, y=y, mode="markers", marker=dict(color=NAVY, size=9), hovertemplate="rain %{x:+.0f} mm, harvested/sown %{y:+.3f}<extra></extra>", name="Years"))
    b = np.polyfit(x, y, 1); xs = np.linspace(x.min(), x.max(), 5)
    f1.add_trace(go.Scatter(x=xs, y=np.polyval(b, xs), mode="lines", line=dict(color=BASE, width=2), hoverinfo="skip"))
    f1.update_xaxes(title_text="Yala rain, detrended (mm)"); f1.update_yaxes(title_text="harvested/sown, detrended")
    f2 = go.Figure(go.Bar(x=yrs, y=share, marker_color=MID, hovertemplate="%{x}: %{y:.1f}% of supply<extra></extra>")); f2.update_yaxes(title_text="import share, %")
    f3 = go.Figure(go.Scatter(x=fx.index, y=fx.values, mode="lines", line=dict(color=MID, width=2.2), hovertemplate="%{x|%b %Y}: %{y:.0f} LKR per USD<extra></extra>"))
    f3.add_vrect(x0="2022-01-01", x1="2022-12-31", fillcolor=SOFT, opacity=0.5, line_width=0); f3.update_yaxes(title_text="USD/LKR")
    for fg in (f1, f2, f3):
        lc.style(fg, 420, legend=False); fg.update_layout(showlegend=False)
    for col, fg, c, (title, cap, cav) in zip(cols, (f1, f2, f3), colors, SC.P09):
        with col:
            st.markdown(f'<div class="s-card-top" style="border-top:3px solid {c}"><div class="s-card-h">{esc(title)}</div></div>', unsafe_allow_html=True)
            st.plotly_chart(fg, width="stretch", config={"displayModeBar": False})
            st.markdown(f'<div class="s-capt">{esc(cap.format(r=r, n=n))}</div><div class="s-cav">{flat(cav)}</div>', unsafe_allow_html=True)


# ---------------- 10 ----------------
def s10():
    items = [(h, "<ol>" + "".join(f"<li>{esc(i)}</li>" for i in its) + "</ol>") for h, its in SC.P10]
    cards(items, [NAVY, CORAL, MID])


BODY = {1: s1, 2: s2, 3: lc.page3, 4: s4, 5: s5, 6: lc.page6, 7: lc.page7, 8: lc.page8, 9: s9, 10: s10}


def render(n):
    header(n)
    BODY[n]()
    footer(n)
