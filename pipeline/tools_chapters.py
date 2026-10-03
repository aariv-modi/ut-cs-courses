"""Quick stats: how much of the data depends on textbook chapter references."""
import json, glob, collections, pathlib
from common import ROOT

n = 0; books = collections.Counter(); per = []
files = sorted(glob.glob(str(ROOT / "data/extracted/*.json")))
for f in files:
    x = json.load(open(f, encoding="utf8"))
    cr = x.get("chapter_refs") or []
    if cr:
        n += 1
        per.append((len(cr), pathlib.Path(f).stem, x.get("detail_level"), len(x.get("topics") or [])))
        for r in cr:
            books[(r.get("textbook") or "?")[:70]] += 1
print("syllabi with chapter refs:", n, "of", len(files), "| total refs", sum(p[0] for p in per))
print("detail_level == chapters_only:", [p for p in per if p[2] == "chapters_only"])
print("ref-heavy, few explicit topics (refs>=3, topics<8):", [p for p in per if p[0] >= 3 and p[3] < 8])
for b, c in books.most_common(20):
    print(c, b)
tb = collections.Counter()
for f in files:
    for t in json.load(open(f, encoding="utf8")).get("textbooks") or []:
        tb[(t.get("title") or "")[:60]] += 1
print("distinct textbook titles:", len(tb))
