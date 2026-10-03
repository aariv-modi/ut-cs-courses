"""Group syllabi that cite textbook chapters into batches (same book -> same agent) for TOC resolution."""
import json, glob, re, pathlib, collections
from common import ROOT

ds = json.load(open(ROOT / "data/dataset.json", encoding="utf8"))
uses = collections.defaultdict(list)
for num, c in ds["courses"].items():
    for e in c["instructors"]:
        if e.get("syllabus_id"):
            uses[e["syllabus_id"]].append({"course": "C S " + num, "instructor": e["name"], "term": e["pdf_term"]})

items = []
for f in sorted(glob.glob(str(ROOT / "data/extracted/*.json"))):
    x = json.load(open(f, encoding="utf8"))
    if x.get("chapter_refs"):
        sid = pathlib.Path(f).stem
        items.append({"syllabus_id": sid, "text_file": f"data/syllabi/{sid}.txt", "uses": uses.get(sid, []),
                      "textbooks_listed": x.get("textbooks"), "chapter_refs": x["chapter_refs"]})

def book_key(it):
    b = (it["chapter_refs"][0].get("textbook") or "zzz").lower()
    return re.sub(r"[^a-z]", "", b)[:12]

items.sort(key=book_key)
n = 4
(ROOT / "data/chapter_batches").mkdir(exist_ok=True)
size = -(-len(items) // n)
for i in range(n):
    chunk = items[i * size:(i + 1) * size]
    json.dump(chunk, open(ROOT / f"data/chapter_batches/cb_{i+1}.json", "w", encoding="utf8"), indent=1)
    print(i + 1, len(chunk), "syllabi:", sorted({(r.get("textbook") or "?")[:35] for it in chunk for r in it["chapter_refs"]})[:6])
