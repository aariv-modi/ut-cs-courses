"""CS 331: topic list rebuilt after a line-by-line review of all four syllabi (project owner asked for the most
accurate, complete representation).

Sources per instructor:
* Fares Fraij - SimpleSyllabus page: learning outcomes, dated schedule, notes.
* Dana Moshkovitz Aaronson - course-information handout: topic list (section 5), exams, homework guide.
* Greg Plaxton - syllabus PDF: 14-module outline (slide file names; the topic column is interleaved in the PDF text).
* Kevin Tian - syllabus PDF says "The syllabus is on the course website" (hidden link). The website's dated schedule
  and the section titles of the posted lecture notes (Parts I-V) are in data/supplemental/331_tian_*.txt, accepted
  by the validator through overrides.supplemental_sources. Later units (continuous, randomized, complexity) are
  only named on the schedule; complexity-theory topics are therefore hedged ("possible").
Textbook section numbers alone (e.g. Fraij's Kleinberg-Tardos readings) are never used as evidence.
Worked example problems (e.g. Tian's largest subarray sum) are listed in as_written, not as rows.
Re-runnable: rebuilds the topic list from scratch each time.
"""
import json
from common import ROOT

path = ROOT / "data/topic_out/331.json"
d = json.load(open(path, encoding="utf8"))
F, A, P, T = "Fares Fraij", "Dana Moshkovitz Aaronson", "Greg Plaxton", "Kevin Tian"
WEB = "https://kjtian.github.io/cs331_fa26.html"


def c(evidence, where, as_written=None, status="stated"):
    return {"status": status, "evidence": evidence, "where": where, "as_written": as_written or evidence}


def tw(quote, date, as_written=None, status="stated"):            # Tian, course-website schedule
    return c(quote, f"Course website schedule ({date}), linked from the syllabus", as_written, status)


def tn(quote, part, as_written=None):                             # Tian, lecture-notes section titles
    return c(quote, f"Lecture notes {part} (posted on the course website)", as_written)


def pm(slide, module, as_written=None):                           # Plaxton, course outline
    return c(slide, f"Course Outline, module {module}", as_written)


