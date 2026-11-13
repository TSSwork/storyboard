"""KPI cards, inline SVG icons, the verdict strip and the confetti reveal.

Everything is drawn here as HTML/SVG/CSS so the folder needs no network at runtime.
"""
import html
import time

import streamlit as st

esc = html.escape


def _svg(body: str) -> str:
    return ('<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.6" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{body}</svg>')


ICON = {
    "tag": _svg('<path d="M3 12V4a1 1 0 0 1 1-1h8l9 9-9 9z"/><circle cx="7.5" cy="7.5" r="1.3"/>'),
    "trend_up": _svg('<path d="M3 17l6-6 4 4 8-8"/><path d="M15 7h6v6"/>'),
    "trend_down": _svg('<path d="M3 7l6 6 4-4 8 8"/><path d="M15 17h6v-6"/>'),
    "bolt": _svg('<path d="M13 2 4 14h7l-1 8 9-12h-7z"/>'),
    "wave": _svg('<path d="M2 12c2.5-4 5-4 7.5 0s5 4 7.5 0 3.5-3 5-2"/><path d="M2 18c2.5-4 5-4 7.5 0s5 4 7.5 0"/>'),
    "rain": _svg('<path d="M7 15a4 4 0 0 1-.5-8A5.5 5.5 0 0 1 17 7.5a3.75 3.75 0 0 1 0 7.5z"/><path d="M8 18l-1 3M12 18l-1 3M16 18l-1 3"/>'),
    "target": _svg('<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.2"/>'),
    "check": _svg('<circle cx="12" cy="12" r="9"/><path d="m8 12 3 3 5-6"/>'),
    "shield": _svg('<path d="M12 3 5 6v6c0 4.5 3 7.5 7 9 4-1.5 7-4.5 7-9V6z"/>'),
    "leaf": _svg('<path d="M5 19c0-8 5-14 15-15-1 10-7 15-15 15z"/><path d="M5 19 13 11"/>'),
    "globe": _svg('<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3.5 3 14.5 0 18M12 3c-3 3.5-3 14.5 0 18"/>'),
    "coins": _svg('<ellipse cx="9" cy="7" rx="6" ry="3"/><path d="M3 7v5c0 1.7 2.7 3 6 3s6-1.3 6-3V7"/><path d="M9 15v2c0 1.7 2.7 3 6 3s6-1.3 6-3v-5c0-1.5-2-2.7-5-3"/>'),
    "sparkle": _svg('<path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5 18 18M6 18l2.5-2.5M15.5 8.5 18 6"/>'),
    "calendar": _svg('<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>'),
}

