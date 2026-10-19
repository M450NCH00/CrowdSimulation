# Describing environments to LLMs: findings (Q1 to Q5)

> For issue [#52](https://github.com/M450NCH00/CrowdSimulation/issues/52). Built from the five
> entries in [entries.md](entries.md) only; every quotation here is repeated from an entry, with the
> entry's locator. `[inference]` marks my reasoning. Q6, the recommendation, is in
> [verdict.md](verdict.md) and is **a proposal**.

Companion files: [entries](entries.md) · [verdict](verdict.md) · [token estimates](token-estimates.md) ·
[search log](search-log.md) · [missing papers](missing-papers.md) ·
[BibTeX](refs-environment-description.bib)

**Short answers**
- **Q1.** Five methods, all text except one image variant: template prose with a crowd summary
  ([Durupinar-AffectCrowd]); short event strings plus labelled positions ([Ntarouis-CrowdGenAgents]);
  a place tree flattened to prose, with no numbers ([Park-GenerativeAgents]); coordinate lists plus
  an ASCII map ([Chen-MAPFLLM]); and six encodings of one grid ([Martorell-TextToSpace]). Only
  negsim and Durupinar describe the scene egocentrically; the measured comparisons are all
  allocentric.
- **Q2.** Two measured comparisons of formats, neither about people in conflict: a text map beat a
  coordinate list and an image for multi-agent pathfinding at 4 and 8 agents, on very few runs
  ([Chen-MAPFLLM], Table 3); Cartesian encodings beat grid drawings and prose for grid navigation,
  most for mid-sized models ([Martorell-TextToSpace]). Rewording around a crowd description changed
  little ([Durupinar-AffectCrowd]).
- **Q3.** Selection by radius, or by range, field of view and occlusion, capped at the three nearest
  ([Durupinar-AffectCrowd]); nearest first is the only stated order. Prompt length grows with the
  number described ([Chen-MAPFLLM], faster than linear). One measured quality curve, for a central
  planner: success falls as agents are added ([Chen-MAPFLLM], Table 1).
- **Q4.** The three simulation papers about people limit the description to what can be perceived;
  the two benchmark papers give the full state. None of the five adds age, gender or disability to
  the people described. The repository's attribute evidence ([Yoldas-YieldBias], issue #16) is the
  reference here.
- **Q5.** No comparison of description formats for pedestrian or crowd conflicts was found, nor a
  measure of decision quality against the number of nearby people described to one agent. Seven gaps
  are listed in §5, each with the searches behind it.

---

## §1. Q1: Methods

### Table 1. Description methods

"Form" uses the issue's categories. "Evidence" is evidence about how well the **description**
works; most of the five measure the whole system instead.

| Method | Form | What is included (geometry · others · their attributes · self) | Numbers and directions | Evidence of how well it works | Cost reported | Entry |
|---|---|---|---|---|---|---|
| **negsim today** (for comparison) | First- or third-person prose, one fixed line per field | Passage width, wall distances, a narrowing ahead · **one** other person in full, the rest as "Other people are walking around you as well." · body width; age and gender when visible · own age, gender, task, speed, width | Egocentric: "ahead of you and {angle}° to your {side}"; distances to 0.1 m, widths to 0.01 m, speeds to 0.01 m/s, whole degrees (`describe.py` docstring) | None yet | ~220 tokens for the situation block (my count, [token-estimates.md](token-estimates.md)) | — |
| **M1. Crowd summary + nearest few in full** | Second-person prose from a fixed template, under capitalised headers | No geometry; the place as one free-text context · everyone visible as a summary and counts by cue; the **three nearest** in full · outward expression only (face, gesture, voice, movement, speed, spacing) · own personality, affect, memory, felt pressure | "the distance and direction" (§3.1, p. 5); units and rounding not reported | Wording variants measured; the description itself never varied | 1 call per agent per step; 200 output tokens max | [Durupinar-AffectCrowd] |
| **M2. Events + labelled entities** | Hybrid: short text events ("agent_0 is running") plus entities with positions | Objects labelled by the user · all entities in a radius, then filtered by novelty and importance · anonymous IDs and their actions · persona, emotional and physical state | "absolute positions and relative distances" (§2.4, p. 265); no bearing; units not reported | Human ratings of the whole system; none of the description | Requests ~linear in agent count (2,000 at 50 to 6,000+ at 250) | [Ntarouis-CrowdGenAgents] |
| **M3. Place tree as prose** | Third-person prose; containment tree flattened ("there is a stove in the kitchen") | Areas and objects by name, only those the agent has seen · others within a visual range, as action statements · names, relationships from memory · own summary description, plan | **None**: places are name paths ("The Lin family's house: garden: house garden.", §5.1, p. 13) | Architecture ablation only; one reported description failure (the "one-person bathroom") | "thousands of dollars" for 25 agents over two days | [Park-GenerativeAgents] |
| **M4. Coordinate list + ASCII map** (and an image variant) | Third-person text: each agent's cell and goal, a character map, and each agent's legal moves | The whole map · **all** agents, every step · none · (central planner: no self) | Allocentric integer cells, "The bottom-left cell is (0,0)" (Figure 2, p. 3); up/down/left/right | **Measured**: image vs obstacle list vs text map (Table 3) | Tokens per agent step grow faster than linear (Appendix B) | [Chen-MAPFLLM] |
| **M5. Six encodings of one grid** | Cartesian (JSON, chess notation), topographic (symbol grid, word grid), textual (row, column prose) | 5×5 grid, agent and goal · no other agents · — · agent position | Allocentric grid positions; UP/DOWN/LEFT/RIGHT | **Measured**: six formats × six model sizes, 100 trials each | Not reported | [Martorell-TextToSpace] |

### What the table shows

- **Prose dominates when the subject is people; coordinates and grids when it is space.** All three
  sources that simulate people use prose or short text events (M1, M2, M3). The two measured
  comparisons (M4, M5) are spatial tasks with coordinates and grids. `[inference]` negsim sits
  between the two: prose, but with explicit metric numbers.
- **Only two describe direction relative to the agent.** negsim ("ahead of you and 30° to your
  left") and M1 ("the distance and direction", form unreported). M2 gives "absolute positions"; M4
  and M5 use grid coordinates; M3 uses no directions at all.
- **Geometry is thin everywhere.** M1 passes the place as one free-text sentence; M3 passes room
  names; M2 passes labelled objects. Widths, wall distances and capacities, which decide a doorway
  conflict, appear in none of the three crowd or sandbox sources. `[inference]` negsim's Layer 4
  description is already richer in geometry than any source found.
- **Units and rounding are almost never reported.** Only M4 and M5, whose numbers are integer cells,
  show the numbers in full. M1 and M2 give no rendered example of a distance.

## §2. Q2: How well each method works

**At least one measured comparison of description formats was found** (two: M4 and M5). Neither
concerns people in conflict.

### Results, with their quotations

1. **Text map vs coordinate list vs image, multi-agent pathfinding** ([Chen-MAPFLLM], room map,
   GPT-4-turbo, 5 scenarios per setting, arXiv v2). Table 3 (p. 6), success %:

   | Agents | MM (image + text) | TOO (obstacle coordinates) | TOM (ASCII map) |
   |---|---|---|---|
   | 2 | 100 | 100 | 100 |
   | 4 | 20 | 60 | 80 |
   | 8 | 0 | 0 | 20 |

   "We found that with an image-based input, the results are even worse." and "The failure of TOO
   further indicates that LLMs do not know how to combine high-level intuitions of where obstacles
   are with concrete reasoning during path planning." (§3.3, p. 7). Caveats: one model, five
   scenarios a cell, a central planner rather than one agent's view.
2. **Cartesian vs grid drawing vs prose, single-agent grid navigation** ([Martorell-TextToSpace],
   LLaMA 3 1B to 90B, 100 trials per model and format). "Notably, Cartesian SIRs consistently
   outperformed Topographic and Textual SIRs across model sizes" (§4, p. 6). "the 8B model achieves a
   66% success rate with the JSON SIR but only 30% with its best non-cartesian SIR (Symbol Grid)."
   and "the largest models (70B and 90B) always exceed a 74% success rate" (§4, p. 6). Caveats: one
   agent, no obstacles, no people; the size of the gap at 70B to 90B is not given per format in the
   text.
3. **Rewording around a crowd description** ([Durupinar-AffectCrowd], appraisal probe, N = 40 per
   cell). "plain versus formal wording makes essentially no difference" and "Dropping the
   outward-only clause, the social-framing line, or the situational context barely moves any cue."
   (§4.3.3, p. 19). Removing the personality block "collapses every gap to |∆V |, |∆A| < 0.01"
   (§4.3.3, p. 19). Caveat: the perception description was held fixed; only the text around it
   changed.
4. **The backend matters as much as the format** ([Durupinar-AffectCrowd], Table 4, p. 20): parse
   errors 0% for three backends and 67% for llama3.2:3b; gpt-4o-mini "nearly erases the personality
   gap on the calm, alarm, and joyous scenes" (§4.3.4, p. 19). [Martorell-TextToSpace] shows the same
   in another form: the smallest models are "near chance level—around 10%—for all SIR types except
   for JSON" (§4, p. 6).
5. **Two description failures reported but not tested.** The missing capacity: agents entered a
   one-person bathroom because its name suggested more; the proposed fix, "describing the dorm
   bathroom as a "one-person bathroom," instead of a "dorm bathroom."" ([Park-GenerativeAgents],
   §7.2, p. 17). The missing motion: "The absence of trajectory information in the environmental
   representation prevented authentic herding pattern formation." ([Ntarouis-CrowdGenAgents], §4.1,
   p. 272). Neither fix was measured.

