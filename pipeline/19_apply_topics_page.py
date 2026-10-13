"""CS 314: the topic list is the course topics-list page
(https://www.cs.utexas.edu/~scottm/cs314/handouts/topicsList.htm), applied identically to both instructors
(Kaur, Scott), at the project owner's request: both sections teach the same content from that page.

The page's numbered major topics (and a few sub-topics that are main topics in their own right) are whittled to
the same granularity as other courses. "Course Introduction", "General skills" headings and the
"Prerequisite knowledge" list are not topics. Every row is credited to both instructors with the same verbatim quote
from data/supplemental/314_topicsList.txt (accepted by the validator via topic_in extra_text_files).
Re-runnable: it rebuilds the topic list from scratch each time.
"""
import json
from common import ROOT

URL = "https://www.cs.utexas.edu/~scottm/cs314/handouts/topicsList.htm"
page = json.load(open(ROOT / "data/supplemental/314_topicsList.json", encoding="utf8"))
path = ROOT / "data/topic_out/314.json"
d = json.load(open(path, encoding="utf8"))
INSTRUCTORS = ["Amrita Kaur", "Michael Scott"]

# label -> (page topic number, verbatim quote: a major-topic title or a sub-topic under it)
ROWS = [
    ("Algorithm analysis", 2, "Complexity / Algorithm Analysis"),
    ("Encapsulation", 3, "Encapsulation"),
    ("Reasoning about programs with pre/post conditions", 3, "pre and post conditions, writing and checking"),
    ("Inheritance", 4, "Inheritance"),
    ("Polymorphism", 5, "Polymorphism"),
    ("Generics", 6, "Generics"),
    ("Interfaces", 7, "Interfaces"),
    ("Iterators", 8, "Iterators"),
    ("Abstract classes", 9, "Abstract Classes"),
    ("Maps", 10, "Maps, Sets"),
    ("Sets", 10, "Maps, Sets"),
    ("Linked lists", 11, "Linked Lists"),
    ("Recursion", 12, "Recursion"),
    ("Recursive backtracking", 13, "Recursive Backtracking"),
    ("Sorting and searching algorithms", 14, "Searching, Simple Sorts"),
    ("Stacks", 15, "Stacks"),
    ("Queues", 16, "Queues"),
    ("Trees", 18, "Trees"),
    ("Binary search trees", 19, "Binary Search Trees"),
    ("Balanced binary search trees", 20, "Red-Black Trees"),
    ("Huffman code trees", 21, "Hoffman code tress"),
    ("Heaps", 22, "Heaps"),
    ("Priority queues", 22, "priority queue interface and implementation"),
    ("Graphs", 23, "Graphs"),
    ("Tries", 24, "The Trie data structure. Implementation and uses."),
    ("Hash tables", 25, "Hash tables"),
    ("Dynamic programming", 26, "Dynamic Programming"),
    ("Functional programming in Java", 27, "Functional Programming in Java via streams."),
    ("Debugging", 28, "debug code using a debugger"),
]
majors = {t["n"]: t for t in page["topics"]}
EXTRA = {"Sorting and searching algorithms": " (also topic 17: Fast Sorting)"}

topics = []
for label, n, quote in ROWS:
    m = majors[n]
    assert quote == m["topic"] or quote in m["subtopics"], (label, quote)
    where = f"Course topics list page (topicsList.htm), topic {n}: {m['topic']}{EXTRA.get(label, '')}"
    cov = {"status": "stated", "evidence": quote, "where": where, "as_written": quote}
    topics.append({"label": label, "coverage": {i: dict(cov) for i in INSTRUCTORS}})
d["topics"] = topics
for who in INSTRUCTORS:
    d["instructors"][who]["external_schedule_url"] = URL
d["notes"] = ("Topic list taken from the course topics-list page (topicsList.htm), which both sections teach; "
              "applied identically to both instructors at the project owner's request.")
json.dump(d, open(path, "w", encoding="utf8"), indent=1, ensure_ascii=False)
print(len(topics), "topics, identical for", INSTRUCTORS)
