# RF-14, tasks 1 and 2: the extractor's references and the agents' debrief sources (round 1)

Issue #69. Sources are keyed as in `sources.md`.

## Task 1: every extractor reference

RF-11 (`llm_negotiation/runs/rf11_round1_head_on/head_on/runs/run_{1,2,3}.json`) wrote 25 rules
with **27 references**: 23 in the 21 readable rules and 4 in the raw text of the 4 schema-error rules.
Each was stored `check_status: unchecked`.

| Result | References | What they are |
| --- | --- | --- |
| **No source given** | 24 | `citation: "no known source"`. Kinds: none 8, habit 7, common sense 7, local custom 2. Nothing to look up: each only restates what the debriefs said, or says no source was cited. |
| **Points to the participants** | 3 | A citation that names the debriefs themselves ("as reported by participants") with session locators. Checked against the debriefs at those locators, below. |
| **Names a law, guidance or published study** | **0** | |

So **none of the 27 references is a publication**, and none could be `verified`, `misattributed` or
`not found` in the issue's sense. The three that point to the participants were checked as claims
about the debriefs (locators are rows of RF-11's run 2 prompt; `S…` rows shown in full map in order
to `sampled_sessions`; a row not in the sample was shown to the extractor only as a table row, with
its debrief kind but not its words):

| Reference (run 2) | Locators | What the debriefs at the locators say | Result |
| --- | --- | --- | --- |
| "Singapore pedestrian keep-left convention as reported by participants"; claim: people say they keep left, yet ease to their own right | S042 p2, S186 p2 | S186 p2: "keeping to the left/right when passing and giving way" (not keep left). S042 was a table row only: the extractor did not see its words. | **Misattributed** at its locators. The claim itself holds across the full set: 66 of RF-11's 384 debriefs say keep left, and those agents passed left 33 times and right 33 times (`extraction_report.md`, section 5). |
| "Everyday courtesy to elders as reported by participants"; claim: giving an elderly person, or one with a cane or suitcase, extra room is ordinary courtesy on Singapore walkways | S030 p2, S041 p2, S175 p2 | All three say it ("an elderly person pulling a bulky suitcase … gets extra room"; "giving an elderly, distracted person carrying a suitcase extra room"; "leaving space for an elderly person with a cane and a suitcase is ordinary courtesy"). None names Singapore (S030: "here"). | **Verified as a report of the debriefs**, except "Singapore", which the extractor added. |
| "Everyday courtesy and keep-side custom reported by participants"; claim: keep to a side and let the more constrained person through | S030 p2, S144 p2 | S030: slowing and giving way to the elderly person; S144: "yield and keep to my right". | **Verified as a report of the debriefs.** |

Extractor references that check out: **0 of 27 as sources**; 2 of the 3 participant citations as
reports of what the participants said.

## Task 2: the agents' debrief sources

Every debrief of every paid run of the track (round 1 head-on, and RF-32 to RF-36's groups and
crowds): **2,681 debriefs** over 14 runs, none with a parse error.

| | All 14 runs | Round 1 head-on pairs (8 runs) |
| --- | --- | --- |
| Debriefs | 2,681 | 1,684 |
| With a `source` named | **0** | **0** |
| Kind `law_or_guidance` or `published_study` | **0** | **0** |
| Kind `common_sense` | 1,563 (0.58) | 1,025 (0.61) |
| Kind `habit` | 906 (0.34) | 493 (0.29) |
| Kind `local_custom` | 141 (0.05) | 139 (0.08) |
| Kind `none` | **71 (0.03)** | **27 (0.02)** |

(Per run: `runs/*/debriefs.jsonl`; the round 1 runs are `rf_pilot`, `rf_pilot_v2`, `rf10`, `rf27`,
`rf28` (both), `rf29`, `rf30`.)

So the share of distinct debrief sources that check out is **0 of 0**: no agent ever named one, and
the share of `none` is 3%. Against the extractor: both cite nothing. The agents say their decisions
came from common sense and habit, and a few from local custom. Since no source is named, the
**claims** in the `local_custom` debriefs are what can be checked. Grouped by what they assert
(keyword grouping of the 141; one debrief can make more than one):

| Claim | Debriefs (approx.) | Example | Check | Result |
| --- | --- | --- | --- | --- |
| a. In Singapore people keep left on walkways | 56 that say "left" (53 of them with "Singapore") | "in Singapore it's just ordinary courtesy to give way and keep left" | Singapore's Code of Conduct for Users of Public Paths advises pedestrians "to keep left when not overtaking" ([MOT2024]; pedestrian tips added August 2020, [LTA2020]). **No published study of what Singapore pedestrians actually do was found** (`sources.md`, "Looked for, not found"). | **Verified as guidance; behaviour unmeasured.** Under the user's decision (published studies only) this is *what is advised*, not evidence that people do it. Where guidance has been measured against behaviour, they diverged: in Korea, under a keep-left rule, 59.3% kept left while 73.7% preferred the right ([Jung2013], abstract). |
| b. Giving way to seniors is local courtesy | 62 that mention an elder, an older person, a cane or "aunty"/"uncle" | "in Singapore it's a common local habit to give way and leave room for seniors" | When a young and an older adult meet, "the young adult contributed more to the avoidance regardless of passing order" ([Rapos2021], abstract, Results; Canada). | **Partly verified**: the behaviour is measured, though not in Singapore, and as a share of the avoidance, not as courtesy. |
| c. Keeping right is a widespread informal convention | 3 that say "right" and not "left" | "Keeping to the right when passing someone coming the other way is a widespread informal convention" | Right preference measured in France ([Moussaid2009], section 4.2) and Beijing (68.75% of 960 samples, [CircleAntipode2019], Table 1); left in Japan ([Echeverria2026]). | **Verified where traffic keeps right; not universal.** |

What this means:
- **Neither the extractor nor the agents give a reference RF-14 can check.** The track's design asked
  both for references (D8); what they give is "common sense" and "habit". That is a finding about
  the model, reported as such: the agents behave as if following a convention without naming one.
- **What the agents say is not what they do** (RF-11, section 5, now with the evidence): the debriefs
  that say keep left follow official Singapore guidance, but those agents passed on either side
  equally, and the agents overall passed right to right in most resolved sessions.
