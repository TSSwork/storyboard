"""The rain map's grid must reproduce the corrected national and Dambulla-box series the study used."""
import numpy as np
import pandas as pd

from story import common, rainmap


def test_grid_matches_national_and_box_series():
    g = rainmap.grid()
    reg = pd.read_csv(common.DATA / "era5_regional_monthly.csv", parse_dates=["month"]).set_index("month")
    reg = reg[reg.n_nat == reg.days_in_month]
    w = np.cos(np.deg2rad(g.lat))
    nat = (g.rain_mm * w).groupby(g.month).sum() / w.groupby(g.month).sum()
    both = pd.concat([nat.rename("grid"), reg.rain_nat], axis=1, join="inner")
    assert len(both) > 180 and (both.grid - both.rain_nat).abs().max() < 0.5
    box = g[(g.lat - 7.86).abs().le(0.3001) & (g.lon - 80.65).abs().le(0.3001)]
    wb = np.cos(np.deg2rad(box.lat))
    dam = (box.rain_mm * wb).groupby(box.month).sum() / wb.groupby(box.month).sum()
    both = pd.concat([dam.rename("grid"), reg.rain_dam], axis=1, join="inner")
    assert (both.grid - both.rain_dam).abs().max() < 0.5


def test_one_month_map_has_every_land_cell():
    m = rainmap.month_map(pd.Timestamp("2024-06-01"))
    assert len(m) == 541 and m.rain_mm.ge(0).all()


def test_wettest_area_summary():
    s = rainmap.summary(pd.Timestamp("2024-06-01"))
    assert s["wettest_mm"] >= s["island_mm"] >= s["driest_mm"] >= 0
