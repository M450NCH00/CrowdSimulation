# The resolution gate

Threshold, fixed in the config before the run: 0.50 of the design's sessions resolved in `plan_only`. Reason: Step 1 asks whether LLM agents can resolve the conflict on their own plans, so the gate is the plan_only rate (ORCA does not steer the pair apart), pooled over the design's 192 sessions of 32 cells x 2 geometries x 3 conditions (exact repeats and counterfactual pairs left out, so each cell counts once per geometry and condition). 0.50 means the plans resolve the meeting more often than not; it is a judgement, not a sourced number. Head-on walkers in life almost never collide, so 0.50 is lenient against people, and strict against plain ORCA here, which passes within the near-miss distance and never counts as resolved (RF-9: 0 of 72). RF-9's pilot resolved 0.24 before resolve_v6's fixes, so failing the gate is a possible Step 1 result.

Pooled `plan_only`: 21 of 64 (0.33). The encounter type **fails** the gate.

| Group | Resolved | Rate |
| --- | --- | --- |
| all (plan_only) | 21 / 64 | 0.33 (95% CI 0.23 to 0.45) |
| condition independent | 21 / 64 | 0.33 (95% CI 0.23 to 0.45) |
| geometry layout=aligned | 13 / 32 | 0.41 (95% CI 0.26 to 0.58) |
| geometry layout=apart_20cm | 8 / 32 | 0.25 (95% CI 0.13 to 0.42) |
| baseline plan_orca | 20 / 64 | 0.31 (95% CI 0.21 to 0.43) |
| baseline plain_orca | 0 / 64 | 0.00 (95% CI 0.00 to 0.06) |
