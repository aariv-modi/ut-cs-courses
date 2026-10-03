"""Build the undergrad C S course list (title, description, prerequisite text).

Source: UT CS department course page (has prerequisite text; the 2026-27 catalog does not)
cross-checked against catalog.utexas.edu/courses/c_s/ (authoritative code/title/hours list).
"""
import re, json, html
from bs4 import BeautifulSoup
from common import fetch, ROOT

DEPT = "https://www.cs.utexas.edu/undergraduate/degrees-and-programs/courses"
CAT = "https://catalog.utexas.edu/courses/c_s/"
ATOZ = "https://catalog.utexas.edu/general-information/coursesatoz/c-s/"   # authority: courses in the current catalog


def norm(s):
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def catalog_courses():
    soup = BeautifulSoup(fetch(CAT), "html.parser")
    out = {}
    for b in soup.select("div.courseblock"):
        code = b.select_one(".detail-ut_code")
        if not code:
            continue
        code = norm(code.get_text()).replace("C S ", "")
        out[code] = {
            "title": norm(b.select_one(".detail-title").get_text()),
            "hours": norm(b.select_one(".detail-hours_html").get_text()),
            "catalog_description": norm(b.select_one(".courseblockextra").get_text()) if b.select_one(".courseblockextra") else "",
        }
    return out


def atoz_keys():
    """(hours-digit, level+suffix) pairs on the catalog A-Z page; the hours digit may be 'X' (any credit hours)."""
    page = fetch(ATOZ)
    keys = set()
    for h5 in BeautifulSoup(page, "html.parser").select("h5"):
        code = norm(h5.get_text()).split(". ")[0]
        for m in re.finditer(r"(?<![A-Z0-9])([\dX])(\d{2}[A-Z]?)(?![A-Za-z0-9])", code):
            keys.add((m.group(1), m.group(2)))
    return keys


def dept_courses():
    soup = BeautifulSoup(fetch(DEPT), "html.parser")
    out = {}
    for item in soup.select("div.accordion-item"):
        h = item.select_one(".accordion-button")
        body = item.select_one(".accordion-body")
        if not h or not body:
            continue
        m = re.match(r"(\d{3}[A-Z]?)\s+(.*)", norm(h.get_text()))
        if not m:
            continue
        out[m.group(1)] = {"title": m.group(2), "text": norm(body.get_text())}
    return out


def split_prereq(text):
    m = re.search(r"\bPrerequisites?:\s*(.*)$", text)
    if not m:
        return text, ""
    return text[: m.start()].strip(), m.group(1).strip()


if __name__ == "__main__":
    cat, dept, atoz = catalog_courses(), dept_courses(), atoz_keys()
    courses, dropped = {}, []
    for code in sorted(set(cat) | set(dept)):
        if not re.fullmatch(r"\d{3}[A-Z]?", code):
            continue  # skips variable-credit multi-number entries (109, 209, 309 ...)
        if int(code[1:3]) >= 80:  # UT numbering: first digit = credit hours; last two digits >= 80 = graduate
            continue
        if (code[0], code[1:]) not in atoz and ("X", code[1:]) not in atoz:
            dropped.append(code)   # not in the current catalog (old course still on the dept page)
            continue
        c, d = cat.get(code, {}), dept.get(code, {})
        desc, prereq = split_prereq(d.get("text", ""))
        courses[code] = {
            "code": f"C S {code}",
            "number": code,
            "title": c.get("title") or d.get("title"),
            "hours": c.get("hours", ""),
            "description": desc or c.get("catalog_description", ""),
            "prerequisites_text": prereq,
            "in_catalog": code in cat,
            "in_dept_page": code in dept,
        }
    (ROOT / "data" / "courses.json").write_text(json.dumps(courses, indent=1), encoding="utf8")
    print(len(cat), "catalog,", len(dept), "dept page ->", len(courses), "undergrad courses")
    print("dropped (not in current catalog A-Z):", dropped)
    print("only in catalog:", [c for c in courses if not courses[c]["in_dept_page"]])
    print("only in dept page:", [c for c in courses if not courses[c]["in_catalog"]])
    print("no prereq text:", sum(1 for c in courses.values() if not c["prerequisites_text"]))
