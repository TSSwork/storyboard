"""The four dashboard pages. Plain words on screen; the method lives in the speaking guides (story_pages/).

Every number comes from story.metrics or data/ at run time.
"""
import html

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from story import common as C
from story import metrics as M
from story import ui

esc = html.escape
NAVY, SOFT, CORAL, PAPER, GRID, MUTED, RAIN = C.NAVY, C.SOFT, C.CORAL, C.PAPER, C.GRID, C.MUTED, C.RAIN
SAGE, SLATE = "#5e9e83", "#8aa3b2"
FONT = "Noto Sans, DejaVu Sans, sans-serif"
CFG = {"displayModeBar": False}


def style(fig, height=440, legend=True):
    fig.update_layout(height=height, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family=FONT, color=NAVY, size=13),
                      margin=dict(l=8, r=8, t=24, b=8), showlegend=legend, legend=dict(orientation="h", y=1.08, x=0),
                      hoverlabel=dict(bgcolor="white", font=dict(family=FONT, color=NAVY)), hovermode="x unified")
    fig.update_xaxes(gridcolor=GRID, linecolor=GRID, tickfont=dict(color=MUTED), showgrid=False)
    fig.update_yaxes(gridcolor=GRID, linecolor=GRID, tickfont=dict(color=MUTED), zeroline=False)
    return fig


def header(n, act, title, lede):
    st.markdown(f'<div class="s-label"><span class="sq"></span>{n:02d} · {esc(act)}</div><h1 class="s-h1">{esc(title)}</h1>'
                f'<p class="lede">{esc(lede)}</p>', unsafe_allow_html=True)


def footer(src):
    st.markdown(f'<div class="s-foot"><span>Source: {esc(src)}</span><span>Exploratory · not proof of cause</span></div>', unsafe_allow_html=True)


def pick_veg(key):
    return st.segmented_control("Vegetable", C.VEGS, default="Cabbage", key=key, label_visibility="collapsed") or "Cabbage"


def rs(x):
    return f"Rs {x:,.0f}"


# ---------------- 1 ----------------
def p1():
    header(1, ACT[0], "Vegetable prices swing wildly",
           "Wholesale prices at Dambulla, a major vegetable wholesale market. Pick a vegetable and see how far its price moves.")
    veg = pick_veg("p1_veg")
    k = M.price_kpis(veg)
    jump_word = "rise" if k["jump_pct"] > 0 else "fall"
    ui.kpi_row([
        ui.kpi("tag", "Cheapest month", rs(k["low"]), k["low_month"].strftime("%b %Y"), "flat", "/kg"),
        ui.kpi("trend_up", "Most expensive month", rs(k["high"]), k["high_month"].strftime("%b %Y"), "bad", "/kg"),
        ui.kpi("bolt", "Biggest one-month move", f"{abs(k['jump_pct']):.0f}%", f"{jump_word}, {k['jump_month'].strftime('%b %Y')}", "soft"),
        ui.kpi("wave", "Months with a swing over 20%", f"{k['big_move_share'] * 10:.0f} in 10", f"{k['high'] / k['low']:.0f}× gap, cheapest to dearest", "soft"),
    ])
    show_rain = st.toggle("Show rainfall underneath", value=True, key="p1_rain")
    p = M._prices()[veg].dropna()
    rain, _ = C.national_rain()
    rain = rain.loc[p.index.min():].dropna()
    rows = 2 if show_rain else 1
    fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, row_heights=[0.65, 0.35] if show_rain else [1], vertical_spacing=0.06)
    fig.add_trace(go.Scatter(x=p.index, y=p.values, mode="lines", line=dict(color=NAVY, width=2.2), name=f"{veg} price",
                             fill="tozeroy", fillcolor="rgba(182,223,237,.25)", hovertemplate="Rs %{y:,.0f}/kg<extra></extra>"), 1, 1)
    fig.update_yaxes(title_text="Rs per kg", row=1, col=1)
    if show_rain:
        fig.add_trace(go.Bar(x=rain.index, y=rain.values, marker_color=RAIN, name="Rain across the island", hovertemplate="%{y:.0f} mm<extra></extra>"), 2, 1)
        fig.update_yaxes(title_text="Rain, mm", row=2, col=1)
    style(fig, 470)
    st.plotly_chart(fig, width="stretch", config=CFG)
    st.markdown('<p class="hook">So, can last month\'s rain warn us about next month\'s price?</p>', unsafe_allow_html=True)
    footer("Central Bank of Sri Lanka daily wholesale prices (monthly average); ERA5-Land rainfall")


