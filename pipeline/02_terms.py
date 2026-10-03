"""Fetch C S sections per term: past terms from the public Syllabi & CVs repository
(instructors + syllabus PDFs), the upcoming term from the CS department class listing.

Window (fixed by the project owner; summers are never included):
  Fall 2025, Spring 2026, Fall 2026  -> syllabi repository
  Spring 2027                        -> CS dept class homepages listing (no syllabi posted yet)
"""
import re, json, html
from bs4 import BeautifulSoup
from common import fetch, ROOT

REPO = "https://utdirect.utexas.edu/apps/student/coursedocs/nlogon/"
DEPT_LIST = "https://apps.cs.utexas.edu/apps/classes/homepages"
PAST = [(2025, "Fall", 9), (2026, "Spring", 2), (2026, "Fall", 9)]
NEXT = (2027, "Spring")
txt = lambda el: re.sub(r"\s+", " ", html.unescape(el.get_text(" "))).strip()


def undergrad(num):
    m = re.fullmatch(r"(\d{3})[A-Z]?", num)
    return bool(m) and int(num[1:3]) < 80


def past_term(year, name, code):
    page = fetch(REPO, params={"year": year, "semester": code, "department": "C S",
                               "course_type": "In Residence", "search": "Search"})
    soup = BeautifulSoup(page, "html.parser")
    rows = []
    for tr in soup.select("#results_table tbody tr"):
        td = tr.find_all("td")
        if len(td) < 7:
            continue
        num = txt(td[1]).replace("C S ", "")
        if not undergrad(num):
            continue
        instr = [s.strip() for s in td[4].get_text("\n").split("\n") if s.strip()]
        syl = td[6].find("a", href=True)
        cv = [{"name": a.get_text(strip=True).replace(" CV", ""), "url": a["href"]} for a in td[5].find_all("a", href=True)]
        rows.append({"term": f"{name} {year}", "course": num, "unique": txt(td[2]), "title": txt(td[3]),
                     "instructors": instr, "syllabus_path": syl["href"] if syl else None, "cvs": cv})
    return rows


def next_term(year, name):
    page = fetch(DEPT_LIST, params={"field_semester_value": name, "field_class_year_value[value][year]": year})
    soup = BeautifulSoup(page, "html.parser")
    rows = []
    for tr in soup.select("table tbody tr"):
        td = tr.find_all("td")
        if len(td) < 3:
            continue
        m = re.match(r"(\d{3}[A-Z]?)\s*(.*)", txt(td[1]))
        if not m or not undergrad(m.group(1)):
            continue
        rows.append({"term": f"{name} {year}", "course": m.group(1), "unique": txt(td[0]), "title": m.group(2),
                     "instructors": [txt(td[2]).rstrip(" ;")] if txt(td[2]) else [], "syllabus_path": None, "cvs": []})
    return rows


if __name__ == "__main__":
    # Syllabi repository only. Registrar sections (incl. Spring 2027) are merged in by 02b_registrar_sections.py;
    # the CS department's planning listing is no longer used for offered terms.
    sections = []
    for y, n, c in PAST:
        r = past_term(y, n, c)
        sections += r
        print(f"{n} {y}: {len(r)} undergrad sections, {len({x['course'] for x in r})} courses, "
              f"{sum(1 for x in r if x['syllabus_path'])} with syllabus")
    (ROOT / "data" / "sections_repo.json").write_text(json.dumps(sections, indent=1), encoding="utf8")
