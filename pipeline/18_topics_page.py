"""Parse the CS 314 topics list page (data/supplemental/314_topicsList.html) into its outline.

The page has a "Prerequisite knowledge" list, then "Topics Covered in CS314" as a numbered list of major topics,
each with nested sub-topics.  Output: data/supplemental/314_topicsList.json
  {"prerequisite_knowledge": [...], "topics": [{"n": 1, "topic": "...", "subtopics": ["..."]}], "page_text": "..."}
"""
import re, json, html
from html.parser import HTMLParser
from common import ROOT


class P(HTMLParser):
    def __init__(self):
        super().__init__()
        self.lists = []            # stack of "ul"/"ol"
        self.li = []               # stack of [text-buffer] per open li
        self.in_topics = False
        self.prereq, self.topics = [], []
        self.cur_top = None
        self.all_text = []

    def handle_starttag(self, tag, attrs):
        if tag in ("ul", "ol"):
            self.lists.append(tag)
        elif tag == "li":
            self.li.append([])

    def handle_endtag(self, tag):
        if tag in ("ul", "ol"):
            if self.lists: self.lists.pop()
        elif tag == "li" and self.li:
            txt = re.sub(r"\s+", " ", html.unescape("".join(self.li.pop()))).strip()
            depth = len(self.lists)                      # depth of this li's own list
            if not txt:
                return
            if not self.in_topics:
                self.prereq.append(txt)
            elif depth == 1:
                self.cur_top["topic"] = self.cur_top.get("topic") or txt
            else:
                self.cur_top["subtopics"].append(txt)

    def handle_data(self, d):
        self.all_text.append(d)
        if "Topics Covered in CS314" in d:
            self.in_topics = True
        # text of a li (own text only: stop collecting into parent while a nested li is open)
        if self.li:
            self.li[-1].append(d)

    # a numbered top-level topic starts when an <li> opens at depth 1 inside the topics <ol>
    def handle_startendtag(self, tag, attrs):
        pass


def parse(raw):
    # simple, robust second pass: split the numbered list by top-level <li> using a depth counter
    body = raw[raw.find("Topics Covered in CS314"):]
    pre = raw[:raw.find("Topics Covered in CS314")]
    clean = lambda s: re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()
    prereq = [clean(x) for x in re.findall(r"<li>(.*?)</li>", pre, re.S | re.I) if clean(x)]
    # tokenise list structure
    toks = re.findall(r"<(/?)(ol|ul|li)\b[^>]*>|([^<]+)|<[^>]+>", body, re.I)
    topics, depth, cur, buf, stack = [], 0, None, [], []
    for close, tag, text in toks:
        tag = (tag or "").lower()
        if tag in ("ol", "ul"):
            if not close:
                depth += 1
            else:
                if buf and stack and stack[-1] == "sub" and cur is not None:
                    pass
                depth -= 1
        elif tag == "li":
            if not close:
                # opening li: flush any pending text to the item that owns it
                txt = clean(" ".join(buf)); buf = []
                if txt and stack:
                    if stack[-1] == "top" and cur is not None and not cur["topic"]:
                        cur["topic"] = txt
                    elif stack[-1] == "top" and cur is not None:
                        pass
                kind = "top" if depth == 1 else "sub"
                stack.append(kind)
                if kind == "top":
                    cur = {"n": len(topics) + 1, "topic": "", "subtopics": []}
                    topics.append(cur)
            else:
                txt = clean(" ".join(buf)); buf = []
                kind = stack.pop() if stack else None
                if kind == "top" and cur is not None and txt and not cur["topic"]:
                    cur["topic"] = txt
                elif kind == "sub" and cur is not None and txt:
                    cur["subtopics"].append(txt)
        elif text:
            buf.append(text)
        # text directly after a top-level <li> opens, before its nested <ul>: capture as the topic title
        if tag == "ul" and not close and depth == 2 and cur is not None and not cur["topic"]:
            txt = clean(" ".join(buf)); buf = []
            if txt: cur["topic"] = txt
    return prereq, topics, clean(raw)


if __name__ == "__main__":
    raw = open(ROOT / "data/supplemental/314_topicsList.html", encoding="cp1252", errors="ignore").read()
    prereq, topics, page_text = parse(raw)
    json.dump({"prerequisite_knowledge": prereq, "topics": topics, "page_text": page_text},
              open(ROOT / "data/supplemental/314_topicsList.json", "w", encoding="utf8"), indent=1)
    print(len(prereq), "prerequisite items;", len(topics), "major topics;", sum(len(t["subtopics"]) for t in topics), "sub-topics")
    for t in topics:
        print(f"{t['n']:>2}. {t['topic']}  ({len(t['subtopics'])})")
