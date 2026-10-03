"""Merge extracted syllabus data into the dataset the site consumes, and build the topic search index.

Inputs : data/dataset.json, data/extracted/*.json, data/derived/*.json (textbook-chapter topics, optional),
         data/aliases.json (concept -> alias list, optional), data/overrides.json (known-bad syllabi, optional)
Outputs: site/src/data/dataset.json, site/public/search-index.json
"""
import json, re, collections, pathlib
from common import ROOT

ds = json.load(open(ROOT / "data/dataset.json", encoding="utf8"))
ext_dir, der_dir = ROOT / "data/extracted", ROOT / "data/derived"
overrides = json.load(open(ROOT / "data/overrides.json", encoding="utf8")) if (ROOT / "data/overrides.json").exists() else {}
aliases = json.load(open(ROOT / "data/aliases.json", encoding="utf8")) if (ROOT / "data/aliases.json").exists() else {}
bad = overrides.get("exclude_syllabus_ids", {})
catalog_text = json.load(open(ROOT / "data/catalog_text.json", encoding="utf8"))
history_dept_only = json.load(open(ROOT / "data/history_dept_only.json", encoding="utf8")) if (ROOT / "data/history_dept_only.json").exists() else {}
history = json.load(open(ROOT / "data/history.json", encoding="utf8")) if (ROOT / "data/history.json").exists() else {}


def load(path):
    return json.load(open(path, encoding="utf8")) if path.exists() else None


def _hit(needle, text):
    return re.search(r"(?<![a-z0-9])" + re.escape(needle.lower()) + r"s?(?![a-z0-9])", text) is not None


def alias_for(topic):
    """Related search terms for a topic. Word-boundary match on the concept name or on a distinctive alias
    (multi-word or >=5 chars); search-only: results found this way are labelled 'related-term match' in the UI."""
    t = topic.lower()
    out = []
    for concept, al in aliases.items():
        keys = [concept] + [a for a in al if " " in a or len(a) >= 5]
        if any(_hit(k, t) for k in keys):
            out += [concept] + al
    return " ".join(dict.fromkeys(out))


removed_links = []


def clean_url(u, who):
    """Public, valid URLs only: drop Canvas (login-gated) and non-URL text; add a missing https://."""
    if not u:
        return None
    u = u.strip()
    if re.search(r"instructure\.com|canvas", u, re.I):
        removed_links.append({"who": who, "url": u, "reason": "Canvas (login-gated, not public)"}); return None
    if not re.match(r"^(https?://|www\.|[A-Za-z0-9.-]+\.(edu|com|org|io|net)(/|$))", u):
        removed_links.append({"who": who, "url": u, "reason": "not a URL"}); return None
    if not u.startswith("http"):
        u = "https://" + u
    return u


