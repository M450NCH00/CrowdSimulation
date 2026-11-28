# rf15_round1_keep_line_analysis

RF-8's factor analysis (`python -m analysis`) of round 1's head-on sessions under `protocol.execution:
keep_line`, the execution every result from RF-29 on uses (issue #70, RF-15). No new code, no model call.

    uv run --no-project --python 3.13 --with-requirements analysis/requirements.txt python -m analysis \
      llm_negotiation/runs/rf10_round1_head_on_keep_line/outcomes.csv \
      llm_negotiation/runs/rf30_round1_head_on_keep_line/outcomes.csv \
      --intent-codebook intent_v2 --reasons-codebook reasons_v1 \
      --out llm_negotiation/runs/rf15_round1_keep_line_analysis

The settings are RF-10's (seed 63, Holm's correction over the whole report, the same codebooks). The inputs
are RF-29's re-execution of RF-10's independent sessions and RF-30's non-verbal and talk sessions, the same
288 sessions as RF-30's pooled gate. RF-10's own `analysis/` (under `as_prompted`, which undid sidesteps) is
unchanged.

**`mapping_compact.csv`**: the same command with `--mapping-factors
own_assertiveness,knows_other,finds_other_attractive,own_mobility_aid`, the four factors with an effect
that survives Holm's correction in `report.md`, section 1 (chosen by that rule before looking at the
mapping). Every other output of that run is identical to this folder's, so only its mapping is kept. The
full `mapping.csv` has 402 combinations, 330 of them seen once, too sparse to read as a lookup table.

The intent-against-plan check (section 7) covers non-verbal and talk only: the re-execution folder has no
`decisions.jsonl`. The independent sessions' intents and plans are RF-10's, word for word, so RF-10's figure
for them stands (`../rf10_round1_head_on/analysis/report.md`, section 7: 55 of 163, 0.337).
