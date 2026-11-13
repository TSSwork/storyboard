"""Research dashboard: four interactive pages in the sidebar, the page itself in the main area.

Pages: story/pages.py. Numbers: story/metrics.py (from data/). Cards and icons: story/ui.py.
Speaking guides for the presenter are in story_pages/ and are not shown here.
Run from this folder:  uv run streamlit run app.py
"""
import streamlit as st

from story import ui
from story.pages import PAGES

st.set_page_config(page_title="Research storyboard", layout="wide")
st.markdown(
    """
<style>
@font-face { font-family: "Noto Sans"; font-weight: 400; src: url("app/static/fonts/NotoSans-Regular.ttf"); }
@font-face { font-family: "Noto Sans"; font-weight: 500; src: url("app/static/fonts/NotoSans-Medium.ttf"); }
@font-face { font-family: "Noto Sans"; font-weight: 600; src: url("app/static/fonts/NotoSans-SemiBold.ttf"); }
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
.stButton > button:disabled, .stButton > button[kind="primary"]:disabled { opacity: .35; cursor: not-allowed; }
.progress { height: 3px; background: var(--tint); border-radius: 2px; margin: 12px 0 8px; }
.progress > div { height: 3px; background: var(--ink); border-radius: 2px; transition: width .25s ease; }
.pager { text-align: center; color: var(--muted); font-size: 1rem; font-variant-numeric: tabular-nums; }
.pager b { color: var(--ink); font-weight: 600; }

.s-label { color: var(--muted); font-size: .95rem; font-weight: 500; margin-bottom: .25rem; }
.s-label .sq { display: inline-block; width: 8px; height: 8px; background: var(--coral); margin-right: 10px; vertical-align: middle; }
.s-h1 { font-size: 2.1rem; font-weight: 600; line-height: 1.2; letter-spacing: -0.01em; margin: 0 0 .35rem; padding: 0; color: var(--ink); }
.s-sub { color: var(--muted); font-size: 1.05rem; margin: 0 0 1rem; }
.s-foot { display: flex; justify-content: space-between; gap: 1rem; color: var(--muted); font-size: .8rem; border-top: 1px solid var(--rule); padding-top: .6rem; margin-top: 1rem; }
.s-card-h { font-weight: 600; font-size: 1.1rem; margin-bottom: .6rem; color: var(--ink); }
[data-testid="stVerticalBlockBorderWrapper"] { border-color: var(--rule); }
.nav-group { font-size: .78rem; line-height: 1.4; color: var(--muted); font-weight: 500; margin: 1rem .2rem .75rem; padding: 1.1rem .4rem 0; border-top: 1px solid var(--rule); }
.nav-group.first { border-top: none; margin-top: .5rem; padding-top: 0; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"]:has(.nav-group) { margin-bottom: 0; }
[data-testid="stSidebar"] button[kind="tertiary"] { color: var(--ink); font-weight: 400; justify-content: flex-start; text-align: left; border: none; background: transparent; padding: .4rem .6rem; min-height: 2.25rem; border-radius: 8px; }
[data-testid="stSidebar"] button[kind="tertiary"] > div { justify-content: flex-start; gap: .6rem; }
[data-testid="stSidebar"] button[kind="tertiary"]:hover:not(:disabled) { background: #d9ecf4; color: var(--ink); }
[class*="st-key-navon_"] button { background: #d6ebf4 !important; font-weight: 600 !important; }
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: .25rem; }
</style>
""",
    unsafe_allow_html=True,
)
st.markdown(ui.CSS, unsafe_allow_html=True)

N = len(PAGES)
if "page" not in st.session_state:
    st.session_state.page = 0


def go(delta):
    st.session_state.page = min(max(st.session_state.page + delta, 0), N - 1)


# Sidebar: brand, start button, pages grouped by act. Click a row to jump.
def goto(k):
    st.session_state.page = k


with st.sidebar:
    st.markdown('<h3 class="brand">Rain &amp; vegetable prices</h3>', unsafe_allow_html=True)
    if st.session_state.page != 0:
        st.button("Start from page 1", icon=":material/play_arrow:", type="primary", key="start", width="stretch", on_click=goto, args=(0,))
    else:  # same height, so the list below does not jump when the button appears
        st.markdown('<div style="height:3.5rem"></div>', unsafe_allow_html=True)
    last_act = None
    for k in range(N):
        title, icon, act, _ = PAGES[k]
        if act != last_act:
            last_act = act
            st.markdown(f'<div class="nav-group{" first" if k == 0 else ""}">{last_act}</div>', unsafe_allow_html=True)
        on = k == st.session_state.page
        st.button(title, icon=icon, key=f"{'navon' if on else 'nav'}_{k}", type="tertiary", width="stretch", on_click=goto, args=(k,))
i = st.session_state.page
n = i + 1

# Page body; a new container key per page replays the entrance animation
with st.container(key=f"page_{n}"):
    PAGES[i][3]()

# Control bar: act (left), page n / total (centre), previous and next (right)
with st.container(key="pbar"):
    st.markdown(f'<div class="progress"><div style="width:{n / N * 100:.0f}%"></div></div>', unsafe_allow_html=True)
    left, mid, right = st.columns([2, 3, 2], vertical_alignment="center")
    left.markdown(f'<div class="act">{PAGES[i][2]}</div>', unsafe_allow_html=True)
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
