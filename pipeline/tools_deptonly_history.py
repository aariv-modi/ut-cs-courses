"""Evidence check: how often does the CS dept listing show a course/term that the syllabi repository has no record of?"""
import importlib
t = importlib.import_module("02_terms")

rows = []
for y in range(2016, 2026):
    for name, code in (("Spring", 2), ("Fall", 9)):
        repo = {s["course"] for s in t.past_term(y, name, code)}
        dept = {s["course"] for s in t.next_term(y, name)}
        rows.append((f"{name} {y}", sorted(dept - repo), sorted(repo - dept), len(dept), len(repo)))
tot_dept_only = sum(len(r[1]) for r in rows)
tot_repo_only = sum(len(r[2]) for r in rows)
for r in rows:
    print(f"{r[0]:12} dept-courses {r[3]:2} repo-courses {r[4]:2} | dept-only {r[1]} | repo-only {r[2]}")
print("total dept-only (course,term) pairs:", tot_dept_only, "| repo-only:", tot_repo_only)
