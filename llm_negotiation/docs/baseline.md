# The baselines: what "plain ORCA" means

Every comparison in issue #28 and in the sub-issues after it is measured against "plain
ORCA". This file fixes what that is, before any experiment, so that a later result cannot
quietly move it.

**Values set by the user in this issue. Supervisor sign-off: pending unless the work log records otherwise.**
(`WORK_LOG-28.md` records no sign-off.)

## 1. The two baselines

| | `orca_perturbed_v1` | `orca_unperturbed_v1` |
|---|---|---|
| Role | **primary** | secondary |
| File | `configs/baselines/orca_perturbed_v1.yaml` | `configs/baselines/orca_unperturbed_v1.yaml` |
| Directives | none: plain ORCA | none: plain ORCA |
| Perturbation of the preferred velocity | 1e-4 m/s, every agent, every step (section 3) | none |
| `max_neighbours` | 40 `[placeholder]` | 40 `[placeholder]` |
| `sensing_radius` | 12.5 m `[placeholder]` | 12.5 m `[placeholder]` |
| `orca.tie_break` | `brake` (DD26) | `brake` (DD26) |
| Everything else | as the scenario sets it | as the scenario sets it |

**Why two.** Unperturbed ORCA deadlocks in an exactly symmetric meeting: two agents
exactly head-on, or arriving at a crossing at the same instant, brake and never turn
(`derivations.md`, section 14). That is a property of the algorithm in exact symmetry, not
of people, and a rule compared against it would get credit for breaking a deadlock that a
real crowd never has. The primary baseline therefore breaks exact symmetry the way the
reference implementation does (section 3). The unperturbed baseline is reported beside it
so that the effect of the perturbation itself can be seen.

**"Rule-following" is a baseline with rules on top.** A rule-following condition uses the
same baseline file and adds `directives: {provider: rules, ...}`. Nothing else differs
between it and the plain condition it is compared with.

## 2. The values

| Value | Status | Reason |
|---|---|---|
| Neighbour limit 40 | `[placeholder]` | Set by the user in issue #28, as noted in #26. Issue #26 found that the limit decides how often bodies overlap in a crowd: with the 10 cited from practice (Menge's example, `parameters.md`), 512 overlap episodes in the two-way flow, deepest 8 cm; with 40, 87 episodes, deepest 2.3 cm. Forty has no source. |
| Sensing radius 12.5 m | `[placeholder]` | Set by the user in issue #28. It is the bound below which ORCA's paper says a neighbour can matter at all within τ, at these speeds (`parameters.md`, section 2: `(v_max + v_max) τ` plus the two radii). That is a property of the algorithm, not a measured range at which people attend to each other, so as a *human* sensing radius it is a placeholder until sourced. |
| Sensing radius 5 m | `[placeholder]`, sensitivity check only | Menge's example uses 5 m. Not a baseline value: the behaviour checks run head-on and overtaking at 5 m too, as a level of their own experiment on top of a baseline, and report how the results move. |
| Tie-break `brake` | design (DD26) | An exact tie between the two passing sides takes no side. RVO2 sends it to the right. A "keep right" inside the baseline of a study of which side people take would be a rule in disguise. |
| Perturbation 1e-4 m/s | cited, and measured (section 3) | |

The physical parameters of the agents (radius, speeds, time horizons) are the scenarios'
own, cited or tagged in `parameters.md`; a baseline does not touch them.

## 3. The perturbation

**What it is.** On every step, for every agent, a vector is added to the preferred velocity:
its direction uniform on the circle, its length uniform on [0, 1e-4] m/s, drawn anew each
time. It comes from a random stream of its own, seeded by the run's seed (and separate from
the arbiter's tie-break), so a run is still reproducible to the byte.

**Where it comes from.** The RVO2 library's own examples do exactly this, with the same
distribution and the same magnitude, under the comment "Perturb a little to avoid deadlocks
due to perfect symmetry" (`examples/Blocks.cc`, lines 178–186, and `examples/Roadmap.cc`,
lines 322–331, cached in `refs/si1_rvo2_75822bb_excerpts.txt:785-797` and `:822-832`). In
those examples the preferred speed is 1, so the magnitude is 1e-4 of it.

**Why this magnitude.** Measured before the baselines were frozen (`WORK_LOG-28.md`, entry
"Choosing the perturbation"): the three exactly symmetric layouts of issue #26, and the
10 cm offset head-on, with 40 neighbours, 20 seeds each.

