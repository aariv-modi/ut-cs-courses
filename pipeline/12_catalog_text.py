"""Authoritative description + prerequisite text per course, with provenance and conflict flags -> data/catalog_text.json

Descriptions : UT catalog 2026-27 A-Z page (current catalog).
Prerequisites: 1) UT Registrar course schedule wording (Spring 2027, else Fall 2026) - the current official text
               2) 2025-26 catalog A-Z page (project owner's chosen reference)
               3) CS department course list, 4) syllabus-stated prerequisite
               Disagreements between 1) and 2), and between the official text and a current syllabus, are recorded as flags.
"""
import json, re, html, glob
from bs4 import BeautifulSoup
from common import ROOT

ds = json.load(open(ROOT / "data/dataset.json", encoding="utf8"))["courses"]
reg = json.load(open(ROOT / "data/registrar/parsed.json", encoding="utf8"))
ov = json.load(open(ROOT / "data/overrides.json", encoding="utf8"))


def parse_atoz(path):
    out = {}
    h = open(path, encoding="utf8", errors="ignore").read()
    for h5 in BeautifulSoup(h, "html.parser").select("h5"):
        head = html.unescape(h5.get_text()).replace("\xa0", " ").strip()
        m = re.match(r"C S ([\dX]\d{2}[A-Z]?)\.\s*(.*?)\.?$", head)
        if not m:
            continue
        body, n = [], h5.find_next_sibling()
        while n is not None and n.name not in ("h5", "h3", "h4"):
            body.append(re.sub(r"\s+", " ", n.get_text(" ")).strip()); n = n.find_next_sibling()
        out[m.group(1)[1:]] = " ".join(body).strip()
    return out


new = parse_atoz(ROOT / "data/raw/atoz_cs.html")        # 2026-27: descriptions only
old = parse_atoz(ROOT / "data/raw/atoz_2526.html")      # 2025-26: description + notes + prerequisites
tidy = lambda s: re.sub(r"\s+([,.;:])", r"\1", re.sub(r"\s+", " ", s)).strip()   # catalog text has "313E , 314" spacing

CUT = r"(?:Designed to accommodate|Restricted enrollment|Partially taught|Taught as a Web|Course number may be repeated|Additional hour|Hour\(s\) to be arranged|Laboratory hour|Priority is for|Same As|Restricted to|See department headnote|Only one of the following|May not be counted)"


def reg_prereq(line):
    if not line or line.startswith("NO PREREQ"):
        return None
    m = re.match(r"Prerequisite[s]?:\s*(.*)", line)
    body = m.group(1) if m else line
    body = re.split(r"\s+" + CUT, body)[0].strip()
    return tidy(body)


def split_old(text):
    m = re.search(r"Prerequisite[s]?:\s*(.*)$", text)
    pre = tidy(re.split(r"\s+" + CUT, m.group(1))[0]) if m else None
    desc = text[:m.start()] if m else text
    return desc.strip(), pre



NOTE_KEEP = re.compile(r"^(Restricted|May not be counted|Only one of the following|Same As|Taught as a Web|Partially taught|Course number may be repeated|Priority is for)", re.I)


def notes_from(text):
    """Student-relevant notes (restrictions, crediting limits, cross-listing, delivery mode), one short sentence each."""
    t = re.sub(r"See department headnote", "", text or "")
    sents = re.split(r"(?<=[.])\s+(?=[A-Z])", t)
    out = []
    for x in sents:
        x = tidy(x)
        if NOTE_KEEP.match(x) and len(x) <= 240:
            out.append(x if x.endswith(".") else x + ".")
    return out


# registrar prerequisite per course code (first heading seen; Spring 2027 preferred over Fall 2026)
reg_by_code = {}
for term in ("Fall 2026", "Spring 2027"):                          # later overwrites earlier -> Spring 2027 wins
    for r in reg[term]:
        p = reg["_prereqs"].get(r["heading"])
        if p is not None and r["code"]:
            reg_by_code[r["code"]] = (reg_prereq(p), term, r["heading"])

