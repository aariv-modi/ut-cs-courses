# Syllabus extraction spec

Input: a syllabus text file (pdftotext -layout output; may be messy columns/tables). If the text file is
under 1500 characters the PDF is probably scanned: read the PDF file directly instead (Read tool supports PDFs).

Output: one JSON file per syllabus at `data/extracted/<syllabus_id>.json`. Valid JSON only, UTF-8.

```json
{
  "syllabus_id": "...",
  "course_codes_in_document": ["C S 429"],
  "term_in_document": "Fall 2026",
  "prerequisites_stated": "verbatim prerequisite sentence(s) from the syllabus, or null",
  "course_description_stated": "one or two sentence verbatim description if present, or null",
  "textbooks": [
    {"title": "...", "authors": "...", "edition": "3rd" , "year": 2016, "isbn": "978..." ,
     "status": "required | recommended | optional | unspecified", "notes": null}
  ],
  "detail_level": "weekly_schedule | topic_list | chapters_only | minimal",
  "external_schedule_url": "URL of a course website/Canvas page that holds the real schedule, or null",
  "topics": [
    {"topic": "short noun phrase, e.g. 'Cache memories'",
     "kind": "explicit | textbook_chapter",
     "evidence": "verbatim quote from the syllabus (<=30 words) that supports this topic",
     "where": "section heading, week/date, or page where it appears",
     "textbook_ref": null}
  ],
  "chapter_refs": [
    {"textbook": "title as written (and edition if given)", "ref": "Ch. 4-5 / Sections 2.1-2.3 / Chapters 1, 3",
     "context": "the topic text or week label printed next to the reference, if any"}
  ],
  "notes": "anything unusual: scanned, schedule missing, multiple sections with different content, etc."
}
```

Rules (accuracy over coverage — this data is shown to students making decisions):
1. Only record what the syllabus actually says. Never add topics from your own knowledge of what such a course
   "usually" covers. If the syllabus lists no topics, return an empty `topics` list and set detail_level "minimal".
2. `kind: "explicit"` = the syllabus names the topic (in a topics list, weekly schedule, learning outcomes,
   description of modules, assignment descriptions that name technical content). Each needs a verbatim `evidence` quote.
3. Do NOT turn logistics into topics (exams, grading, office hours, policies, due dates, "review", "midterm").
4. Learning objectives count as topics only when they name technical content (e.g. "implement dynamic programming").
5. When the schedule just says "Ch. 4" or "Sections 3.1-3.4" with no topic name, put it in `chapter_refs` (do not
   invent the chapter's topics; a later step resolves them from the textbook's table of contents). Include the
   textbook identity the reference points to, if it can be determined from the syllabus; otherwise "unknown".
6. Granularity: one entry per distinct concept, 2-8 words, no duplicates. Prefer the syllabus's own wording
   (keep terms like "MESI" or "Tomasulo" if written). Typically 10-60 topics for a topic-rich syllabus.
7. Record the edition and ISBN exactly as written; null if absent. Do not guess.
8. If a syllabus covers several courses/sections, record all codes in `course_codes_in_document`.
9. Keep `evidence` quotes verbatim (fix only line-break hyphenation).
