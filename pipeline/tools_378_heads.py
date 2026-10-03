"""Download every C S 378 section syllabus in the window and print the first lines of each (to read the real topic)."""
import json, re, subprocess
from common import fetch, ROOT

S = json.load(open(ROOT / "data/sections.json", encoding="utf8"))
out = ROOT / "data/syllabi"; out.mkdir(exist_ok=True)
seen = {}
for s in S:
    if s["course"] != "378" or not s["syllabus_path"]:
        continue
    m = re.search(r"/download/(\d+)/", s["syllabus_path"])
    if not m:
        continue
    sid = m.group(1)
    if sid in seen:
        continue
    pdf = out / f"{sid}.pdf"
    if not pdf.exists():
        pdf.write_bytes(fetch("https://utdirect.utexas.edu" + s["syllabus_path"], binary=True))
    txt = out / f"{sid}.txt"
    if not txt.exists():
        subprocess.run(["pdftotext", "-layout", str(pdf), str(txt)], check=False)
    seen[sid] = (s["term"], s["instructors"][0])
ov = json.load(open(ROOT / "data/overrides.json", encoding="utf8"))["offering_titles"]
for sid, (term, inst) in seen.items():
    if sid in ov:
        continue
    t = (out / f"{sid}.txt").read_text(encoding="utf8", errors="ignore")
    lines = [re.sub(r"\s+", " ", l).strip() for l in t.splitlines() if l.strip()][:7]
    print(f"{sid}|{term}|{inst}|" + " // ".join(lines)[:260])
print(len(seen), "distinct 378 syllabi;", sum(1 for s in seen if s in ov), "already titled")
