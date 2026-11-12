"""Chunked, low-memory profile of CSV files. Usage: profile_csv.py file [file...]
Skips leading '#' comment lines; prints rows, per-column dtype/null%/nunique(capped)/min/max/top values."""
import sys, io, pandas as pd, numpy as np
from collections import Counter

def prof(path, chunk=200_000, cap=2000):
    with open(path, errors="replace") as f:
        skip = 0; meta = []
        for line in f:
            if line.startswith("#"): skip += 1; meta.append(line.strip())
            else: break
    n = 0; nulls = Counter(); uniq = {}; mn = {}; mx = {}; dt = {}; top = {}; head = None
    for ch in pd.read_csv(path, skiprows=skip, chunksize=chunk, low_memory=False, on_bad_lines="skip"):
        if head is None: head = ch.head(2)
        n += len(ch)
        for c in ch.columns:
            s = ch[c]; nulls[c] += int(s.isna().sum()); dt.setdefault(c, str(s.dtype))
            if str(s.dtype) == "object" or c not in uniq or len(uniq.get(c, ())) < cap:
                u = uniq.setdefault(c, set())
                if len(u) < cap: u.update(s.dropna().unique()[: cap])
            if pd.api.types.is_numeric_dtype(s) and s.notna().any():
                mn[c] = min(mn.get(c, np.inf), s.min()); mx[c] = max(mx.get(c, -np.inf), s.max())
            elif s.notna().any():
                try:
                    a, b = s.dropna().min(), s.dropna().max()
                    mn[c] = min(mn.get(c, a), a); mx[c] = max(mx.get(c, b), b)
                except Exception: pass
            if c in uniq and len(uniq[c]) <= 8:
                top.setdefault(c, Counter()).update(s.dropna().astype(str))
    print(f"\n### {path}\nrows={n}  meta={meta[:4]}")
    for c in head.columns:
        u = len(uniq[c]); t = ""
        if c in top and u <= 8: t = " top=" + str(dict(top[c].most_common(8)))
        print(f"- {c} [{dt[c]}] null={nulls[c]/max(n,1):.1%} nuniq={'>='+str(cap) if u>=cap else u} min={str(mn.get(c))[:30]} max={str(mx.get(c))[:30]}{t[:120]}")
for p in sys.argv[1:]: prof(p)
