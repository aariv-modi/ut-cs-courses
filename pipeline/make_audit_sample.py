"""Random audit sample: topics (precision) and whole syllabi (recall). Seeded for reproducibility."""
import json, glob, random, pathlib
from common import ROOT

random.seed(20261002)
pool, files = [], sorted(glob.glob(str(ROOT / "data/extracted/*.json")))
for f in files:
    x = json.load(open(f, encoding="utf8"))
    sid = pathlib.Path(f).stem
    for t in x.get("topics", []):
        if t.get("kind") == "explicit" and t.get("supported", True) and t.get("evidence_verified") in ("exact", "fuzzy"):
            pool.append({"syllabus_id": sid, "text_file": f"data/syllabi/{sid}.txt", "topic": t["topic"], "evidence": t["evidence"], "where": t.get("where")})
precision = random.sample(pool, 80)
rich = [pathlib.Path(f).stem for f in files if json.load(open(f, encoding="utf8")).get("detail_level") in ("weekly_schedule", "topic_list")]
recall = random.sample(rich, 6)
json.dump({"precision_sample": precision, "recall_syllabi": [{"syllabus_id": s, "text_file": f"data/syllabi/{s}.txt", "extracted_file": f"data/extracted/{s}.json"} for s in recall]},
          open(ROOT / "data/audit_sample.json", "w", encoding="utf8"), indent=1)
print(len(pool), "eligible topics; sampled", len(precision), "topics and", len(recall), "syllabi")
