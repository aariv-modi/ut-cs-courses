"""Merge registrar sections into the repository sections -> data/sections.json.

Rule for "offered" (project owner's decision):
  * a syllabus in the repository  => the section was offered (even if the registrar later marks it cancelled)
  * otherwise the registrar must show at least one non-cancelled section
Spring 2027 comes from the registrar only (no syllabi exist yet); cancelled sections do not count.
Conflicts and ambiguous cases are written to data/offered_conflicts.json for the audit report.
"""
import json, re, collections
from common import ROOT

repo = json.load(open(ROOT / "data/sections_repo.json", encoding="utf8"))
reg = json.load(open(ROOT / "data/registrar/parsed.json", encoding="utf8"))
ov = json.load(open(ROOT / "data/overrides.json", encoding="utf8"))
SPLIT = set(ov.get("split_courses", []))
TITLES = ov["registrar_titles"]
WINDOW = ["Fall 2025", "Spring 2026", "Fall 2026", "Spring 2027"]
UNDERGRAD = lambda code: bool(code) and int(code[1:3]) < 80


def name_tokens(n):
    return [t for t in re.findall(r"[a-z]+", n.lower())]


def same_person(reg_name, repo_name):
    """Registrar 'LAST, FIRST MIDDLE' vs repository 'First Last' (initial-only first names allowed)."""
    last, first = [p.strip() for p in reg_name.split(",", 1)] if "," in reg_name else (reg_name.split()[-1], " ".join(reg_name.split()[:-1]))
    lt, ft = name_tokens(last), name_tokens(first)
    rt = name_tokens(repo_name)
    if not lt or not ft or not rt:
        return False
    surname_ok = all(t in rt for t in lt) or rt[-1] in lt
    return surname_ok and rt[0][:1] == ft[0][:1]


def topic_key(code, title, syllabus_path=None):
    """Course key used downstream: plain code, or code + canonical topic for variable-topic numbers."""
    if code not in SPLIT:
        return code
    m = re.search(r"/download/(\d+)/", syllabus_path or "")
    if m and m.group(1) in ov["offering_titles"]:
        return f"{code}|{ov['offering_titles'][m.group(1)]}"
    m = re.search(r"/doc/([a-z0-9]+)", syllabus_path or "")
    if m and m.group(1) in ov["web_syllabus_titles"]:
        return f"{code}|{ov['web_syllabus_titles'][m.group(1)]}"
    return f"{code}|{TITLES[title.strip().upper()]}"


# repository coverage: (key, term) -> list of instructor names that have a repository section
cover = collections.defaultdict(list)
for s in repo:
    cover[(topic_key(s["course"], s["title"], s["syllabus_path"]), s["term"])] += s["instructors"]

merged = list(repo)
conflicts = {"registrar_only_added": [], "ambiguous_cancelled_mix": [], "syllabus_but_registrar_cancelled_or_absent": [], "unmapped_titles": []}
reg_keys = set()
for term in WINDOW:
    for r in reg[term]:
        code = r["code"]
        if not code or not UNDERGRAD(code) or code in ("109", "309"):   # 109/309 (Think Lab / FRI numbers) are outside the project scope
            continue
        if code in SPLIT and r["title"].upper() not in TITLES:
            conflicts["unmapped_titles"].append([term, r["heading"]]); continue
        key = topic_key(code, r["title"])
        live = r["sections"] - r["cancelled"]
        reg_keys.add((key, term, live > 0))
        if live <= 0:
            continue                                   # all sections cancelled: registrar adds nothing
        names = r.get("instructors_live", r["instructors"]) if term == "Spring 2027" else r["instructors"]
        have = cover.get((key, term), [])
        missing = [n for n in names if not any(same_person(n, h) for h in have)]
        if term != "Spring 2027" and not names and not have:
            missing = [None]                            # live section with no instructor listed (e.g. independent study)
        if term == "Spring 2027" and not names:
            missing = [None]
        excl = {(a, b, c) for a, b, c, _ in ov.get("registrar_exclude_instructors", [])}
        missing = [n for n in missing if (term, code, n) not in excl]   # verified section-by-section: their only sections are cancelled
        for n in missing:
            if r["cancelled"] and n is not None and have:
                conflicts["ambiguous_cancelled_mix"].append([term, r["heading"], n, f"{r['sections']} sections, {r['cancelled']} cancelled"])
            merged.append({"term": term, "course": code, "unique": "", "title": r["title"], "instructors": [n] if n else [],
                           "syllabus_path": None, "cvs": [], "source": "registrar"})
            conflicts["registrar_only_added"].append([term, r["heading"], n])
            cover[(key, term)] += [n] if n else []

# repository sections whose registrar heading has no live section (kept per the project owner's rule; reported)
live_keys = {(k, t) for k, t, lv in reg_keys if lv}
for s in repo:
    k = topic_key(s["course"], s["title"], s["syllabus_path"])
    if (k, s["term"]) not in live_keys:
        conflicts["syllabus_but_registrar_cancelled_or_absent"].append([s["term"], k, s["instructors"], s["syllabus_path"]])
dedup = {json.dumps(x): x for x in conflicts["syllabus_but_registrar_cancelled_or_absent"]}
conflicts["syllabus_but_registrar_cancelled_or_absent"] = list(dedup.values())


# ---- normalise instructor names: registrar 'LAST, FIRST M' -> 'First Last'; upgrade initial-only repository first names --------
def _pretty(reg_name):
    last, first = [p.strip() for p in reg_name.split(",", 1)]
    last_t = re.sub(r"(?<![A-Za-z])Mc(\w)", lambda m: "Mc" + m.group(1).upper(), last.title())
    toks = first.split()
    given = toks[1] if len(toks[0]) == 1 and len(toks) > 1 else toks[0]   # 'C GREG' -> Greg
    return f"{given.title()} {last_t}"

reg_names = {n for t in WINDOW for r in reg[t] for n in r["instructors"]}
repo_names = {n for s in merged if s.get("source") != "registrar" for n in s["instructors"]}

def _upgrade(n):                                   # repository name with an initial-only first name
    if len(n.split()[0]) > 1:
        return n
    m = [r for r in reg_names if same_person(r, n)]
    return (_pretty(m[0]).split()[0] + " " + " ".join(n.split()[1:])) if len({_pretty(x) for x in m}) == 1 else n

def _display(n):
    if s_src == "registrar":
        m = [r for r in repo_names if same_person(n, r)]
        up = {_upgrade(x) for x in m}
        return next(iter(up)) if len(up) == 1 else _pretty(n)
    return _upgrade(n)

ALIAS = ov.get("instructor_aliases", {})
for s in merged:
    s_src = s.get("source")
    s["instructors"] = sorted({ALIAS.get(x, x) for x in (_display(n) for n in s["instructors"])})

json.dump(merged, open(ROOT / "data/sections.json", "w", encoding="utf8"), indent=1)
json.dump(conflicts, open(ROOT / "data/offered_conflicts.json", "w", encoding="utf8"), indent=1)
print(len(repo), "repository sections +", len(conflicts["registrar_only_added"]), "registrar-only sections =", len(merged))
for k, v in conflicts.items():
    print(f"  {k}: {len(v)}")
