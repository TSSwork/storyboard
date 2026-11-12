"""Research storyboard: audience view. Pages in the sidebar; slide or interactive chart in the main area.

Reads storyboard/NN_*/storyboard.png and the page title from each README. Notes live in the READMEs, not here.
Run: uv run streamlit run research-story/app.py
"""
import re
from pathlib import Path

import streamlit as st

import build_figures as bf
from live_charts import LIVE

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
.block-container { padding-top: 1.5rem; max-width: 100%; }
[data-testid="stSidebar"] { background: #e9f4f9; border-right: 1px solid var(--rule); }
[data-testid="stSidebar"] [role="radiogroup"] { gap: .5rem; }
[data-testid="stSidebar"] [role="radiogroup"] label { align-items: flex-start; line-height: 1.35; }
h1, h2, h3, h4 { font-weight: 600; letter-spacing: -0.01em; color: var(--ink); }
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


# Sidebar: every page, click to jump
st.sidebar.markdown('<h3 class="brand">Research storyboard</h3>', unsafe_allow_html=True)
st.sidebar.radio("Pages", range(N), key="page", format_func=lambda k: f"{k + 1:02d}  {TITLES[k]}", label_visibility="collapsed")
i = st.session_state.page
n = i + 1

# Slide: interactive chart where one exists (tab 1), always the static slide (tab 2)
if n in LIVE:
    live, static = st.tabs(["Interactive", "Static slide"])
    with live:
        st.markdown(f"#### {TITLES[i]}")
        LIVE[n]()
    static.image(str(PAGES[i] / "storyboard.png"), width="stretch")
else:
    st.image(str(PAGES[i] / "storyboard.png"), width="stretch")

# Control bar: act (left), page n / total (centre), previous and next (right)
with st.container(key="pbar"):
    st.markdown(f'<div class="progress"><div style="width:{n / N * 100:.0f}%"></div></div>', unsafe_allow_html=True)
    left, mid, right = st.columns([2, 3, 2], vertical_alignment="center")
    left.markdown(f'<div class="act">{bf.ACTS[n]}</div>', unsafe_allow_html=True)
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
