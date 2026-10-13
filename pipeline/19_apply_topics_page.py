"""CS 314: credit BOTH instructors (Kaur, Scott) with every topic on the course topics-list page
(https://www.cs.utexas.edu/~scottm/cs314/handouts/topicsList.htm), as the project owner asked.

* Kaur's syllabus PDF links to the page (hidden hyperlink). Scott's syllabus points to his course web page and numbers
  exam coverage "Topics 1 - 9" etc. but does not print this URL; the credit for him is recorded as such.
* Adds the page's numbered MAJOR topics only (sub-topics are not rows; merged into existing labels where they match); rows that already exist (same concept) just gain
  the missing instructor's credit. The "Prerequisite knowledge" list and "Course Introduction" are not treated as topics.
* Quotes come from data/supplemental/314_topicsList.txt (accepted by the validator via topic_in extra_text_files).
Idempotent: rows/credits added by an earlier run (marked supplemental) are removed first.
"""
import json, re
from common import ROOT

URL = "https://www.cs.utexas.edu/~scottm/cs314/handouts/topicsList.htm"
page = json.load(open(ROOT / "data/supplemental/314_topicsList.json", encoding="utf8"))
path = ROOT / "data/topic_out/314.json"
d = json.load(open(path, encoding="utf8"))
KAUR, SCOTT = "Amrita Kaur", "Michael Scott"
norm = lambda s: re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()

# ---- undo a previous run
d["topics"] = [t for t in d["topics"] if not t.get("supplemental")]
for t in d["topics"]:
    for k in [k for k, c in t["coverage"].items() if c.get("supplemental")]:
        del t["coverage"][k]

MAJOR_TO_EXISTING = {
    "Complexity / Algorithm Analysis": ["Algorithm analysis"], "Encapsulation": ["Encapsulation"], "Inheritance": ["Inheritance"],
    "Polymorphism": ["Polymorphism"], "Iterators": ["Iterators"], "Recursion": ["Recursion"],
    "Searching, Simple Sorts": ["Sorting and searching algorithms"], "Stacks": ["Stacks"], "Queues": ["Queues"],
    "Trees": ["Trees"], "Binary Search Trees": ["Binary search trees"], "Heaps": ["Heaps"], "Graphs": ["Graphs"],
    "The Trie data structure. Implementation and uses.": ["Tries"], "Hash tables": ["Hash tables"],
    "Dynamic Programming": ["Dynamic programming"], "Functional Programming in Java via streams.": ["Functional programming in Java"],
    "Maps, Sets": ["Maps", "Sets"], "Red-Black Trees": ["Balanced binary search trees"], "Fast Sorting": ["Sorting and searching algorithms"],
}
MAJOR_NEW_LABEL = {"Generics": "Generics", "Interfaces": "Interfaces", "Abstract Classes": "Abstract classes", "Linked Lists": "Linked lists",
                   "Recursive Backtracking": "Recursive backtracking",
                   "Hoffman code tress": "Huffman code trees"}
SKIP_MAJOR = {"Course Introduction", "General skills"}
SHORT = [
    ("rules of algorithm analysis", "Rules of algorithm analysis (what counts as one statement)"),
    ("application of Big O, determining t(N)", "Determining t(N), the exact statement count of code"),
    ("application of Big O, determining f(n)", "Determining f(n), the approximate statement count of code"),
    ("various Big O functions", "Common Big O functions, O(1) through O(N!)"),
    ("given a Big O function, a value of N", "Predicting runtime for different values of N"),
    ("overriding the, equals", "Overriding equals; instanceof vs. getClass()"),
]


def short_label(text):
    for pre, lab in SHORT:
        if text.lower().startswith(pre.lower()):
            return lab
    t = re.sub(r"\s+", " ", text).strip()
    return t if len(t) <= 88 else t[:85].rsplit(" ", 1)[0] + "..."


rows = {norm(t["label"]): t for t in d["topics"]}
log = {"new_rows": 0, "credited_existing": 0}


def credit(row, instructor, evidence, where, as_written):
    if instructor in row["coverage"]:
        return False
    row["coverage"][instructor] = {"status": "stated", "evidence": evidence, "where": where, "as_written": as_written, "supplemental": "topicsList.htm"}
    return True


def where_for(instr, n, major):
    base = f"Course topics list page (topicsList.htm), topic {n}: {major}"
    if instr == KAUR:
        return base + ". Linked from this syllabus."
    return base + ". Scott's syllabus points to his course web page and numbers exam coverage as topics, but does not print this URL."


def add(label, evidence, n, major, as_written):
    key = norm(label)
    row = rows.get(key)
    if row is None:
        row = {"label": label, "coverage": {}, "supplemental": True}
        d["topics"].append(row); rows[key] = row; log["new_rows"] += 1
    for instr in (KAUR, SCOTT):
        if credit(row, instr, evidence, where_for(instr, n, major), as_written):
            log["credited_existing"] += 0 if row.get("supplemental") else 1
    return row


for t in page["topics"]:
    n, major = t["n"], t["topic"]
    if major not in SKIP_MAJOR:
        for lab in MAJOR_TO_EXISTING.get(major, [MAJOR_NEW_LABEL.get(major, short_label(major))]):
            add(lab, major, n, major, major)

# instructors: both point at the page as their detailed topic source
for who in (KAUR, SCOTT):
    d["instructors"][who]["external_schedule_url"] = URL
d["notes"] = (d.get("notes") or "") + " Topics-list page (topicsList.htm) credited to both instructors at the project owner's request."
json.dump(d, open(path, "w", encoding="utf8"), indent=1, ensure_ascii=False)
print(log, "| total rows now:", len(d["topics"]))
