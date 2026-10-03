# Topic merge spec

Goal: for one course taught by several professors, group their extracted topics into ROWS of a comparison table
(rows = topics, columns = professors, a check mark where a professor teaches that topic). Rows must line up the SAME topic
across professors.

Input: `data/merge_in/<course>.json` = {course, code, title, instructors:[{key, name, topics:[{id, topic}]}]}.
Each topic has a unique id like "A12" (instructor key + number).

Output: `data/merge_out/<course>.json`:
```json
{"course": "429",
 "rows": [ {"label": "Cache memories", "ids": ["A14", "B9", "C11"]},
           {"label": "Pipelining", "ids": ["A20"]} ]}
```

Rules (a wrong merge puts a false check mark in front of students, so be conservative):
1. EVERY id from the input appears in exactly one row. Do not invent ids; do not drop or duplicate any.
2. Put topics in the same row only when a student would consider them the same topic: synonyms, singular/plural,
   same concept worded differently or at slightly different detail (e.g. "Caches" and "Cache memories").
3. Do NOT merge when one topic is a broad umbrella and the other is a specific sub-topic that the same syllabus also lists
   separately, when they name different techniques/algorithms/tools (e.g. "Quicksort" vs "Mergesort"), or when you are
   not sure. When unsure, keep separate rows.
4. A single professor may have several ids in one row only if their own topics are genuinely duplicates of each other.
5. `label`: a short neutral noun phrase (2-7 words). Prefer the wording the professors themselves used; never add
   content that none of the merged topics says. For a one-id row, use that topic's text as the label.
6. Order does not matter (rows are sorted later).
7. Use only the topic text in the input file. Do not consult syllabi or other files.

Validate with python that every id appears exactly once before replying. Reply with ONE short line: courses done and
anything odd.

8. Work ISOLATION (a previous run was corrupted by agents sharing a script): do your own judgment course by course.
   Never run, reuse or write any script or file in /tmp or any shared location, and never touch another course's files.
   Write each output with the Write tool (or a python snippet) ONLY to data/merge_out/<your course>.json. Any helper
   script you need goes under data/merge_tmp/batch_<N>/ (N = your batch number) and must only read your own courses.
9. Do NOT use rule-based/fuzzy automatic merging. Decide every row yourself by reading the topic texts.
   Related-but-different topics (e.g. "Inheritance" vs "Polymorphism" vs "Encapsulation", "Stacks" vs "Stacks and queues",
   a method vs its family) belong in SEPARATE rows.
