"""CS 429H: corrections after a line-by-line review of Gheith's and Elnozahy's syllabi (project owner approved).

Adds missing rows (computer system organization, stacks, logic synthesis), credits Gheith for the ISA, fixes
Elnozahy's assembly evidence, and adds hedged ("possible") credits: Gheith for sequential and transistor-level
circuits (his Verilog line names flip-flops and transistors), Elnozahy for I/O support.
Gheith's flip-flop quote is checked against data/supplemental/17035167_pypdf.txt (same PDF; pdftotext lost ligatures).
Re-runnable: every change is a set/replace, not an append.
"""
import json
from common import ROOT

path = ROOT / "data/topic_out/429H.json"
d = json.load(open(path, encoding="utf8"))
G, E = "Ahmed Gheith", "Mootaz Elnozahy"
rows = {t["label"]: t for t in d["topics"]}


def cov(status, evidence, where, as_written=None):
    return {"status": status, "evidence": evidence, "where": where, "as_written": as_written or evidence}


def row(label, after=None, rename_from=None):
    if rename_from and rename_from in rows and label not in rows:
        r = rows.pop(rename_from); r["label"] = label; rows[label] = r
    if label not in rows:
        r = {"label": label, "coverage": {}}
        i = next((k + 1 for k, t in enumerate(d["topics"]) if t["label"] == after), len(d["topics"]))
        d["topics"].insert(i, r); rows[label] = r
    return rows[label]


# 1. Computer system organization (both)
r = row("Computer system organization", after=None)
d["topics"].remove(r); d["topics"].insert(0, r)
r["coverage"][G] = cov("stated", "The different parts (processor, memory, I/O) * How the parts interact", "Topics: Computer architecture")
r["coverage"][E] = cov("stated", "Understanding the organization of a computer system.", "Learning Outcomes")

# 2. Instruction set architecture: Gheith's "master plan as viewed by software"
r = row("Instruction set architecture", rename_from="Instruction set design")
r["coverage"][G] = cov("stated", "Computer architecture (a computer's master plan as viewed by software)", "Topics")

# 3. Stacks (Elnozahy, week 3)
r = row("Stacks", after="Assembly language (x86 and ARM)")
r["coverage"][E] = cov("stated", "Week 3 (2/2-6): Transistor-based circuits, stacks, ARM", "Week 3", "stacks")

# 4. Logic synthesis (Elnozahy overview)
r = row("Logic synthesis", after="Verilog hardware description")
r["coverage"][E] = cov("stated", "The logic design track covers topics such as logic circuits, logic design, Verilog and logic synthesis.", "Overview", "logic synthesis")

# 5. Elnozahy assembly evidence: names both real-processor ISAs
r = rows["Assembly language (x86 and ARM)"]
r["coverage"][E] = cov("stated", "introduction of assembly language programming with examples taken from real processors ... Week 3 (2/2-6): Transistor-based circuits, stacks, ARM ... Week 4 (2/9-13): Arithmetic cts, heaps and programs, x86",
                       "Track 2: System programming; Weeks 3-4", "assembly language programming (ARM, x86)")

# 6. Gheith, hedged: his Verilog line names flip-flops and transistors; topics list "Technology, circuits, logic"
VER = "Verilog: a hardware design language used to describe hardware using logic gates, flip-flops, wires, and transistors"
rows["Sequential circuits and finite state machines"]["coverage"][G] = cov(
    "possible", VER, "Programming languages (Verilog); hedged: flip-flops named as Verilog building blocks, sequential circuits not listed as a topic", "flip-flops")
rows["Transistor-level circuits"]["coverage"][G] = cov(
    "possible", VER, "Programming languages (Verilog) and Topics: Technology, circuits, logic; hedged: transistors named, not listed as a topic", "transistors")

# 7. Elnozahy, hedged: architecture track covers "support for memory and I/O operations"
r = row("I/O support in the processor and memory system", after="Programming I/O devices")
r["coverage"][E] = cov("possible", "The processor architecture track covers topics such as the basic design of a processor, pipelining, caching and support for memory and I/O operations.",
                       "Overview; hedged: no week of the schedule names I/O", "support for memory and I/O operations")

d["notes"] = (d.get("notes") or "").split(" Reviewed line by line")[0] + " Reviewed line by line against both syllabi (Oct 2026); hedged credits are marked possible."
json.dump(d, open(path, "w", encoding="utf8"), indent=1, ensure_ascii=False)
print(len(d["topics"]), "topics")