HEDGE = re.compile(r"(?<![a-z])(may|might|possibly|time permitting|if time|time allows|tentative|optional|extra topics?|as time)(?![a-z])", re.I)
INFERRED = re.compile(r"(?<![a-z])(inferred|infer|uncertain|presumed|likely|assum\w*|probably|unclear|garbled)(?![a-z])", re.I)
index, stats, rejected =[], collections.Counter(), []
for num, c in ds["courses"].items():
    prereq_votes, desc_votes = [], []
    if c["status"] != "active":   # last Fall/Spring term before the window (summers never searched); None = no record since Fall 2010
        c["last_offered_earlier"] = history.get(num)
        if not c["last_offered_earlier"] and num in history_dept_only:   # dept listing only: shown as unverified
            c["last_listed_unverified"] = history_dept_only[num]
    for e in c["instructors"]:
        sid = e.get("syllabus_id")
        x = load(ext_dir / f"{sid}.json") if sid else None
        if not x:
            continue
        if sid in bad:
            e["syllabus_excluded"] = bad[sid]
            stats["excluded"] += 1
            continue
        e["offering_title"] = None if c.get("base_number") else overrides.get("offering_titles", {}).get(sid)
        td = (x.get("term_in_document") or "").strip()
        e["document_term"] = td or None
        if td and e.get("pdf_term") and e["pdf_term"].lower() not in td.lower():
            e["syllabus_note"] = f"This syllabus is dated {td}, though it is filed under {e['pdf_term']}."
        e["detail_level"] = x.get("detail_level")
        e["external_schedule_url"] = clean_url(x.get("external_schedule_url"), f"{c['code']} / {e['name']}")
        e["textbooks"] = x.get("textbooks") or []
        rejected += [(sid, t["topic"], t.get("evidence", "")) for t in (x.get("topics") or []) if t.get("kind") == "explicit" and (t.get("evidence_verified") == "failed" or not t.get("supported", True))]
        topics = [t for t in (x.get("topics") or []) if t.get("kind") == "explicit" and t.get("evidence")
                  and t.get("evidence_verified") in ("exact", "fuzzy", None)   # quote must occur in the syllabus
                  and t.get("supported", True)]                                  # and must support the topic label
        d = load(der_dir / f"{sid}.json")
        if d:
            topics += d.get("topics", [])
        seen, uniq = set(), []
        for t in topics:
            k = t["topic"].strip().lower()
            if k not in seen:
                seen.add(k); uniq.append(t)
        for t in uniq:   # topics the syllabus itself hedges ("may include", "time permitting", optional ...)
            if t.get("kind") == "explicit":
                t["hedged"] = bool(HEDGE.search(t.get("evidence", "") + " " + t.get("where", "")))
            else:   # textbook-derived: weaker when the agent flagged the book/section mapping as inferred or uncertain
                t["hedged"] = bool(INFERRED.search(t.get("evidence", "")))
        e["topics"] = uniq
        if x.get("prerequisites_stated"):
            prereq_votes.append(x["prerequisites_stated"])
        if x.get("course_description_stated"):
            desc_votes.append(x["course_description_stated"])
        stats["syllabi_with_topics" if uniq else "syllabi_no_topics"] += 1
        for t in uniq:
            index.append({"id": len(index), "course": c["code"], "title": e.get("offering_title") or c["title"], "instructor": e["name"], "term": e["pdf_term"],
                          "topic": t["topic"], "kind": "possible" if (t.get("hedged") and t["kind"] == "explicit") else t["kind"], "evidence": t.get("evidence", ""), "aliases": alias_for(t["topic"]),
                          "url": f"/course/{num.lower()}/"})
    if c.get("base_number"):   # topic course split out of a variable-topic number: the syllabus is the authority
        c["description_is_generic"] = not desc_votes
        if desc_votes:
            c["description"] = collections.Counter(desc_votes).most_common(1)[0][0]
    ct = catalog_text.get(num, {})                 # authoritative text from 12_catalog_text.py
    if not c.get("base_number") and ct.get("description"):
        c["description"], c["description_source"] = ct["description"], ct["description_source"]
    c["prerequisites_text"] = ct.get("prerequisites") or ""
    c["prerequisites_source"] = ct.get("prerequisites_source") or ""
    notes = []
    for e in c["instructors"]:                     # instructor-stated prerequisites, shown when they add to / differ from the official text
        sid = e.get("syllabus_id"); xx = load(ext_dir / f"{sid}.json") if sid else None
        ps = xx.get("prerequisites_stated") if xx else None
        differs = any(f["type"] == "syllabus_differs" and f.get("instructor") == e["name"] for f in ct.get("flags", []))
        if ps and (c.get("base_number") or differs) and sid not in bad:
            notes.append({"instructor": e["name"], "term": e.get("pdf_term"), "text": ps})
    c["prerequisites_notes"] = notes
    stats["prereq_" + ("registrar" if "Registrar" in c["prerequisites_source"] else "catalog" if "catalog" in c["prerequisites_source"] else "none")] += 1

# ---- topic matrix: rows = topics, columns = professors -------------------------------------------------------------
import string
merge_dir = ROOT / "data/merge_out"
matrix_stats = collections.Counter()



# ---- merge safety net: a merged row may only keep topics that share a distinctive word ---------------------------------
GENERIC = set("algor progr syste model desig analy struc funct metho techn appli intro basic conce funda topic gener advan "
              "using other relat types imple tools softw compu scien probl".split())
_STOP = set("and or of the a an in on for to with from by as at is are be via using use".split())


def _stems(t):
    return {w[:5] for w in re.findall(r"[a-z0-9]+", t.lower()) if w not in _STOP and len(w) > 2} - GENERIC


def _compat(a, b):
    return bool(_stems(a) & _stems(b))


def split_row(label, ids, topic_of):
    """Partition ids into groups in which every pair of topic texts is compatible (greedy, in id order)."""
    groups = []
    for i in ids:
        for g in groups:
            if all(_compat(topic_of(i), topic_of(j)) or topic_of(i).lower() == topic_of(j).lower() for j in g):
                g.append(i); break
        else:
            groups.append([i])
    if len(groups) == 1:
        return [(label, ids)]
    out = []
    for g in groups:
        texts = collections.Counter(topic_of(i) for i in g)
        out.append((min(texts, key=lambda t: (-texts[t], len(t))), g))
    return out


