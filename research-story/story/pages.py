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
from story import rainmap as R
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
        ui.kpi("tag", "Cheapest month", rs(k["low"]), k["low_month"].strftime("%b %Y"), "flat", "/kg", color="blue"),
        ui.kpi("trend_up", "Most expensive month", rs(k["high"]), k["high_month"].strftime("%b %Y"), "bad", "/kg", color="pink"),
        ui.kpi("bolt", "Biggest one-month move", f"{abs(k['jump_pct']):.0f}%", f"{jump_word}, {k['jump_month'].strftime('%b %Y')}", "soft", color="orange"),
        ui.kpi("wave", "Months with a swing over 20%", f"{k['big_move_share'] * 10:.0f} in 10", f"{k['high'] / k['low']:.0f}× gap, cheapest to dearest", "soft", color="purple"),
    ])
    left, right = st.columns([3, 2], gap="large")
    with left:
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
        style(fig, 560)
        st.plotly_chart(fig, width="stretch", config=CFG)
    with right:
        rain_map()
    st.markdown('<p class="hook">So, can last month\'s rain warn us about next month\'s price?</p>', unsafe_allow_html=True)
    footer("Central Bank of Sri Lanka daily wholesale prices (monthly average); ERA5-Land rainfall")


MAP_SCALE = [[0, "#f6fafc"], [0.15, "#dcefF6"], [0.4, "#8cc0d6"], [0.7, "#2f7292"], [1, "#002941"]]
MAP_MAX = 600   # mm; fixed so months can be compared (about the 98th percentile of all cell-months)
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


@st.cache_data
def island_outline():
    import json
    g = json.load(open(C.DATA / "sri_lanka_boundary.geojson"))
    f = [x for x in g["features"] if x["properties"].get("ISO3166-1-Alpha-3") == "LKA"][0]
    xs, ys = [], []
    for poly in f["geometry"]["coordinates"]:
        for ring in poly:
            xs += [p[0] for p in ring] + [None]; ys += [p[1] for p in ring] + [None]
    return xs, ys


def rain_map():
    view = st.radio("Map", ["A real month", "Typical month"], horizontal=True, key="p1_mapview", label_visibility="collapsed")
    if view == "A real month":
        ms = R.months()
        m = st.select_slider("Month", options=ms, value=ms[-1], format_func=lambda d: pd.Timestamp(d).strftime("%b %Y"),
                             key="p1_month", label_visibility="collapsed")
        df, label = R.month_map(m), pd.Timestamp(m).strftime("%B %Y")
    else:
        k = st.select_slider("Month", options=list(range(1, 13)), value=5, format_func=lambda i: MONTHS[i - 1],
                             key="p1_cal", label_visibility="collapsed")
        df, label = R.typical_map(k), f"a typical {MONTHS[k - 1]} (average {R.months()[0].year}–{R.months()[-1].year})"
    z = df.pivot(index="lat", columns="lon", values="rain_mm")
    fig = go.Figure(go.Heatmap(x=z.columns, y=z.index, z=z.values, zmin=0, zmax=MAP_MAX, colorscale=MAP_SCALE, hoverongaps=False,
                               colorbar=dict(title=dict(text="mm", side="top"), thickness=10, len=0.6, outlinewidth=0, tickfont=dict(color=MUTED)),
                               hovertemplate="%{z:.0f} mm<extra></extra>"))
    xs, ys = island_outline()
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=NAVY, width=1), hoverinfo="skip", showlegend=False))
    for name, (la, lo) in R.BOXES.items():
        fig.add_shape(type="rect", x0=lo - R.HALF, x1=lo + R.HALF, y0=la - R.HALF, y1=la + R.HALF, line=dict(color=CORAL, width=1.6, dash="dot"))
        fig.add_annotation(x=lo + R.HALF, y=la + R.HALF, text=name, showarrow=False, xanchor="left", yanchor="bottom", font=dict(color=NAVY, size=11))
    fig.add_trace(go.Scatter(x=[79.85], y=[6.94], mode="markers", marker=dict(color="white", size=8, symbol="square", line=dict(color=NAVY, width=1.5)),
                             hoverinfo="skip", showlegend=False))
    fig.add_annotation(x=79.85, y=6.94, text="Colombo (Pettah)", showarrow=False, xanchor="left", yanchor="top", yshift=-7, font=dict(color=NAVY, size=11),
                       bgcolor="rgba(255,255,255,.85)", borderpad=2)
    for a in fig.layout.annotations[:-1]:
        a.update(bgcolor="rgba(255,255,255,.85)", borderpad=2)
    fig.update_xaxes(visible=False, range=[79.4, 82.1]); fig.update_yaxes(visible=False, scaleanchor="x", scaleratio=1, range=[5.8, 9.95])
    style(fig, 470, legend=False); fig.update_layout(hovermode="closest")
    st.plotly_chart(fig, width="stretch", config=CFG)
    st.markdown(f'<p class="fine">Rain in {esc(label)}. Darker blue = more rain. '
                'Dotted squares: the two areas whose rain we also tested on page 3.</p>', unsafe_allow_html=True)