CSS = """
<style>
:root { --sage:#5e9e83; --slate:#8aa3b2; --card-shadow: 0 1px 2px rgba(0,41,65,.04), 0 8px 24px -12px rgba(0,41,65,.14); }
.kpi-row { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:1rem; margin:.4rem 0 1.1rem; }
.kpi-row.three { grid-template-columns:repeat(3,minmax(0,1fr)); }
@media (max-width: 900px) { .kpi-row, .kpi-row.three { grid-template-columns:repeat(2,minmax(0,1fr)); } }
@media (max-width: 560px) { .kpi-row, .kpi-row.three { grid-template-columns:1fr; } }
.kpi { border-radius:16px; padding:1rem 1.15rem 1.05rem; box-shadow:0 6px 18px -8px rgba(24,43,73,.28); min-width:0; color:#fff; }
.kpi.c-blue { background:#3977F6; } .kpi.c-purple { background:#8865E8; } .kpi.c-green { background:#23936F; }
.kpi.c-slate { background:#6B7C93; } .kpi.c-navy { background:#182B49; }
.kpi.c-cyan { background:#25B8C8; color:#182B49; } .kpi.c-orange { background:#F5A33B; color:#182B49; } .kpi.c-pink { background:#F06B9A; color:#182B49; }
.kpi-top { display:flex; align-items:center; min-height:2.6em; line-height:1.3; gap:.6rem; font-size:.86rem; font-weight:600; opacity:.95; }
.kpi-ico { width:34px; height:34px; border-radius:50%; background:rgba(255,255,255,.22); display:grid; place-items:center; flex:none; }
.kpi-val { font-size:2rem; font-weight:700; letter-spacing:-.02em; margin:.55rem 0 .15rem; font-variant-numeric:tabular-nums; line-height:1.1; overflow-wrap:anywhere; }
.kpi-val small { font-size:.95rem; font-weight:500; margin-left:.25rem; letter-spacing:0; opacity:.85; }
.kpi-chip { display:inline-block; font-size:.8rem; font-weight:600; padding:.18rem .6rem; border-radius:999px; margin-top:.35rem; background:rgba(255,255,255,.24); }
.kpi.c-cyan .kpi-chip, .kpi.c-orange .kpi-chip, .kpi.c-pink .kpi-chip { background:rgba(255,255,255,.45); }
.verdicts { display:flex; flex-wrap:wrap; gap:.5rem; margin:.6rem 0 .2rem; }
.vd { display:flex; align-items:center; gap:.45rem; background:#fff; border:1px solid var(--rule); border-radius:999px; padding:.35rem .8rem .35rem .45rem; font-size:.88rem; }
.vd .dot { width:24px; height:24px; border-radius:50%; display:grid; place-items:center; }
.vd .dot svg { width:14px; height:14px; }
.vd.good .dot { background:#e5f2ec; color:#2f6b52; } .vd.soft .dot { background:var(--tint); color:#1d5574; }
.vd.flat .dot { background:#edf2f5; color:#4c6472; } .vd.bad .dot { background:#fde9e9; color:#a23b3b; }
.vd.sel { border:1.5px solid var(--ink); font-weight:600; }
.vd .lab { color:var(--muted); font-weight:400; }

.lede { font-size:1.08rem; color:var(--muted); margin:.1rem 0 .9rem; max-width:62rem; }
.hook { font-size:1.2rem; font-weight:500; color:var(--ink); margin:.6rem 0 0; }
.hook::before { content:""; display:inline-block; width:8px; height:8px; background:var(--coral); border-radius:50%; margin-right:.6rem; vertical-align:middle; }
[data-testid="stMarkdownContainer"] p.fine { color:var(--muted); font-size:.84rem; margin:.3rem 0 0; line-height:1.5; }

.reveal-wrap { display:grid; place-items:center; text-align:center; padding:3.5rem 1rem 1rem; }
.reveal-ico { width:64px; height:64px; border-radius:50%; background:var(--tint); color:var(--ink); display:grid; place-items:center; margin:0 auto 1rem; }
.reveal-ico svg { width:30px; height:30px; }
.reveal-q { font-size:1.6rem; font-weight:600; margin:0 0 .4rem; color:var(--ink); }
.reveal-sub { color:var(--muted); margin:0 0 1.2rem; }
.st-key-reveal_btn button { max-width:20rem; margin:0 auto; display:flex; min-height:3rem !important; border-radius:999px !important; font-size:1.05rem; }
.st-key-hide_btn button { border:none !important; color:var(--muted) !important; background:transparent !important; text-decoration:underline; text-underline-offset:3px; min-height:2rem !important; }
.take { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:1rem; margin-top:.4rem; }
@media (max-width: 900px) { .take { grid-template-columns:1fr; } }
.take .card { border-radius:16px; padding:1.3rem 1.4rem; box-shadow:0 6px 18px -8px rgba(24,43,73,.28); color:#fff; }
.take .card.c-green { background:#23936F; } .take .card.c-pink { background:#F06B9A; color:#182B49; } .take .card.c-blue { background:#3977F6; }
.take .card .kpi-ico { background:rgba(255,255,255,.22); }
.take .card h3 { color:inherit; }
.guess-q { text-align:center; font-weight:600; color:var(--ink); margin:.4rem 0 .5rem; }
.st-key-guess { width:100% !important; align-self:center; }
.st-key-guess [data-testid="stButtonGroup"] div:has(> button) { justify-content:center; }
.st-key-guess button { flex:0 0 auto !important; width:auto !important; padding:0 .9rem !important; }
.guess-result { display:flex; align-items:center; gap:.7rem; background:#fff; border:1px solid var(--rule); border-left:5px solid #F5A33B; border-radius:12px; padding:.8rem 1rem; margin:.2rem 0 1rem; font-weight:500; }
.guess-result svg { color:#F5A33B; flex:none; }
.take .card h3 { font-size:1.15rem; margin:.7rem 0 .45rem; padding:0; }
.take .card p { margin:0; line-height:1.55; }
.take .big { font-size:2.4rem; font-weight:700; letter-spacing:-.02em; color:inherit; line-height:1; margin-top:.9rem; font-variant-numeric:tabular-nums; }
.take .big small { font-size:.9rem; opacity:.85; font-weight:500; margin-left:.3rem; letter-spacing:0; }

@media (prefers-reduced-motion: no-preference) {
  @keyframes rise { from { opacity:0; transform:translateY(8px); } to { opacity:1; transform:none; } }
  @keyframes pagein { from { opacity:0; transform:translateX(18px); } to { opacity:1; transform:none; } }
  [class*="st-key-page_"] { animation: pagein .45s cubic-bezier(.2,.7,.2,1) both; }
  .kpi, .vd, .take .card { animation: rise .45s cubic-bezier(.2,.7,.2,1) both; }
  .kpi:nth-child(2), .take .card:nth-child(2) { animation-delay:.07s; }
  .kpi:nth-child(3) { animation-delay:.14s; } .take .card:nth-child(3) { animation-delay:.35s; }
  .kpi:nth-child(4) { animation-delay:.21s; }
  .take .card:nth-child(2) { animation-delay:.18s; }
  .kpi, .vd { transition: border-color .2s ease; }
}
</style>
"""


