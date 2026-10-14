"""CS 439: topic list rebuilt after a line-by-line review of all three syllabi (project owner asked for the most
accurate, complete representation).

Sources per instructor:
* Ahmed Gheith - syllabus PDF: weekly course outline, assignment list, catalog description.
* Alison Norman - syllabus PDF (course goals, core-topic subtopics) defers to the course website ("An overview schedule
  is available on the course website"). The website's dated schedule and project page (HTML comments removed) are in
  data/supplemental/439_norman_schedule.txt, accepted by the validator through overrides.supplemental_sources.
* Mootaz Elnozahy - SimpleSyllabus PDF: goals, five-part course structure, catalog description.
  Norman's site says it is "taught in conversation and collaboration with Dr. Mootaz Elnozahy" and his project windows
  match hers, but his own syllabus does not name the projects, so nothing is credited to him from her site.
Assigned readings alone are not used as evidence; lecture titles and project objectives are.
Re-runnable: rebuilds the topic list from scratch each time.
"""
import json
from common import ROOT

path = ROOT / "data/topic_out/439.json"
d = json.load(open(path, encoding="utf8"))
G, N, E = "Ahmed Gheith", "Alison Norman", "Mootaz Elnozahy"
SCHED = "https://www.cs.utexas.edu/~ans/classes/cs439/schedule.html"


def c(evidence, where, as_written=None, status="stated"):
    return {"status": status, "evidence": evidence, "where": where, "as_written": as_written or evidence}


def gw(quote, week, as_written=None):
    return c(quote, f"Course Outline, week {week}", as_written)


def ns(quote, date, as_written=None):
    return c(quote, f"Course website schedule ({date}), linked from the syllabus", as_written)


def np(quote, project, as_written=None):
    return c(quote, f"Course website project page, {project}", as_written)


