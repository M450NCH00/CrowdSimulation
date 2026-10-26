# Work Log — Issue #66: [Feature] RF-11: Step 2 rule extractor with references, debrief support and a held-out fidelity check

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/66
**Branch:** feat/66-rf11-rule-extractor (stacked on `feat/104-rf30-head-on-keep-line`, as the RF issues are)
**Started:** 2026-10-26 (Monday)

## Understanding the issue
Step 2 of track #55: from the head-on sessions the LLM agents **resolved**, find the hidden rule
or pattern behind how they resolved them, with the reference each rule comes from. An LLM (the
"extractor") reads the results and writes the rules; the code around it does the rest
mechanically: the held-out split, the tables, the sampling, the checks, the fidelity score, the
matching of rules across three runs, and storage with provenance.

**The user's decisions (2026-10-26, this session):**
- **Head-on goes on to extraction.** The pooled gate passed narrowly (102 of 192, 0.53, CI 0.46
  to 0.60; RF-30). The report states the narrow pass as a caveat for the supervisor.
- **Paid runs approved for this issue only.** I proposed a cap of USD 0.05 (three extractions at
  about USD 0.01, plus retries); it goes into `CLAUDE.md` under pending item 1 once the preview
  confirms the budget guard's worst case fits it (otherwise I ask again before recording).

**Data.** Round 1's sessions are in two experiments: the independent condition is RF-10's,
re-executed under `keep_line` with no LLM call (`runs/rf10_round1_head_on_keep_line`, 96 rows),
and non-verbal and talk are RF-30's (`runs/rf30_round1_head_on_keep_line`, 192 rows). The gate
pooled their **design** sessions (192: first run of each cell, no counterfactual pair).

## Plan
1. Work log; read the "before starting" files (done: `resolution.md`, `log-schema.md`,
   `rulegen/writer.py`, `keep_left_head_on.v1.yaml`).
