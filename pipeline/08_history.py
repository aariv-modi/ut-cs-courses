"""For courses with no section in the window, find the most recent earlier Fall/Spring term they were taught.

Source: syllabi repository only (Fall 2010 on); the CS dept listing also shows cancelled sections, so it is not evidence. Summers are never searched.
Output: data/history.json  {course_number: "Spring 2019" | null}
"""
import json, importlib
from common import ROOT

t = importlib.import_module("02_terms")
ds = json.load(open(ROOT / "data/dataset.json", encoding="utf8"))
need = {n for n, c in ds["courses"].items() if c["status"] != "active"}

# terms before the window, newest first: Spring 2025 ... Fall 2010 (no summers)
terms = []
for y in range(2025, 2009, -1):
    if y < 2025:
        terms.append((y, "Fall", 9))
    terms.append((y, "Spring", 2))
terms = [x for x in terms if not (x[0] == 2010 and x[1] == "Spring")]   # repository starts Fall 2010
terms = sorted(set(terms), key=lambda x: (x[0], 1 if x[1] == "Fall" else 0), reverse=True)

found = {}
for y, name, code in terms:
    if not need - set(found):
        break
    seen = {s["course"] for s in t.past_term(y, name, code)}   # repository (registrar section records) only
    for n in need & seen:
        found.setdefault(n, f"{name} {y}")
    print(f"{name} {y}: {len(seen)} courses; resolved {len(found)}/{len(need)}")

# Courses with no repository record at all: see whether the CS dept listing ever showed them (2016+). Kept separate and
# labelled "unverified" in the UI, because the dept listing also contains cancelled sections.
dept_only = {}
for y, name, code in terms:
    if y < 2016 or not (need - set(found) - set(dept_only)):
        continue
    for n in (need - set(found)) & {s["course"] for s in t.next_term(y, name)}:
        dept_only.setdefault(n, f"{name} {y}")
json.dump(dept_only, open(ROOT / "data/history_dept_only.json", "w", encoding="utf8"), indent=1)
print("dept-listing-only (unverified):", dept_only)

out = {n: found.get(n) for n in sorted(need)}
json.dump(out, open(ROOT / "data/history.json", "w", encoding="utf8"), indent=1)
print("never found since Fall 2010:", [n for n, v in out.items() if not v])