CATALOG = "Requires writing of synchronized multithreaded programs and pieces of an operating system."
ROWS = [
    ("Operating system overview and history", {
        G: gw("Overview of operating systems and concurrency", 1),
        N: ns("History of Operating Systems", "Aug 24-26", "Introduction & themes; history of operating systems"),
        E: c("We will quickly cover the history of operating systems, review some hardware concepts from 429", "Course Structure, Part 1",
             "History of operating systems; review of hardware concepts")}),
    ("Resource management", {
        N: c("The second goal is for you to learn how an OS manages the resources of a computer to improve the user experience.", "Course Goals",
             "How an OS manages the resources of a computer"),
        E: c("The course will show how operating systems manage the resources of a computer", "Goals and Overview: To understand resource management",
             "Resource management")}),
    ("Processes", {
        G: gw("Processes and system calls", 9),
        N: ns("Processes", "Aug 31-Sep 2", "Processes; limited direct execution"),
        E: c("This part covers the process and thread abstractions in operating systems", "Course Structure, Part 2", "Process abstraction")}),
    ("System calls (fork, exec)", {
        G: c("Fork, exec and other system calls", "Assignments; Course Outline, weeks 8-9"),
        N: np("Become familiar with shells, fork(), exec(), and other systems concepts", "Project 0 (UTCS Shell); Project 2 (User Programs)",
              "fork(), exec(); how user programs interact with the OS")}),
    ("Writing a shell", {
        G: c("A simple shell", "Assignments"),
        N: np("Project 0: UTCS Shell", "Project 0")}),
    ("CPU scheduling", {
        G: gw("Scheduling", 12),
        N: ns("More Processes and CPU Scheduling", "Sep 2", "CPU scheduling; thread scheduling (Project 1)"),
        E: c("We will focus on the core ideas in operating systems: virtual addressing, memory protection, concurrent programming, file systems, and scheduling",
             "Goals and Overview", "scheduling")}),
    ("Threads", {
        G: c("Cooperative multi-threading ... Preemptive multi-threading", "Assignments; Course Outline, weeks 2-3",
             "Cooperative and preemptive multi-threading"),
        N: ns("Threads and Too Much Milk!", "Sep 9", "Threads; Project 1: Threads (thread state, thread scheduling)"),
        E: c("This part covers the process and thread abstractions in operating systems", "Course Structure, Part 2", "Thread abstraction")}),
    ("Interrupts", {
        N: np("Understanding interrupts, thread state, and thread scheduling", "Project 1 (Threads)", "interrupts")}),
    ("Synchronization and critical sections", {
        G: c("parallelism and critical sections", "Assignments; Course Outline, weeks 2-4"),
        N: c("Synchronization: Concurrency Bugs, Synchronization Concepts, Synchronization Code", "Subtopic Information for Core Topics; schedule Sep 9-28",
             "Synchronization concepts and code; Too Much Milk; producers/consumers; readers/writers"),
        E: c("Concurrency control will focus on reasoning about concurrent threads that share memory, message passing, and various locking schemes.",
             "Goals and Overview: To understand concurrency control; Course Structure, Part 2", "Concurrency control; synchronization")}),
    ("Locks, semaphores, and monitors", {
        G: gw("High level synchronization primitives", 4),
        N: ns("Locks and Semaphores", "Sep 14-16", "Locks and semaphores; monitors"),
        E: c("various locking schemes", "Goals and Overview: To understand concurrency control")}),
    ("Message passing", {
        E: c("delves into synchronization using both shared-memory, asynchronous, and message passing abstraction", "Course Structure, Part 2",
             "Shared-memory, asynchronous, and message-passing synchronization")}),
    ("Deadlock and race conditions", {
        G: gw("Revisiting deadlocks, race conditions, and synchronization", 13),
        N: ns("Deadlock and Monitors", "Sep 16; Thanksgiving 'Deadlock Revisited'", "Deadlock; concurrency bugs")}),
    ("Software safety (Therac-25 case study)", {
        N: ns("The Importance of Safety", "Sep 23", "The importance of safety (Therac-25)")}),
    ("Virtual memory", {
        G: c("Virtual memory", "Course Outline, weeks 6-7; Assignments"),
        N: c("Virtual Memory: Virtual Memory Mechanisms, Virtual Memory Policies", "Subtopic Information for Core Topics; schedule Oct 5-14",
             "Memory overview; virtual memory mechanisms and policies"),
        E: c("This part covers the shocking fact that memory is not infinite", "Course Structure, Part 3 (Memory management); Goals: virtual addressing",
             "Memory management; virtual addressing")}),
    ("Paging and page replacement", {
        N: np("Understanding paging, page replacement, and other virtual memory concepts", "Project 3 (Virtual Memory)")}),
    ("Memory protection", {
        N: c("We will focus on the core ideas in operating systems: virtual addressing, memory protection,", "Course Goals", "memory protection"),
        E: c("We will focus on the core ideas in operating systems: virtual addressing, memory protection,", "Goals and Overview", "memory protection")}),
    ("Heap memory management and garbage collection", {
        N: ns("Heap Memory Management and Garbage Collection", "Oct 19")}),
    ("Storage devices (disks, flash, SSDs)", {
        N: ns("Stable Storage and File Systems", "Oct 21", "Stable storage"),
        E: c("Durable storage comes in the form of flash memory, disks, and, well, ....tapes!", "Course Structure, Part 4",
             "Durable storage media: flash, disks, tapes")}),
    ("File systems", {
        G: c("Implementing the ext2 read path", "Assignments; Course Outline, weeks 5 and 7", "File systems; ext2 read path"),
        N: c("File Systems: File Systems, File Systems and the Hardware", "Subtopic Information for Core Topics; schedule Oct 21-Nov 18; Project 4",
             "File system efficiency and usability; directory structure, file growth (Project 4)"),
        E: c("Part 4: File systems", "Course Structure, Part 4")}),
    ("Crash consistency and journaling", {
        N: ns("File System Consistency", "Nov 2", "File system consistency")}),
    ("Distributed file systems", {
        N: ns("Fancy File Systems", "Nov 18 (readings: NFS, the Google File System)", "Fancy file systems (NFS, GFS)")}),
    ("Executable files and loading", {
        G: c("Executable files and loading", "Course Outline, week 8; Assignments (ELF loading)", "Executable files and ELF loading")}),
    ("Computer security", {
        G: c("Authentication and authorization", "Course Outline, weeks 10-11", "Authentication, authorization, access control"),
        N: ns("The Security Mindset", "Nov 30"),
        E: c("introduces preliminary concepts about security", "Course Structure, Part 5", "preliminary concepts about security")}),
    ("Authentication and authorization", {G: gw("Authentication and authorization", 10)}),
    ("Access control lists and capabilities", {G: gw("Access control lists, capabilities, etc.", 11)}),
    ("Networking", {
        G: c("Networking", "Course Outline, week 14; Assignments"),
        N: ns("Networks and Their Abstractions", "Nov 9-11", "Networks and their abstractions; sockets"),
        E: c("This part covers networking, distributed and parallel computing", "Course Structure, Part 5", "networking")}),
    ("Parallel and distributed computing", {
        N: ns("Parallel and Distributed Computing", "Nov 11-16", "Sockets and parallel programming; parallel and distributed computing"),
        E: c("This part covers networking, distributed and parallel computing", "Course Structure, Part 5", "distributed and parallel computing")}),
    ("Virtual machines and containers", {G: gw("Virtual machines, containers, etc", 15)}),
    ("Implementing operating system components", {
        G: c("An operating system that can run a complex program (e.g. networked doom) [group project]", "Assignments; Course Description",
             "Building pieces of an OS; group project: an OS that runs a complex program"),
        N: np("Your other projects will exercise your knowledge of threads, user programs, virtual memory, and file systems.", "Overview",
              "Projects: threads, user programs, virtual memory, file systems"),
        E: c(CATALOG, "Catalog Description; five group programming assignments", "Writing pieces of an operating system")}),
]

d["topics"] = [{"label": lab, "coverage": cov} for lab, cov in ROWS]
d["instructors"][N].update({"detail_level": "weekly_schedule", "external_schedule_url": SCHED,
                            "document_note": "Syllabus defers to the course website; topics come from its dated schedule and project page."})
d["notes"] = ("Reviewed line by line against all three syllabi (Oct 2026). Norman's topics come from the course website her syllabus points to. "
              "Elnozahy's syllabus gives a five-part outline only; Norman's site says the course is taught in collaboration with him, "
              "but nothing is credited to him from her site.")
json.dump(d, open(path, "w", encoding="utf8"), indent=1, ensure_ascii=False)
print(len(ROWS), "topics;", {n: sum(n in cov for _, cov in ROWS) for n in (G, N, E)})
