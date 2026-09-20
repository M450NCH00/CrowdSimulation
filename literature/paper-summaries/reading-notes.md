# Reading notes — observations that are NOT paper content

Prepared for issue [#14](https://github.com/M450NCH00/CrowdSimulation/issues/14).

Everything in the six summary files is sourced to a paper. **This file is where my own
observations live**, kept separate on purpose. Claims about what a paper says still carry
locators; claims about what that *means* for the FYP are mine and are marked.

---

## 1. Tensions between papers

Stated, not resolved.

### T1 — LLM agents agree far more reliably than the human studies suggest people do

- **GameChat:** with dialogue, "[t]he correct consensus was always reached", and the
  higher-priority agent went first in 100% of scenarios versus 50% without communication
  (§V-B.2, p. 6; Table III, p. 6). The authors attribute this to LLMs being "designed to
  be very honest and cooperative" (§V-B.2, p. 6).
- **Pütz & Hassan:** among human workplace conflicts, "submission is the most frequent,
  followed by stand-off and compromise" (Abstract) — i.e. **stand-off, where neither party
  concedes, is a common human outcome**.
- **Toluei & Tahririan:** name explicit conditions under which disagreements are **not**
  resolved (Abstract).

The tension: a 100% consensus rate may be *less* humanlike, not more. Both sides are
stated; deciding whether GameChat's rate is a validity problem requires the mapping
decision this issue excludes.

### T2 — Wu et al.'s alignment claim is broader than its evidence, within one paper

- **Conclusion:** the phenomenon "aligns well with real-world data" (§8, p. 5171).
- **But:** the human comparison exists only for the Keynesian Beauty Contest (NYT
  experiment, N = 61,140; §4.2, p. 5168), and for the evacuation case the authors
  themselves say better metrics are needed and leave them "for future study" (§7,
  p. 5171).

### T3 — Does interaction history matter?

- **Wu et al.:** attribute spontaneous cooperation "primarily … to the agents' in-context
  learning ability over long-term interactions" (§7, p. 5171).
- **Zhang et al.:** gave their distillation access to agents' decision history and found
  "the final generated function did not make use of the history" (§5.2, p. 14), repeated
  in the Conclusions (§7, p. 21).

These are not strictly contradictory — one is about agents behaving, the other about what
a distilled function needs — but they pull in opposite directions for a project that must
decide whether a reusable pattern needs memory.

### T4 — How many conflict-style categories exist

- **Rahim & Magner:** five styles, with CFA support for the five-factor model in four of
  five samples (p. 122, p. 130).
- **Same paper, p. 123:** reports Weider-Hatfield's conclusion that individuals "might
  select among three, not five, distinct conflict styles", and Hocker and Wilmot's
  three-type clustering.

### T5 — Zhang's ground truth is not the same model family as the work it builds on

- **Zhang et al.** take their simulation workflow and prompts from Wu et al. (§4.2, p. 9;
  §6.1, p. 19) but generate ground truth with **Gemma3:27b** (§5.1, p. 13).
- **Wu et al.** ran everything on **`gpt-4-0314`** (§4, p. 5166).

So "DFD reproduces LLM-driven crowd behaviour" means Gemma3's behaviour in Wu's setup, not
GPT-4's. Whether the two models behave alike in that setup is not addressed in either
paper.

---

## 2. Gaps for this FYP that these six papers do not cover

1. **Nobody codes LLM dialogue against human conflict categories.** The three Group 1
   papers report task metrics (deadlocks, escape counts, fidelity); the three Group 2
   papers describe human talk. No paper does both.
2. **No human data on the FYP's actual scenario.** None of the six studies a physical
   passing conflict. The human settings are workplace meetings, a classroom task, and
   questionnaires about organisational conflict.
3. **No usable reliability figure for any human scheme.** Rahim & Magner report
   self-report reliabilities, not inter-rater agreement (p. 123); for papers 05 and 06 the
   question is unanswerable from the abstracts.
4. **No base rate for how often LLM agents fail to resolve.** GameChat reports zero
   deadlocks with dialogue (Table III, p. 6), which is an outcome of its design rather
   than a distribution; nothing comparable to a human impasse rate exists in these six.
5. **Two of the six are inaccessible**, so half the human side of the argument rests on
   abstracts. That is a structural weakness in the current evidence base, not a
   presentational one.
6. **Nothing addresses extracting a rule from *dialogue*.** Zhang et al. distil from
   perception–decision pairs, and state that encoding "context information on agent
   interactions as features" is future work (§7, p. 21).

---

## 3. Novelty check (required for all three Group 1 papers)

The FYP proposes: (a) LLM agents resolve a conflict through dialogue, (b) a reusable
pattern is extracted from that dialogue, (c) the pattern is validated against human
behaviour.

### 01 Wu et al. — does it already do this?

- **(a) Partly.** LLM agents communicate during a spatial conflict (evacuation congestion)
  and the communication changes exit distribution (§6.2, p. 5171). But the conflict is
  many-agent congestion, not a two-party standoff.
- **(b) No.** Nothing is extracted for reuse.
- **(c) Partly, elsewhere in the paper.** Human comparison exists for KBC (§4.2, p. 5168),
  not for the evacuation case (§7, p. 5171).

### 02 Zhang et al. — does it already do this?

- **(a) Indirectly.** Its ground-truth simulation includes a communication phase (§4.2,
  p. 9), but the paper studies exit choice, not conflict resolution between two parties.
- **(b) YES — and this is the uncomfortable one.** DFD extracts an interpretable decision
  function from LLM-driven crowd behaviour and runs the simulation without the LLM
  afterwards (§4.4, p. 11; §5.5, pp. 18–19). **This is, in substance, roadmap steps 3–4 of
  this FYP, already published, on crowd evacuation, by an NTU group.**
- **(c) No.** Validity is explicitly inherited from the reference data (§6.1, p. 19).

**Stated plainly: the FYP cannot claim "extracting a reusable rule from LLM-driven crowd
behaviour" as novel.** What is left, and it is narrower: extracting from **inter-agent
conflict dialogue** (which Zhang et al. list as future work, §7, p. 21) and **validating
against human behaviour** (which they explicitly do not do, §6.1, p. 19).

### 03 GameChat — does it already do this?

- **(a) YES.** Two LLM agents resolve a symmetric doorway conflict through natural-language
  dialogue, with deadlock-free results (§IV-C, p. 4; Table III, p. 6). **This is the FYP's
  proposed starting scenario, already built and evaluated.**
- **(b) No.** A fresh dialogue runs per encounter (§IV-C, p. 4).
- **(c) No.** Validation is against baselines and a designer-defined priority ordering
  (§V, p. 5); real-robot validation is future work (§VI, p. 7).

### Consequence for the FYP's novelty claim — my judgement

Each half of the FYP is already published separately: **GameChat does the dialogue,
DFD does the extraction.** Neither does both, and neither validates against human
behaviour. So the defensible claim is the **conjunction**, stated narrowly:

> extract a reusable conflict-resolution rule *from LLM-to-LLM dialogue*, and check that
> rule against how people actually resolve comparable conflicts.

Anything broader — "novel use of LLMs for conflict resolution", "novel extraction of
rules from LLM crowds" — is contradicted by these three papers and should not appear in
the report. **This should go to the supervisor now rather than at write-up.**

---

## 4. My own methodological concerns

Separate from the authors' stated limitations, which are recorded in each summary file.

1. **Wu et al.'s evacuation result is thinner than its framing.** Table 2 (p. 5171) shows
   100.0 vs 99.8 escaped at round 50, and at round 15 the *no-communication* condition is
   ahead (51.2 vs 48.8). Five runs, no dispersion, no significance test. The defensible
   claim is the authors' narrower one about all five runs completing; the prose around it
   invites a stronger reading.
2. **GameChat's 100% is a post-tuning number.** The authors say prompt problems "became
   less and less frequent" after "carefully modifying the prompts" (§V-B.2, p. 6). A rate
   obtained after iterating on prompts against the same scenarios is at risk of being
   tuned to the evaluation.
3. **GameChat's priority ordering is supplied, and that limits what it shows.** The LLM
   infers urgency from task text, but correctness is scored against the designers'
   ordering (§IV-C, p. 4). It demonstrates that LLMs can apply a hierarchy, not that one
   emerges from negotiation.
4. **Version hazard on GameChat.** I read arXiv v2 (9 May 2026); the IEEE MRS version was
   published 4 December 2025 (Crossref). The preprint is *newer* than the published paper,
   so section and table numbers may not correspond. Earlier repo files cite it as MRS 2025
   without noting that the text consulted was the preprint.
5. **Zhang et al.'s fidelity target is a model, not a world.** Every metric measures
   distance from Gemma3's behaviour. A distilled function could be perfectly faithful and
   still unlike any human crowd — which the authors acknowledge (§6.1, p. 19), but it
   deserves emphasis because this project would inherit exactly the same structure.
6. **Applying Rahim's five styles to transcripts is a leap.** The instrument assigns
   scores from 28 self-report items (p. 123); it has no procedure for labelling an
   utterance. Borrowing the vocabulary is fine; calling the result "validated" is not.
7. **Half the human evidence is abstract-only.** Papers 05 and 06 could not be opened. The
   project should not build a coding scheme on category names whose definitions nobody on
   this project has read.
8. **A same-authors caution on the five styles.** The definitions in paper 04 come from
   the instrument's own author (Rahim), and the critique that the factor structure may be
   three rather than five is quoted *within* that same paper (p. 123). An independent
   assessment should be read before the taxonomy is adopted.
