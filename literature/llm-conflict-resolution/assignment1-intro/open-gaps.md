# Open gaps — Assignment 1 introduction

Prepared for issue [#10](https://github.com/M450NCH00/CrowdSimulation/issues/10).
Companion files: [`paper-selection.md`](paper-selection.md), [`introduction-draft.md`](introduction-draft.md).

Part 1 judged coverage **sufficient** (with one condition), so an introduction was
drafted. This file lists what is still missing or unverified, in two groups:

- **A. Resolve before submission.** The draft is only as accurate as these checks.
- **B. Nice to have.** Claims that would improve the introduction but have no source in
  the current literature review, so they were left out of the draft. Each would need a
  follow-up search issue; none was searched for here, because this issue forbids it.

---

## A. Resolve before submission

### G1 — Zhang et al. [2] full text *(blocking)*
- **What:** the Research Gap sentence says DFD compares its rules with symbolic regression
  "rather than human behaviour". Only the first half is in the abstract. The second half
  is inferred from what the abstract leaves out, so it carries
  `[needs verification against full text]` in the draft.
- **Why it matters:** DFD is the closest prior work. If it *does* validate against human
  data, or distils rules from inter-agent dialogue, the gap paragraph is wrong and must be
  rewritten, not just trimmed.
- **How to close:** get the PDF through the NTU library (ACM DL blocked automated access
  in issue #8; the paper is CC-BY). Check its evaluation section for (a) any comparison
  with empirical human or pedestrian data and (b) whether agents communicate. Then remove
  the marker or rewrite the sentence.

### G2 — "Why crowd simulation matters" is thin
- **What:** the Background establishes importance only through the evacuation example
  ("evacuees all trying to leave quickly can congest the exits" [1], [2]). The issue's
  structure asks for a broad opening on why crowd simulation matters.
- **Gap:** no selected paper says this directly.
- **Available fix within the review:** Wang et al. (2015), *Physica A* 428:396–409
  (supervisor-assigned), simulates stadium evacuation and reports that casualties rise
  sharply under panic and that obstacles reduce them (abstract). Adding it means a
  **sixth** reference, over the issue's 3–5 cap. Either raise the cap or swap it in for a
  paper whose role another covers. Wu [1] is the only candidate, and removing it would
  lose the full-text cost evidence (G3 in the source map).
- **Otherwise:** a paper on crowd-safety applications of simulation (event planning,
  crowd disasters). The current review has none.

### G3 — Incomplete IEEE reference fields
- [2] Zhang et al.: no volume, issue or article number had been assigned when issue #8
  checked it. Re-check on the ACM DL before submission.
- [3] GameChat: cited as IEEE MRS 2025, but only the arXiv v2 text (9 May 2026) was
  read. The IEEE Xplore record (pages, DOI) was not retrieved, and **section/table
  numbers and the 2.767 s figure should be re-checked against the published version**.
  If the published version differs, cite the version actually read.

### G4 — CrowdGym is named but not cited
- **What:** "Introducing the Study" names CrowdGym as the simulation environment the
  project builds on. This is a scope statement, not a claim about the literature, but a
  marker may expect a citation.
- **Gap:** the CrowdGym report (Goh Chen Wei, NTU FYP AY2025/26) is not part of the
  issue #8 review, so this issue's sourcing rule did not allow citing it.
- **How to close:** decide with the supervisor whether an unpublished FYP report may be
  cited; if yes, it becomes a sixth reference (see G2 for the cap problem).

### G5 — The research gap is bounded by the review, not by a systematic search
- **What:** "None of the reviewed studies extracts a reusable rule from LLM-to-LLM
  conflict dialogue and validates it against how people resolve the same conflict."
- **Status:** true of the 14 papers in the issue #8 review, and worded that way on
  purpose. It is **not** evidence that no such work exists. Issue #8 was a targeted
  review, and its own `search-log.md` records blocked sources (ACM DL, APS, Springer,
  ScienceDirect).
- **How to close:** a short targeted search for "LLM dialogue" + "distillation" /
  "convention extraction" + "pedestrian validation" before the final report makes a
  stronger novelty claim. This does not block Assignment 1, as long as the wording stays
  limited to the reviewed studies.

---

## B. Nice to have — claims that lack a source in the current review

Each of these would improve the introduction but lacks a source from the current
literature review, so it was **left out of the draft**.

| # | Claim that would help | Where it would go | What kind of paper would supply it |
|---|---|---|---|
| N1 | Conflicts make **crowd simulations** (not robots) stall or deadlock | Background | A crowd-simulation paper reporting gridlock or deadlock at bottlenecks or in counterflow in agent-based or social-force models. The only deadlock evidence selected is GameChat [3], which is multi-robot navigation. The draft avoids saying "crowd simulation" in the deadlock sentences for this reason. |
| N2 | Per-conflict LLM calls are **quantitatively** infeasible at 10,000 agents | Research Gap / significance | A paper measuring LLM-agent simulation cost or latency against population size. The review has only Wu [1]'s dollar costs at 100 agents, GameChat [3]'s per-dialogue latency at 2–5 agents, and Zhang [2]'s qualitative statement. The draft never puts a number on 10,000-agent cost. |
| N3 | How **real pedestrians** decide who gives way in a narrow corridor | Introducing the Study (validation) | A behavioural study of yielding decisions in two-person head-on encounters. The review has Moeller [5] (non-spatial game), Yamamoto 2019 (how bodies physically pass, not who yields) and the Jülich trajectory data (no behavioural finding). The draft therefore calls the link to Moeller an analogy, not direct evidence. |
| N4 | LLM-derived behaviour has been **validated against human crowd data** | Research Gap | Any paper that checks LLM-agent crowd behaviour against empirical trajectories. Its presence or absence would sharpen G5. |
| N5 | Human conflict resolution is **culturally variable** (relevant to the Singapore-only scope of the Phase 1 dataset) | Scope | Cross-cultural pedestrian or coordination studies. Echeverría-Huarte 2026 covers Spain and Japan, but for free walking, not conflict. |

---

## Corrections to the issue #8 review found during this issue

These do not affect the draft, which follows the primary text, but the review files on
`docs/8-lit-review-llm-conflict-resolution` should be corrected:

1. `topic1-llm-conflict.md`, GameChat entry: says only two agents were evaluated. The
   cached arXiv v2 reports 3-, 4- and 5-agent doorway results (§IV-E, §V-B.4, Table IV).
2. Same entry: says the priority ordering is "supplied by the designer" and the LLM
   "applies a hierarchy". The prompt does not contain the ordering (§IV-C). The designers
   define the ground truth, and the LLM infers urgency from free-text tasks (Table II).
3. `topic2-sociological-grounding.md`, Moeller entry: the 26% and 21% figures are
   rounded from counts (5 and 4 of 19). They are not wrong, but the paper reports the
   counts, so cite the counts.
