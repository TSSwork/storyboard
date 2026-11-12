"""Storyboard review and rehearsal tool. Reads storyboard/NN_*/{storyboard.png,README.md}; keeps no second copy.

Run: uv run streamlit run research-story/app.py
"""
import re
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
PAGES = sorted(p for p in (ROOT / "storyboard").iterdir() if p.is_dir() and (p / "README.md").exists())

st.set_page_config(page_title="Research storyboard", layout="wide")
st.markdown(
    """
<style>
:root { --ink:#1c2430; --muted:#667085; --rule:#e6e2d9; --accent:#0f6b78; --paper:#fbfaf7; }
.stApp { background: var(--paper); color: var(--ink); }
[data-testid="stSidebar"] { background: #f4f1ea; border-right: 1px solid var(--rule); }
h1, h2, h3 { letter-spacing: -0.01em; }
.label { font-size: .72rem; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); font-weight: 700; margin: 1.1rem 0 .15rem; }
.body { font-size: 1.02rem; line-height: 1.55; margin: 0 0 .4rem; }
.qual { border-left: 3px solid #b7791f; padding: .15rem 0 .15rem .8rem; }
.flow { border: 1px solid var(--rule); background: #fff; padding: .9rem 1rem; border-radius: 6px; min-height: 12rem; }
.flow.now { border-color: var(--accent); }
img { border: 1px solid var(--rule); border-radius: 4px; }
</style>
""",
    unsafe_allow_html=True,
)


def parse(path: Path) -> dict:
    text = (path / "README.md").read_text()
    title = re.match(r"# (.+)", text).group(1)
    parts = re.split(r"^## ", text, flags=re.M)[1:]
    secs = {p.split("\n", 1)[0].strip(): p.split("\n", 1)[1].strip() for p in parts}
    demo = re.search(r"\*\*Demonstrates:\*\* (.+)", text)
    return {"title": title, "stage": demo.group(1) if demo else "", "secs": secs, "img": path / "storyboard.png"}


DOCS = [parse(p) for p in PAGES]
labels = [d["title"] for d in DOCS]

st.sidebar.markdown("### Research storyboard")
mode = st.sidebar.radio("Mode", ["Author", "Presentation", "Story flow"], index=0, key="mode")
if "i" not in st.session_state:
    st.session_state.i = 0
pick = st.sidebar.selectbox("Page", range(len(DOCS)), index=st.session_state.i, format_func=lambda k: labels[k])
st.session_state.i = pick
i = st.session_state.i
doc = DOCS[i]


def nav():
    a, b, c = st.columns([1, 1, 6])
    if a.button("Previous", disabled=i == 0, key="prev"):
        st.session_state.i = i - 1
        st.rerun()
    if b.button("Next", disabled=i == len(DOCS) - 1, key="next"):
        st.session_state.i = i + 1
        st.rerun()
    c.caption(f"Page {i + 1} of {len(DOCS)}")


def section(name: str, cls: str = "body"):
    st.markdown(f'<div class="label">{name}</div>', unsafe_allow_html=True)
    body = doc["secs"].get(name, "")
    st.markdown(f'<div class="{cls}">{body}</div>' if cls == "qual" else body)


def leave_presentation():
    st.session_state.mode = "Author"


if mode == "Presentation":
    # Audience view: no sidebar, no toolbar, no notes. The slide fills the width.
    st.markdown(
        "<style>[data-testid='stSidebar'],[data-testid='stToolbar'],header{display:none!important}"
        ".block-container{padding-top:1rem;max-width:100%}</style>",
        unsafe_allow_html=True,
    )
    st.image(str(doc["img"]), width="stretch")
    a, b, c, d = st.columns([1, 1, 1, 5])
    if a.button("Previous", disabled=i == 0, key="prev"):
        st.session_state.i = i - 1
        st.rerun()
    if b.button("Next", disabled=i == len(DOCS) - 1, key="next"):
        st.session_state.i = i + 1
        st.rerun()
    c.button("Exit", on_click=leave_presentation, key="exit")
    d.caption(f"Page {i + 1} of {len(DOCS)}")
elif mode == "Author":
    nav()
    st.markdown(f"## {doc['title']}")
    st.caption(f"Demonstrates: {doc['stage']}")
    left, right = st.columns([3, 2], gap="large")
    left.image(str(doc["img"]), width="stretch")
    with left:
        section("Visual")
        section("Evidence")
        section("Explanation")
    with right:
        section("Purpose")
        section("Story")
        section("Interpretation")
        st.markdown('<div class="label">Limitations</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="qual body">{doc["secs"]["Limitations"]}</div>', unsafe_allow_html=True)
        section("Transition")
else:
    st.markdown("## Story flow")
    st.caption("Check that each page picks up where the last one left off.")
    prev_take = DOCS[i - 1]["secs"]["Story"] if i else "Start of the story."
    c1, c2, c3 = st.columns(3, gap="medium")
    c1.markdown(f'<div class="flow"><div class="label">Previous page says</div>{prev_take}</div>', unsafe_allow_html=True)
    c2.markdown(
        f'<div class="flow now"><div class="label">This page: {doc["title"]}</div>{doc["secs"]["Purpose"]}</div>',
        unsafe_allow_html=True,
    )
    c3.markdown(
        f'<div class="flow"><div class="label">Hands over to next</div>{doc["secs"]["Transition"]}</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="label">All pages</div>', unsafe_allow_html=True)
    st.table({"Page": [f"{k + 1:02d}" for k in range(len(DOCS))], "Demonstrates": [d["stage"] for d in DOCS],
              "Story": [d["secs"]["Story"] for d in DOCS]})
    nav()
