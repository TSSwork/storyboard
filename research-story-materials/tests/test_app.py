from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parents[2] / "research-story" / "app.py")


def run(page):
    at = AppTest.from_file(APP, default_timeout=60)
    at.session_state.page = page
    at.run()
    assert not at.exception, at.exception
    return at


def text(at):
    return " ".join(m.value for m in at.markdown)


def test_five_pages_render():
    for p in range(5):
        run(p)
    at = run(0)
    assert len([b for b in at.sidebar.button]) >= 5


def test_dashboard_switches_market_and_region():
    at = run(2)
    at.radio(key="p2_market").set_value("Pettah (Colombo)").run()
    assert not at.exception
    at.radio(key="p2_region").set_value("Hill country (Nuwara Eliya)").run()
    assert not at.exception
    assert "Typical miss" in text(at)


def test_beans_shows_no_help():
    at = run(2)
    at.session_state.p2_veg = "Beans"
    at.run()
    assert "No help" in text(at)


def test_conclusion_reveal_and_back():
    at = run(4)
    assert "Rain helps some vegetables" not in text(at)
    at.button(key="reveal_btn").click().run()
    assert "Rain helps some vegetables" in text(at)
    at.session_state.page = 0
    at.run()
    assert not at.exception
    at.session_state.page = 4
    at.run()
    assert not at.exception


def test_rain_map_real_and_typical_month():
    at = run(0)
    assert "Darker blue = more rain" in text(at)
    at.radio(key="p1_mapview").set_value("Long-term monthly average").run()
    assert not at.exception
    assert "Darker blue = more rain" in text(at)


def test_spot_the_pattern_page():
    at = run(1)
    assert "Spot the pattern yourself" in text(at)
    assert "Strong" in text(at)          # cabbage, rain one month earlier: r = +0.60
    at.session_state.pp_lag = 0
    at.run()
    assert not at.exception and "Barely any" in text(at)   # cabbage, same month: r = +0.10


def test_guess_is_remembered_through_the_reveal():
    at = run(4)
    at.session_state.guess = "Carrot"
    at.run()
    at.button(key="reveal_btn").click().run()
    t = text(at)
    assert "You guessed carrot" in t and "cabbage" in t
