"""Diff offered terms and instructors between the pre-audit snapshot and the current data/dataset.json."""
import json
from common import ROOT

old = json.load(open(ROOT / "data/snapshots/pre_audit/dataset.json", encoding="utf8"))["courses"]
new = json.load(open(ROOT / "data/dataset.json", encoding="utf8"))["courses"]


def terms(c):
    return list(c["terms_offered"]) + (["Spring 2027"] if c["offered_next"] else [])


added = sorted(set(new) - set(old)); removed = sorted(set(old) - set(new))
print("courses added:", added); print("courses removed:", removed)
n_t = n_i = 0
for k in sorted(set(old) & set(new)):
    a, b = old[k], new[k]
    ta, tb = terms(a), terms(b)
    ia = {e["name"]: e["terms"] for e in a["instructors"]}; ib = {e["name"]: e["terms"] for e in b["instructors"]}
    if ta != tb:
        n_t += 1; print(f"TERMS {k}: {ta} -> {tb}")
    if ia != ib:
        n_i += 1
        gone = {n: t for n, t in ia.items() if n not in ib}; came = {n: t for n, t in ib.items() if n not in ia}
        chg = {n: (ia[n], ib[n]) for n in ia if n in ib and ia[n] != ib[n]}
        print(f"INSTR {k}: removed {gone} | added {came} | changed {chg}")
print(f"\ncourses with changed terms: {n_t}; changed instructors: {n_i}")