def _norm(t):
    return " ".join(re.findall(r"[a-z0-9]+", t.lower()))


def regroup_exact(rows, topic_of, owner_of):
    """After splitting, put rows together when a topic text is identical (ignoring case/punctuation) and no professor would
    end up twice in the merged row. Pure text equality, so it can never create a false match."""
    merged = []   # [label, ids, owners, norms]
    for label, ids in rows:
        norms = {_norm(topic_of(i)) for i in ids}
        owners = {owner_of(i) for i in ids}
        for m in merged:
            if (m[3] & norms) and not (m[2] & owners):
                m[1] += ids; m[2] |= owners; m[3] |= norms
                break
        else:
            merged.append([label, list(ids), set(owners), set(norms)])
    return [(m[0], m[1]) for m in merged]


def cell_kind(t):
    if t.get("kind") == "explicit":
        return "possible" if t.get("hedged") else "stated"
    return "textbook_uncertain" if t.get("hedged") else "textbook"


for num, c in ds["courses"].items():
    cols = [e for e in c["instructors"] if e.get("topics")]
    if not cols:
        continue
    keys = {e["name"]: string.ascii_uppercase[i] for i, e in enumerate(cols)}
    by_id = {}
    for e in cols:
        for j, t in enumerate(e["topics"]):
            by_id[f"{keys[e['name']]}{j+1}"] = (e, j, t)
    rows = None
    if len(cols) >= 2:
        mp = merge_dir / f"{num}.json"
        if mp.exists():
            m = json.load(open(mp, encoding="utf8"))
            ids = [i for r in m["rows"] for i in r["ids"]]
            if sorted(ids) == sorted(by_id) and len(ids) == len(set(ids)):
                rows = []
                for r in m["rows"]:
                    parts = split_row(r["label"], r["ids"], lambda i: by_id[i][2]["topic"])
                    if len(parts) > 1:
                        matrix_stats["rows_split_by_safety_net"] += 1
                    rows += parts
                before = len(rows)
                rows = regroup_exact(rows, lambda i: by_id[i][2]["topic"], lambda i: by_id[i][0]["name"])
                matrix_stats["rows_regrouped_by_exact_text"] += before - len(rows)
                matrix_stats["merged_courses"] += 1
            else:
                matrix_stats["INVALID_merge_fallback"] += 1
                print("merge file invalid for", num, "- using unmerged rows; missing:", sorted(set(by_id) - set(ids))[:5], "extra:", sorted(set(ids) - set(by_id))[:5])
        else:
            matrix_stats["no_merge_fallback"] += 1
    if rows is None:
        rows = [(t["topic"], [i]) for i, (_, _, t) in by_id.items()]
    out_rows = []
    for label, ids in rows:
        cells = {}
        for i in ids:
            e, j, t = by_id[i]
            ci = cols.index(e)
            first = cells.setdefault(ci, {"kind": cell_kind(t), "topic": t["topic"], "evidence": t.get("evidence", ""), "where": t.get("where", ""), "also": []})
            if first["topic"] != t["topic"] and t["topic"] not in first["also"]:
                first["also"].append(t["topic"])
        pos = min(by_id[i][1] / max(len(by_id[i][0]["topics"]), 1) for i in ids)
        out_rows.append({"label": label, "cells": cells, "n": len(cells), "pos": round(pos, 4)})
    out_rows.sort(key=lambda r: (-r["n"], r["pos"]))
    c["matrix"] = {"columns": [{"name": e["name"], "term": e.get("pdf_term"), "url": e.get("pdf_url") or e.get("syllabus_url")} for e in cols], "rows": out_rows}
    matrix_stats["courses_with_matrix"] += 1
json.dump(removed_links, open(ROOT / "data/removed_links.json", "w", encoding="utf8"), indent=1)
print("links removed:", len(removed_links))
print("matrix:", dict(matrix_stats))

# index urls are written with a placeholder; the site prepends BASE_URL client-side
for r in index:
    r["url"] = "__BASE__" + r["url"].lstrip("/")
(ROOT / "site/src/data").mkdir(parents=True, exist_ok=True)
json.dump(ds, open(ROOT / "site/src/data/dataset.json", "w", encoding="utf8"))
json.dump(index, open(ROOT / "site/public/search-index.json", "w", encoding="utf8"))
json.dump(rejected, open(ROOT / "data/rejected_topics.json", "w", encoding="utf8"), indent=1)
print("rejected topics:", len(rejected))
print(dict(stats), "| index entries:", len(index))
