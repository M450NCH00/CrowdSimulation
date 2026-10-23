"""Screening designs (issue #62, RF-7; ``docs/screening-designs.md``): which cells of a full
factorial a design runs.

**A regular fractional factorial** (:func:`fraction`), two levels per factor. With N runs (16 or
32) there are b = log2 N base factors, crossed in full; each further factor's column is the
product of some base columns, its *generator*. A design with k factors is a 2^(k-p) design,
p = k - b. Its **resolution** is the length of its shortest defining word: at resolution IV or
higher no main effect is aliased with another main effect or with any two-factor interaction,
which is what a screen needs. :func:`aliasing_problems` checks exactly that on the cells
themselves, not on the generators.

The generators are published, not chosen here (:data:`GENERATORS`, :data:`SOURCES`):

- **16 runs, 5 to 8 factors; 32 runs, 6 to 11 factors:** the NIST/SEMATECH e-Handbook of
  Statistical Methods, section 5.3.3.4.7, Table 3.17, whose summaries come from Box, Hunter &
  Hunter (1978) and Montgomery (2000); each design's file is cached as ``refs/rf7_nist_2to<k>m<p>.txt``.
- **32 runs, 12 to 16 factors:** Table 3.17 stops at 11 factors in 32 runs. Chen & Cheng (2006,
  *Annals of Statistics* 34: 546-558, Corollary 3.6 and section 4) show that every regular
  resolution IV design with 5N/16 < k <= N/2 factors is a projection of the saturated one, the
  2^(16-11) design whose 16 columns are every odd-length product of the 5 base factors, and that
  it has minimum aberration. So the 16-factor design is that one, and a design of 12 to 15
  factors deletes columns from it: the deletion with minimum aberration, found by searching
  every deletion (tested: :func:`word_length_pattern`). These designs nest: each is the one
  before with one more column.

At most N/2 two-level factors fit in N runs at resolution IV (Chen & Cheng 2006, section 2), so
32 runs hold 16 factors and no more.

**A balanced random sample** (:func:`balanced_sample`): N distinct cells of the full factorial,
each factor's levels as equally often as N allows, drawn with a seed.

**A balanced subset** (:func:`balanced_subset`): n of a design's cells, each factor's levels as
equally often as possible; the exact-repeat set (D14) is one.
"""

from __future__ import annotations

import itertools
import math
import random
from typing import Any, Mapping, Optional, Sequence

#: The run sizes a fractional design may have.
RUN_SIZES = (16, 32)
#: Per run size and number of factors, the generators of the factors after the base ones: each
#: a product of base factors, numbered from 1 (``"123"`` is the product of the first three).
#: Factors 1 to b (b = log2 of the run size) are the base factors themselves.
GENERATORS: dict[tuple[int, int], tuple[str, ...]] = {
    # NIST/SEMATECH e-Handbook, Table 3.17 (refs/rf7_nist_2to<k>m<p>.txt)
    (16, 5): ("1234",),
    (16, 6): ("123", "234"),
    (16, 7): ("123", "234", "134"),
    (16, 8): ("234", "134", "123", "124"),
    (32, 6): ("12345",),
    (32, 7): ("1234", "1245"),
    (32, 8): ("123", "124", "2345"),
    (32, 9): ("2345", "1345", "1245", "1235"),
    (32, 10): ("1234", "1235", "1245", "1345", "2345"),
    (32, 11): ("123", "234", "345", "134", "145", "245"),
    # Chen & Cheng 2006: the saturated 2^(16-11) design and its minimum-aberration projections
    **{
        (32, k): ("123", "124", "125", "134", "135", "145", "234", "235", "245", "345", "12345")[: k - 5]
        for k in range(12, 17)
    },
}
NIST = "NIST/SEMATECH e-Handbook of Statistical Methods, section 5.3.3.4.7, Table 3.17"
CHEN_CHENG = "Chen & Cheng (2006), Ann. Statist. 34: 546-558, Corollary 3.6: a projection of the saturated 2^(16-11) design"
SOURCES: dict[tuple[int, int], str] = {key: NIST if key[1] <= 11 else CHEN_CHENG for key in GENERATORS}


