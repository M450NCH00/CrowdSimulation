# Supervisor meeting — talking points (last two weeks)

Speaking notes drawn from five papers most relevant to the FYP. The first column gives each
paper's number, which is also the start of its summary file's name in this folder:

| # | Paper | Side |
|---|---|---|
| 03 | GameChat — Mahadevan, Zhang & Chandra (IEEE MRS 2025) | LLM conflict resolution |
| 04 | Rahim & Magner (1995), *Confirmatory Factor Analysis of the Styles of Handling Interpersonal Conflict* | Human conflict styles |
| 07 | Yeung & Ho (2020), *Focus on Opportunities or Limitations?* | Human, age/gender |
| 09 | Borah & Mihalcea (2024), *Implicit Bias in Multi-Agent LLM Interactions* | LLM, gender |
| 10 | Mouri Zadeh Khaki & Choi (2026), *Fairness in LLM Negotiator Agents* | LLM, gender |

Locators (§, table, page) point into those papers; full detail is in each summary file.
Anything marked *(my view)* is my own interpretation, not a paper's claim.

---

## Part 1 — What GameChat does, and where it stops

### 1.1 GameChat resolves a doorway conflict by LLM dialogue
- Two robots, each with its own gpt-4o-mini instance, talk in natural language to decide who
  has higher priority. Scenarios: a 0.4 m doorway and a 0.4 m × 0.4 m intersection, 18
  versions each (03, §V, p. 5).
- **Headline result:** a standard controller without communication deadlocked in **18 of 18**
  doorway runs. With dialogue: no deadlocks, and the higher-priority agent went first
  **100%** of the time, against 50% (chance) without communication (03, Table III).
- An exchange took about **2.8 s** on average (03, §V-B.2).
- The dialogue only decides leader/follower; a separate game-theoretic controller executes
  the motion. If the agents can't agree in time, a fallback rule ("Strategy 1") lets whoever
  reaches the doorway sooner go first (03, §IV-D).

### 1.2 Priority comes from exchanging tasks
- The prompt tells each agent it is "taking someone to TASK" and to keep talking until it
  knows whether its priority is higher or lower, based on both agents' tasks (03, §IV-C, p. 3).
- Tasks are private, so the protocol effectively requires both tasks to be exchanged before
  priority can be decided.
- Task types in priority order: hospital > airport > grocery (03, §IV-C, p. 4).
- *Careful:* the paper doesn't say agents "always" reveal their task first. The only example
  conversation is in Figure 3, which is an image.

### 1.3 Proposed improvement: yield early without revealing your own task
- If the first speaker's task clearly outranks mine, I can just yield. There's no need to
  state my own task.
- **Why it matters:** when the agents are still talking as they reach the doorway, the delay
  gives longer completion times and a longer wait for the higher-priority agent (03, §V-B.3).
  Shorter exchanges help.
- **Caveats:** the first speaker still has to reveal something, so this saves the second
  speaker's message, not the first. It also assumes the first agent's claim is honest.
- *(my view)* "If the other's task outranks mine, yield immediately" is itself a **rule that
  needs no LLM**, which is exactly the kind of reusable pattern this FYP aims to extract. It
  can be presented as a first example of pattern extraction, not only as an efficiency tweak.

### 1.4 Gap: no gender or age
- Confirmed by full-text search: GameChat contains no demographic terms at all. The only
  identity an agent has is its task (03, §IV-C).
- The prompt already has an **empty slot**: the agent is "taking *someone*", and that passenger
  is never described. Age or gender could be added without redesigning the protocol.

### 1.5 Honesty: lying set aside, over-cooperation is the real concern
- I'm not modelling deception: it's a minority behaviour in real life, and handling it would
  mean agents questioning each other's claims.
- GameChat's authors list it as their own limitation: honest LLMs cooperate well but a
  dishonest agent could falsely claim priority, and deception is left to future work
  (03, §VI, p. 7).
- **The bigger realism problem is over-cooperation.** The authors say the correct agreement
  "was always reached" because LLMs are designed to be "very honest and cooperative"
  (03, §V-B.2). They also note the 100% came only after prompt fixes for task forgetting and
  hallucinated instructions (same section).
- *(my view)* Real people don't converge that reliably. A system with guaranteed agreement
  can't reproduce realistic hesitation or standoffs.

### 1.6 Gap: equal-priority cases are never tested
- The two-agent runs deliberately used "every combination of priorities such that neither was
  the same" (03, §V-A, p. 5). The scoring needs a correct ordering, so a tie can't be scored.
- The 3–5 agent runs do include two agents of the same type (Fig. 8), ranked by a pairwise
  vote over LLM rankings, but the paper doesn't say how same-type agents were ordered or what
  counted as correct between them (03, §IV-E; Table IV).
- *(my view)* In a real crowd, equal priority is the **normal** case (everyone is commuting).
  With no task difference to go on, the LLM has to rely on something else, and in this FYP's
  setup that means the persona. **An equal-priority doorway run where only the personas change
  is the cleanest test of demographic bias available, and GameChat never ran it.**

---

## Part 2 — Why personas matter

### 2.1 Personas change how agents communicate and what they concede
- A persona of **just a name and a gender** changed the LLMs' justifications: agents gave
  reasons that followed traditional gender norms even though the personas contained no skills
  (09, §7).
