"""Reconcile the site's offered terms with the registrar, per course (non-topic courses) and for topic courses by number."""
import json, collections
from common import ROOT

ds = json.load(open(ROOT / "data/snapshots/pre_audit/site_data/dataset.json", encoding="utf8"))["courses"]
reg = json.load(open(ROOT / "data/registrar/parsed.json", encoding="utf8"))
TERMS = ["Fall 2025", "Spring 2026", "Fall 2026", "Spring 2027"]
VAR = {"378", "378H", "329E", "109", "309"}

# registrar: code -> term -> (sections, cancelled)
R = collections.defaultdict(dict)
for t in TERMS:
    for r in reg[t]:
        a = R[r["code"]].setdefault(t, [0, 0])
        a[0] += r["sections"]; a[1] += r["cancelled"]

site = collections.defaultdict(set)
for k, c in ds.items():
    base = c.get("base_number") or k
    for t in c["terms_offered"]:
        site[base].add(t)
    if c["offered_next"]:
        site[base].add("Spring 2027")

only_site, only_reg, all_cancelled = [], [], []
for code in sorted(set(R) | set(site)):
    for t in TERMS:
        live = code in R and t in R[code] and R[code][t][0] - R[code][t][1] > 0
        canc_only = code in R and t in R[code] and R[code][t][0] == R[code][t][1]
        s = t in site[code]
        if s and not live:
            (all_cancelled if canc_only else only_site).append((code, t))
        if live and not s:
            only_reg.append((code, t))
print("A) site says offered, registrar has ONLY CANCELLED sections:", all_cancelled)
print("B) site says offered, registrar has NO section at all:", [x for x in only_site if x[0] not in VAR])
print("   (variable-topic numbers:", [x for x in only_site if x[0] in VAR], ")")
print("C) registrar has a live section, site does NOT list the term:", [x for x in only_reg if x[0] not in ("109", "309")])
print("   (109/309 not in scope:", sorted({x[0] for x in only_reg if x[0] in ("109", "309")}), ")")