class DesignError(ValueError):
    """A design that cannot be built as asked."""


def base_count(runs: int) -> int:
    if runs not in RUN_SIZES:
        raise DesignError(f"a fractional design has {' or '.join(map(str, RUN_SIZES))} cells, not {runs}")
    return int(math.log2(runs))


def smallest_runs(factors: int) -> int:
    """The fewest cells (of :data:`RUN_SIZES`) that hold ``factors`` two-level factors at
    resolution IV or higher."""
    if factors > max(RUN_SIZES) // 2:
        raise DesignError(
            f"{factors} two-level factors do not fit a resolution IV design of at most {max(RUN_SIZES)} cells: "
            f"N cells hold at most N/2 factors at resolution IV (Chen & Cheng 2006). Fix some factors at one level"
        )
    return next(runs for runs in RUN_SIZES if factors <= runs // 2)


def generators(factors: int, runs: int) -> tuple[str, ...]:
    """The generators of a 2^(k-p) design with ``factors`` factors in ``runs`` cells; none when the
    design is the full factorial (2^k = runs). Refuses what the tables do not hold."""
    b = base_count(runs)
    if factors > runs // 2:
        raise DesignError(
            f"{factors} two-level factors in {runs} cells: at resolution IV, {runs} cells hold at most {runs // 2} "
            f"factors (Chen & Cheng 2006). Fix some factors at one level, or ask for more cells"
        )
    if factors < b:
        raise DesignError(f"{factors} two-level factors have only {2 ** factors} combinations, fewer than {runs} cells: use kind full")
    if factors == b:
        return ()
    return GENERATORS[(runs, factors)]


def fraction(factors: int, runs: int) -> list[tuple[int, ...]]:
    """The cells of the design as rows of -1 and +1, one column per factor: the base factors in
    standard order (the first changes fastest), then each generated column."""
    b = base_count(runs)
    words = generators(factors, runs)
    rows = []
    for index in range(runs):
        base = tuple(1 if index >> bit & 1 else -1 for bit in range(b))
        rows.append(base + tuple(math.prod(base[int(ch) - 1] for ch in word) for word in words))
    return rows


def aliasing_problems(rows: Sequence[Sequence[int]], names: Optional[Sequence[str]] = None) -> list[str]:
    """What breaks resolution IV in these cells (empty if nothing): a factor not balanced, two
    main effects aliased, or a main effect aliased with a two-factor interaction of two other
    factors. Checked on the columns themselves: aliased means equal up to sign."""
    k = len(rows[0])
    names = list(names or (str(i + 1) for i in range(k)))
    columns = [tuple(row[i] for row in rows) for i in range(k)]
    found = []
    for i, column in enumerate(columns):
        if sum(column) != 0:
            found.append(f"{names[i]} is not balanced")
    for i, j in itertools.combinations(range(k), 2):
        if columns[i] in (columns[j], tuple(-v for v in columns[j])):
            found.append(f"{names[i]} is aliased with {names[j]}")
    for i in range(k):
        for j, l in itertools.combinations([n for n in range(k) if n != i], 2):
            product = tuple(a * b for a, b in zip(columns[j], columns[l]))
            if columns[i] in (product, tuple(-v for v in product)):
                found.append(f"{names[i]} is aliased with the interaction {names[j]} x {names[l]}")
    return found


def word_length_pattern(factors: int, runs: int) -> tuple[int, ...]:
    """(A1, A2, ..., Ak): how many defining words of each length the design has. The resolution is
    the first length with a word; minimum aberration means the smallest pattern from A3 on."""
    b = base_count(runs)
    masks = [sum(1 << (int(ch) - 1) for ch in word) for word in generators(factors, runs)]
    counts = [0] * factors
    for size in range(1, len(masks) + 1):
        for chosen in itertools.combinations(masks, size):
            product = 0
            for mask in chosen:
                product ^= mask
            counts[size + bin(product).count("1") - 1] += 1
    return tuple(counts)


def resolution(factors: int, runs: int) -> Optional[int]:
    """The design's resolution; ``None`` for the full factorial (it has no defining word)."""
    pattern = word_length_pattern(factors, runs)
    return next((length for length, count in enumerate(pattern, start=1) if count), None)


# --- a balanced random sample -------------------------------------------------------------------


def _balanced_column(levels: Sequence[Any], n: int, rng: random.Random) -> list[Any]:
    """``n`` levels, each as often as ``n`` allows (the extra ones on levels drawn at random), shuffled."""
    extra = rng.sample(range(len(levels)), n % len(levels))
    column = [level for k, level in enumerate(levels) for _ in range(n // len(levels) + (k in extra))]
    rng.shuffle(column)
    return column


def balanced_sample(levels: Sequence[Sequence[Any]], n: int, rng: random.Random, attempts: int = 1000) -> list[tuple[Any, ...]]:
    """``n`` distinct cells of the full factorial of ``levels`` (one sequence per factor), each
    factor balanced as well as ``n`` allows: every level ``n // L`` or ``n // L + 1`` times.

    Each factor's column is drawn balanced and shuffled on its own; a draw with two equal cells is
    drawn again. Asking for the whole factorial gives it in full."""
    total = math.prod(len(chosen) for chosen in levels)
    if n > total:
        raise DesignError(f"a sample of {n} cells from a full factorial of {total}: ask for at most {total}, or use kind full")
    if n == total:
        return list(itertools.product(*levels))
    for _ in range(attempts):
        cells = list(zip(*(_balanced_column(chosen, n, rng) for chosen in levels)))
        if len(set(cells)) == n:
            return cells
    raise DesignError(f"no balanced sample of {n} distinct cells was found in {attempts} draws: ask for fewer cells, or use kind full")


# --- a balanced subset --------------------------------------------------------------------------


def imbalance(cells: Sequence[Mapping[str, Any]], levels: Mapping[str, Sequence[Any]]) -> int:
    """Over every factor, how far its most frequent level is ahead of its least frequent one in
    ``cells``: 0 when every factor is balanced. ``levels`` gives each factor's levels."""
    total = 0
    for name, chosen in levels.items():
        counts = [sum(1 for cell in cells if cell[name] == level) for level in chosen]
        total += max(counts) - min(counts)
    return total


def balanced_subset(cells: Sequence[Mapping[str, Any]], levels: Mapping[str, Sequence[Any]], n: int, rng: random.Random, restarts: int = 20) -> list[int]:
    """The indices of ``n`` of ``cells``, chosen with ``rng`` so that each factor's levels occur as
    equally often as possible (:func:`imbalance`): from several random starts, swap a chosen cell
    for another while that lowers the imbalance; the best end wins, the earliest on a tie."""
    if not 1 <= n <= len(cells):
        raise DesignError(f"{n} of {len(cells)} cells: ask for 1 to {len(cells)}")
    best: Optional[tuple[int, list[int]]] = None
    for _ in range(restarts):
        chosen = sorted(rng.sample(range(len(cells)), n))
        score = imbalance([cells[i] for i in chosen], levels)
        improved = True
        while improved and score:
            improved = False
            for position, outside in itertools.product(range(n), (i for i in range(len(cells)) if i not in chosen)):
                trial = sorted([*chosen[:position], outside, *chosen[position + 1:]])
                trial_score = imbalance([cells[i] for i in trial], levels)
                if trial_score < score:
                    chosen, score, improved = trial, trial_score, True
                    break
        if best is None or score < best[0]:
            best = (score, chosen)
        if score == 0:
            break
    return best[1]
