"""Apply pass-2 verifier corrections (data/topic_verify/*.json) to data/topic_out; log every change to data/verify_changes.json."""
import json, glob, os
from common import ROOT
log = []
for vf in sorted(glob.glob(str(ROOT / "data/topic_verify/[!_]*.json"))):
    v = json.load(open(vf, encoding="utf8")); c = v["course"]
    p = ROOT / f"data/topic_out/{c}.json"; d = json.load(open(p, encoding="utf8"))
    T = {t["label"]: t for t in d["topics"]}
    for r in v.get("remove", []):
        t = T.get(r["topic"])
        if t and r["instructor"] in t["coverage"]:
            old = t["coverage"].pop(r["instructor"]); log.append({"course": c, "op": "remove", **r, "was": old["evidence"]})
        else: log.append({"course": c, "op": "remove-skipped", **r})
    for a in v.get("add", []):
        t = T.get(a["topic"])
        if not t: log.append({"course": c, "op": "add-skipped-no-topic", **a}); continue
        t["coverage"][a["instructor"]] = {k: a.get(k, "") for k in ("status", "evidence", "where", "as_written")}
        log.append({"course": c, "op": "add", **a})
    for m in v.get("merge", []):
        labs = [l for l in m["labels"] if l in T]
        if len(labs) < 2: log.append({"course": c, "op": "merge-skipped", **m}); continue
        cov = {}
        for l in labs:
            for k, x in T[l]["coverage"].items(): cov.setdefault(k, x)
        first = T[labs[0]]
        d["topics"] = [t for t in d["topics"] if t["label"] not in labs[1:]]
        first["label"] = m["into"]; first["coverage"] = cov
        T = {t["label"]: t for t in d["topics"]}
        log.append({"course": c, "op": "merge", **m})
    for x in v.get("drop_topics", []):
        d["topics"] = [t for t in d["topics"] if t["label"] != x["label"]]; log.append({"course": c, "op": "drop", **x})
    d["topics"] = [t for t in d["topics"] if t["coverage"]]
    json.dump(d, open(p, "w", encoding="utf8"), indent=1, ensure_ascii=False)
json.dump(log, open(ROOT / "data/verify_changes.json", "w", encoding="utf8"), indent=1, ensure_ascii=False)
import collections; print(collections.Counter(x["op"] for x in log))
for x in log:
    if "skipped" in x["op"]: print(x)