`[inference]` Taken together: structured, explicit positions helped in both measured spatial tasks,
but which structure helped differed (a text map in M4, coordinates in M5), and the gaps shrank or
vanished with stronger models and smaller problems. Nothing here measures a format for a decision
about **who goes first**, and nothing shows that a format that helps pathfinding helps a social
judgement.

## §3. Q3: Many agents

| Question | [Durupinar-AffectCrowd] | [Ntarouis-CrowdGenAgents] | [Park-GenerativeAgents] | [Chen-MAPFLLM] | [Martorell-TextToSpace] |
|---|---|---|---|---|---|
| **Who is included** | Within 8 m, inside a 200° cone, not occluded (§3.1, p. 4) | Everything within a configurable radius (§2.4, p. 265), then filtered by novelty and importance (p. 266) | Agents and objects "within a preset visual range" (§5, p. 12) | All agents (central planner) | No other agents |
| **Cap on the number** | **Three** described in full; the rest counted (§3.1, p. 5) | None reported | None reported; one observation per reaction prompt (§4.3.1, p. 11) | None | — |
| **Order** | Nearest first `[inference from "three nearest"]` | Not reported | Not reported | Agent number | — |
| **What is said about each** | Distance, direction, face, gesture, voice, movement, speed, spacing | ID and action | Name and action, plus memories about that person | Current cell, goal, legal moves | — |
| **Growth with numbers** | Bounded by the cap `[inference]`; "every agent consumes a call each step" (§4.1, p. 7) | Requests "rising almost linearly from approximately 2 000 requests for 50 agents to over 6 000 for 250 agents" (§3.3, p. 271) | Not reported | Tokens per agent step "growing faster than linear" (Appendix B, p. 12) | — |
| **Quality vs number described** | Not measured (the probe fixes 5 or 6 others, §4.3, p. 17) | Not measured (only latency and requests) | Not measured | **Measured** for a planner: room-map success 100 / 80 / 20% at 2 / 4 / 8 agents (Table 1, p. 4) | — |

