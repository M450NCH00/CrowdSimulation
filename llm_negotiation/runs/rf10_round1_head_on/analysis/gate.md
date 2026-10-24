# The resolution gate

Threshold, fixed in the config before the run: 0.50 of the design's sessions resolved in `plan_only`. Reason: Step 1 asks whether LLM agents can resolve the conflict on their own plans, so the gate is the plan_only rate (ORCA does not steer the pair apart), pooled over the design's 192 sessions of 32 cells x 2 geometries x 3 conditions (exact repeats and counterfactual pairs left out, so each cell counts once per geometry and condition). 0.50 means the plans resolve the meeting more often than not; it is a judgement, not a sourced number. Head-on walkers in life almost never collide, so 0.50 is lenient against people, and strict against plain ORCA here, which passes within the near-miss distance and never counts as resolved (RF-9: 0 of 72). RF-9's pilot resolved 0.24 before resolve_v6's fixes, so failing the gate is a possible Step 1 result.

Pooled `plan_only`: 59 of 192 (0.31). The encounter type **fails** the gate.

| Group | Resolved | Rate |
| --- | --- | --- |
| all (plan_only) | 59 / 192 | 0.31 (95% CI 0.25 to 0.38) |
| condition independent | 22 / 64 | 0.34 (95% CI 0.24 to 0.47) |
| condition non_verbal | 17 / 64 | 0.27 (95% CI 0.17 to 0.38) |
| condition talk | 20 / 64 | 0.31 (95% CI 0.21 to 0.43) |
| geometry layout=aligned | 32 / 96 | 0.33 (95% CI 0.25 to 0.43) |
| geometry layout=apart_20cm | 27 / 96 | 0.28 (95% CI 0.20 to 0.38) |
| baseline plan_orca | 65 / 192 | 0.34 (95% CI 0.28 to 0.41) |
| baseline plain_orca | 0 / 192 | 0.00 (95% CI 0.00 to 0.02) |
