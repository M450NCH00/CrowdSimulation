# Work Log — Issue #4: [Docs] Compile literature review README (papers 1, 2, 3, 7)

**Issue:** https://github.com/M450NCH00/CrowdSimulation/issues/4
**Branch:** docs/4-literature-readme (based on `docs/2-lit-review-llm-human-behaviour`)
**Started:** 2026-09-07

## Understanding the issue

`literature/papers.md` (produced by issue #2) holds seven full review entries in a
dense, template-driven format aimed at *me* re-checking claims. This issue asks for a
different artefact from a **subset** of that material: a standalone, plain-language
`literature/README.md` covering papers **1, 2, 3 and 7**, readable by someone who never
opens `papers.md`.

Key constraints, read carefully:

- **Identify the four papers by their position/handle in `papers.md`**, explicitly not
  from memory or from the issue text. Verified before writing anything (see below).
- The relevance sections must be **pulled from the existing `Relevance` field**, not
  rewritten from scratch. So this is a compilation/reframing task, not a new analysis.
- **Every claim must trace to a verifiable source**; anything unverifiable gets
  `[unverified — needs confirmation]`.
- Needs a closing paragraph naming the **research gap** — what none of the four
  address, which this FYP does.

### Paper identification (done first, from the file itself)

`grep -nE "^### \[" literature/papers.md` gives this order, and the summary table at the
top of `papers.md` numbers them identically 1–7:

| # | Handle | Title |
|---|--------|-------|
| 1 | `[Aher-TE]` | Using Large Language Models to Simulate Multiple Humans and Replicate Human Subject Studies |
| 2 | `[Argyle-OOM]` | Out of One, Many: Using Language Models to Simulate Human Samples |
| 3 | `[Cheng-MP]` | Marked Personas: Using Natural Language Prompts to Measure Stereotypes in Language Models |
| 4 | `[Wang-NYR]` | LLM-based Human Simulations Have Not Yet Been Reliable |
| 5 | `[Hullman-VAL]` | This human study did not involve human subjects |
| 6 | `[Zhong-DDC]` | Data-driven Crowd Modeling Techniques: A Survey |
| 7 | `[Park-GA]` | Generative Agents: Interactive Simulacra of Human Behavior |

**Selected: 1 Aher-TE, 2 Argyle-OOM, 3 Cheng-MP, 7 Park-GA.** Body order and summary
table agree, so the numbering is unambiguous. Noting the incidental pattern for the PR
description: the selected four are exactly the peer-reviewed LLM-behaviour papers —
the excluded three are the two preprints (4, 5) and the crowd-simulation survey (6).

### Assumptions made

- **A-path**: the issue writes `/CrowdSimulation/literature/README.md`. As with issue
  #2, `CLAUDE.md` says this repo *is* CrowdSimulation and the prefix is obsolete, so the
  file goes at `literature/README.md`.
- **A-branch**: the issue names `docs/2-lit-review-llm-human-behaviour` under "Branch".
  That branch has an **open, unmerged PR (#3)**. Rather than silently extending an open
  PR's scope, I branched `docs/4-literature-readme` off it and will target the PR at it.
  GitHub auto-retargets to `main` if PR #3 merges first. Flagged rather than assumed
  silently — if the intent was to commit straight onto the lit branch, this is a
  one-command change.

## Plan

1. Verify preconditions; confirm paper numbering from `papers.md` itself. *(done)*
2. Create branch + work log. *(done)*
3. Re-read the four full entries in `papers.md`, especially each `Relevance` field.
4. Write `literature/README.md`: intro → four paper sections → closing gap paragraph.
5. Verify: every claim traceable; no number without a source; self-contained.
6. Push, open PR stating which handles were selected and why (acceptance criterion 1).

## Progress log

### 2026-09-07 — Branch created, papers identified from the file
- What I did: Confirmed clean tree and that the lit branch is in sync with origin.
  Identified papers 1/2/3/7 by grepping the headings in `papers.md` and cross-checking
  against its summary table, before reading any content.
- Why: The issue explicitly forbids guessing which papers these are.
- Result / what I found: Unambiguous — body order and table numbering match.
- Next step: Write the README from the existing entries.

## Open questions / risks

- (to be filled during the work)

## Summary (fill in at the end)

- (to be filled at the end)