2. `negsim/extraction/` (standard library only, as negsim is):
   - **sources and gate:** read several experiment folders, pool their design sessions, check
     each fixed the same gate and recompute it (`analysis.gate`'s rule); skip an encounter type
     that fails, and say so;
   - **tables:** one row per agent per resolved session, in words an LLM can read; a factor of
     the other only as the agent was told it (RF-8's rule, `analysis/load.py`); the failed
     sessions counted per combination; coin-flip cells from the exact-repeat set (RF-8's rule,
     `analysis/noise.py`);
   - **split:** 25% of the resolved sessions, by session, seeded, set aside first;
   - **sample:** 10 to 20 resolved sessions in full, covering each outcome and condition, a
     different seed per run;
   - **rules:** parse the YAML reply; check every field; `predict` evaluated mechanically;
     `protected_attribute` for a rule that reads ethnicity or perceived attractiveness; the
     fidelity scorer against the majority-class baseline; matching across runs (95%
     `[placeholder]` agreement on the main table) and keeping (2 of 3 runs);
   - **experiment:** config, preview (worst case), budget guard on the experiment's own calls,
     `--confirm`, records of every prompt and raw reply, a write-once store with provenance, a
     report.
3. Template `extract_v1` (a new kind, `rule_extraction`), frozen in the manifest.
4. Mock policy and tests (the list in task 8), plus a cross-check against RF-8's analysis tables.
5. Mock rehearsals: RF-3's mock rehearsal (acceptance criterion), and round 1's real data with the
   mock extractor.
6. Docs (`docs/rule-extraction.md`, READMEs), then the paid run: balance, pricing page, one
   extraction first, read it, then the other two.

## Progress log

### 2026-10-26 — Started
- What I did: branch from `feat/104-rf30-head-on-keep-line`; read the issue, track #55 and the
  "before starting" files; looked at the round 1 data and RF-8's analysis tables.
- Design choices (mine, to check):
  - **One row per agent**, not per session, because a rule such as "keep right" is about what
    each person does, and RF-8's "factor of the other as told" is per agent. The split is by
    session, so the two people of a held-out session are both held out.
  - **Design sessions only** (as the gate): exact repeats and counterfactual pairs would count
    their cells two or three times in the table.
  - **"Failed sessions counted per factor combination":** with 16 factors almost every failed
    session is its own combination, so the table counts them per condition, geometry, the two
    first plans' sides and the failure (collision, near miss, deadlock, time limit), and a second
    table gives, per factor level, the resolved and failed sessions.
  - **Rules are not in rule format** (the format no longer matters, RF-12 translates), so they
    are stored in an extraction store laid out like the writer's staging database (write-once
    files, SHA-256 manifest, ids from a hash) but not checked against the rule schemas.
- Next step: build the tables and the split.

### 2026-10-26 — The extractor, built and tested on the mock
- What I did: `negsim/extraction/` (`table.py`, `prompt.py`, `rules.py`, `experiment.py`,
  `mock.py`); template `extract_v1` (new kind `rule_extraction`), frozen; configs
  `configs/extraction/round1_head_on.yaml` and `rf3_mock_rehearsal.yaml`; layer dispatch in
  `run_experiment.py`; `docs/rule-extraction.md`; `log-schema.md` and `resolution.md` updated.
- **Round 1's tables:** 192 pooled design sessions, gate recomputed as RF-30's (102 of 192, CI
  0.46 to 0.60, passes); main 76 sessions (152 agent rows), held out 26 (52 rows), failed 90. The
  user message is about 86k to 91k characters (about 27k tokens), the system message 4.5k.
- **Found:** 23 of the 24 exact-repeat cells are coin flips (only 18 main-table rows are in a
  repeated cell). Consistent with RF-9's 77% flip rate on identical prompts.
- **Wording fixed before freezing** (the template had not been used): each agent calls the other
  "Person 1" in its own words (its view's label), so the sampled sessions' header says so; the
  trigger reasons' agent numbers (`perceives:0`) are dropped; the failed table's header says the
  sides are each person's own.
- **Acceptance criterion:** `rf3_mock_rehearsal.yaml` runs three times on RF-3's mock rehearsal
  (rebuilt from its records first: its `outcomes.csv` predated RF-8's columns). Head-on and
  single-file had no resolved session and are skipped and said so; overtaking (6 resolved, 4 main)
  gives 2 rules stored 3/3 with fidelity, 1 protected rule counted and not stored. On round 1's
  data the mock gives 3 stored rules (3/3, 2/3, 3/3) and is reproducible byte for byte.
- **Bugs found by the tests:** `any()` over `glob()` generators was always true (every resumed run
  was refused); fixed. YAML aliases (`&id001`) in rule files; written through JSON now.
- **Decisions of mine (to check):**
  - A resume refuses any change of config, client or source data once a run has a record,
    **except the budget**, which changes nothing that is sent (the resolution layer compares the
    budget too). So a cap raised with your approval can finish an aborted run.
  - A worst case above the cap does not stop a confirmed run (as `stop_at_cap`); the guard stops
    any call that could pass the cap.
  - `transport_retries: 0` for round 1, so that the guard's bound per call (USD 0.019) lets the
    three runs and a retry fit under USD 0.05. Worst case of the whole experiment: USD 0.107 (peak,
    no cache, full replies, every retry). Expected: about USD 0.006 a run off-peak.
  - `predict` may not read an outcome, the debrief kind or the cell's stability; it may read
    `signalled` and `spoke`, which makes the rule `needs_communication`.
  - "pretty" alone in prose ("pretty much") is not taken for attractiveness, unlike
    `protected_reference`, which would discard a valid rule for a figure of speech.
- Tests: `tests/test_extraction.py` (41) and `analysis/tests/test_extraction_tables.py` (3: the
  extractor's tables agree with RF-8's `agents_table` on every agent row of round 1, and its
  coin-flip cells with `analysis.noise.stability`).

## Open questions / risks
- The 95% matching threshold is a `[placeholder]` (the issue says so).
- The narrow gate pass (lower bound 0.46) is a caveat on everything extracted from head-on.

## Summary (fill in at the end)
