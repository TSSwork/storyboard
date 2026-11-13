from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "app.py")


def run(page):
    at = AppTest.from_file(APP, default_timeout=60)
    at.session_state.page = page
    at.run()
    assert not at.exception, at.exception
    return at


def text(at):
    return " ".join(m.value for m in at.markdown)


def test_four_pages_render():
    for p in range(4):
        run(p)
    at = run(0)
    assert len([b for b in at.sidebar.button]) >= 4


def test_dashboard_switches_market_and_region():
    at = run(1)
    at.radio(key="p2_market").set_value("Pettah (Colombo)").run()
    assert not at.exception
    at.radio(key="p2_region").set_value("Hill country (Nuwara Eliya)").run()
    assert not at.exception
    assert "Typical miss" in text(at)


def test_beans_shows_no_help():
    at = run(1)
    at.session_state.p2_veg = "Beans"
    at.run()
    assert "No help" in text(at)


def test_conclusion_reveal_and_back():
    at = run(3)
    assert "Rain helps some vegetables" not in text(at)
    at.button(key="reveal_btn").click().run()
    assert "Rain helps some vegetables" in text(at)
    at.session_state.page = 0
    at.run()
    assert not at.exception
    at.session_state.page = 3
    at.run()
    assert not at.exception


def test_rain_map_real_and_typical_month():
    at = run(0)
    assert "Darker blue = more rain" in text(at)
    at.radio(key="p1_mapview").set_value("Typical month").run()
    assert not at.exception
    assert "Darker blue = more rain" in text(at)