# ---------------- pattern ----------------
LAGS = {0: "Same month", 1: "1 month earlier", 2: "2 months earlier", 3: "3 months earlier"}


def p_pattern():
    header(2, ACT[0], "Spot the pattern yourself",
           "Does a wetter-than-usual month come before a price jump? Every dot is one month. "
           "Pick a vegetable and how long the rain takes to show up in the price.")
    veg = pick_veg("pp_veg")
    lag = st.select_slider("Rain from", options=list(LAGS), value=1, format_func=LAGS.get, key="pp_lag")
    d = M.pattern(veg, lag)
    r = M.pattern_r(veg, lag)
    word = M.strength_word(r)
    rs_all = {L: M.pattern_r(veg, L) for L in LAGS}
    best = max(rs_all, key=lambda L: abs(rs_all[L]))
    ui.kpi_row([
        ui.kpi("wave", "Link between rain and price", word, f"r = {r:+.2f} on a −1 to +1 scale",
               color={"Strong": "blue", "Moderate": "cyan"}.get(word, "slate")),
        ui.kpi("trend_up" if r >= 0 else "trend_down", "Direction", "Wetter → dearer" if r >= 0 else "Wetter → cheaper",
               "in the months compared", color="orange"),
        ui.kpi("calendar", f"Strongest delay for {veg.lower()}", LAGS[best], f"r = {rs_all[best]:+.2f}", color="purple"),
        ui.kpi("tag", "Months compared", f"{len(d)}", f"{d.month.min():%b %Y} – {d.month.max():%b %Y}", color="green"),
    ])
    left, right = st.columns([3, 2], gap="large")
    with left:
        fig = go.Figure(go.Scatter(x=d.rain_z, y=d.price_chg, mode="markers", customdata=d.month.dt.strftime("%b %Y"),
                                   marker=dict(color="#3977F6", size=9, opacity=.6, line=dict(color="white", width=.5)),
                                   hovertemplate="%{customdata}<br>rain %{x:+.1f} vs usual<br>price %{y:+.0f}%<extra></extra>"))
        b = np.polyfit(d.rain_z, d.price_chg, 1); xs = np.linspace(d.rain_z.min(), d.rain_z.max(), 5)
        fig.add_trace(go.Scatter(x=xs, y=np.polyval(b, xs), mode="lines", line=dict(color="#F5A33B", width=3), hoverinfo="skip"))
        fig.add_hline(y=0, line=dict(color=GRID, width=1)); fig.add_vline(x=0, line=dict(color=GRID, width=1))
        fig.update_xaxes(title_text="← drier than usual      rain      wetter than usual →", zeroline=False)
        fig.update_yaxes(title_text="price change vs a normal month, %")
        style(fig, 430, legend=False); fig.update_layout(hovermode="closest")
        st.plotly_chart(fig, width="stretch", config=CFG)
    with right:
        allr = pd.Series({v: M.pattern_r(v, lag) for v in C.VEGS}).sort_values()
        fig2 = go.Figure(go.Bar(x=allr.values, y=allr.index, orientation="h",
                                marker_color=["#F06B9A" if v == veg else "#c9d8f8" for v in allr.index],
                                text=[f"{x:+.2f}" for x in allr.values], textposition="outside", cliponaxis=False,
                                hovertemplate="%{y}: r = %{x:+.2f}<extra></extra>"))
        fig2.update_xaxes(range=[-0.7, 0.8], title_text="strength of the link (r)", zeroline=True, zerolinecolor=MUTED)
        style(fig2, 430, legend=False); fig2.update_layout(hovermode="closest", title=dict(text=f"All seven · rain {LAGS[lag].lower()}", font=dict(size=14), x=0))
        st.plotly_chart(fig2, width="stretch", config=CFG)
    st.markdown('<p class="hook">A pattern is a clue, not proof. The next page puts it to a real test.</p>', unsafe_allow_html=True)
    st.markdown('<p class="fine">With 7 vegetables × 4 delays = 28 links, a few can look strong just by chance.</p>', unsafe_allow_html=True)
    footer("CBSL Dambulla wholesale prices; ERA5-Land national rain. Exploratory patterns (lag_correlations.csv reproduced)")


