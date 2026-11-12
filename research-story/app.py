"""Research storyboard: audience view. Pages in the sidebar; slide or interactive chart in the main area.

Reads storyboard/NN_*/storyboard.png and the page title from each README. Notes live in the READMEs, not here.
Run: uv run streamlit run research-story/app.py
"""
import re
from pathlib import Path

import streamlit as st

import slides
from slide_copy import ACTS

ROOT = Path(__file__).resolve().parent
PAGES = sorted(p for p in (ROOT / "storyboard").iterdir() if p.is_dir() and (p / "README.md").exists())

st.set_page_config(page_title="Research storyboard", layout="wide")
st.markdown(
    """
<style>
:root { --ink:#002941; --muted:#52707f; --rule:#d8e6ee; --coral:#fd6e6e; --soft:#b6dfed; --tint:#e3f1f7; --paper:#f6fafc; }
html, body, .stApp, [data-testid="stMarkdownContainer"] { font-family: "Noto Sans", system-ui, sans-serif; }
.stApp { background: var(--paper); color: var(--ink); }
/* hide Deploy and the app menu, but keep the toolbar: it holds the button that reopens the sidebar */
[data-testid="stToolbarActions"], [data-testid="stMainMenu"], [data-testid="stAppDeployButton"], [data-testid="stDecoration"] { display: none !important; }
.block-container { padding-top: 4.25rem; padding-bottom: 1.5rem; max-width: 100%; }
/* control bar sits at the bottom of the screen even on short slides */
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] { min-height: calc(100vh - 6rem); }
[data-testid="stLayoutWrapper"]:has(> .st-key-pbar) { margin-top: auto; }
[data-testid="stSidebar"] { background: #e9f4f9; border-right: 1px solid var(--rule); }
h1, h2, h3, h4 { font-weight: 600; letter-spacing: -0.01em; color: var(--ink); }
.brand { margin-bottom: .75rem; }
.brand::before { content: ""; display: inline-block; width: 8px; height: 8px; background: var(--coral); margin-right: 8px; vertical-align: middle; }
.act { color: var(--muted); font-size: .9rem; }
.stButton > button { border: 1px solid var(--ink); color: var(--ink); background: transparent; border-radius: 8px; min-height: 2.5rem; transition: background-color .15s ease; }
.stButton > button:hover:not(:disabled) { background: var(--soft); border-color: var(--ink); color: var(--ink); }
.stButton > button:focus-visible { outline: 2px solid var(--ink); outline-offset: 2px; }
.stButton > button[kind="primary"] { background: var(--ink); color: #fff; }
.stButton > button[kind="primary"]:hover:not(:disabled) { background: #0b3c5a; color: #fff; }
img { border: 1px solid var(--rule); border-radius: 8px; }
.progress { height: 3px; background: var(--tint); border-radius: 2px; margin: 12px 0 8px; }
.progress > div { height: 3px; background: var(--ink); border-radius: 2px; transition: width .25s ease; }
.pager { text-align: center; color: var(--muted); font-size: 1rem; font-variant-numeric: tabular-nums; }
.pager b { color: var(--ink); font-weight: 600; }

.s-label { color: var(--muted); font-size: .95rem; font-weight: 500; margin-bottom: .25rem; }
.s-label .sq { display: inline-block; width: 8px; height: 8px; background: var(--coral); margin-right: 10px; vertical-align: middle; }
.s-h1 { font-size: 2.1rem; font-weight: 600; line-height: 1.2; letter-spacing: -0.01em; margin: 0 0 .35rem; padding: 0; color: var(--ink); }
.s-sub { color: var(--muted); font-size: 1.05rem; margin: 0 0 1rem; }
.s-foot { display: flex; justify-content: space-between; gap: 1rem; color: var(--muted); font-size: .8rem; border-top: 1px solid var(--rule); padding-top: .6rem; margin-top: 1rem; }
.s-cards { display: grid; gap: 1rem; margin-bottom: .5rem; }
.s-card { background: #fff; border: 1px solid var(--rule); border-radius: 8px; padding: 1.1rem 1.25rem; min-height: 14rem; }
.s-card-h { font-weight: 600; font-size: 1.1rem; margin-bottom: .6rem; color: var(--ink); }
.s-card p, .s-card li { font-size: 1rem; line-height: 1.55; }
.s-card ol { padding-left: 1.2rem; margin: 0; }
.s-card li { margin-bottom: .75rem; }
.s-card-top { background: #fff; border: 1px solid var(--rule); border-bottom: none; border-radius: 8px 8px 0 0; padding: .9rem 1.1rem .2rem; }
.s-capt { font-size: .95rem; }
.s-cav { color: var(--muted); font-size: .85rem; margin-top: .25rem; }
.s-facts { display: grid; grid-template-columns: 9rem 1fr; gap: .6rem 1rem; align-items: baseline; }
.s-k { color: var(--muted); font-weight: 500; }
.s-v { font-size: 1.05rem; }
.s-flow { display: flex; align-items: center; gap: .6rem; margin-top: 1.6rem; }
.s-box { border: 1px solid var(--rule); background: #fff; padding: .85rem 1rem; border-radius: 8px; flex: 1; text-align: center; }
.s-box.dark { background: var(--ink); color: #fff; border-color: var(--ink); font-weight: 500; }
.s-arr { color: var(--muted); font-size: 1.3rem; }
.s-arr.big { font-size: 2rem; }
.s-note { font-size: .95rem; line-height: 1.6; margin-top: 1rem; }
.s-diagram { display: flex; align-items: center; gap: 1.2rem; margin: 1rem 0 1.6rem; }
.s-stack { display: flex; flex-direction: column; gap: .9rem; flex: 1.3; }
.s-mc { border: 1px solid var(--rule); background: #fff; border-radius: 8px; padding: 1rem 1.2rem; line-height: 1.5; flex: 1; }
.s-mc.hi { background: var(--tint); border: 1.5px solid var(--ink); }
.s-mc.mid { flex: .8; text-align: center; }
.s-two { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; }
.s-chips { display: flex; gap: .5rem; }
.s-chip { border: 1px solid var(--rule); background: #fff; padding: .5rem 1.1rem; border-radius: 8px; font-variant-numeric: tabular-nums; }
.s-chip.on { background: var(--tint); border: 2px solid var(--ink); font-weight: 600; }
ul.s-list { margin: 0; padding-left: 1.2rem; }
ul.s-list li { margin-bottom: .55rem; line-height: 1.5; }
[data-testid="stVerticalBlockBorderWrapper"] { border-color: var(--rule); }
.nav-group { font-size: .78rem; color: var(--muted); font-weight: 500; margin: 1.4rem 0 .35rem .6rem; }
[data-testid="stSidebar"] button[kind="tertiary"] { color: var(--ink); font-weight: 400; justify-content: flex-start; text-align: left; border: none; background: transparent; padding: .4rem .6rem; min-height: 2.25rem; border-radius: 8px; }
[data-testid="stSidebar"] button[kind="tertiary"] > div { justify-content: flex-start; gap: .6rem; }
[data-testid="stSidebar"] button[kind="tertiary"]:hover:not(:disabled) { background: #d9ecf4; color: var(--ink); }
[class*="st-key-navon_"] button { background: #d6ebf4 !important; font-weight: 600 !important; }
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: .25rem; }
</style>
""",
    unsafe_allow_html=True,
)

