"""Cross-check: courses seen in the CS dept class listing vs the syllabi repository, per term."""
import json, importlib
from common import ROOT

t = importlib.import_module("02_terms")
sections = json.load(open(ROOT / "data/sections.json", encoding="utf8"))
for year, name in [(2025, "Fall"), (2026, "Spring"), (2026, "Fall")]:
    term = f"{name} {year}"
    dept = t.next_term(year, name)
    repo_courses = {s["course"] for s in sections if s["term"] == term}
    dept_courses = {s["course"] for s in dept}
    print(f"{term}: repo {len(repo_courses)} courses | dept listing {len(dept_courses)} courses | "
          f"in dept only: {sorted(dept_courses - repo_courses)} | in repo only: {sorted(repo_courses - dept_courses)}")
