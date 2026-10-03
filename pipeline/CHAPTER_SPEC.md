# Textbook chapter -> topic resolution spec

Some syllabi only cite textbook chapters ("Ch. 8: Software Testing", "Sections 3.1-3.4"). Your job: turn those
references into topics using the textbook's REAL table of contents, fetched from the web.

Input: a batch file `data/chapter_batches/cb_N.json`. Each entry has a `syllabus_id`, `text_file` (the syllabus text,
read it for context), `textbooks_listed`, and `chapter_refs` ([{textbook, ref, context}]).

Output: one JSON file per syllabus at `data/derived/<syllabus_id>.json` (create the directory if needed):

```json
{
  "syllabus_id": "...",
  "topics": [
    {"topic": "short name, normally the chapter/section title from the TOC (<=8 words)",
     "kind": "textbook_chapter",
     "evidence": "Syllabus cites \"<ref as written>\"; <Book, edition> Ch. 8 is titled \"<chapter title>\".",
     "where": "the syllabus context (week/date/label) the reference appeared in",
     "textbook_ref": {"book": "...", "edition": "...", "chapter": "8", "toc_url": "URL you actually fetched"}}
  ],
  "unresolved": [{"ref": "...", "textbook": "...", "reason": "TOC not found / edition unknown / ambiguous book / ..."}]
}
```

Hard rules (this is shown to students; wrong is worse than missing):
1. Topic names come ONLY from a table of contents you actually fetched (WebFetch/WebSearch: publisher page, Library of
   Congress catdir TOC, author/book website, Google Books, university library, Open Library). Never from memory or
   from what you think the chapter "probably" covers. Record the URL you used in `toc_url`.
2. The edition must match the one the syllabus uses. If the syllabus doesn't state an edition and chapter numbering differs
   across editions, or you can only find a different edition's TOC, put the reference in `unresolved` with the reason.
   If the chapter title is identical in the nearby editions and the syllabus's context text names the same topic, you may
   resolve it and say so in `evidence`.
3. If a ref covers a range (Ch. 4-6) emit one topic per chapter title; for section refs (Sec 2.1-2.3) use the section titles
   if the TOC lists sections, else the chapter title with the evidence noting only sections were cited.
4. Do not duplicate topics the syllabus already names explicitly (the explicit topics are in `data/extracted/<id>.json`);
   it is fine to skip a chapter whose title just repeats an explicit topic.
5. A textbook the syllabus calls "optional/recommended" without any chapter assignment should not be expanded.
6. Do not copy book text. Titles of chapters/sections only.
7. Validate each file parses as JSON. If a book's TOC can't be found at all, write the file with empty `topics` and the
   refs under `unresolved`.

When finished reply with ONE short line: files written, number of topics resolved, number of unresolved refs, and which
books you couldn't find a TOC for.
