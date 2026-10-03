"""Prepare per-course topic-merge inputs: every (instructor, topic) gets an id; agents group ids into rows."""
import json, string
from common import ROOT

ds = json.load(open(ROOT / "site/src/data/dataset.json", encoding="utf8"))
out_dir = ROOT / "data/merge_in"; out_dir.mkdir(exist_ok=True)
courses = []
for k, c in ds["courses"].items():
    es = [e for e in c["instructors"] if e.get("topics")]
    if len(es) < 2:
        continue
    inst = []
    for i, e in enumerate(es):
        key = string.ascii_uppercase[i]
        inst.append({"key": key, "name": e["name"],
                     "topics": [{"id": f"{key}{j+1}", "topic": t["topic"]} for j, t in enumerate(e["topics"])]})
    json.dump({"course": k, "code": c["code"], "title": c["title"], "instructors": inst},
              open(out_dir / f"{k}.json", "w", encoding="utf8"), indent=1)
    courses.append((k, sum(len(i["topics"]) for i in inst)))
# balance into 5 batches by topic count
NB = 9
batches = [[] for _ in range(NB)]
loads = [0] * NB
for k, n in sorted(courses, key=lambda x: -x[1]):
    i = loads.index(min(loads)); batches[i].append(k); loads[i] += n
for i, b in enumerate(batches):
    json.dump(b, open(ROOT / f"data/merge_in/_batch_{i+1}.json", "w"), indent=1)
    print(i + 1, loads[i], "topics:", b)
