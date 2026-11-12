#!/usr/bin/env python3
"""Extract the price tables from HARTI Weekly Food Commodities Bulletins.

Uses `pdftotext -bbox` (poppler) word coordinates, so no third-party Python
packages are needed.

    python extract.py                # one sample PDF per year  -> tables_sample/
    python extract.py --all          # every PDF                -> tables/
    python extract.py f1.pdf f2.pdf  # specific files           -> tables/ (or -o DIR)

Output: one long-format CSV per table type (rice, vegetables, farmgate ...).

Matrix tables (location x commodity, plus the Colombo annexes):
  week_start, week_end, table, section, row, group, column, min, max
Summary tables (Pettah/Colombo wholesale & retail):
  week_start, week_end, table, section, commodity, min, max, avg_this_week,
  avg_last_week, avg_last_year, chg_last_week_pct, chg_last_year_pct
Farmgate table: same, but older bulletins also carry Rs/kg changes
  (chg_*_rs); columns a bulletin does not have are left empty.

`section` is the nearest heading above the row (e.g. "Rice > Local"). Empty
cells ("-") are simply missing rows/blank values. Table numbers drift between
years, so files are named by content (retail_rice, summary_wholesale, ...).
"""
import argparse
import csv
import html
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
PDF_DIR = HERE / "harti_bulletins"

