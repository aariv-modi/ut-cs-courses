"""Merge courses + sections into the per-course dataset the site needs."""
import json, re, datetime, collections
from common import ROOT

TERM_ORDER = ["Fall 2025", "Spring 2026", "Fall 2026"]   # past/current, oldest -> newest
NEXT = "Spring 2027"
REPO_BASE = "https://utdirect.utexas.edu"

courses = json.load(open(ROOT / "data/courses.json", encoding="utf8"))
sections = json.load(open(ROOT / "data/sections.json", encoding="utf8"))

# ---- variable-topic courses (e.g. C S 378): every distinct topic becomes its own course -------------
ov = json.load(open(ROOT / "data/overrides.json", encoding="utf8"))
slug = lambda t: re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")

def topic_of(s):
    p = s.get("syllabus_path") or ""
    m = re.search(r"/download/(\d+)/", p)
    if m: return ov["offering_titles"].get(m.group(1))
    m = re.search(r"/doc/([a-z0-9]+)", p)
    if m: return ov["web_syllabus_titles"].get(m.group(1))
    return ov["dept_listing_titles"].get(s["title"].strip())

for base in ov.get("split_courses", []):
    base_rec = courses.pop(base)
    for s in sections:
        if s["course"] != base: continue
        topic = topic_of(s)
        if not topic:
            raise SystemExit(f"no topic title for {base} section {s['term']} {s['instructors']} {s['title']} {s['syllabus_path']}")
        key = f"{base}-{slug(topic)}"
        s["course"] = key
        courses.setdefault(key, dict(base_rec, number=key, title=topic, base_number=base))
# ------------------------------------------------------------------------------------------------------

def split_name(n):
    if "," in n:
        last, first = [p.strip() for p in n.split(",", 1)]
    else:
        parts = n.split(); last, first = parts[-1], " ".join(parts[:-1])
    return last, first

def surname_key(n): return split_name(n)[0].lower()

# canonical full names seen in the repository (past terms), keyed by surname
full_names = {}
for s in sections:
    if s["term"] in TERM_ORDER and s.get("source") != "dept":
        for i in s["instructors"]:
            full_names.setdefault(surname_key(i), set()).add(i)

def canon(name, course):
    """Map a (possibly abbreviated) name to a full repository name if surname + initial agree."""
    last, first = split_name(name)
    cands = [f for f in full_names.get(last.lower(), []) if f.lower().split()[0][:1] == first[:1].lower()]
    if len(cands) == 1: return cands[0], True
    # surname-only fallback within the same course in the window
    same = {f for s in sections if s["course"] == course and s["term"] in TERM_ORDER for f in s["instructors"] if surname_key(f) == last.lower()}
    if len(same) == 1: return next(iter(same)), True
    pretty = f"{first.title()} {last.title()}".strip() if len(first) > 1 else f"{first}. {last.title()}"
    return pretty, False

out = {}
for num, c in courses.items():
    secs = [s for s in sections if s["course"] == num]
    by_term = {t: [s for s in secs if s["term"] == t] for t in TERM_ORDER + [NEXT]}
    taught_past = [t for t in TERM_ORDER if by_term[t]]
    rec = dict(c)
    rec["terms_offered"] = taught_past
    rec["last_offered"] = taught_past[-1] if taught_past else None
    rec["offered_next"] = bool(by_term[NEXT])
    rec["status"] = "active" if (taught_past or by_term[NEXT]) else "potentially_retired"
    rec["section_counts"] = {t: len(v) for t, v in by_term.items() if v}
    # instructors: past terms with their most recent syllabus; next term from dept listing
    inst = {}
    cands = collections.defaultdict(list)                  # instructor -> [(term index, path, section title)]
    for ti, t in enumerate(TERM_ORDER):
        for s in by_term[t]:
            for name in s["instructors"]:                  # names already normalised in 02b
                e = inst.setdefault(name, {"name": name, "terms": [], "syllabus_path": None, "syllabus_term": None, "pdf_path": None, "pdf_term": None, "pdf_title": None, "syllabus_title": None, "name_verified": True})
                if t not in e["terms"]: e["terms"].append(t)
                if s["syllabus_path"]:
                    cands[name].append((ti, s["syllabus_path"], s["title"]))
    pdf_id = lambda p: int(re.search(r"/download/(\d+)/", p).group(1)) if "/download/" in p else -1
    for name, cs_ in cands.items():                        # "most recent syllabus": latest term; within a term the highest PDF id (any is acceptable)
        e = inst[name]
        ti, p, ttl = max(cs_, key=lambda x: (x[0], pdf_id(x[1]), x[1]))
        e["syllabus_path"], e["syllabus_term"], e["syllabus_title"] = p, TERM_ORDER[ti], ttl
        pdfs = [x for x in cs_ if "/download/" in x[1]]
        if pdfs:
            ti2, p2, ttl2 = max(pdfs, key=lambda x: (x[0], pdf_id(x[1])))
            e["pdf_path"], e["pdf_term"], e["pdf_title"] = p2, TERM_ORDER[ti2], ttl2
    for s in by_term[NEXT]:
        for raw in s["instructors"]:
            name, ok = raw, True        # registrar names are official and complete
            e = inst.setdefault(name, {"name": name, "terms": [], "syllabus_path": None, "syllabus_term": None, "pdf_path": None, "pdf_term": None, "pdf_title": None, "syllabus_title": None, "name_verified": ok})
            if NEXT not in e["terms"]: e["terms"].append(NEXT)
    for e in inst.values():
        pp = e.pop("pdf_path"); e["pdf_url"] = REPO_BASE + pp if pp else None
        p = e.pop("syllabus_path"); e["syllabus_url"] = (p if p and p.startswith("http") else REPO_BASE + p) if p else None
    rec["instructors"] = sorted(inst.values(), key=lambda e: (e["terms"][-1] != NEXT, e["name"]))
    out[num] = rec

json.dump({"generated": datetime.date.today().isoformat(), "window": TERM_ORDER + [NEXT], "courses": out},
          open(ROOT / "data/dataset.json", "w", encoding="utf8"), indent=1)
a = [c for c in out.values() if c["status"] == "active"]
print(len(out), "courses;", len(a), "active;", len(out) - len(a), "potentially retired")
print("offered next:", sum(c["offered_next"] for c in out.values()))
print("instructor entries:", sum(len(c["instructors"]) for c in out.values()),
      "| with syllabus:", sum(1 for c in out.values() for e in c["instructors"] if e["syllabus_url"]),
      "| next-term only (no syllabus yet):", sum(1 for c in out.values() for e in c["instructors"] if not e["syllabus_url"]),
      "| unverified names:", sum(1 for c in out.values() for e in c["instructors"] if not e["name_verified"]))
print(json.dumps({k: v for k, v in out["429"].items() if k in ("last_offered","offered_next","instructors","status")}, indent=1)[:1500])
