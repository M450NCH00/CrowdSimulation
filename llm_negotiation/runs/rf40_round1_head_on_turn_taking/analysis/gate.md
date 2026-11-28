# The resolution gate

Threshold, fixed in the config before the run: 0.50 of the design's sessions resolved in `plan_only`. Reason: Step 1 asks whether LLM agents can resolve the conflict on their own plans, so the gate is the plan_only rate (ORCA does not steer the pair apart), pooled over the design's 192 sessions of 32 cells x 2 geometries x 3 conditions (exact repeats and counterfactual pairs left out, so each cell counts once per geometry and condition). 0.50 means the plans resolve the meeting more often than not; it is a judgement, not a sourced number. Head-on walkers in life almost never collide, so 0.50 is lenient against people, and strict against plain ORCA here, which passes within the near-miss distance and never counts as resolved (RF-9: 0 of 72). RF-9's pilot resolved 0.24 before resolve_v6's fixes, so failing the gate is a possible Step 1 result.

Pooled `plan_only`: 123 of 192 (0.64). The encounter type **passes** the gate.

| Group | Resolved | Rate |
| --- | --- | --- |
| all (plan_only) | 123 / 192 | 0.64 (95% CI 0.57 to 0.71) |
| condition non_verbal | 40 / 64 | 0.62 (95% CI 0.50 to 0.73) |
| condition silent | 42 / 64 | 0.66 (95% CI 0.53 to 0.76) |
| condition talk | 41 / 64 | 0.64 (95% CI 0.52 to 0.75) |
| geometry layout=aligned | 68 / 96 | 0.71 (95% CI 0.61 to 0.79) |
| geometry layout=apart_20cm | 55 / 96 | 0.57 (95% CI 0.47 to 0.67) |
| baseline plan_orca | 129 / 192 | 0.67 (95% CI 0.60 to 0.73) |
| baseline plain_orca | 0 / 192 | 0.00 (95% CI 0.00 to 0.02) |
