# Work Log — Issue #35: [Research] PT-1 Literature: simulator-independent rule representations (is a portable rule core feasible?)

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/35
**Branch:** `docs/35-simulator-independent-rule-representations`
**Started:** 2026-10-18

## Understanding the issue

Every rule this repository extracts is written in negsim's own terms: geometric encounter
classes, ORCA directive fields, thresholds tuned to ORCA, and at most two roles
(`llm_negotiation/docs/rule-format.md` §§2–7; issue #34, "Why this track exists"). Issue #34
proposes, **without anyone's agreement yet**, a *portable rule core*: a rule written once over a
fixed, versioned vocabulary (conflict types, roles, features, actions), carried out by each
simulator through a perception adapter and an action adapter, checked by shared conformance
tests, and tested on unseen scenarios.

This issue does not build any of that. It asks the literature one question: **can a conflict
rule be written down once, independently of any simulator, and still be carried out faithfully by
several different simulators?** In six parts:

- **Q1** how other fields write rules or norms independently of the system that follows them
  (institutional grammar, normative MAS, and one simulation interoperability standard, with what
  made "write once, run in many" work there and what limits it);
- **Q2** whether any crowd, pedestrian, game or robot-navigation study ran the *same behaviour
  rule* in two or more simulators, kept apart from studies that run different simulators on the
  same scenario;
- **Q3** existing taxonomies or ontologies the vocabulary could adopt;
- **Q4** the failure modes of abstracting a rule away from its simulator, with evidence;
- **Q5** novelty: arXiv:2409.00993 read in full, plus a search for LLM-derived norms written down
  for reuse by other systems;
- **Q6** a verdict (feasible / feasible with changes / not supported) and a recommended
  representation (adopt IG 2.0, adapt it, or extend this repository's own format).

The answer has to be bounded by what the entries support; the game-theory review already says
the "generic simulator" requirement is a design goal, not a finding
(`literature/game-theory/g6-transfer-across-games.md`, "What this means for the FYP", point 1).

### Assumptions I am making (judgement calls, not instructions from the issue)

- **A1. Branch base.** The workflow says branch from `main`, but `origin/main` is still
  `5a0f7be` and has none of the four files this issue says to read. Every branch since #8 is
  stacked on the one before; for #30 and #32 the user was asked and chose to stack each time
  (`WORK_LOG-30.md` P2, `WORK_LOG-32.md` P1). I therefore cut this branch from
  `feat/32-fictional-ethnicity-passage-meetings` (`81d85f8`, PR #33's head, in sync with
  origin) and will target the PR at that branch. A merge into a non-default branch will not
  close #35 by itself.
- **A2. Cache prefix.** Sources for this issue are cached as `refs/pr_*` (portable rules),
  following `gt_*` (#20) and `sr_*` (#22). PDFs are tracked as before unless oversized; those
  go in `.gitignore` with a re-download link, as in #20 and #22.
- **A3. Three reads beyond "these, and only these"**, each for a stated reason:
  1. #34's "Constraints for every issue in this track", because they bind this issue (no paid calls;
     no change to `llm_negotiation/`; mark decisions and assumptions; nothing may switch the group
     on);
  2. issue #20's risk R4 (`WORK_LOG-20.md`) and `g6-transfer-across-games.md` §3, which the issue
     cites as the reason the novelty paper matters;
  3. *(added later in the session)* the single rule file `single_file_first_arrival.v1.yaml`, to
     check #34's worked example (flag F4).
- **A4. Stubs** for sources I cannot open live in `representations.md` under their group, with
  exactly the issue's six lines, and are listed in `missing-papers.md` (#22's A2 reading).
- **A5. "Read in full"** means the whole body text, read from the cached extract; reference
  lists and appendices only where a claim needs them. An entry read only in part says which
  sections.
- **A6. Extra entry group.** Q2 needs studies that are none of the five seed groups (model
  docking and replication; same controller in several robot simulators). They go in a sixth group
  in `representations.md`, "Precedent: the same rule in more than one simulator".
- **A7. What is committed, now that I know the repository is public** (`gh repo view`:
  `PUBLIC`). Text extracts are committed for every source read, as the issue asks. PDFs are
  committed only when the copy is openly licensed or from arXiv (the practice of #16, #20 and
  #22); the three PDFs that are author or repository copies without an open licence are
  gitignored with a re-download link. Chapter 1 of *Conflicting Agents* (Kluwer, ©2002), read
  from the user's own copy in the parent FYP folder, is cached on disk but **gitignored, text
  included**: it is a copyrighted book, not an open source.

## Plan

1. Branch and work log. **(done)**
2. Read what the issue lists, and only that (A3 aside). **(done)**
3. Read arXiv:2409.00993 in full from `refs/gt_arxiv_2409_00993.txt`; check for a published
   version. **(done)**
4. Confirm every seed lead from its own page (arXiv API, Crossref, publisher or journal page);
   resolve the `[unverified lead]`s; download what is open, check each first page against the
   expected title, cache text as `refs/pr_*`. **(done)**
5. Targeted searches, each logged with its query and outcome: Q2 (same rule in two or more
   simulators), Q3 (taxonomies of pedestrian situations and conflicts), Q5 (LLM-derived norms
   written down for reuse). **(done: 30 searches)**
6. Write the entries (`representations.md`), grouped as the seed leads are, plus A6's group.
   **(done)**
7. `novelty-check.md`. **(done)**
8. `feasibility.md`: the idea restated in my own words with what is unclear or inconsistent in
   it, then Q1–Q6, every claim citing an entry. **(done)**
9. `verdict.md`, one page at most, written for PT-7. **(done)**
10. `search-log.md`, `missing-papers.md`, `refs-portable-rules.bib`. **(done)**
11. Check every acceptance criterion and workflow §5b; post progress comments at milestones;
    push; open the PR against PR #33's branch; comment on the issue.

## Progress log

### 2026-10-18 — Preconditions, branch, and the required reading
- What I did: checked preconditions (remote `M450NCH00/CrowdSimulation`, `gh` authenticated,
  tree clean, not a linked worktree); read the issue (no comments) and the four items it lists:
  #34 "Why this track exists" and "The idea"; `g6-transfer-across-games.md` "What this means for
  the FYP"; `research-gap.md` §3 and §5; `rule-format.md` §§1–7. Also #34's constraints (A3).
- Why: workflow steps 0–3; the issue's "Before starting".
- Result / what I found:
  - `origin/main` has none of the four files; they exist only on the stack (A1).
  - Three things in the reading that shape the search: (1) the review of 35 simulator rules found
    **no source that evaluates one rule with two different kinds of agent** (`research-gap.md`
    §3(a)), so Q2 needs a search of its own; (2) the same review separates a rule's *form*
    (portable) from its *content* (a local convention, e.g. which side) (§3, on
    [Pruekprasert-RightOfWay]); (3) today's format already treats "what a rule may read" as a
    question of what **both** agents can compute identically (`rule-format.md` §5). That is a
    conformance question in miniature, and it is where Q4's "two implementations of the same term
    disagree" would bite.
- Next step: the novelty paper, then the seed leads.

### 2026-10-18 — The novelty paper, read in full
- What I did: read arXiv:2409.00993 in full (about 2,700 words; 5 pages) from a reading-order
  re-extraction of the cached PDF `refs/gt_arxiv_2409_00993.pdf` (the cached `-layout` text
  interleaves the two columns). Checked for a published version: the arXiv record has no
  journal reference or DOI, Crossref finds nothing by title, and a web search found only the
  arXiv listing and blog reposts. It stays `[preprint]`.
- Why: Q5; risk R4 of `WORK_LOG-20.md` ("until it is read in full, the FYP's novelty claim is
  unverified").
- Result / what I found: the paper's "norms" are **behaviour patterns the authors read off the
  agents' punishment choices and natural-language judgements** (Results, the paragraphs on
  Figure 4). Nothing is written down as a rule, nothing is stored, nothing is reused by another
  system, and there is one game. Transfer to other games is named as future work (Conclusion).
  So it overlaps the FYP in method (LLM agents, dialogue, norms) but not in what the FYP does with
  the result. Full entry in `novelty-check.md`.
- Next step: confirm the seed leads.

### 2026-10-18 — Sourcing: seeds confirmed, unverified leads resolved, 20 sources cached
- What I did: confirmed every seed from the arXiv API, Crossref or the source's own page, with
  open-access status from OpenAlex; ran the targeted searches for Q2, Q3 and Q5 (queries in
  `search-log.md`); downloaded each source into its own empty folder, checked its first page
  against the expected title, and cached the reading-order text as `refs/pr_*.txt` (A2, A7).
- Why: the issue's sourcing rules; no identifier guessed.
- Result / what I found:
  - **No wrong paper was downloaded.** Every first page matched.
  - **The `[unverified lead]`s:**
    - Crawford and Ostrom (1995) **exists** (*APSR* 89(3), 582–600, doi:10.2307/2082975) but is
      closed. The only free copy found is a JSTOR printout on a third-party site, which I did not
      use. → stub.
    - "Modelling Institutions Using Dynamic Deontics" **exists**: Frantz, Purvis, Nowostawski and
      Savarimuthu, COIN IX, LNCS, 211–233, 2014, doi:10.1007/978-3-319-07314-9_12. It is closed,
      and Academia.edu returns 403. → stub. The same authors' "nADICO: A Nested Grammar of
      Institutions" (PRIMA 2013, doi:10.1007/978-3-642-44927-7_31) was also found.
    - "Linking sanctions to norms in practice" **exists**: arXiv:2205.10295 (2022). The authors are
      **Mellema and Dignum** (two authors, not "et al."). No published version was found.
    - Gomes et al. (2018) **exists**: *ACM Computing Surveys* 51(3), article 49,
      doi:10.1145/3179993. I read the authors' accepted version, from co-author Broman's KTH page.
    - Francis et al. (2023) **exists** and has been published: *ACM THRI* 14(2), 2025,
      doi:10.1145/3700599 (CC BY). ACM and Aston blocked automated download, so I read arXiv v4,
      which may differ from the 65-page published version.
  - **Confirmed as the issue asked:** JASSS 14(2) 6 is Hollander and Wu (2011), "The Current
    State of Normative Agent-Based Systems", doi:10.18564/jasss.1750. arXiv:2005.12712 is Kleinmeier,
    Köster and Drury, published as *J. R. Soc. Interface* 17(171), 20200396 (2020). I read arXiv
    v2, because the publisher blocked automated download.
  - **Not obtained (stubs):** Crawford and Ostrom 1995; the COIN 2014 dynamic-deontics chapter;
    the *Institutional Grammar* book (Palgrave 2022, doi:10.1007/978-3-030-86372-2, closed); and
    Donkin et al. 2017. Donkin et al. is open access (CC BY), but ScienceDirect and Aberystwyth both
    refused automated download. Frantz's 2015 Otago thesis (open access, covering nADICO) sits
    behind a JavaScript portal; it is logged as an unread lead, not stubbed, because it is not a
    seed.
  - **Added from the searches:**
    - Q2: docking and replication (Axtell et al. 1996; Edmonds and Hales 2003; Wilensky and
      Rand 2007) and HuNavSim 2.0.
    - Q1 and Q4: FMI (Blochwitz et al. 2011; the FMI 3.0.2 specification; Bertsch et al. 2017)
      and the LCIM (Wang, Tolk and Wang 2009).
    - Q3: Tessier et al.'s conflict typology (chapter 1).
    - Q5: CRSEC (Ren et al., IJCAI 2024), TR2MTL (Manas et al., IEEE IV 2024) and Savarimuthu et
      al. (COINE 2024).
- Next step: read, and write the entries.

### 2026-10-18 — Groups 1–3 read and written up (11 entries, 3 stubs)
- What I did:
  - Read in full: [Frantz-IG2], [Neumann-HomoSocionicus], [Hollander-NormativeABS],
    [Mellema-Sanctions], [Blochwitz-FMI], [Bertsch-ReferenceFMUs], [Wang-LCIM].
  - Read in sections: [Frantz-IG2Codebook], [FMI-3.0.2], [Gomes-CoSim].
  - Wrote their entries and the three institutional-grammar stubs in `representations.md`.
  - Also cached the IG Parser README `[documentation]`, and Galán and Izquierdo (2005). The latter
    was found through [Neumann-HomoSocionicus] Note 7: a re-implementation of the very norms game
    arXiv:2409.00993 builds on.
  - Re-extracted every PDF text as UTF-8 (pdftotext's default Latin-1 garbled names; line numbers
    unchanged).
- Why: Q1 and Q4 rest on these groups.
- Result / what I found (the threads that will carry the verdict):
  1. **Nothing in groups 1–2 is both shared between systems and executable.** IG is a shared
     coding specification for text; its IG Script is parseable into tables, not run
     ([Frantz-IG2Codebook] §4.1; IG Parser README). Normative-MAS norms are executable only
     inside the system that defines them ([Neumann-HomoSocionicus] Table 4;
     [Hollander-NormativeABS] ¶2.19–¶2.23). How norms travel between systems was an open
     question in 2011 ([Hollander-NormativeABS] ¶5.4, ¶5.10).
  2. **FMI works because one executable implementation travels behind a small typed
     interface**, and was deliberately "less powerful, but much simpler" ([Blochwitz-FMI] §1;
     [FMI-3.0.2] §1.3). #34's standalone engine is that shape; its adapters are FMI's "tool
     dependent wrapper".
  3. **Even so, implementations drift:** 5 of 10 importing tools failed one reference test
     ([Bertsch-ReferenceFMUs] §4.3). Wrappers absorb domain decisions, and results depend on the
     coupling step ([Gomes-CoSim] §5.2, §4.3). A shared schema plus API reaches only LCIM's
     syntactic level ([Wang-LCIM] §4.1).
  4. Two parts that the idea lacks turned up in the norm literature: a **deactivation condition**
     and a **deadline** ([Mellema-Sanctions] §1), and the violation-handling / meta-norm split
     that queue cutting needs (§6). IG's **activation condition / execution constraint** split
     gives the core and its binding separate places ([Frantz-IG2] §3.1).
- Next step: groups 4–6, then the novelty sources.

### 2026-10-18 — Groups 4–6 and the novelty sources read; all entries written
- What I did:
  - Read in full: [Curtis-Menge], [Kleinmeier-Cooperation], [EscuderoJimenez-HuNavSim2],
    [Axtell-Docking], [Edmonds-Replication], [Wilensky-MakingModelsMatch],
    [Galan-Reimplementing].
  - Read in sections: [Francis-SocNavPrinciples]; [Tessier-ConflictingAgents] (chapter 1,
    pp. 4–21); for the novelty check, CRSEC (§2, §3.1, §4), TR2MTL (§I, §IV–§VI) and Savarimuthu
    et al. (§1, §4, §6).
  - Term-searched arXiv:2409.00993's full text, as #16's novelty check did.
  - Wrote groups 4–6 and the Donkin et al. stub.
- Why: Q2 to Q5.
- Result / what I found:
  1. **Q2 has a plain answer.** No crowd, pedestrian, game or robot-navigation study read here ran
     one behaviour rule in two simulators and compared the behaviour.
     - Menge holds one behaviour layer fixed across three motion models inside one framework.
       The trajectories differed, and each model needed its own time step (Figure 4, labels
       decoded from interleaved text).
     - HuNavSim 2.0 runs one behaviour engine in four host simulators but compares nothing across
       them.
     - The only direct precedents are social-simulation docking and replication studies. All four
       found differences hidden in details nobody counted as part of the rule: agent activation
       order, event order, tie-breaking, ≤ against <, run length.
  2. **Every pedestrian-side "portable" behaviour layer is portable by design intent only**
     ([Kleinmeier-Cooperation] §II A; [EscuderoJimenez-HuNavSim2] §III).
  3. **Q3:** no source classifies pedestrian situations by *what is contested*.
     [Tessier-ConflictingAgents] gives the top level (physical/resource against knowledge
     conflicts) and a hardness distinction that separates a passage from a queue.
     [Francis-SocNavPrinciples] gives established *geometric* scenario names, including "the one
     leaving goes first" for rooms.
  4. **Q5:** LLM-derived norms *are* written down in prior work, but only for LLM agents inside
     one environment (CRSEC's quintuple with a natural-language core) or as LLM *translations* of
     human-written law into temporal logic, monitored in one simulator (TR2MTL). Neither runs a
     rule across simulators.
  5. A decision for honesty in Q2: Menge's figure labels were decoded by me from interleaved
     characters (`∆tO=RC0.A1 s` → "Δt ORCA = 0.1 s"). The decoding is unambiguous, but it is mine,
     so the entry says so.
- Next step: `novelty-check.md`, then `feasibility.md` and `verdict.md`.

### 2026-10-18 — Synthesis written; deliverables verified; corrections made on the way
- What I did:
  - Wrote `novelty-check.md`, `feasibility.md` (the idea restated, flags F1–F11, Q1–Q6),
    `verdict.md`, `missing-papers.md`, `search-log.md` and `refs-portable-rules.bib`.
  - Added #35 to `README.md` (roadmap row 5e, three findings, directory layout), as #16, #20
    and #22 did.
  - Opened one more file, outside "these, and only these": the rule file
    `single_file_first_arrival.v1.yaml`, to check #34's worked example. It ranks by
    `agent.time_to_segment_s`, a *predicted* arrival, which became flag F4.
- Why: the deliverables list; workflow §5b.
- Result / what I found:
  - **Verdict: feasible with changes.** The claim must be decision conformance (same Situation →
    same Decision), with behaviour across simulators measured against an equivalence standard
    fixed in advance.
  - Recommended representation: extend this repository's format, restructured around an adapted
    IG 2.0, with Mellema's deactivation and deadline and IG profiles.
  - **Verification run:**
    - a script cross-checked every handle cited in every file against the entries defined (28),
      every BibTeX key named in an entry against the `.bib` (27 records), and the `.bib`'s
      braces. No undefined handle, no missing key, balanced;
    - 51 of the numbers and quotations relied on in `feasibility.md` and `verdict.md` were grepped
      against their cached texts. All were found except one, which is split by a hyphen across a
      page in the extract ("dif-" / "ferences") and is correct;
    - `verdict.md` is 490 words, one page.
  - **Corrections made, so the record is honest:**
    1. My first issue comment said "21 entries"; it is 19 plus 4 stubs. The comment was edited in
       place and says so.
    2. My first README line said "5 papers unobtained"; it is 4 (plus 2 read only as preprints).
    3. In this log (entry "Groups 1–3") and in the issue comment I wrote that 5 of 10 FMI importers
       "failed one reference test". [Bertsch-ReferenceFMUs] §4.3 says "five tools show errors in ME
       due to violations of the calling sequence" on the Integer and Boolean reference FMUs.
       `feasibility.md` uses the exact wording. The earlier log entry is left as written, per the
       workflow.
    4. `search-log.md`'s first tally of full and partial reads was wrong (12 and 7). It is 14 and
       5 in `representations.md`, plus 1 and 3 in `novelty-check.md`.
- Next step: push, open the PR against PR #33's branch, comment on the issue.

## Open questions / risks

**For the user or the supervisor to decide**

- **Q1. The idea's own inconsistencies** (`feasibility.md` §2). F1 (where today's ORCA conditions go),
  F4 (`arrival_order`: predicted against recorded) and F6 (time units and the engine's call rate)
  must be settled before PT-8 writes vocabulary v0. They are design decisions, not findings.
- **Q2. The recommended representation is my design proposal**: extend this repository's format
  around an adapted IG 2.0 (`feasibility.md` §8.2). It is argued from the entries, but it is
  `[inference]` and needs sign-off. So does the verdict's re-statement of the claim as *decision
  conformance*.
- **Q3. Copyright and the public repository.** As the issue asks, and as #16, #20 and #22 did,
  `refs/` now holds full-text extracts of every source read. Three of the copies carry no open
  licence:
  - the IG 2.0 accepted manuscript ("This article is protected by copyright. All rights
    reserved.");
  - the ACM accepted version of Gomes et al.;
  - Axtell et al.'s 1995 preprint.

  Their PDFs are gitignored but their text is committed (work log A7). The book chapter is
  local-only. **The user may prefer to gitignore those three text files too.** That would also
  need them removed from this branch's history before merge, since they are already in commits
  `8c40ae9` and `fa46612`.
- **Q4. Closing the issue.** The PR targets `feat/32-fictional-ethnicity-passage-meetings` (A1), so
  `Closes #35` will not close the issue on merge, as with #30 and #32.

**Risks in the evidence**

- **R1. Q2's "none found" is bounded by this search**: 30 web searches, English only, one session
  (`search-log.md` §2). A study running one pedestrian rule in two simulators could exist under
  terms not tried.
- **R2. The docking evidence comes from social simulation, not crowd simulation.** Carrying its
  lesson over (behaviour diverges on update order, ties, strictness) is an inference, supported
  only indirectly by [Curtis-Menge] Figure 4 and [Kleinmeier-Cooperation] §II C.
- **R3. Two figures were reconstructed by me**: Menge's Figure 4 time-step labels (decoded from
  interleaved characters) and Francis et al.'s Table III columns (re-ordered from jumbled text).
  Both are flagged in their entries. A human check of the PDFs would remove the doubt.
- **R4. Eight entries were read in sections only** (codebook, FMI specification, Gomes, Francis,
  Tessier, CRSEC, TR2MTL, Savarimuthu). Claims are limited to the sections listed.
- **R5. ADICO is cited second-hand**, through [Frantz-IG2] §2. M1 was not obtained.
- **R6. Versions.** Francis et al. were read as arXiv v4, which may differ from the 2025 journal
  version. Kleinmeier et al. were read as arXiv v2. Savarimuthu et al.'s post-proceedings version
  was not checked. If Horiguchi et al. is later published, its citation should be updated.
- **R7. Not searched**: rule-interchange standards outside simulation engineering (W3C RIF, OASIS
  LegalRuleML, W3C ODRL). They are the closest thing to a "portable rule core" outside
  simulation and are listed as a lead (`search-log.md` §6).
- **R8. The FMI and HLA analogies are mine.** Those standards move models and data, not norms
  (`feasibility.md` §3.2, item 5). How far their lessons transfer to rules is `[inference]`.
- **R9. The verdict precedes PT-2 to PT-6.** PT-5 and PT-6 (the simulators) may show that one of the
  testbeds cannot host an adapter at all. PT-7 should re-check §8 against them.

## Summary

**What changed.** A new folder `literature/portable-rules/` (seven files), 21 cached text extracts
`refs/pr_*.txt` plus the IG Parser README, three `.gitignore` entries with re-download links, and
`README.md` (row 5e, three findings, layout). Nothing under `llm_negotiation/`, the Phase 1 dataset
or the pipeline was touched. No paid call was made, and no code was written.

**Why.** Issue #35 (PT-1 of track #34) asks whether a conflict rule can be written once and carried
out faithfully by several simulators.

**The answer, in short:**
- Writing it once: yes, long established for norms.
- Carried out faithfully: never shown for behaviour rules in the four fields. The docking evidence
  says behaviour diverges on details outside the rule.
- **Verdict: feasible with changes**, claimed as decision conformance, with behaviour measured per
  simulator. Recommended representation: extend this repository's format around an adapted IG
  2.0.
- arXiv:2409.00993 (risk R4) shares the method only; the new part is the combination.

**How it was verified** (workflow §5b, since there is no test suite for a review):
- **Locators**: every claim in the entries carries a section, paragraph, table, figure, page or
  equation locator, or is marked `[inference]` / `[unverified]`. Of the numbers and quotations
  `feasibility.md` and `verdict.md` rely on, 51 were grepped against the cached texts. All were
  found, one split by a hyphen.
- **Consistency**: a script found no undefined handle in any file, no BibTeX key missing from the
  `.bib`, and balanced braces.
- **Sourcing**: every entry was confirmed from its own page, arXiv record or Crossref, with OpenAlex
  for open access. Every download was first-page-checked; no wrong paper.
- **Uncertainty stated**: "Open questions / risks" above is not empty (Q1–Q4, R1–R9).
- **Caching**: every source read is in `refs/` (A2, A7).

**Acceptance criteria** (issue #35):
- [x] `feasibility.md` restates the idea in my own words and flags what is unclear or inconsistent
  in it: §1, §2 (F1–F11).
- [x] Every entry is confirmed from its own page, with its status recorded: each entry's
  "Status"; `search-log.md` §§2–3.
- [x] Every claim has a locator, or is marked `[inference]` or `[unverified]`.
- [x] Q1 to Q6 are each answered: `feasibility.md` §§3–8. Q3 is answered for conflict types,
  roles and rule structure and **only partly for features and actions**, stated as such in §5.
- [x] arXiv:2409.00993 is read in full, with an entry and a plain statement on novelty:
  `novelty-check.md` §§1, 2, 4.
- [x] Q2 says plainly whether any study ran the same rule in two simulators: `feasibility.md` §4.1.
- [x] `verdict.md` fits on one page (490 words).
- [x] Unobtainable sources are stubbed and listed in `missing-papers.md` (M1–M4; plus V1–V2 and S1).
- [x] Nothing is called feasible beyond what the entries support (`feasibility.md` §8.4), and
  "Open questions / risks" is not empty.

**Session note.** The issue was finished in one session; nothing is left half-done. The unread
leads are listed in `search-log.md` §6 for whoever continues the track.