- Telling an agent the **other side's** gender changed its opening move: sellers opened at $50
  in 62.5% of games against female buyers versus 58.75% against male buyers (10, §4.1).
- The reasons for accepting a deal differed by the other side's gender: relationship-based
  with female sellers, opportunity-based with male sellers (10, §4.2).
- From the wider search (not one of these five papers): without any persona, an LLM behaves
  like a default middle-aged man.
- **Suggested framing:** personas measurably change how agents communicate and what they
  concede, so any pattern extracted *without* them reflects an unstated default persona
  rather than a neutral one.

### 2.2 Dialogue amplifies bias
- In 09, bias rose from the first response to the last in **all six** conditions that involved
  discussion (09, Table 1; §5.1.1).
- In the setting where every agent privately claims the same task (the closest to a priority
  conflict), gpt-3.5's score went from **0.27 to 0.57** (09, Table 1).
- *(my view)* Phase 1 (`run01`) was single-shot, so a GameChat-style exchange may produce
  **larger** demographic effects than `run01` shows.

### 2.3 Log the first message, not just the outcome
- In 10, the gender effect came through the **opening offer**, while the stated reasoning
  stayed the same (10, §4.1).
- *(my view)* In a doorway exchange, bias may sit in who claims priority first. That would be
  invisible if only the final yielder is recorded.

### 2.4 Effects can depend on role
- In 10, the gender effect was sizeable when the seller knew the buyer's gender ($5.47 vs
  $4.97) but **negligible** in the reverse direction ($12.56 vs $12.57) (10, §4.1–4.2).
- Being *given* a gender and *knowing the other's* gender are different manipulations and
  may not behave alike.

---

## Part 3 — The human side

### 3.1 The five conflict-handling styles (04)
Rahim's five styles sit on two dimensions, **concern for self** and **concern for others**
(04, p. 123):

| Style | Concern for self | Concern for other | Doorway analogue *(my mapping)* |
|---|---|---|---|
| Dominating | high | low | go first regardless |
| Obliging | low | high | yield / step aside |
| Integrating | high | high | exchange information to find the best outcome for both (what GameChat does) |
| Compromising | moderate | moderate | alternate / partial give |
| Avoiding | low | low | halt, wait, withdraw |

**Caveats to raise myself:**
- It's a **self-report questionnaire** (5 samples, 2,076 workplace respondents). It has **no
  rules for labelling a transcript**, so using it to code LLM dialogue goes beyond how it was
  validated (04, §6 of summary; p. 123).
- Even the number of styles is disputed: some researchers argue for three, not five
  (04, p. 123).
- The five-style structure didn't hold fully across all five samples (04, p. 130).
- *(my view)* GameChat's outcome is binary (leader/follower), so it only captures dominating
  versus obliging. The five-style scheme could describe *how* the agents got there.

### 3.2 How age and gender affect conflict handling in real people (07)
- **Gender:** in 416 Hong Kong Chinese workers, gender predicted **none** of the five styles
  (07, Study 1, Table 1).
- **Age is messier:**
  - Younger workers used obliging and avoiding **more**, the opposite of what the abstract
    suggests (07, Study 1; General Discussion).
  - An indirect path through perceived career limits points the other way (07, Study 1–2
    mediation results).
  - The second study (268 managers and professionals) found no raw correlation between age
    and any style (07, Study 2, Table 2).
- **Limits:** self-report, workplace relationships, adults only. The closest cultural match to
  Singapore among these papers, but not a brief encounter between strangers.

### 3.3 Link to Phase 1
- `run01` flagged **female personas yielding more** than male personas (gaps of 0.27 to 0.43
  in `yield_likelihood`, `dataset/generated/validation_report.md`).
- Paper 10 shows the same direction, but in an LLM (10, §4.1). The only human study here
  found no gender effect (07, Study 1).
- **Among these papers, the pattern has LLM support but no human support.**

---

## Part 4 — Bigger-picture points

### 4.1 "Bias" in these papers means unfairness, not unrealism
- Papers 09 and 10 measure bias as departure from **equal treatment**; neither compares against
  real human behaviour (09, §4; 10, §4.1–4.3).
- This FYP needs **realism**. If real groups do differ, "debiasing" would make the simulation
  *less* realistic.
- This explains why much of the LLM-bias literature can't settle the FYP's question on its own.

### 4.2 The key data gap
- Both human papers (04, 07) are workplace questionnaires about ongoing relationships, not
  strangers meeting for a few seconds.
- The one direct measurement from the wider search (Rapos et al. 2021, *Gait & Posture*;
  abstract only) found **young walkers do more of the avoiding when meeting an older walker**.
  That is the opposite of `run01`'s "elderly yield at least as much as young adults".

---

## Part 5 — Questions for my supervisor

1. Should the next experiment be the **equal-priority doorway with only the personas varied**?
2. Should Phase 1 be re-run on a **second model**? One paper from the wider search found the
   gender effect flipping direction between models.
3. Is the target **realism** (match real people, even where groups differ) or **fairness**?
   This decides whether any debiasing belongs in the pipeline.
4. Is labelling LLM transcripts with Rahim's five styles acceptable, given the instrument was
   never validated for coding conversations?