TITLES = [re.match(r"# \d+ - (.+)", (p / "README.md").read_text()).group(1) for p in PAGES]
N = len(PAGES)
if "page" not in st.session_state:
    st.session_state.page = 0


def go(delta):
    st.session_state.page = min(max(st.session_state.page + delta, 0), N - 1)


# Sidebar: brand, start button, pages grouped by act. Click a row to jump.
NAV = ["Opening question", "Scope and data", "Prices and rain", "The experiment", "Evaluation", "Main result", "Robustness", "Accuracy", "Wider context", "Conclusions"]
ICONS = [":material/help:", ":material/map:", ":material/show_chart:", ":material/account_tree:", ":material/fact_check:",
         ":material/bar_chart:", ":material/tune:", ":material/ssid_chart:", ":material/public:", ":material/flag:"]


def goto(k):
    st.session_state.page = k


with st.sidebar:
    st.markdown('<h3 class="brand">Research storyboard</h3>', unsafe_allow_html=True)
    st.button("Start from page 1", icon=":material/play_arrow:", type="primary", key="start", width="stretch", on_click=goto, args=(0,))
    last_act = None
    for k in range(N):
        if ACTS[k + 1] != last_act:
            last_act = ACTS[k + 1]
            st.markdown(f'<div class="nav-group">{last_act}</div>', unsafe_allow_html=True)
        on = k == st.session_state.page
        st.button(NAV[k], icon=ICONS[k], key=f"{'navon' if on else 'nav'}_{k}", type="tertiary", width="stretch", on_click=goto, args=(k,))
i = st.session_state.page
n = i + 1

# Slide: native, vector; sharp at any size
slides.render(n)

# Control bar: act (left), page n / total (centre), previous and next (right)
with st.container(key="pbar"):
    st.markdown(f'<div class="progress"><div style="width:{n / N * 100:.0f}%"></div></div>', unsafe_allow_html=True)
    left, mid, right = st.columns([2, 3, 2], vertical_alignment="center")
    left.markdown(f'<div class="act">{ACTS[n]}</div>', unsafe_allow_html=True)
    mid.markdown(f'<div class="pager"><b>{n}</b> / {N}</div>', unsafe_allow_html=True)
    r1, r2 = right.columns(2)
    r1.button("Previous", icon=":material/arrow_back:", disabled=i == 0, key="prev", width="stretch", on_click=go, args=(-1,))
    r2.button("Next", icon=":material/arrow_forward:", icon_position="right", type="primary", disabled=i == N - 1, key="next", width="stretch", on_click=go, args=(1,))

# Keyboard: right arrow or Page Down = next, left arrow or Page Up = previous
st.iframe(
    """<script>
const d = window.parent.document;
if (!window.parent.__storyKeys) {
  window.parent.__storyKeys = true;
  d.addEventListener('keydown', (e) => {
    const t = e.target, tag = (t.tagName || '').toLowerCase();
    if (['input', 'textarea', 'select'].includes(tag) || t.isContentEditable || t.getAttribute('role') === 'slider') return;
    const press = (label) => {
      const b = [...d.querySelectorAll('.st-key-pbar button')].find(x => x.innerText.includes(label) && !x.disabled);
      if (b) { e.preventDefault(); b.click(); }
    };
    if (e.key === 'ArrowRight' || e.key === 'PageDown') press('Next');
    else if (e.key === 'ArrowLeft' || e.key === 'PageUp') press('Previous');
  });
}
</script>""",
    height=1,
)