HEDGE_T = "hedged: the website names only 'Complexity theory' (weeks 13-16); notes for that unit are not posted yet"
ROWS = [
    ("Stable matching", {
        F: c("Stable Marriage", "Schedule Aug 27"),
        P: pm("01B_stable_marriage", 1, "Stable marriage"),
        T: tn("Stable matching", "Part IV (Greedy algorithms)")}),
    ("Proofs of algorithm correctness", {
        F: c("including constructing rigorous correctness proofs", "Learning Outcomes; Writing Algorithms and Justification Requirements"),
        A: c("An argument for the algorithm's correctness.", "Guide to writing up homework"),
        T: tw("Proofs (Part I, Section 2)", "8/24 mini-lecture", "Proofs: what is a good proof?, proof techniques")}),
    ("Running-time analysis and asymptotic notation", {
        F: c("Analyze the time and space complexity of algorithms using formal asymptotic notation.", "Learning Outcomes; Schedule Sep 01 (Complexity)"),
        A: c("An analysis of the algorithm's running time.", "Guide to writing up homework"),
        P: pm("01A_introduction", 1, "Course overview; growth of functions"),
        T: tw("Asymptotics (Part I, Section 3)", "8/26 mini-lecture", "Asymptotics")}),
    ("Amortized analysis", {P: pm("05C_amortized_analysis", 5, "Amortized analysis")}),
    ("Data structures review (lists, heaps, BSTs, hash tables)", {
        T: tw("Data structures (Part I, Section 7)", "9/2 mini-lecture", "Data structures: lists, heaps, binary search trees, hash tables")}),
    ("Splay trees and augmented trees", {P: c("06A_splay_trees ... 06B_augmented_trees", "Course Outline, module 6", "Splay trees; augmented trees")}),
    ("Graph basics and representations", {
        T: tw("Graphs (Part I, Section 4)", "9/9 mini-lecture", "Graphs: definitions, trees, representing a graph")}),
    ("Graph traversal (BFS/DFS)", {
        F: c("Undirected/Directed Graph Traversal", "Schedule Sep 01-03"),
        A: c("Graphs search", "Course Material (topics)", "Graph search"),
        P: pm("02A_basic_graph_algs", 2, "Graph traversal"),
        T: tn("Breadth-first search", "Part V (Graph algorithms)", "Search: breadth-first search, depth-first search")}),
    ("Greedy algorithms", {
        F: c("Greedy Algorithms", "Schedule Sep 08-10"),
        A: c("greedy algorithms", "Course Material (topics)"),
        P: pm("02B_greedy_algs", 2, "Greedy algorithms"),
        T: tw("Greedy algorithms (Part IV, Sections 1, 2, 3)", "9/21-9/28",
              "Greedy algorithms: exchange arguments, greedy stays ahead; fractional knapsack, scheduling (total completion time, lateness)")}),
    ("Minimum spanning trees", {
        F: c("Minimum Spanning Trees: Kruskal's, Prim's, Reverse Delete", "Schedule Sep 15"),
        P: pm("03B_kruskal_mst", 3, "Kruskal's MST algorithm"),
        T: tn("Minimum spanning tree", "Part IV (Greedy algorithms)")}),
    ("Single-source shortest paths (Dijkstra)", {
        F: c("Develop proficiency with graph algorithms, including traversal methods, shortest-path algorithms, and minimum spanning tree algorithms.",
             "Learning Outcomes; hedged: Dijkstra's algorithm is not named", "shortest-path algorithms", "possible"),
        P: pm("03A_dijkstra_sssp", 3, "Dijkstra's single-source shortest paths algorithm"),
        T: tn("Dijkstra", "Part V (Graph algorithms)", "Shortest paths: Dijkstra; heuristics for s-t shortest path")}),
    ("Bellman-Ford shortest paths", {
        F: c("Sequence alignment, Bellman-Ford shortest paths", "Schedule Oct 06", "Bellman-Ford shortest paths"),
        P: pm("05A_bellman_ford_and_floyd_warshall", 5, "The Bellman-Ford and Floyd-Warshall algorithms"),
        T: tn("Bellman-Ford", "Part V (Graph algorithms)", "Bellman-Ford; arbitrage")}),
    ("All-pairs shortest paths (Floyd-Warshall)", {
        P: pm("05A_bellman_ford_and_floyd_warshall", 5, "The Bellman-Ford and Floyd-Warshall algorithms"),
        T: tn("All-pairs shortest paths", "Part III (Dynamic programming)")}),
    ("Divide and conquer", {
        F: c("Divide and Conquer", "Schedule Sep 17-24"),
        A: c("divide and conquer", "Course Material (topics)"),
        P: pm("03C_divide_and_conquer", 3, "Divide and conquer recurrences"),
        T: tw("Recursion (Part II, Sections 1, 2, 4)", "8/24-8/31", "Recursion (divide and conquer)")}),
    ("Solving recurrences", {
        F: c("Divide and Conquer: Merge Sort, Recurrences", "Schedule Sep 24; notes: Master method (CLRS 4.5)", "Recurrences; Master method"),
        P: c("Divide and conquer recurrences", "Course Outline, module 3"),
        T: tn("Recurrences", "Part II (Recursion)")}),
    ("Sorting algorithms (mergesort, quicksort)", {
        F: c("Divide and Conquer: Merge Sort, Recurrences ... Randomized Quicksort", "Schedule Sep 24, Nov 19", "Merge sort; randomized quicksort"),
        P: pm("14B_quicksort", 14, "Randomized sorting"),
        T: tn("Sorting", "Part II (Recursion)", "Sorting; inversions")}),
    ("Selection and median finding", {
        F: c("Randomized Median Finding", "Schedule Dec 01"),
        T: tn("Selection", "Part II (Recursion)")}),
    ("Fast multiplication (integers, Strassen's algorithm)", {
        T: c("Multiplication ... Strassen's algorithm", "Lecture notes Part II (Recursion), posted on the course website", "Multiplication; Strassen's algorithm; Fibonacci numbers")}),
    ("Fast Fourier Transform", {
        P: pm("04A_fast_fourier_transform", 4, "The Fast Fourier Transform algorithm"),
        T: tn("Fast Fourier transform", "Part II (Recursion)")}),
    ("Dynamic programming", {
        F: c("Dynamic Programming", "Schedule Sep 29-Oct 06"),
        A: c("dynamic programming", "Course Material (topics); Test 2"),
        P: pm("04B_dynamic_programming", 4, "Dynamic programming"),
        T: tw("Dynamic programming (Part III, Sections 1, 2)", "9/2-9/16",
              "Dynamic programming: largest jump, largest subarray sum, balanced parentheses, scheduling, longest increasing subsequence, "
              "longest palindromic substring, game theory, directed acyclic graphs")}),
    ("Knapsack and subset sum", {
        F: c("Dynamic Programming: subset sum", "Schedule Oct 01", "Subset sum"),
        P: pm("05B_knapsack", 5, "The knapsack problem"),
        T: tn("Subset sum", "Part III (Dynamic programming)")}),
    ("Sequence alignment and longest common subsequence", {
        F: c("Sequence alignment, Bellman-Ford shortest paths", "Schedule Oct 06", "Sequence alignment"),
        T: tn("Longest common subsequence", "Part III (Dynamic programming)")}),
    ("Maximum flow and min-cut", {
        F: c("Ford-Fulkerson max-flow algorithm, Max-flow min-cut theorem", "Schedule Oct 08-15"),
        A: c("network flow", "Course Material (topics); Test 2"),
        P: c("07A_ford_fulkerson ... 07B_edmonds_karp", "Course Outline, module 7", "Ford-Fulkerson and Edmonds-Karp max-flow algorithms"),
        T: tn("Maxflow-mincut theorems", "Part V (Graph algorithms)", "Flows and cuts: maxflow-mincut theorems, maxflow algorithms")}),
    ("Network flow applications and reductions", {
        F: c("Max-flow min-cut theorem, applications", "Schedule Oct 08, Oct 15", "Max-flow applications"),
        P: pm("08A_project_selection", 8, "A project selection problem"),
        T: tn("Flow reductions", "Part V (Graph algorithms)")}),
    ("Bipartite matching", {P: pm("08B_bipartite_matching", 8, "Bipartite matching")}),
    ("Linear programming", {
        A: c("network flow; linear programming.", "Course Material (topics); Test 2", "linear programming"),
        P: pm("08C_linear_programming", 8, "Linear programming")}),
    ("Continuous algorithms", {T: tw("Continuous algorithms", "10/19-10/28 lectures")}),
    ("Linear algebra review", {T: tw("Linear algebra (Part I, Section 5)", "10/21 mini-lecture", "Linear algebra: notation, linear subspaces, spectral theory")}),
    ("Probability review", {T: tw("Probability (Part I, Section 6)", "10/14 mini-lecture", "Probability: conditioning and independence, expectation and variance")}),
    ("Randomized algorithms", {
        F: c("Halting problem, Randomized algorithms, Randomized Quicksort", "Schedule Nov 19, Dec 01", "Randomized algorithms; randomized quicksort; randomized median finding"),
        P: pm("14A_randomized_algs", 14, "Randomized algorithms"),
        T: tw("Randomized algorithms", "11/2-11/9 lectures")}),
    ("Polynomial-time reductions", {
        F: c("Polynomial Time Reduction", "Schedule Oct 20-27"),
        A: c("Karp reductions and NP-Completeness;", "Course Material (topics)", "Karp reductions"),
        P: pm("09A_polynomial-time_reductions", 9, "Polynomial-time reductions"),
        T: tw("Complexity theory", "11/16-12/7 lectures", "complexity theory", "possible") | {"where": f"Course website schedule (11/16-12/7); {HEDGE_T}"}}),
    ("Complexity classes (P, NP, coNP, EXP)", {
        A: c("P, NP, coNP, PSPACE, EXP;", "Course Material (topics)"),
        P: pm("09C_the_class_NP", 9, "The class NP"),
        T: tw("Complexity theory", "", "complexity theory", "possible") | {"where": f"Course website schedule (11/16-12/7); {HEDGE_T}"}}),
    ("NP-completeness", {
        F: c("Polynomial Time Reduction, NP-Completeness", "Schedule Oct 27"),
        A: c("Karp reductions and NP-Completeness;", "Course Material (topics)", "NP-Completeness"),
        P: pm("10A_NP-completeness", 10, "NP-completeness"),
        T: tw("Complexity theory", "", "complexity theory", "possible") | {"where": f"Course website schedule (11/16-12/7); {HEDGE_T}"}}),
    ("Satisfiability", {P: pm("09B_satisfiability", 9, "Satisfiability")}),
    ("Three-dimensional matching", {P: pm("10B_three-dimensional_matching", 10, "The three-dimensional matching problem")}),
    ("Graph coloring", {
        F: c("Graph Coloring", "Schedule Oct 29"),
        P: pm("11A_graph_coloring", 11, "The graph coloring problem")}),
    ("PSPACE and PSPACE-completeness", {
        F: c("PSPACE/PSPACE-completeness", "Schedule Nov 10"),
        A: c("P, NP, coNP, PSPACE, EXP;", "Course Material (topics)", "PSPACE"),
        P: pm("11B_PSPACE", 11, "PSPACE and PSPACE-completeness")}),
    ("Turing machines", {
        F: c("Turing Machine", "Schedule Nov 12; notes: Sipser 3.1"),
        P: pm("11C_turing_machines", 11, "Turing machines")}),
    ("Undecidability and the halting problem", {
        F: c("Undecidability, Halting problem", "Schedule Nov 17-19"),
        A: c("undecidability, the halting problem, Turing reductions;", "Course Material (topics); Test 3"),
        P: c("12A_undecidability ... 12B_halting_problem", "Course Outline, module 12", "Undecidability; the halting problem")}),
    ("Approximation algorithms", {
        F: c("Approximation Algorithms", "Schedule Nov 03-10"),
        P: c("12C_load_balancing ... 13A_vertex_cover ... 13B_set_cover", "Course Outline, modules 12-13",
             "Approximation algorithms: load balancing, vertex cover, set cover")}),
    ("Backtracking", {F: c("including greedy algorithms, divide-and-conquer, dynamic programming, and backtracking.", "Learning Outcomes", "backtracking")}),
]

d["topics"] = [{"label": lab, "coverage": cov} for lab, cov in ROWS]
it = d["instructors"]
it[T].update({"detail_level": "weekly_schedule", "external_schedule_url": WEB,
              "document_note": "Syllabus PDF defers to the course website; topics come from the website schedule and posted lecture-note section titles."})
d["notes"] = ("Reviewed line by line against all four syllabi (Oct 2026). Plaxton's module titles are interleaved in the PDF text, so quotes "
              "use slide file names. Tian's topics come from the course website linked in his syllabus; his complexity-theory unit is "
              "named only, so specific complexity topics are hedged. Textbook section numbers are not used as evidence.")
json.dump(d, open(path, "w", encoding="utf8"), indent=1, ensure_ascii=False)
print(len(ROWS), "topics;", {n: sum(n in cov for _, cov in ROWS) for n in (F, A, P, T)})