norm_nums = lambda s: set(re.findall(r"\b\d{3}[A-Z]?\b", s or ""))
canon = lambda s: re.sub(r"[^a-z0-9]", "", (s or "").lower())
syl_prereq = {}
for f in glob.glob(str(ROOT / "data/extracted/*.json")):
    x = json.load(open(f, encoding="utf8"))
    if x.get("prerequisites_stated"):
        syl_prereq[f.split("\\")[-1].split("/")[-1][:-5]] = x["prerequisites_stated"]

out = {}
for key, c in ds.items():
    base = c.get("base_number") or key
    code = base
    rec = {"description": None, "description_source": None, "prerequisites": None, "prerequisites_source": None, "flags": [], "registrar": None, "catalog_2526": None}
    # ---- description
    if not c.get("base_number"):
        d = new.get(code[1:], "")
        if d:
            rec["description"], rec["description_source"] = tidy(d), "UT catalog 2026-27"
        else:
            od, _ = split_old(old.get(code[1:], ""))
            if od:
                rec["description"], rec["description_source"] = tidy(od), "UT catalog 2025-26 (no 2026-27 text)"
    # ---- prerequisites
    o = old.get(code[1:])
    cat_pre = split_old(o)[1] if o else None
    rec["catalog_2526"] = cat_pre
    rec["notes"] = []
    r = reg_by_code.get(code)
    rec["registrar"] = {"text": r[0], "term": r[1]} if r else None
    if r and (r[0] or r[2]):
        rec["prerequisites"] = r[0] or "None listed"
        rec["prerequisites_source"] = f"UT Registrar course schedule ({r[1]})"
        if cat_pre and canon(cat_pre) != canon(r[0]):
            rec["flags"].append({"type": "registrar_vs_catalog_2526", "registrar": r[0], "catalog_2526": cat_pre})
        if not cat_pre and r[0] and o is not None:
            rec["flags"].append({"type": "registrar_has_prereq_catalog_none", "registrar": r[0]})
    elif cat_pre:
        rec["prerequisites"], rec["prerequisites_source"] = cat_pre, "UT catalog 2025-26"
    elif c.get("prerequisites_text") and c.get("prerequisites_source") == "department":
        rec["prerequisites"], rec["prerequisites_source"] = c["prerequisites_text"], "UT CS department course list (not in registrar or 2025-26 catalog)"
        rec["flags"].append({"type": "dept_page_only"})
    # ---- restrictions & notes (registrar wording preferred; 2025-26 catalog sentences as supplement)
    regline = reg["_prereqs"].get(r[2]) if r else None
    notes = notes_from(regline) if regline else []
    for sent in (notes_from(o) if o else []):        # 2025-26 catalog sentences not already given by the registrar
        if re.match(r"(May not be counted|Only one of the following|Restricted)", sent, re.I) and not any(canon(sent) == canon(x) for x in notes):
            notes.append(sent)
    rec["notes"] = notes
    # ---- syllabus-stated (most recent syllabus per instructor)
    for e in c["instructors"]:
        sid = e.get("syllabus_id")
        if sid and sid in syl_prereq and rec["prerequisites"]:
            sn, rn = norm_nums(syl_prereq[sid]), norm_nums(rec["prerequisites"])
            if sn and not (sn <= rn or rn <= sn):
                rec["flags"].append({"type": "syllabus_differs", "instructor": e["name"], "syllabus_says": syl_prereq[sid][:300]})
    out[key] = rec

json.dump(out, open(ROOT / "data/catalog_text.json", "w", encoding="utf8"), indent=1)
import collections
print("descriptions:", collections.Counter(r["description_source"] for r in out.values()))
print("prerequisites:", collections.Counter((r["prerequisites_source"] or "none").split(" (")[0] for r in out.values()))
print("flags:", collections.Counter(f["type"] for r in out.values() for f in r["flags"]))