| Magnitude (m/s) | Symmetric head-on | Symmetric crossing | Directly behind | Offset head-on |
|---|---|---|---|---|
| 0 | deadlock in 20 of 20 | deadlock in 20 of 20 | no overtaking (29.5 s) | 12.2 s, passes left in 20 of 20 |
| 1e-6 to 1e-3 | no deadlock; 12.3–12.4 s; left in 9, right in 11 | no deadlock; 12.5–12.6 s | overtakes; 31.7–32.1 s | unchanged |
| 1e-2 | no deadlock; 12.3 s | no deadlock; 12.4–12.5 s | 32.0–32.2 s | unchanged |
| 1e-4, R = 5 m | no deadlock; 12.2 s | no deadlock; 12.4 s | 31.9–32.0 s | unchanged |

- **It does its job.** Every exact deadlock is broken, in every seed, at every magnitude
  from 1e-6 m/s up; 1e-4 is in that range with room on both sides.
- **It changes nothing else.** The non-degenerate meeting, 10 cm off, comes out the same
  to the 0.1 s reported, on the same side, at every magnitude.
- **It is not behaviour.** 1e-4 m/s is 0.008% of the 1.3 m/s walking speed and about
  1/1,900 of the spread of desired walking speeds measured by Moussaïd et al. (0.19 m/s,
  `parameters.md`). Over the few seconds an encounter lasts it moves an agent by well
  under a millimetre.
- **It has a source.** Any magnitude in the working range would do; this one is the
  reference implementation's.

**What it does change**, qualitatively: directly behind a slower walker, unperturbed ORCA
never overtakes (the two settle at one speed: issue #26's "hurried along" artefact). With
the perturbation the faster walker goes round, on a side the noise picks. That is the
point of breaking a symmetry, and it is why the unperturbed baseline is reported too.

## 4. Frozen

`configs/baselines/MANIFEST.json` holds the SHA-256 of each baseline file (line endings
normalised to LF). `negsim.experiment.baselines.load_baseline` refuses a file that is not
listed there, or whose contents no longer match, and its error names the file to write
instead. **A baseline is never edited after issue #28. Any change creates `_v2`.**

## 5. Using a baseline

```yaml
baseline: orca_perturbed_v1          # at the top of an experiment, or in a level of a factor
```

The baseline's settings are laid on the scenario before the experiment's own
`scenario_overrides`, so a level can still change one of them; the 5 m sensitivity check is
such a level. Every run records the baseline (`config.json`: `baseline`, with the file's
SHA-256, and `perturbation`) and the scenario as actually used (`scenario`). An experiment
without `baseline:` runs as in issue #26: the scenario's own settings, no perturbation.

## 6. Seeds: a baseline run and a rule run are paired (issue #30)

**What a seed decides.** A run's seed (`config.json`: `seed`) seeds two random streams, each
of its own: the baseline's perturbation (section 3) and the arbiter's tie-break, if a run
asks for a random one. Where the agents start is the scenario's own business: a scenario
that randomises it (the jitter of the two-way flow) uses `scenario.seed`, which is the
scenario's seed plus `repeat − 1`, the same for every level of an experiment.

**How it is derived.** An avoidance experiment says how in `design.seeding`:

| `seeding` | A run's seed | Since |
|---|---|---|
| `paired` (the default) | `design.seed` plus the run's `repeat` | issue #30 |
| `per_run` | `design.seed` plus the run's `run_index`, its place in the design | issues #26 and #28 |

Under `paired`, every level of every factor of one repeat runs on the same seed, so the plain
run and the rule run of one scenario instance draw the same perturbations and differ only
where the rules act: a comparison between them is paired, repeat by repeat. Under
`per_run` two levels of one repeat drew different perturbations, and a comparison between
them was between two samples (`WORK_LOG-28.md`, Q9). **DD66 (decision):** `paired` is the
default; every committed experiment config of issues #26 and #28 says `seeding: per_run`, so
that it still reproduces its committed runs. Every run records its `seeding`.

**Why a rule run with no rule reproduces the baseline exactly.** With no rule switched on,
the rule provider gives every agent plain ORCA's directive on every step. The run loop then
does the same computations in the same order, draws the same perturbations from the same
stream, and writes the same trajectory, to the byte.
*Tested:* `tests/test_pair_exposure.py::test_a_rule_run_with_no_rule_writes_the_baseline_trajectory`, which also
checks that under `per_run` the two differ.

A generated rule is replayed on the seed of the very baseline run its conflict case came
from (`rule-generation.md`, replay), so that comparison is paired too.