# ---------------- 2 ----------------
def p2():
    header(2, ACT[1], "Does rain help? Try it",
           "Each month we made two forecasts of next month's price: one from past prices only, one that also knew the rain. "
           "Change the settings and see which one missed by less.")
    veg = pick_veg("p2_veg")
    a, b = st.columns(2)
    region = M.REGIONS[a.radio("Where rain is measured", list(M.REGIONS), horizontal=True, key="p2_region")]
    market = M.MARKETS[b.radio("Market", list(M.MARKETS), horizontal=True, key="p2_market")]
    k = M.rain_kpis(veg, region, market)
    g = k["gain_pct"]
    change = f"{abs(g):.0f}% {'smaller' if g >= 0 else 'larger'} overall error" if abs(g) >= 0.5 else "about the same error"
    ui.kpi_row([
        ui.kpi("tag", "Typical miss, prices only", rs(k["miss_without"]), "past prices alone", "flat", "/kg"),
        ui.kpi("rain", "Typical miss, adding rain", rs(k["miss_with"]), change, k["tone"], "/kg"),
        ui.kpi("check", "Verdict", k["label"], {"good": "survives strict checks", "soft": "looks better, not proven",
                                                "flat": "too small to trust", "bad": "rain adds nothing"}[k["tone"]], k["tone"]),
        ui.kpi("target", "Price landed inside our range", f"{k['inside_with']:.0f} in 10", f"prices only: {k['inside_without']:.0f} in 10 · aim: 8", "soft"),
    ])
    f = M.forecast_path(veg, region, market)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=list(f.target_month) + list(f.target_month[::-1]), y=list(f.hi) + list(f.lo[::-1]), fill="toself",
                             fillcolor="rgba(182,223,237,.38)", line=dict(width=0), name="Likely range (with rain)", hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=f.target_month, y=f.without, mode="lines", line=dict(color=SLATE, width=1.8, dash="dot"), name="Forecast, prices only",
                             hovertemplate="prices only: Rs %{y:,.0f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=f.target_month, y=f["with"], mode="lines", line=dict(color=SAGE, width=2.2), name="Forecast, adding rain",
                             hovertemplate="with rain: Rs %{y:,.0f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=f.target_month, y=f.actual, mode="lines+markers", line=dict(color=NAVY, width=2.2), marker=dict(size=4),
                             name="Actual price", hovertemplate="actual: Rs %{y:,.0f}<extra></extra>"))
    fig.update_yaxes(title_text="Rs per kg")
    style(fig, 420)
    st.plotly_chart(fig, width="stretch", config=CFG)
    st.markdown('<div class="s-label" style="margin-top:.2rem">All seven vegetables, with these settings</div>', unsafe_allow_html=True)
    ui.verdict_strip(M.verdicts(region, market), veg)
    st.markdown(f'<p class="fine">{k["n"]} real month-ahead forecasts, {f.target_month.min():%b %Y} – {f.target_month.max():%b %Y}. '
                'Rain is only ever the rain already observed, never future rain.</p>', unsafe_allow_html=True)
    footer("forecast_model_comparison_v2.csv, forecast_results_v2.csv (stored backtest results; nothing re-estimated here)")


# ---------------- 3 ----------------
@st.cache_data
def p3_data():
    mon = pd.read_csv(C.DATA / "era5_monthly.csv", parse_dates=["month"]).set_index("month")
    yl = pd.read_csv(C.DATA / "dcs_national_yala.csv"); yl["y"] = yl.season_label.astype(str).str[:4].astype(int); yl = yl[(yl.y >= 2010) & (yl.y <= 2025)].copy()
    yl["rain"] = [mon.loc[f"{y}-03":f"{y}-08", "rain_mm"].sum() for y in yl.y]; yl["hs"] = yl.harv_000ha / yl.sown_000ha
    dt = lambda s, yr: s - np.polyval(np.polyfit(yr, s, 1), yr)
    x, y = dt(yl.rain.values, yl.y.values), dt(yl.hs.values, yl.y.values)
    rb = pd.read_csv(C.DATA / "rice_annual_balance.csv"); rb = rb[(rb.y >= 2010) & (rb.y <= 2025)]
    share = pd.Series((rb.fao_rice_imp_000t / (rb.rice_eq_000t + rb.fao_rice_imp_000t) * 100).values, index=rb.y.values).dropna()
    fx = pd.read_csv(C.DATA / "usd_lkr_spot_rate.csv", parse_dates=["Date"]).set_index("Date")["Exchange Rate"].resample("MS").mean().dropna()
    return x, y, float(np.corrcoef(x, y)[0, 1]), len(yl), share, fx


