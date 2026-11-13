from story import ui


def test_kpi_card_contains_value_tone_and_icon():
    h = ui.kpi("tag", "Typical miss", "Rs 42", "↓ 19%", "good")
    assert "Rs 42" in h and "kpi-chip good" in h and "<svg" in h


def test_kpi_escapes_text():
    h = ui.kpi("tag", "<b>", "1", "<i>")
    assert "&lt;b&gt;" in h and "&lt;i&gt;" in h and "<b>" not in h


def test_kpi_without_note_has_no_chip():
    assert "kpi-chip" not in ui.kpi("tag", "Label", "1")


def test_icons_are_svg():
    assert ui.ICON and all(v.startswith("<svg") for v in ui.ICON.values())
    for k in ["tag", "trend_up", "bolt", "wave", "rain", "target", "check", "shield", "leaf", "globe", "coins", "sparkle"]:
        assert k in ui.ICON