WORD = re.compile(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>')
NUMT = re.compile(r"-?\d[\d,]*\.\d+")
TITLE = re.compile(r"^(Table\s*\d+|Annex\s*\d+|Farmgate)", re.I)
WEEK = re.compile(r"Week\s*\d+", re.I)
HEADER_WORDS = set("commodity range average price change compared to this last week year "
                   "rs/kg rs piece kg".split())

SUMMARY_COLS = ["min", "max", "avg_this_week", "avg_last_week", "avg_last_year",
                "chg_last_week_pct", "chg_last_year_pct"]
FARM_COLS = SUMMARY_COLS[:5] + ["chg_last_week_rs", "chg_last_week_pct",
                                "chg_last_year_rs", "chg_last_year_pct"]
HEAD_MATRIX = ["week_start", "week_end", "table", "section", "row", "group", "column", "min", "max"]
HEAD_SUMMARY = ["week_start", "week_end", "table", "section", "commodity"] + SUMMARY_COLS
HEAD_FARM = ["week_start", "week_end", "table", "section", "commodity"] + FARM_COLS


# ----------------------------------------------------------------- reading
def read_pages(pdf):
    xml = subprocess.run(["pdftotext", "-bbox", str(pdf), "-"],
                         capture_output=True, text=True, check=True).stdout
    for chunk in xml.split("<page ")[1:]:
        yield [(float(a), float(b), float(c), float(d), html.unescape(t))
               for a, b, c, d, t in WORD.findall(chunk)]


def to_lines(words, ytol=4.5):
    lines = []
    for w in sorted(words, key=lambda w: (w[1] + w[3]) / 2):
        ym = (w[1] + w[3]) / 2
        if lines and abs(ym - lines[-1][0]) <= ytol:
            lines[-1][1].append(w)
        else:
            lines.append([ym, [w]])
    return [sorted(ws, key=lambda w: w[0]) for _, ws in lines]


def tokens(ws):
    """[(kind, x0, x1, value)] kind: N number, D dash (empty/range marker), T text."""
    out = []
    for x0, _, x1, _, t in ws:
        t2 = t.replace("−", "-").replace("–", "-")
        if NUMT.fullmatch(t2):
            out.append(("N", x0, x1, float(t2.replace(",", ""))))
        elif re.fullmatch(r"-+", t2):
            out.append(("D", x0, x1, None))
        elif re.fullmatch(r"\d[\d,]*\.\d+-+", t2):  # "600.00-" glued
            m = len(t2.rstrip("-"))
            xm = x0 + (x1 - x0) * m / len(t2)
            out.append(("N", x0, xm, float(t2.rstrip("-").replace(",", ""))))
            out.append(("D", xm, x1, None))
        else:
            out.append(("T", x0, x1, t))
    if len(out) > 1 and out[0][0] == "T" and re.fullmatch(r"\d{1,2}", out[0][3]):
        out = out[1:]  # page number in the margin
    return out


def text_of(toks):
    return re.sub(r"\s+", " ", " ".join(t[3] for t in toks if t[0] == "T")).strip()


def is_data(toks):
    return any(t[0] in "ND" for t in toks)


# --------------------------------------------------------------- utilities
def clusters(xs, gap):
    """Group 1-D positions split at gaps > gap; return [(mean, count)]."""
    out = []
    for x in sorted(xs):
        if out and x - out[-1][-1] <= gap:
            out[-1].append(x)
        else:
            out.append([x])
    return [(sum(g) / len(g), len(g)) for g in out]


def columns_exact(xs, n):
    for gap in (4, 5, 6, 7, 8, 10, 12, 14):
        c = clusters(xs, gap)
        if len(c) == n:
            return [m for m, _ in c]
    return None


def nearest(cs, x):
    return min(range(len(cs)), key=lambda i: abs(cs[i] - x))


def slug_for(title):
    t = title.lower()
    if "annex" in t:
        for k, s in ((r"\brice\b", "rice"), ("vegetable", "vegetables"), ("fruit", "fruits"), ("fish", "fish")):
            if re.search(k, t):
                return "annex_retail_" + s
        return None  # annex 05 food composition etc.
    if "farmgate" in t:
        return "farmgate"
    w = "wholesale" if "wholesale" in t else "retail" if "retail" in t else None
    if w is None:
        return None
    if re.match(r"table\s*\d+\s*[:\-]?\s*(pettah|colombo)", t) and "selected" not in t:
        return f"summary_{w}"
    for k, s in (("sub", "subsidiary"), ("dried fish", "dried_fish"),
                 ("fish", "fish_eggs" if w == "wholesale" else "fish"), ("meat", "meat"),
                 ("vegetable", "vegetables"), ("fruit", "fruits"), (r"\brice\b", "rice")):
        if re.search(k, t):
            return f"{w}_{s}"
    return None


# ---------------------------------------------------------- page structure
def split_page(lines):
    """-> (title, header_lines, body_lines) as lists of token-lists, or None."""
    L = [tokens(ws) for ws in lines]
    L = [t for t in L if t]
    if not L:
        return None
    first = text_of(L[0])
    if not TITLE.match(first):
        return None
    title, i = first, 1
    while i < len(L) and not WEEK.search(title) and "contd" not in title.lower() and i < 3:
        nxt = text_of(L[i])
        if WEEK.search(nxt) or (not is_data(L[i]) and len(L[i]) <= 6 and not re.search(r"\d", nxt)):
            title += " " + nxt
            i += 1
        else:
            break
    if i < len(L) and WEEK.search(text_of(L[i])) and not is_data(L[i]) and len(L[i]) <= 12:
        i += 1
    return title, L[i:]


def split_header(rest, slug):
    d = next((k for k, t in enumerate(rest) if is_data(t)), len(rest))
    if slug == "farmgate" or slug.startswith("summary"):
        def hdr(t):
            return t and all(set(re.sub(r"[^a-z/]+", " ", w[3].lower()).split()) <= HEADER_WORDS
                             for w in t if w[0] == "T")
        h = max([k for k in range(d) if hdr(rest[k])], default=-1) + 1
        return rest[:h], rest[h:]
    if slug.startswith("annex"):
        h = next((k for k in range(d) if any(w[3].upper() == "CROP" for w in rest[k])), -1) + 1
        return rest[:h], rest[h:]
    return rest[:d], rest[d:]


def header_labels(header, centers):
    """(group, leaf) per column centre from header text positions."""
    lines = []
    for toks in header:
        ph = []
        for _, x0, x1, t in [w for w in toks if w[0] == "T"]:
            if ph and x0 - ph[-1][1] < 5:
                ph[-1] = (ph[-1][0], x1, ph[-1][2] + " " + t)
            else:
                ph.append((x0, x1, t))
        ph = [p for p in ph if p[1] >= centers[0] - 14]  # drop the row-label column header
        if ph:
            lines.append(ph)
    res = []
    for cx in centers:
        leaf, groups = "", []
        for k, ph in enumerate(lines):
            if k == len(lines) - 1:
                leaf = min(ph, key=lambda p: abs((p[0] + p[1]) / 2 - cx))[2]
            else:
                cur = None
                for a, b, t in sorted(ph):
                    if a - 8 <= cx:
                        cur = t
                if cur:
                    groups.append(cur)
        res.append((" | ".join(groups), leaf))
    return res


def walk(body, col_of, edges):
    """Yield (block, section, label, {col: [values]}) for each data row.
    col_of(x) -> column index for N/D tokens; edges = x where each block's labels begin."""
    nb = len(edges)
    sect = [[] for _ in range(nb)]
    after_data = [True] * nb

    def blk_text(x):
        return max(i for i in range(nb) if edges[i] <= x + 0.5)

    for toks in body:
        per = [{"t": [], "cells": defaultdict(list), "data": False} for _ in range(nb)]
        for kind, x0, x1, v in toks:
            if kind == "T":
                per[blk_text(x0)]["t"].append(v)
            else:
                c, b = col_of((x0 + x1) / 2)
                per[b]["data"] = True
                if kind == "N":
                    per[b]["cells"][c].append((x0, v))
        for b, d in enumerate(per):
            label = " ".join(d["t"]).strip()
            if not label:
                continue
            if d["data"]:
                after_data[b] = True
                if d["cells"]:
                    yield b, " > ".join(sect[b]), label, d["cells"]
            else:
                if after_data[b]:
                    sect[b] = []
                sect[b].append(label)
                after_data[b] = False


# ------------------------------------------------------------- extraction
def extract_pdf(pdf, rows):
    m = re.match(r"(\d{4}-\d\d-\d\d)_to_(\d{4}-\d\d-\d\d)", pdf.name)
    ws, we = m.groups() if m else ("", "")
    warn = []
    for pno, words in enumerate(read_pages(pdf), 1):
        sp = split_page(to_lines(words))
        if not sp:
            continue
        title, rest = sp
        slug = slug_for(title)
        if not slug or not rest:
            continue
        tid = re.sub(r"\s+", " ", TITLE.match(title).group(1))
        base = [ws, we, tid]
        header, body = split_header(rest, slug)
        if not body:
            continue

        if slug == "farmgate" or slug.startswith("summary"):
            hl = next((t for t in header if any(w[3].lower() == "commodity" for w in t)), [])
            nblk = max(1, sum(1 for w in hl if w[3].lower() == "commodity"))
            cols = SUMMARY_COLS if slug != "farmgate" else (
                FARM_COLS if re.search("change", " ".join(text_of(t) for t in header), re.I)
                else FARM_COLS[:2] + ["avg_this_week"])
            k = len(cols)
            xs = [(w[1] + w[2]) / 2 for t in body for w in t if w[0] == "N"]
            cs = columns_exact(xs, k * nblk)
            if cs is None:
                warn.append(f"{pdf.name} p{pno} {tid}: could not find {k * nblk} numeric columns")
                continue
            # label column of block b starts just right of block b-1's last numeric column
            edges = [-1e9]
            for b in range(1, nblk):
                lastc = b * k - 1
                ends = [w[2] for t in body for w in t
                        if w[0] == "N" and nearest(cs, (w[1] + w[2]) / 2) == lastc]
                edges.append(max(ends, default=cs[lastc] + 8) + 1)
            col_of = lambda x: (nearest(cs, x) % k, nearest(cs, x) // k)
            for b, sect, label, cells in walk(body, col_of, edges):
                rec = [None] * k
                for c, vals in cells.items():
                    rec[c] = sorted(vals)[0][1]
                rows[slug].append(base + [sect, label] + rec + [None] * (len(FARM_COLS if slug == "farmgate" else cols) - k))
        else:
            dx = [(w[1] + w[2]) / 2 for t in body for w in t if w[0] == "D"]
            cl = clusters(dx, 6)
            if not cl:
                continue
            top = max(n for _, n in cl)
            cs = [m for m, n in cl if n >= 0.2 * top]
            labs = header_labels(header, cs) if header else [("", f"col{j}") for j in range(len(cs))]
            col_of = lambda x: (nearest(cs, x), 0)
            for b, sect, label, cells in walk(body, col_of, [-1e9]):
                for j, vals in sorted(cells.items()):
                    vals = [v for _, v in sorted(vals)]
                    rows[slug].append(base + [sect, label, labs[j][0], labs[j][1], vals[0], vals[-1]])
    return warn


def write(rows, outdir):
    outdir.mkdir(parents=True, exist_ok=True)
    for slug, data in sorted(rows.items()):
        head = HEAD_FARM if slug == "farmgate" else HEAD_SUMMARY if slug.startswith("summary") else HEAD_MATRIX
        if slug.startswith("summary"):
            data = [r[:len(head)] for r in data]
        with open(outdir / f"{slug}.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(head)
            w.writerows(data)
        print(f"{slug:24s} {len(data):7d} rows")


def sample_files():
    out = []
    for yd in sorted(p for p in PDF_DIR.iterdir() if p.is_dir()):
        pdfs = sorted(yd.glob("*.pdf"))
        if pdfs:
            out.append(pdfs[len(pdfs) // 2])
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdfs", nargs="*", type=Path)
    ap.add_argument("--all", action="store_true", help="process every PDF")
    ap.add_argument("-o", "--out", type=Path)
    a = ap.parse_args()
    if a.pdfs:
        files, out = a.pdfs, a.out or HERE / "tables"
    elif a.all:
        files, out = sorted(PDF_DIR.glob("*/*.pdf")), a.out or HERE / "tables"
    else:
        files, out = sample_files(), a.out or HERE / "tables_sample"
    rows, warns = defaultdict(list), []
    for f in files:
        warns += extract_pdf(f, rows)
    write(rows, out)
    for w in warns:
        print("WARN", w, file=sys.stderr)
    print(f"{len(files)} PDFs, {len(warns)} warnings -> {out}")


if __name__ == "__main__":
    main()
