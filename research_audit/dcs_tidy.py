"""Tidy the DCS paddy workbooks (read-only) -> research_audit/derived/dcs_*.csv"""
import openpyxl, pandas as pd, re, glob, os
os.chdir(os.path.join(os.path.dirname(__file__), "..", "raw", "pdf")); OUT = "../../research_audit/derived/"
def rows(f):
    ws = openpyxl.load_workbook(f, data_only=True).active
    return [list(r) for r in ws.iter_rows(values_only=True)]
# national
for s in ("Maha", "Yala"):
    r = rows(f"PaddyExtent_{s}_Season-1951-2024.xlsx")
    data = [x[1:10] for x in r if x[1] is not None and re.match(r"^\d{4}", str(x[1]))]
    d = pd.DataFrame(data, columns=["season_label","sown_000ac","sown_000ha","harv_000ac","harv_000ha","yield_bu_ac","yield_kg_ha","prod_000bu","prod_000mt"])
    d.insert(0,"season",s); d.to_csv(f"{OUT}dcs_national_{s.lower()}.csv", index=False); print(s, len(d), d.season_label.iloc[0], d.season_label.iloc[-1])
# district production (Maha / Yala)
long = []
for s in ("Maha", "Yala"):
    f = glob.glob(f"Production-{s}_Season*.xlsx")[0]; r = rows(f)
    hi = next(i for i,x in enumerate(r) if any(str(c).upper()=="DISTRICT" for c in x if c))
    hdr = r[hi]; c0 = next(i for i,c in enumerate(hdr) if c and str(c).upper()=="DISTRICT")
    for x in r[hi+1:]:
        if x[c0] is None: continue
        for j in range(c0+1, len(hdr)):
            if hdr[j] is None: continue
            long.append((s, str(x[c0]).strip(), str(hdr[j]), x[j]))
p = pd.DataFrame(long, columns=["season","district","year_label","prod_000mt"]); p.to_csv(OUT+"dcs_district_production_long.csv", index=False)
print("district prod", p.shape, p.district.nunique(), sorted(p.district.unique())[-6:], p.year_label.unique()[[0,1,2,-1]])
# district extents / yield: 4 sub-columns per year
long = []
for kind, pat in (("sown","Sown_Extent"),("harvested","Harvested_Extent"),("yield","Average_Yeild")):
    for s in ("Maha","Yala"):
        f = glob.glob(f"{pat}-{s}_Season*.xlsx")[0]; r = rows(f)
        hi = next(i for i,x in enumerate(r) if any(c and str(c).strip().upper()=="DISTRICT" for c in x))
        yr, sub = r[hi], r[hi+1]; c0 = next(i for i,c in enumerate(yr) if c and str(c).strip().upper()=="DISTRICT")
        cur = None; cols = {}
        for j in range(c0+1, len(yr)):
            if yr[j] is not None: cur = str(yr[j])
            if sub[j] is not None: cols[j] = (cur, str(sub[j]).strip())
        for x in r[hi+2:]:
            if x[c0] is None: continue
            for j,(y,t) in cols.items(): long.append((kind, s, str(x[c0]).strip(), y, t, x[j]))
e = pd.DataFrame(long, columns=["measure","season","district","year_label","type","value"]); e.to_csv(OUT+"dcs_district_extent_yield_long.csv", index=False)
print("district extents", e.shape, e.district.nunique(), e.type.unique(), e.value.map(lambda v: v=='-').mean().round(3))
print(sorted(e.district.unique()))