def p3():
    header(3, ACT[2], "Rain is only one piece",
           "Food prices in Sri Lanka also depend on the rice harvest, on imports and on the rupee. Each is shown on its own; they are not combined into one score.")
    x, y, r, n, share, fx = p3_data()
    fx0 = fx.loc["2021-01"].iloc[0]
    ui.kpi_row([
        ui.kpi("leaf", "Wetter growing seasons, better paddy harvests", f"r = {r:+.2f}", f"{n} seasons · a link, not proof", "soft"),
        ui.kpi("globe", "Rice bought from abroad, peak year", f"{share.max():.0f}%", f"of supply in {share.idxmax()} · {share.iloc[-1]:.0f}% in {share.index[-1]}", "flat"),
        ui.kpi("coins", "Rupee price of one US dollar", rs(fx.iloc[-1]), f"+{(fx.iloc[-1] / fx0 - 1) * 100:.0f}% since Jan 2021", "bad"),
    ])
    cols = st.columns(3, gap="medium")
    f1 = go.Figure(go.Scatter(x=x, y=y, mode="markers", marker=dict(color=NAVY, size=9, opacity=.85), hovertemplate="rain %{x:+.0f} mm vs usual<extra></extra>"))
    b = np.polyfit(x, y, 1); xs = np.linspace(x.min(), x.max(), 5)
    f1.add_trace(go.Scatter(x=xs, y=np.polyval(b, xs), mode="lines", line=dict(color=SAGE, width=2), hoverinfo="skip"))
    f1.update_xaxes(title_text="season rain vs usual (mm)"); f1.update_yaxes(title_text="share of sown land harvested, vs usual")
    f2 = go.Figure(go.Bar(x=share.index, y=share.values, marker_color=[CORAL if v == share.max() else SOFT for v in share.values],
                          hovertemplate="%{x}: %{y:.1f}% of supply<extra></extra>"))
    f2.update_yaxes(title_text="imported share of rice, %")
    f3 = go.Figure(go.Scatter(x=fx.index, y=fx.values, mode="lines", line=dict(color=NAVY, width=2), hovertemplate="%{x|%b %Y}: Rs %{y:.0f}<extra></extra>"))
    f3.add_vrect(x0="2022-01-01", x1="2022-12-31", fillcolor=SOFT, opacity=.45, line_width=0, annotation_text="2022 crisis", annotation_font_color=MUTED)
    f3.update_yaxes(title_text="Rs per US dollar")
    titles = ["Weather and the rice harvest", "Rice imports", "The exchange rate"]
    notes = ["Short series with policy shocks: an association only.", "Paddy-to-rice conversion (0.67) is an assumption.", "Shows the rupee's fall; no price pass-through is estimated."]
    for col, fg, t, nt in zip(cols, (f1, f2, f3), titles, notes):
        style(fg, 320, legend=False)
        with col, st.container(border=True):
            st.markdown(f'<div class="s-card-h">{esc(t)}</div>', unsafe_allow_html=True)
            st.plotly_chart(fg, width="stretch", config=CFG)
            st.markdown(f'<p class="fine">{esc(nt)}</p>', unsafe_allow_html=True)
    footer("ERA5-Land; Department of Census and Statistics paddy; FAOSTAT; CBSL exchange rates. Context only; none feeds the forecasts.")


# ---------------- 4 ----------------
def p4():
    header(4, ACT[2], "What did we learn?", "Three pages of playing with the data. Here is the short version.")
    if not st.session_state.get("revealed"):
        st.markdown(f'<div class="reveal-wrap"><div><div class="reveal-ico">{ui.ICON["sparkle"]}</div>'
                    '<p class="reveal-q">Ready for the answer?</p><p class="reveal-sub">One click, three findings.</p></div></div>',
                    unsafe_allow_html=True)
        if st.button("Wanna see the conclusion?", type="primary", key="reveal_btn", icon=":material/celebration:"):
            st.session_state.revealed = True
            st.session_state.confetti = True
            st.rerun()
        return
    if st.session_state.pop("confetti", False):
        ui.confetti()
    nat = {v: M.rain_kpis(v, "nat", "dambulla") for v in C.VEGS}
    helped = [v for v in C.VEGS if nat[v]["label"] == "Clear help"]
    gains = [nat[v]["gain_pct"] for v in helped]
    rest = [v for v in C.VEGS if v not in helped]
    miss = np.median([nat[v]["mape_with"] for v in C.VEGS])
    cards = [
        ("check", "good", f"{min(gains):.0f}–{max(gains):.0f}%", "smaller errors", "Rain helps some vegetables",
         f"For {', '.join(v.lower() for v in helped)}, knowing last month's rain made next month's forecast clearly better."),
        ("target", "bad", f"~{miss:.0f}%", "typical miss", "…but not all, and not precisely",
         f"{', '.join(v.lower() for v in rest).capitalize()} showed no gain we can trust. Even the best forecasts still miss by about a quarter of the price."),
        ("sparkle", "soft", "Next", "test on new months", "What it means",
         "This is a research finding about where rain carries information, not a price app. Next: check it on months not yet published, and use rain from the farms themselves."),
    ]
    html_cards = "".join(f'<div class="card"><span class="kpi-ico" style="background:var(--tint)">{ui.ICON[i]}</span>'
                         f'<div class="big">{esc(big)}<small>{esc(sm)}</small></div><h3>{esc(h)}</h3><p>{esc(t)}</p></div>'
                         for i, tone, big, sm, h, t in cards)
    st.markdown(f'<div class="take">{html_cards}</div>', unsafe_allow_html=True)
    st.button("Hide again", type="tertiary", key="hide_btn", on_click=lambda: st.session_state.update(revealed=False))
    footer("Stored results, Dambulla market, rain across the island")


ACT = ["The problem", "The test", "The bigger picture"]
# (sidebar title, material icon, act, render)
PAGES = [
    ("Prices swing wildly", ":material/show_chart:", ACT[0], p1),
    ("Does rain help? Try it", ":material/science:", ACT[1], p2),
    ("Rain is only one piece", ":material/public:", ACT[2], p3),
    ("What did we learn?", ":material/celebration:", ACT[2], p4),
]