# ---------------- 2 ----------------
def p2():
    header(3, ACT[1], "Does rain help? Try it",
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
        ui.kpi("tag", "Typical miss, prices only", rs(k["miss_without"]), "past prices alone", "flat", "/kg", color="blue"),
        ui.kpi("rain", "Typical miss, adding rain", rs(k["miss_with"]), change, k["tone"], "/kg"),
        ui.kpi("check", "Verdict", k["label"], {"good": "survives strict checks", "soft": "looks better, not proven",
                                                "flat": "too small to trust", "bad": "rain adds nothing"}[k["tone"]], k["tone"]),
        ui.kpi("target", "Price landed inside our range", f"{k['inside_with']:.0f} in 10", f"prices only: {k['inside_without']:.0f} in 10 · aim: 8", "soft", color="purple"),
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
    header(4, ACT[2], "Rain is only one piece",
           "Food prices in Sri Lanka also depend on the rice harvest, on imports and on the rupee. Each is shown on its own; they are not combined into one score.")
    x, y, r, n, share, fx = p3_data()
    fx0 = fx.loc["2021-01"].iloc[0]
    ui.kpi_row([
        ui.kpi("leaf", "Wetter growing seasons, better paddy harvests", f"r = {r:+.2f}", f"{n} seasons · a link, not proof", "soft", color="green"),
        ui.kpi("globe", "Rice bought from abroad, peak year", f"{share.max():.0f}%", f"of supply in {share.idxmax()} · {share.iloc[-1]:.0f}% in {share.index[-1]}", "flat", color="orange"),
        ui.kpi("coins", "Rupee price of one US dollar", rs(fx.iloc[-1]), f"+{(fx.iloc[-1] / fx0 - 1) * 100:.0f}% since Jan 2021", "bad", color="purple"),
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
    header(5, ACT[2], "What did we learn?", "Four pages of playing with the data. Here is the short version.")
    if not st.session_state.get("revealed"):
        st.markdown(f'<div class="reveal-wrap"><div><div class="reveal-ico">{ui.ICON["sparkle"]}</div>'
                    '<p class="reveal-q">Ready for the answer?</p><p class="reveal-sub">One click, three findings.</p></div></div>',
                    unsafe_allow_html=True)
        st.markdown('<p class="guess-q">First, your guess: which vegetable does rain help most?</p>', unsafe_allow_html=True)
        _, gmid, _ = st.columns([1, 4, 1])
        gmid.pills("Your guess", C.VEGS, key="guess", label_visibility="collapsed")
        _, mid, _ = st.columns([1, 1, 1])
        if mid.button("Wanna see the conclusion?", type="primary", key="reveal_btn", icon=":material/celebration:", width="stretch"):
            st.session_state.my_guess = st.session_state.get("guess")
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
    best = max(helped, key=lambda v: nat[v]["gain_pct"])
    g = st.session_state.get("my_guess")
    if g:
        if g == best:
            msg = f"You guessed {g.lower()}. Spot on: rain helped {best.lower()} most, {nat[best]['gain_pct']:.0f}% smaller errors."
        elif g in helped:
            msg = f"You guessed {g.lower()}. Close: rain does help it ({nat[g]['gain_pct']:.0f}%), but {best.lower()} gained most ({nat[best]['gain_pct']:.0f}%)."
        else:
            msg = f"You guessed {g.lower()}. A fair guess, but rain gave it no gain we can trust. It helped {best.lower()} most ({nat[best]['gain_pct']:.0f}%)."
        st.markdown(f'<div class="guess-result">{ui.ICON["target"]}<span>{esc(msg)}</span></div>', unsafe_allow_html=True)
    cards = [
        ("check", "good", f"{min(gains):.0f}–{max(gains):.0f}%", "smaller errors", "Rain helps some vegetables",
         f"For {', '.join(v.lower() for v in helped)}, knowing last month's rain made next month's forecast clearly better."),
        ("target", "bad", f"~{miss:.0f}%", "typical miss", "…but not all, and not precisely",
         f"{', '.join(v.lower() for v in rest).capitalize()} showed no gain we can trust. Even the best forecasts still miss by about a quarter of the price."),
        ("sparkle", "soft", "Next", "test on new months", "What it means",
         "This is a research finding about where rain carries information, not a price app. Next: check it on months not yet published, and use rain from the farms themselves."),
    ]
    html_cards = "".join(f'<div class="card c-{ui.TONE_COLOR[tone] if tone != "soft" else "blue"}"><span class="kpi-ico">{ui.ICON[i]}</span>'
                         f'<div class="big">{esc(big)}<small>{esc(sm)}</small></div><h3>{esc(h)}</h3><p>{esc(t)}</p></div>'
                         for i, tone, big, sm, h, t in cards)
    st.markdown(f'<div class="take">{html_cards}</div>', unsafe_allow_html=True)
    st.button("Hide again", type="tertiary", key="hide_btn", on_click=lambda: st.session_state.update(revealed=False))
    footer("Stored results, Dambulla market, rain across the island")


ACT = ["The problem", "The test", "The bigger picture"]
# (sidebar title, material icon, act, render)
PAGES = [
    ("Prices swing wildly", ":material/show_chart:", ACT[0], p1),
    ("Spot the pattern yourself", ":material/scatter_plot:", ACT[0], p_pattern),
    ("Does rain help? Try it", ":material/science:", ACT[1], p2),
    ("Rain is only one piece", ":material/public:", ACT[2], p3),
    ("What did we learn?", ":material/celebration:", ACT[2], p4),
]