COLORS = {"blue", "cyan", "purple", "pink", "orange", "green", "slate", "navy"}
TONE_COLOR = {"good": "green", "soft": "cyan", "flat": "slate", "bad": "pink"}


def kpi(icon: str, label: str, value: str, note: str = "", tone: str = "flat", unit: str = "", color: str | None = None) -> str:
    """One solid-colour KPI card. `color` picks the fill; without it the tone decides (good/soft/flat/bad)."""
    c = color if color in COLORS else TONE_COLOR.get(tone, "slate")
    chip = f'<div class="kpi-chip">{esc(note)}</div>' if note else ""
    u = f"<small>{esc(unit)}</small>" if unit else ""
    return (f'<div class="kpi c-{c}"><div class="kpi-top"><span class="kpi-ico">{ICON[icon]}</span>{esc(label)}</div>'
            f'<div class="kpi-val">{esc(value)}{u}</div>{chip}</div>')


def kpi_row(cards: list[str]) -> None:
    cls = "kpi-row three" if len(cards) == 3 else "kpi-row"
    st.markdown(f'<div class="{cls}">{"".join(cards)}</div>', unsafe_allow_html=True)


def verdict_strip(items: list[tuple[str, str, str]], selected: str) -> None:
    pills = "".join(f'<div class="vd {tone}{" sel" if veg == selected else ""}"><span class="dot">{ICON["leaf"]}</span>'
                    f'{esc(veg)} <span class="lab">· {esc(lab)}</span></div>' for veg, lab, tone in items)
    st.markdown(f'<div class="verdicts">{pills}</div>', unsafe_allow_html=True)


def confetti() -> None:
    """A short, soft burst of paper in the palette colours. Skipped when the viewer prefers reduced motion."""
    st.iframe(
        f"""<script>/* {time.time_ns()} */
const P = window.parent, d = P.document;
if (!P.matchMedia('(prefers-reduced-motion: reduce)').matches) {{
  const c = d.createElement('canvas');
  c.style.cssText = 'position:fixed;inset:0;width:100vw;height:100vh;pointer-events:none;z-index:99999';
  d.body.appendChild(c);
  const W = c.width = P.innerWidth, H = c.height = P.innerHeight, x = c.getContext('2d');
  const cols = ['#002941', '#b6dfed', '#fd6e6e', '#5e9e83', '#8cc0d6', '#f3c98b'];
  const ps = Array.from({{length: 140}}, (_, i) => ({{
    x: W * (i % 2 ? 0.25 : 0.75) + (Math.random() - .5) * 80, y: H * 0.55,
    vx: (Math.random() - .5) * 12, vy: -9 - Math.random() * 9, r: Math.random() * 6.28,
    vr: (Math.random() - .5) * .3, w: 6 + Math.random() * 6, h: 3 + Math.random() * 4, c: cols[i % cols.length] }}));
  const t0 = performance.now();
  (function f(t) {{
    const k = (t - t0) / 2600; x.clearRect(0, 0, W, H);
    for (const p of ps) {{
      p.vy += .32; p.vx *= .99; p.x += p.vx; p.y += p.vy; p.r += p.vr;
      x.save(); x.globalAlpha = Math.max(0, 1 - k * k); x.translate(p.x, p.y); x.rotate(p.r);
      x.fillStyle = p.c; x.fillRect(-p.w / 2, -p.h / 2, p.w, p.h); x.restore();
    }}
    if (k < 1) requestAnimationFrame(f); else c.remove();
  }})(t0);
}}
</script>""",
        height=1,
    )
