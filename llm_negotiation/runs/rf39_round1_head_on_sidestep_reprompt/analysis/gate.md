# The resolution gate

Threshold, fixed in the config before the run: 0.50 of the design's sessions resolved in `plan_only`. Reason: Step 1 asks whether LLM agents can resolve the conflict on their own plans, so the gate is the plan_only rate (ORCA does not steer the pair apart), pooled over the design's 192 sessions of 32 cells x 2 geometries x 3 conditions (exact repeats and counterfactual pairs left out, so each cell counts once per geometry and condition). 0.50 means the plans resolve the meeting more often than not; it is a judgement, not a sourced number. Head-on walkers in life almost never collide, so 0.50 is lenient against people, and strict against plain ORCA here, which passes within the near-miss distance and never counts as resolved (RF-9: 0 of 72). RF-9's pilot resolved 0.24 before resolve_v6's fixes, so failing the gate is a possible Step 1 result.

Pooled `plan_only`: 92 of 192 (0.48). The encounter type **fails** the gate.

| Group | Resolved | Rate |
| --- | --- | --- |
| all (plan_only) | 92 / 192 | 0.48 (95% CI 0.41 to 0.55) |
| condition independent | 20 / 64 | 0.31 (95% CI 0.21 to 0.43) |
| condition non_verbal | 35 / 64 | 0.55 (95% CI 0.43 to 0.66) |
| condition talk | 37 / 64 | 0.58 (95% CI 0.46 to 0.69) |
| geometry layout=aligned | 49 / 96 | 0.51 (95% CI 0.41 to 0.61) |
| geometry layout=apart_20cm | 43 / 96 | 0.45 (95% CI 0.35 to 0.55) |
| baseline plan_orca | 101 / 192 | 0.53 (95% CI 0.46 to 0.60) |
| baseline plain_orca | 0 / 192 | 0.00 (95% CI 0.00 to 0.02) |
