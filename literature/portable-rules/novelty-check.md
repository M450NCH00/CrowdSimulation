# Novelty check (Q5)

> For issue [#35](https://github.com/M450NCH00/CrowdSimulation/issues/35), PT-1. Done on
> 2026-10-18. The issue asks for three things: read arXiv:2409.00993 in full (risk R4 of
> `WORK_LOG-20.md`); search for work where norms or rules derived by LLMs are written down so that
> other systems can reuse them; and state what is new in the portable-rule idea and what is not.
> The format follows issue #16's novelty check (`../demographic-personas/search-log.md` §0).

Companion files: [representations](representations.md) · [feasibility](feasibility.md) ·
[verdict](verdict.md) · [search log](search-log.md) · [refs](refs-portable-rules.bib)

---

## 0. The answer in short

1. **arXiv:2409.00993 overlaps the FYP's method, not its contribution.**
   - What overlaps: LLM agents form norms through dialogue.
   - What does not: nothing is written down as a rule, nothing is run by any other system, the
     setting is one abstract game, and transfer is listed as future work. R4 can be closed on
     that basis (§2).
2. **LLM-derived norms have been written down before, but never for a different system to run.**
   - [Ren-CRSEC] stores them as quintuples whose core is natural language, read only by LLM agents
     in one environment.
   - [Manas-TR2MTL] has an LLM translate *human-written* traffic law into temporal logic, checked
     by a monitor in one simulator.
   - Zhang et al. (2026), already in this repository, distil an LLM-driven crowd into code that
     plain agents run, in one simulator (§3).
3. **Not found in this review:** conflict rules derived by LLM agents, written in a
   simulator-independent vocabulary, carried out by non-LLM agents in more than one simulator,
   and checked against human evidence. That combination is the new part (§4). Every ingredient
   exists on its own somewhere.
4. **This is "none found in this review", not "none exists".** The search covered English-language
   sources over one session, by the routes in [search-log.md](search-log.md).

---

## 1. Full entry for arXiv:2409.00993

### [Horiguchi-NormsLLM]: Evolution of Social Norms in LLM Agents using Natural Language

- Authors / Year / Venue: Ilya Horiguchi, Takahide Yoshida, Takashi Ikegami (Graduate School of
  Arts and Sciences, University of Tokyo) / 2024 / arXiv:2409.00993v1 [cs.MA], 2 September 2024;
  "5 pages, 8 figures" (arXiv comment).
- Link: https://arxiv.org/abs/2409.00993
- Status: `[preprint]`. No published version found: the arXiv record has no journal reference or
  DOI, a Crossref search by title returns nothing, and a web search finds only the arXiv listing
  and reposts (2026-10-18).
- Read: **full text**, every section and footnote and Table 1, from a reading-order re-extraction
  of `refs/gt_arxiv_2409_00993.pdf`. The cached `refs/gt_arxiv_2409_00993.txt` is the same paper
  in two-column layout. ⚠ Figures 1–8 are images; only their captions were read.
- What it represents: **norms as emergent behaviour** of LLM agents playing a game. It does not
  represent norms as written rules.
- Structure:
  - No structure is defined for a norm.
  - The setting is Axelrod's Norms Game, played through command tags (Experiments). In the test
    phase an agent chooses *test* or *cheat*; cheating gains "+30 points" on average and "is
    revealed when scores are announced to all agents". In the discussion phase agents speak in
    turn, and each chooses *next* or *punish*: "The agent using the command pays 20 points to
    punish the target agent by -90 points" (Experiments, "Norms Game"; Table 1).
  - Traits are given in words, "Vengefulness: 5 out of 7 - Boldness: 6 out of 7" (Results, first
    subsection).
  - There are 7 agents (Experiments, "Evolution"). The model is gpt-4-0125-preview at temperature
    0.0 (footnote 1).
- Executable or descriptive: an LLM decides each agent's commands every turn. **The "norm" is the
  authors' reading of what the agents did.** For example: "agents who punished cheating were
  themselves punished. This was because punishing when everyone cheated was judged by other
  agents as behavior that disrupted order. This principle of action is a type of meta-norm as
  described by Axelrod, and it can be considered to have naturally emerged" (Results, "Results of
  Controlling Vengefulness and Boldness"). Nothing is extracted, stored or reused.
- How it travels between systems: not addressed.
- Evidence that it works in two or more systems: none; one game.
- Failure modes and limits stated by the authors:
  - "The vertically elongated violin plot indicates large variations even within the same group"
    (Results, first subsection);
  - "The evolutionary outcomes depend on the initial personality pool" (Results, "Natural
    Language");
  - natural language "also presented difficulties in analysis and interpretation" (Conclusion);
  - transfer is future work: "how the same personality traits ... manifest in different game
    scenarios, providing insights into the transferability of evolved strategies" (Conclusion).
- **Full-text check.** A case-insensitive search of the whole paper finds no hit for "rule",
  "represent", "database", "spatial", "crowd", "navigation" or "pedestrian". "transfer" has one
  hit, the future-work sentence above.
- For the portable rule core: **reject as a representation; it is prior art for the method only**
  [inference].
  - It builds on Axelrod's 1986 game, whose metanorm result [Galan-Reimplementing] showed reverses
    with longer runs, other mutation rates, other payoffs and other selection rules
    ([`representations.md`](representations.md), group 6).
  - Its runs are short: at most 21 turns per discussion with 10 repetitions, and 40 epochs in the
    evolution experiments (Results). So its metanorm observation is a short-run observation. This
    review makes no claim that it is wrong.
- BibTeX: `horiguchi2024normsllm`

---

## 2. What risk R4 asked, answered

R4 (`WORK_LOG-20.md`): the paper "is **LLM agents deriving norms through dialogue**, i.e. the FYP's
own method ... **Until it is read in full, the FYP's novelty claim is unverified.**"

It has now been read in full. Each row is checked against its full text (§1) and against this
repository's own documents:

| | This FYP (issues #24–#32; #34) | arXiv:2409.00993 |
|---|---|---|
| What the dialogue yields | A written rule, stated or negotiated, in a schema (`llm_negotiation/docs/rule-format.md` §§1–2) | Behaviour; the norm is the authors' interpretation (Results) |
| Who acts on it | Non-LLM agents in a simulator, through a rule database (`rule-format.md`, opening) | The same LLM agents |
| Conflict | Space: encounters between pedestrians (`rule-format.md` §3) | An abstract n-person game |
| Personas | Age and gender (issue #16's check) | Vengefulness and boldness, or ~10-word personalities (Results) |
| Reuse elsewhere | Proposed: the portable core (#34) | None; transfer is future work (Conclusion) |

**R4 can be closed, with this wording** [inference]: *the FYP's method (LLM agents reaching norms
through dialogue) has prior art in [Horiguchi-NormsLLM] and [Ren-CRSEC]. Its contribution does not
lie there. It lies in turning an elicited conflict rule into an explicit artefact that non-LLM
agents carry out, and, if #34's idea is adopted, carrying it across simulators.* The report should
cite both papers as prior art for the method.

---

## 3. Other prior work: LLM-derived norms or rules written down

### [Ren-CRSEC]: Emergence of Social Norms in Generative Agent Societies: Principles and Architecture

- Authors / Year / Venue: Siyue Ren, Zhiyao Cui, Ruiqi Song, Zhen Wang, Shuyue Hu / 2024 /
  *Proceedings of IJCAI-24* (Special Track on Human-Centred AI), pp. 7895–7903.
- Link: https://doi.org/10.24963/ijcai.2024/874 | https://arxiv.org/abs/2403.08251
- Status: published at IJCAI 2024 (Crossref record; the proceedings PDF was read).
- Read: these sections: 2.1–2.4, 3.1 and 4, from `refs/pr_ren2024_crsec_ijcai.txt`. Not read:
  most of §1, §3.2–§3.3 (results and human evaluation in detail), the appendices.
- What it represents: norms created, spread and complied with by LLM agents.
- Structure: "we represent a personal norm with a quintuple n = ⟨c, u, α ∈ {'des', 'inj'}, sact ∈
  {T, F}, sval ∈ {T, F}⟩", where "c represents the personal norm in natural language, e.g, 'no
  smoking indoors'". u is a utility from 1 to 100, α marks the norm descriptive or injunctive, and
  the last two flags say whether it is activated and valid (§2.1). Norms are created by an LLM
  from an agent's description, "P ← CreateNorm(G)", and kept in each agent's "personal norm
  database" (§2.1).
- Executable or descriptive: interpreted throughout by LLMs. Detecting conflicts, deciding whether
  to talk, identifying normative information, the sanity checks, synthesis and compliance are all
  "LLM-based operation[s]" (§2.2–§2.4).
- How it travels between systems: within one society, by communication and observation (§2.2).
  Not between systems.
- Evidence that it works in two or more systems: none. The experiments ran in Smallville only,
  with 10 agents (3 norm entrepreneurs), GPT-3.5 and GPT-4, 5 runs of 2 simulated days. "Each run
  costs more than $500 dollars and about 7 days to complete" (§3.1).
- Failure modes and limits stated by the authors: "LLMs may incorrectly classify types of norms,
  or generate normative information that does not align with preceding conversations or
  thoughts", hence a four-step sanity check (§2.3).
- For the portable rule core: **reject the natural-language core; note two fields** [inference].
  A norm whose content only an LLM can read cannot be followed by a plain simulator agent. Its
  importance score and activation/validity flags already have counterparts in today's format
  (`priority`, `status`; `rule-format.md` §2).
- BibTeX: `ren2024crsec`

---

### [Manas-TR2MTL]: TR2MTL: LLM based framework for Metric Temporal Logic Formalization of Traffic Rules

- Authors / Year / Venue: Kumar Manas, Stefan Zwicklbauer, Adrian Paschke / 2024 / *2024 IEEE
  Intelligent Vehicles Symposium (IV)*, Jeju, pp. 1206–1213.
- Link: https://doi.org/10.1109/IV55156.2024.10588650 | https://arxiv.org/abs/2406.05709
- Status: published at IEEE IV 2024 (Crossref record). Read as arXiv v1, which carries the
  notice "Accepted for publication in Proceedings of the IEEE Intelligent Vehicles Symposium".
- Read: these sections: Abstract, I, IV, V and VI, from `refs/pr_arxiv_2406_05709_tr2mtl.txt`. Not
  read: II–III (related work; the method in detail).
- What it represents: **human-written traffic rules**, from the German StVO and the Vienna
  Convention, translated by an LLM into metric temporal logic (Abstract; §I).
- Structure: MTL formulas over predicates and arguments taken from CommonRoad and Lanelet (§IV-A),
  e.g. `yield(ego, other)` and `right_of(other, ego)` (§V). The dataset is 50 rules paired with
  their MTL formulas (§IV-A).
- Executable or descriptive: executable as checks, not as behaviour. The authors "generated
  rule-compliant and non-compliant trajectories using CommonRoad" and verified them "using a
  runtime Python monitor and an MTL parser" (§V-C).
- How it travels between systems: a formal logic plus a predicate vocabulary, and **a hand-written
  mapping**: "The only modification required ... is to write some additional functions to map the
  high-level predicates to the CommonRoad format ... Future work can focus on automating this
  mapping process" (§V-C). "TR2MTL can be adapted to other dataset structures by providing a list
  of available predicates and arguments" (§IV-A).
- Evidence that it works in two or more systems: none. CommonRoad is the only simulator. The marine
  rules and drone dataset are other *rule sets*, not other simulators: 6 marine rules at 50%; 810
  drone instructions at 57.91% against 69.36% for a fine-tuned model (§V-A, Table III).
- Failure modes and limits stated by the authors:
  - 72.91% accuracy with GPT-4 and chain-of-thought on the 50 rules (Table II);
  - "most errors belong to incorrect logical connectives (including incorrect implication
    operator) followed by incorrect predicate" (§V);
  - ambiguous phrases such as "under control" were replaced by hand with concrete terms first
    (§IV-A);
  - "TR2MTL struggles with MTL formulas that have different logical structures from the prompts"
    (§V-B);
  - "Currently, our framework is more of a human-in-loop system" (§VI).
- For the portable rule core: **adapt** [inference].
  - This is the closest published precedent for the core's *shape*: a formal rule over a fixed
    vocabulary of predicates, run in a simulator through a hand-written predicate mapping, which
    is a perception adapter.
  - Its error profile is a warning for whoever has an LLM write cores (SI-4, PT-8): the LLM got
    the logical connectives wrong more than anything else.
- BibTeX: `manas2024tr2mtl`

---

### [Savarimuthu-NormativeLLM]: Harnessing the power of LLMs for normative reasoning in MASs

- Authors / Year / Venue: Bastin Tony Roy Savarimuthu, Surangika Ranathunga, Stephen Cranefield /
  2024 / arXiv:2403.16524v2 [cs.AI]. "Presented at the COINE 2024 workshop at AAMAS 2024 ... will
  appear in the post-proceedings" (arXiv comment).
- Link: https://arxiv.org/abs/2403.16524
- Status: `[preprint]`. Whether the post-proceedings version has appeared was not checked
  `[unverified]`.
- Read: these sections: 1, 4 and 6, from `refs/pr_arxiv_2403_16524v2_savarimuthu.txt`.
- What it represents: a vision of norm-capable LLM agents. It defines no representation.
- Structure: three capabilities, "norm discovery, reasoning and conformance" (§1, §4).
- Executable or descriptive: it argues *against* symbolic norms for open systems. Traditional
  normative agents use "symbolic logical representations" with norms known a priori, which "is
  unrealistic for agents participating in open systems where norms change. Also, the complexity
  and nuances associated with norms can make it difficult to model them using formal approaches"
  (§4).
- How it travels between systems: not addressed. Its first challenge, though, names both of #34's
  adapters for LLM agents: "LLMs produce natural language responses that need to be converted back
  to actions ... responses need some mapping function that link natural language text to actions
  ... A similar effort is needed to map an agent's perception and beliefs into natural language
  prompts" (§6).
- Evidence that it works in two or more systems: none (a vision paper).
- Failure modes and limits stated by the authors: hallucination and reasoning limits (§6,
  challenge 2); cost of training and prompting (§6, challenge 3).
- For the portable rule core: **reject the direction; keep the argument as the counter-position**
  [inference]. This is the strongest statement found for keeping norms *inside* LLMs. A report
  defending the portable core should answer its §4 objection: some norms are too nuanced for a
  fixed vocabulary. #34's L4 "abstain" level is a partial answer.
- BibTeX: `savarimuthu2024normativellm`

---

### Cross-reference only: [Zhang-DFD], already summarised in this repository

Zhang, Andelfinger, Tan and Cai (2026), *ACM TOMACS*, NTU. Summarised in
[`../paper-summaries/02-sense-think-act-reflect.md`](../paper-summaries/02-sense-think-act-reflect.md)
and not summarised again here, as the issue asks.

As that summary records, an LLM-driven crowd is distilled into "a **decision function in commented
Python-like code** that maps perception features to a score for each of the seven exit cells", and
"each agent invokes the decision function with probability p" (its "Form" bullet, citing §4.4 of
the paper). [inference] This is the closest prior work to "LLM-derived behaviour written down so
that a non-LLM system can run it". Its features belong to its own simulator (exit cells, positions,
crowdedness), so running it elsewhere is not addressed.

### Checked and excluded: GameChat

GameChat (Mahadevan et al. 2025), whose method `llm_negotiation/` reimplements (issue #24), is in
this repository as `refs/mahadevan2025_gamechat.txt`. A search of its full text finds no hit for
"extract", "reus", "database" or "memory"; "store" occurs only in "grocery store". It settles
priority per encounter and writes down no standing rule [inference from those searches]. So it is
not prior work for writing rules down.

---

## 4. What is new, and what is not

| Element of #34's idea | Found in prior work? | Where |
|---|---|---|
| LLM agents reach norms through dialogue | **Yes** | [Horiguchi-NormsLLM]; [Ren-CRSEC] |
| LLM-derived norms written down as structured records | **Yes, for LLM readers** | [Ren-CRSEC] (quintuple, natural-language core) |
| An LLM writes rules in a formal, machine-checkable language | **Yes, translating human law** | [Manas-TR2MTL] |
| LLM-derived behaviour distilled into code that non-LLM agents run | **Yes, in one simulator** | [Zhang-DFD] (in repository) |
| A rule or norm format independent of the system that follows it | **As coding schemes and logics, not executed across systems** | [Frantz-IG2]; [Frantz-IG2Codebook]; [Mellema-Sanctions]; [Hollander-NormativeABS] |
| One executable behaviour engine reused by several simulators through wrappers | **Yes, without a behavioural comparison** | [EscuderoJimenez-HuNavSim2]; for models, [Blochwitz-FMI] |
| Behaviour layer kept apart from the motion model | **Yes** | [Curtis-Menge]; [Kleinmeier-Cooperation] |
| Testing whether one rule behaves the same in two implementations | **Yes, in social simulation** | [Axtell-Docking]; [Edmonds-Replication]; [Wilensky-MakingModelsMatch]; [Galan-Reimplementing] |
| **Conflict rules derived by LLM agents, written in a simulator-independent vocabulary, carried out by non-LLM agents in more than one simulator, and tested on held-out conflict types against human evidence** | **Not found** | — |

**Plain statement** [inference]:

> What is new is the combination: taking a conflict rule that LLM agents have elicited, and making
> it a simulator-independent artefact whose behaviour is then checked in more than one simulator,
> on conflict types it was not extracted from. No ingredient on its own is new. The FYP should claim
> the combination and the cross-simulator test, and cite prior work for each ingredient.

**Three caveats the report should carry with that claim:**

1. **The vocabulary is the least novel part.** Institutional grammar and normative MAS have
   represented norms for decades ([Frantz-IG2]; [Hollander-NormativeABS] ¶2.19–¶2.23). The core
   should adapt them and say so, not present a new grammar.
2. **The cross-simulator test is the most novel part, and it has a known failure record.** Every
   docking study read here found differences (group 6 of [`representations.md`](representations.md)).
   A novel claim to "the same behaviour in several simulators" will be judged against that record.
3. **"None found" is bounded by this search.** It covered English-language sources in one session
   ([search-log.md](search-log.md) §2 lists the queries). Two leads were not read: a 2025 survey
   contrasting explicit deontic norms with LLM agents' natural-language norms (arXiv:2509.02515)
   and NormSage (Fung et al. 2023; cited in [Savarimuthu-NormativeLLM]).