`[inference]` Two designs exist: **radius only** (M2, M3), where what the agent is told grows with
density, and **perception rule plus cap** (M1), where it does not. Only the capped design keeps the
prompt length fixed, which matters if negsim ever describes a dense queue at a train door. No study
measured whether a cap of three loses information a decision needs.

## §4. Q4: Perceivable or omniscient; and attributes

- **Perceivable**: [Durupinar-AffectCrowd] (range, cone, occlusion; sound by loudness: "loud calls
  ... carry farther (20 m) than quiet ones such as chattering and gasping (10 m).", §3.1, p. 4),
  [Ntarouis-CrowdGenAgents] (radius), [Park-GenerativeAgents] (visual range, and a remembered map
  that can be out of date: "Agents are not omniscient", §5.1, p. 12). These three are the ones that
  simulate people.
- **Omniscient, by design**: [Chen-MAPFLLM] (a planner for everyone) and [Martorell-TextToSpace]
  (the whole 5×5 grid). `[inference]` Neither choice is tested against the other in any of the five;
  the split follows the task (simulating a person versus solving a puzzle).
- **negsim** is already perceivable-only for its one neighbour (`situation.py`: "Of the other agent
  it is shown only what a person standing there could plausibly perceive"). What it lacks is a rule
  for **which** others are perceived.
- **Visible attributes.** None of the five describes the age, gender or disability of the people an
  agent perceives. [Durupinar-AffectCrowd] limits others to outward expression; [Ntarouis-CrowdGenAgents]
  uses anonymous IDs; [Park-GenerativeAgents] uses names and remembered relationships. So this review
  adds **no new evidence** on what attributes do to decisions. The evidence is already in the
  repository and is not repeated here:
  - [Yoldas-YieldBias] in [`../llm-behavioural-conflict/llm-behavioural-conflict.md`](../llm-behavioural-conflict/llm-behavioural-conflict.md):
    an LLM's decision to yield to a pedestrian changes with the pedestrian's stated attributes,
    differently per model; its "All Else Being Equal" design is the audit to copy.
  - [`../demographic-personas/llm-demographic-effects.md`](../demographic-personas/llm-demographic-effects.md)
    (B1 and B2, issue #16) and [`../demographic-personas/realism-vs-bias-comparison.md`](../demographic-personas/realism-vs-bias-comparison.md)
    on persona effects and whether they match human evidence.
  - `[inference]` Describing several people at once multiplies the attribute question: with ten
    people, each with an apparent age and gender, a decision could shift because of who stands third.
    No source found tests that.

## §5. Q5: The research gap

"None found in this review" means none among the searches and papers in
[search-log.md](search-log.md); it is not a claim that none exists. Search IDs (S1, S2, ...) are
those in `search-log.md` §3.

| # | Gap | What was found instead | Searches behind it |
|---|---|---|---|
| G1 | **No comparison of description formats for pedestrian or crowd conflicts.** Not for doorways, crossings, queues or narrow passages | The two measured comparisons are pathfinding and grid navigation (M4, M5); the crowd papers vary wording, not the description (M1) or nothing (M2) | S1, S5, S10 (extended), S2; screening of 8 crowd and social-navigation papers (search log §4) |
| G2 | **No measure of decision quality against the number of nearby people described to one agent** | One curve for a central planner (M4, Table 1); latency and request counts for a crowd (M2) | S11, S1; Q3 table above |
| G3 | **The perception description itself has not been ablated in any LLM crowd simulation found** (fields removed, cap changed, field of view changed) | M1 drops personality, context and framing lines, keeping the perception text fixed (§4.3, p. 17) | S1, S10; entries M1, M2 |
| G4 | **Egocentric prose with metric numbers, negsim's form, is not compared with coordinates or JSON** | M5 compares allocentric forms only; frame-of-reference benchmarks exist as unread leads (Sidhu & Hockenmaier 2026; a TU Delft thesis), so this gap may be partly filled | S12, S6; search log §5 (unread leads) |
| G5 | **No test of stating a place's capacity or norm explicitly against leaving it to a name or a width** | One reported failure and an untested fix (M3, "one-person bathroom") | S1, S5; entry M3 |
| G6 | **No study of how visible attributes of several perceived people jointly affect a spatial decision** | Single-pedestrian attribute audits in the repository ([Yoldas-YieldBias]); none of the five describes attributes of others | No new search in this issue: relies on the issue #16 and #20 reviews (§4 above) |
| G7 | **Token cost per prompt is rarely reported** for LLM crowd simulations | Requests (M2), output caps (M1), a token chart for a planner (M4) | All entries; S11 |

`[inference]` G1 to G3 together are the gap negsim could fill: a controlled test of how one agent's
view of several people is written (format, cap, fields), on a two- or few-person conflict, measured
by the decision. That would be a design contribution, not a claim that such work cannot exist.
