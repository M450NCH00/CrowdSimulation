"""Whether a rule set helps, against plain ORCA on the same seeds (issue #74, RF-18).

The rule was fixed with the user before any run (``WORK_LOG-74.md``, task 0;
``docs/rule-set-evaluation.md``, section 3):

* A measure is **better** or **worse** only if the exact two-sided sign test over the paired
  seeds, ties dropped, gives p below ``ALPHA`` (with 10 seeds and no ties, 9 of 10 must agree).
* **not used**: no rule of the arm matched on any seed. **harms**: it gridlocks on a seed where
  plain ORCA did not, or severe conflicts are worse. **helps**: severe conflicts are fewer, and
  throughput and delay are not worse. **trade-off**: severe conflicts fewer, but throughput or
  delay worse. **no change**: anything else. Tested in that order.
"""

from __future__ import annotations

from math import comb
from typing import Any, Mapping, Optional, Sequence

ALPHA = 0.05
NOT_USED, HARMS, HELPS, TRADE_OFF, NO_CHANGE = "not used", "harms", "helps", "trade-off", "no change"
VERDICTS = (NOT_USED, HARMS, HELPS, TRADE_OFF, NO_CHANGE)
#: Each measure, and whether a lower value is better.
MEASURES = {"severe_conflicts": True, "throughput_agents_per_min": False, "mean_delay_s": True}
BETTER, WORSE, SAME = "better", "worse", "no difference"


def sign_test(better: int, worse: int) -> float:
    """Exact two-sided sign test: the chance of a split at least this uneven if either way is as
    likely. 1.0 with no untied pair."""
    n = better + worse
    if n == 0:
        return 1.0
    k = min(better, worse)
    return min(1.0, 2.0 * sum(comb(n, i) for i in range(k + 1)) / 2.0**n)


def compare(arm: Sequence[Optional[float]], plain: Sequence[Optional[float]], lower_is_better: bool, alpha: float = ALPHA) -> dict[str, Any]:
    """One measure, seed by seed: how many seeds the arm did better, worse or the same, and the test."""
    better = worse = ties = missing = 0
    for a, p in zip(arm, plain):
        if a is None or p is None:
            missing += 1
        elif a == p:
            ties += 1
        elif (a < p) == lower_is_better:
            better += 1
        else:
            worse += 1
    p_value = sign_test(better, worse)
    direction = SAME if p_value >= alpha else (BETTER if better > worse else WORSE)
    return {"better": better, "worse": worse, "ties": ties, "missing": missing, "p": round(p_value, 6), "direction": direction}


def verdict(per_seed: Sequence[Mapping[str, Any]], alpha: float = ALPHA) -> dict[str, Any]:
    """The verdict of one arm in one scenario. ``per_seed`` holds, for each seed, the arm's
    measures (``arm``) and plain ORCA's (``plain``), as ``measures.run_measures`` gives them."""
    tests = {
        name: compare([entry["arm"][name] for entry in per_seed], [entry["plain"][name] for entry in per_seed], lower, alpha)
        for name, lower in MEASURES.items()
    }
    new_gridlock = [entry["seed"] for entry in per_seed if entry["arm"]["gridlocked"] and not entry["plain"]["gridlocked"]]
    used = any(entry["arm"]["rule_matches"] for entry in per_seed)
    severe = tests["severe_conflicts"]["direction"]
    costs = [name for name in ("throughput_agents_per_min", "mean_delay_s") if tests[name]["direction"] == WORSE]
    reasons = []
    if not used:
        outcome = NOT_USED
        reasons.append("no rule of the set matched on any seed")
    elif new_gridlock or severe == WORSE:
        outcome = HARMS
        if new_gridlock:
            reasons.append(f"gridlocked on seed(s) {new_gridlock}, where plain ORCA did not")
        if severe == WORSE:
            reasons.append("more severe conflicts than plain ORCA")
    elif severe == BETTER and not costs:
        outcome = HELPS
        reasons.append("fewer severe conflicts, and neither throughput nor delay worse")
    elif severe == BETTER:
        outcome = TRADE_OFF
        reasons.append(f"fewer severe conflicts, but worse {' and '.join(costs)}")
    else:
        outcome = NO_CHANGE
        reasons.append("no significant difference in severe conflicts" + (f"; worse {' and '.join(costs)}" if costs else ""))
    return {"verdict": outcome, "reasons": reasons, "tests": tests, "new_gridlock_seeds": new_gridlock, "alpha": alpha, "seeds": len(per_seed)}
