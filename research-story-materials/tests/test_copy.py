import re
from pathlib import Path

from story import metrics as m

ROOT = Path(__file__).resolve().parent.parent          # research-story-materials
APP = ROOT.parent / "research-story"


def test_guide_1_states_the_real_start_year():
    first = m._prices()["Cabbage"].dropna().index.min().year
    years = re.findall(r"every month since (\d{4})", (ROOT / "story_pages/01_prices_swing.md").read_text())
    assert years == [str(first)]


def test_no_unsourced_biggest_market_claim():
    for f in [APP / "story/pages.py", ROOT / "story_pages/01_prices_swing.md"]:
        assert "biggest vegetable market" not in f.read_text()
