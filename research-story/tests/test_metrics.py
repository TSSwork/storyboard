import pandas as pd

from story import common, metrics as m


def test_cabbage_dambulla_national_matches_stored_result():
    k = m.rain_kpis("Cabbage", "nat", "dambulla")
    assert round(k["gain_pct"], 1) == 19.7
    assert k["label"] == "Clear help" and k["tone"] == "good"
    assert round(k["miss_without"]) == 52 and round(k["miss_with"]) == 42
    assert k["n"] == 62


def test_beans_is_no_help():
    k = m.rain_kpis("Beans", "nat", "dambulla")
    assert k["gain_pct"] < 0 and k["label"] == "No help" and k["tone"] == "bad"


def test_inside_range_is_out_of_ten_and_matches_coverage_file():
    k = m.rain_kpis("Cabbage", "nat", "dambulla")
    assert k["inside_without"] == round(0.6935 * 10, 1)
    assert k["inside_with"] == round(0.7742 * 10, 1)


def test_pettah_uses_actual_count():
    c = pd.read_csv(common.DATA / "forecast_model_comparison_v2.csv")
    row = c[(c.market == "pettah") & (c.price_agg == "mean") & (c.model == "AR+rain:nat") & (c.commodity == "Cabbage")].iloc[0]
    assert m.rain_kpis("Cabbage", "nat", "pettah")["n"] == row.n != 62


def test_verdicts_national_dambulla():
    v = {veg: lab for veg, lab, _ in m.verdicts("nat", "dambulla")}
    assert list(v) == common.VEGS
    assert [x for x in v if v[x] == "Clear help"] == ["Cabbage", "Brinjal", "Carrot"]
    assert v["Tomato"] == "A hint, not proven"


def test_price_kpis_shape():
    k = m.price_kpis("Cabbage")
    assert k["high"] > k["low"] > 0 and 0 <= k["big_move_share"] <= 1 and k["jump_pct"] > 0


def test_price_jump_does_not_bridge_gaps():
    s = pd.Series([100.0, 300.0], index=pd.to_datetime(["2020-01-01", "2020-03-01"]))
    assert pd.isna(m.month_changes(s)).all()


def test_forecast_path_lengths():
    f = m.forecast_path("Cabbage", "nat", "dambulla")
    assert len(f) == 62 and (f.lo <= f.hi).all()
    assert list(f.columns) == ["target_month", "actual", "without", "with", "lo", "hi"]
