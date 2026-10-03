# UT CS Course Explorer

A static website showing, for every **undergraduate C S course** at UT Austin: prerequisites, last/next offering,
who taught it in the window, each instructor's most recent public syllabus, and the topics that syllabus covers
(stated in the syllabus, or inferred from the textbook chapters it assigns). A topic search answers
"which course teaches X?".

**Window:** Fall 2025, Spring 2026, Fall 2026 (+ Spring 2027 as the "next" term). Summers are never included.
A course with no section in those four terms shows the last earlier Fall/Spring term it was taught (`08_history.py`, back to Fall 2010), or "no record since Fall 2010".

## Data sources (all public, no login)

| Data | Source |
|---|---|
| Course list, hours | `catalog.utexas.edu/courses/c_s/` |
| Prerequisites, descriptions | UT CS department course list (`cs.utexas.edu/undergraduate/degrees-and-programs/courses`); falls back to the syllabus's own prerequisite line |
| Past/current sections, instructors, syllabus PDFs | UT Syllabi & CVs repository (`utdirect.utexas.edu/apps/student/coursedocs/nlogon/`, HB 2504 / Tex. Educ. Code §51.974) |
| Spring 2027 instructors | UT CS class listing (`apps.cs.utexas.edu/apps/classes/homepages`) |

The registrar's official course schedule requires a UT EID login, so it is **not** used.

## Pipeline (`pipeline/`, Python 3.11+, `pdftotext` from poppler on PATH)

```
pip install -r pipeline/requirements.txt
python 01_courses.py     # catalog + dept page -> data/courses.json (undergrad = last two digits < 80)
python 02_terms.py       # sections per term -> data/sections.json
python 03_build.py       # per-course dataset: last offered, next term, instructors, newest syllabus each
python 04_syllabi.py     # download selected PDFs -> data/syllabi/, extract text
#  -- LLM step (see EXTRACTION_SPEC.md): structured topic extraction -> data/extracted/<syllabus_id>.json
python 05_verify.py      # every quote must occur in the syllabus AND support its topic label
#  -- LLM step (see CHAPTER_SPEC.md): textbook chapter refs -> topics via fetched TOCs -> data/derived/
python 08_history.py     # last offered term for courses not taught in the window -> data/history.json
python 06_export.py      # merge -> site/src/data/dataset.json + site/public/search-index.json
```

Requests are cached (`data/cache/`) and throttled to ~1 request / 0.7 s. Re-running a step is safe.

### What counts as "offered"
A course counts as taught in a past/current term only if the syllabi repository (built from registered sections) has a section
for it. The CS dept class listing also shows cancelled sections, so dept-only course/terms are written to
`data/dept_only_unverified.json` and **not** counted. Spring 2027 can only come from the dept listing, so it is the planned schedule.
Courses with no repository record ever but a dept-listing history (individual-instruction courses 370, 370F, 379H) are shown
as "unverified".

### Accuracy safeguards
- Every *stated* topic carries a verbatim quote; `05_verify.py` checks the quote exists in the syllabus text and that the
  topic's key terms appear in it. Failures are held out (`data/rejected_topics.json`).
- Topics the syllabus hedges ("may include", "time permitting", "optional") are labelled **possible**.
- Textbook-derived topics come only from a table of contents fetched from the web (URL recorded), at the edition the
  syllabus uses; otherwise they are left unresolved.
- "Not found" in search means *the public syllabus doesn't list it*, not that the course doesn't cover it
  (many instructors keep schedules on Canvas).
- `data/overrides.json` holds hand corrections (e.g. titles of variable-topic offerings of C S 378).

### Known gaps
- Some instructors' newest syllabus is a web-format page on `utexas.simplesyllabus.com`, which blocks non-browser
  clients. The site links to it and uses the instructor's older PDF syllabus (labelled) when one exists.
- Spring 2027 instructor names are abbreviated in the source and the schedule can change.
- 32 courses have no prerequisite text on the department page; the syllabus line is used when present.

## Site (`site/`, Astro)

```
cd site && npm install
npm run dev        # local
npm run build      # static output in site/dist
```

## Publish free on GitHub Pages
1. Create a GitHub repo and push this folder (`git init`, `git add .`, `git commit`, `git remote add origin ...`, `git push -u origin main`).
2. Repo **Settings → Pages → Source: GitHub Actions**.
3. The included workflow (`.github/workflows/deploy.yml`) builds and deploys on every push to `main`;
   the site appears at `https://<user>.github.io/<repo>/`.

## Refreshing each semester
Re-run steps 01–06 after the new term's syllabi are posted (the repository fills in within ~7 days of the first day of
classes), update `WINDOW` terms in `02_terms.py`/`03_build.py`, commit the regenerated `site/src/data/` and
`site/public/search-index.json`, and push.

*Unofficial student project; not affiliated with UT Austin. Syllabi remain the property of their authors and are linked, not copied.*
