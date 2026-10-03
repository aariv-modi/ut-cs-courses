"""Parse the registrar schedule extracts (data/registrar/*) into data/registrar/parsed.json.

Registrar = UT Registrar course schedule (login-gated; read by the project owner's signed-in session).
Per term: one record per course heading: code, heading title, instructors, #sections, #cancelled.
Spring 2027 additionally has per-section rows (unique number, instructor, status).
"""
import json, re, collections
from common import ROOT

R = ROOT / "data/registrar"
TERMS = {"20259": "Fall 2025", "20262": "Spring 2026", "20269": "Fall 2026", "20272": "Spring 2027"}


def split_names(s):
    return [x.strip() for x in s.split(";") if x.strip() and x.strip() != "(none listed)"]


def code_of(h):
    m = re.match(r"C S (\d{3}[A-Z]?)\s+(.*)", h)
    return (m.group(1), m.group(2).strip()) if m else (None, h)


parsed = {}
for tc in ("20259", "20262", "20269"):
    recs = []
    for line in (R / f"{tc}_agg.tsv").read_text(encoding="utf8").splitlines():
        h, ins, n, canc = line.split("|")
        code, title = code_of(h)
        recs.append({"code": code, "heading": h, "title": title, "instructors": split_names(ins), "sections": int(n), "cancelled": int(canc)})
    parsed[TERMS[tc]] = recs

# Spring 2027: per-section rows
sec = collections.OrderedDict()
rows = []
for line in (R / "20272_sections.tsv").read_text(encoding="utf8").splitlines():
    h, u, ins, st = line.split("|")
    rows.append({"heading": h, "unique": u, "instructors": split_names(ins), "status": st})
    sec.setdefault(h, []).append(rows[-1])
recs = []
for h, ss in sec.items():
    code, title = code_of(h)
    live = [s for s in ss if "cancel" not in s["status"]]
    recs.append({"code": code, "heading": h, "title": title,
                 "instructors": sorted({n for s in ss for n in s["instructors"]}),
                 "instructors_live": sorted({n for s in live for n in s["instructors"]}),
                 "sections": len(ss), "cancelled": len(ss) - len(live), "uniques": [s["unique"] for s in ss]})
parsed["Spring 2027"] = recs

# prerequisites (registrar wording), keyed by heading
pre = {}
for f in ("20272_prereqs.tsv", "20269_prereqs_extra.tsv"):
    for line in (R / f).read_text(encoding="utf8").splitlines():
        h, p = line.split("|", 1)
        pre[h] = p.strip()
parsed["_prereqs"] = pre
parsed["_sections_2027"] = rows
json.dump(parsed, open(R / "parsed.json", "w", encoding="utf8"), indent=1)
for t, r in parsed.items():
    if not t.startswith("_"):
        print(f"{t}: {len(r)} headings, {sum(x['sections'] for x in r)} sections, {sum(x['cancelled'] for x in r)} cancelled")
print("prereq headings:", len(pre))
