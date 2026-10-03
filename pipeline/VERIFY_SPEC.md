# Pass-2 verification spec
For each assigned course key, independently audit data/topic_out/<course>.json against the syllabus texts listed in data/topic_in/<course>.json (Read every text_file; for empty/garbled PDFs read pdf_file).
Check: (1) PRECISION: does each check mark's evidence quote really support that topic for that instructor? (2) RECALL: topics clearly taught in an instructor's syllabus but not credited to them (search their text under other names). (3) Topic list quality: duplicates/near-duplicates, umbrella-vs-specific mismatches, logistics items, vague labels. (4) Instructor meta (textbooks, prerequisites_stated) copied correctly.
Write ONLY data/topic_verify/<course>.json (UTF-8, Write tool), never touching topic_out:
{"course":"..","remove":[{"topic":"label","instructor":"name","reason":".."}],
 "add":[{"topic":"existing label","instructor":"name","status":"stated|possible","evidence":"verbatim <=40 words from that instructor's text","where":"..","as_written":".."}],
 "merge":[{"labels":["a","b"],"into":"label","reason":".."}],"drop_topics":[{"label":"..","reason":".."}],"notes":".."}
Be conservative: report only clear errors you can defend with a quote. Empty lists are fine. Reply with ONE short line (counts of remove/add/merge).
