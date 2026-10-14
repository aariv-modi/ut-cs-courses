"""CS 429: topic list taken from the shared Joshi/Chatterjee syllabus (section 3.5 Topics: one language module + four
content modules), applied identically to both. Morgan Fong is left out of the topic analysis for now
(overrides.topic_exclude_instructors). Labels state only what the module list names.
Re-runnable: rebuilds the topic list from scratch each time.
"""
import json
from common import ROOT

path = ROOT / "data/topic_out/429.json"
d = json.load(open(path, encoding="utf8"))
INSTRUCTORS = ["Prashant Joshi", "Siddhartha Chatterjee"]
EXCLUDED = json.load(open(ROOT / "data/overrides.json", encoding="utf8")).get("topic_exclude_instructors", {}).get("429", [])

C, DATA, MACH, PROC, STOR = ("Programming in C in a Linux environment", "Representing and manipulating data",
                             "Machine-level representation of programs", "Processor architecture and implementation",
                             "Storage system architecture and performance")
ENC = "Binary encodings of, and basic operations on, basic data types: integers, floating-point numbers, and characters."
DER = "Derived data types: arrays, structures, unions, functions, pointers."
IMPL = "Sequential and pipelined implementations of a representative subset of the A64 ISA."
ROWS = [  # (label, module, verbatim quote)
    ("C programming language", C, "The C programming language."),
    ("Linux shell and programming tools", C, "The Linux command-line (shell) environment. Standard libraries. Programming tools: compilers, build systems, debuggers, version control tools."),
    ("Software design and clean code", C, "Understanding requirements and exploring design choices. Writing clean code."),
    ("Binary encodings of data", DATA, ENC),
    ("Integer arithmetic", DATA, ENC),
    ("Floating-point representation", DATA, ENC),
    ("Character encodings (Unicode, UTF-8)", DATA, "Unicode and UTF-8."),
    ("Arrays, structs, and unions", DATA, DER),
    ("Pointers", DATA, DER),
    ("Data alignment", DATA, "Data alignment."),
    ("Instruction set architecture (Armv8 A64)", MACH, "The Armv8 A64 instruction set architecture (ISA)."),
    ("Data access and arithmetic instructions", MACH, "Data access instructions, arithmetic and logical operations"),
    ("Control flow and branch instructions", MACH, "non-sequential control transfer"),
    ("Procedure calls and returns", MACH, "procedure call/return."),
    ("Stack and heap disciplines", MACH, "Stack and heap disciplines for memory management."),
    ("Code generation for C constructs", MACH, "Code generation for C constructs."),
    ("Dynamic memory allocation", MACH, "Techniques for explicit memory management."),
    ("Logic design basics", PROC, "Basics of logic design."),
    ("Single-cycle processor implementation", PROC, IMPL),
    ("Pipelined processor implementation", PROC, IMPL),
    ("Pipeline hazards, forwarding, stalling, and squashing", PROC, "Dependences and hazards. Forwarding, stalling, squashing."),
    ("Branch prediction", PROC, "Pipeline control. Branch prediction."),
    ("Pipeline performance equation", PROC, "Pipeline performance equation."),
    ("Storage technologies (volatile and non-volatile)", STOR, "Volatile and non-volatile storage technologies."),
    ("Locality of reference", STOR, "Locality of reference."),
    ("Memory hierarchy", STOR, "Memory hierarchy."),
    ("Cache structure and behavior", STOR, "Structure and behavior of caches."),
    ("Memory performance equation", STOR, "Memory performance equation."),
    ("I/O, MMIO, and DMA", STOR, "Secondary storage and I/O. MMIO and DMA."),
]

d["topics"] = []
for label, module, quote in ROWS:
    cov = {"status": "stated", "evidence": quote, "where": f"Section 3.5 Topics, module: {module}", "as_written": quote}
    d["topics"].append({"label": label, "coverage": {i: dict(cov) for i in INSTRUCTORS}})
for name in EXCLUDED:
    d["instructors"].pop(name, None)
d["notes"] = ("Topic list from the shared Joshi/Chatterjee syllabus (identical text; section 3.5 module list, no weekly schedule), "
              "applied identically to both. " + (f"{', '.join(EXCLUDED)} left out of the topic analysis for now." if EXCLUDED else ""))
json.dump(d, open(path, "w", encoding="utf8"), indent=1, ensure_ascii=False)
print(len(d["topics"]), "topics for", INSTRUCTORS, "| excluded:", EXCLUDED)
