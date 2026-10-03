"""Check every 'explicit' topic's evidence quote really occurs in the syllabus text. Drops/flags failures."""
import json, glob, re, pathlib, sys
from common import ROOT

def norm(s):
    s = s.lower().replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = re.sub(r"-\s*\n\s*", "", s)           # line-break hyphenation
    s = re.sub(r"[^a-z0-9]+", " ", s)         # ignore punctuation/columns/bullets
    return re.sub(r"\s+", " ", s).strip()

STOP = set("and or of the a an in on for to with from by as at is are be using use via basic basics introduction intro overview "
           "concepts concept fundamentals topics topic principles applications application techniques methods analysis systems system general".split())
SUPPORT_MIN = 0.5


def stems(s):
    return {w[:5] for w in re.findall(r"[a-z0-9]+", s.lower()) if w not in STOP and len(w) > 2}


tot = ok = 0; fails = []; unsupported = []
for f in sorted(glob.glob(str(ROOT / "data/extracted/*.json"))):
    p = pathlib.Path(f); x = json.load(open(f, encoding="utf8"))
    tp = ROOT / f"data/syllabi/{p.stem}.txt"
    src = norm(tp.read_text(encoding="utf8", errors="ignore")) if tp.exists() else ""
    if len(src) < 800:                        # scanned: cannot verify mechanically
        x["verification"] = "unverifiable_scanned"; json.dump(x, open(f, "w", encoding="utf8"), indent=1); continue
    for t in x.get("topics", []):
        if t.get("kind") != "explicit": continue
        tot += 1
        raw = t.get("evidence", "")
        ev = norm(raw)
        segs = [norm(x) for x in re.split(r"\.\.\.|…", raw) if len(norm(x)) >= 4]
        exact = bool(ev) and (ev in src or (len(ev) > 40 and ev[:40] in src and ev[-40:] in src) or (len(segs) > 1 and all(x in src for x in segs)))
        words = ev.split()
        srcset = set(src.split())
        recall = sum(w in srcset for w in words) / len(words) if words else 0
        t["evidence_verified"] = "exact" if exact else ("fuzzy" if recall >= 0.85 else "failed")
        # The quote must also SUPPORT the topic label: key terms of the topic should appear in its evidence.
        ts, es = stems(t["topic"]), stems(raw + " " + t.get("where", ""))
        t["support"] = round(len(ts & es) / len(ts), 2) if ts else 1.0
        t["supported"] = t["support"] >= SUPPORT_MIN
        if not t["supported"]: unsupported.append((p.stem, t["topic"], raw[:80], t["support"]))
        good = t["evidence_verified"] != "failed"; ok += good
        if not good: fails.append((p.stem, t["topic"], raw[:90], round(recall, 2)))
    json.dump(x, open(f, "w", encoding="utf8"), indent=1)
print(f"{ok}/{tot} evidence quotes verified (exact or >=85% token overlap) ({100*ok/max(tot,1):.1f}%)")
for s in fails[:25]: print(" FAIL", s)
print(len(fails), "failures total")
print(f"{len(unsupported)}/{tot} topics NOT supported by their own evidence (support < {SUPPORT_MIN}); sample:")
for u in sorted(unsupported, key=lambda r: r[3])[:30]: print("  UNSUPPORTED", u)
