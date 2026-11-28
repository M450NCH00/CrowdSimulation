# The resolution gate

Threshold, fixed in the config before the run: 0.50 of the design's sessions resolved in `plan_only`. Reason: Step 1 asks whether LLM agents can resolve the conflict on their own plans, so the gate is the plan_only rate (ORCA does not steer the pair apart), pooled over the design's 192 sessions of 32 cells x 2 geometries x 3 conditions (exact repeats and counterfactual pairs left out, so each cell counts once per geometry and condition). 0.50 means the plans resolve the meeting more often than not; it is a judgement, not a sourced number. Head-on walkers in life almost never collide, so 0.50 is lenient against people, and strict against plain ORCA here, which passes within the near-miss distance and never counts as resolved (RF-9: 0 of 72). RF-9's pilot resolved 0.24 before resolve_v6's fixes, so failing the gate is a possible Step 1 result.

Pooled `plan_only`: 40 of 128 (0.31). The encounter type **fails** the gate.

| Group | Resolved | Rate |
| --- | --- | --- |
| all (plan_only) | 40 / 128 | 0.31 (95% CI 0.24 to 0.40) |
| condition silent | 22 / 64 | 0.34 (95% CI 0.24 to 0.47) |
| condition talk | 18 / 64 | 0.28 (95% CI 0.19 to 0.40) |
| geometry layout=aligned | 20 / 64 | 0.31 (95% CI 0.21 to 0.43) |
| geometry layout=apart_20cm | 20 / 64 | 0.31 (95% CI 0.21 to 0.43) |
| baseline plan_orca | 53 / 128 | 0.41 (95% CI 0.33 to 0.50) |
| baseline plain_orca | 0 / 128 | 0.00 (95% CI 0.00 to 0.03) |
