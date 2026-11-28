"""The tables of RF-53's stage 1 report, from the probe's records (issue #144).

    python -m negsim.probe.report runs/rf53_stage1_frames_probe

Prints Markdown: the share correct per group and per probe in each arm, with Wilson 95% intervals and a
two-sided Fisher exact test between the arms; the facing note (group C against the same messages in A
and B); invented headings (probes 13 and 15); cut-off and unclear replies; reasoning tokens; cost.
Standard library only, like the rest of negsim. Every number is recomputed from ``calls/``.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

from .runner import CALLS_DIR, CONFIG_FILE, load_records

#: Group C's probes and the probes of A and B with the same message, without the note.
NOTE_PAIRS = (("p07", "p01"), ("p08", "p04"), ("p09", "p05"))
NO_HEADING = ("p13", "p15")


def wilson(k: int, n: int, z: float = 1.959964) -> tuple[float, float]:
    """Wilson's 95% interval for k successes in n."""
    if n == 0:
        return (math.nan, math.nan)
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    # The bounds are exactly 0 at k = 0 and 1 at k = n; floating point would leave 0.9999999999999999.
    return (0.0 if k == 0 else max(0.0, centre - half), 1.0 if k == n else min(1.0, centre + half))


def fisher_two_sided(a: int, b: int, c: int, d: int) -> float:
    """Two-sided Fisher exact p for the table [[a, b], [c, d]]: the sum of the probabilities of every
    table with the same margins that is no more likely than the one observed."""
    row1, col1, n = a + b, a + c, a + b + c + d
    if n == 0:
        return 1.0

    def p_of(x: int) -> float:
        return math.comb(col1, x) * math.comb(n - col1, row1 - x) / math.comb(n, row1)

    observed = p_of(a)
    low, high = max(0, row1 + col1 - n), min(row1, col1)
    return min(1.0, math.fsum(p for x in range(low, high + 1) if (p := p_of(x)) <= observed * (1 + 1e-9)))


def _share(rows: Sequence[Mapping[str, Any]]) -> tuple[int, int]:
    return sum(1 for r in rows if r["score"]["outcome"] == "correct"), len(rows)


def _cell(k: int, n: int) -> str:
    if not n:
        return "–"
    low, high = wilson(k, n)
    return f"{k}/{n} ({k / n:.2f}; {low:.2f} to {high:.2f})"


def _p(off: tuple[int, int], on: tuple[int, int]) -> str:
    (k0, n0), (k1, n1) = off, on
    if not n0 or not n1:
        return "–"
    p = fisher_two_sided(k0, n0 - k0, k1, n1 - k1)
    return "< 0.0001" if p < 0.0001 else f"{p:.4f}" if p < 0.01 else f"{p:.2f}"


def report(experiment_dir: Path) -> str:
    experiment_dir = Path(experiment_dir)
    config = json.loads((experiment_dir / CONFIG_FILE).read_text(encoding="utf-8"))["config"]
    records = [r for r in load_records(experiment_dir) if r.get("api_error") is None and r.get("score")]
    arms = [a["name"] for a in config["arms"]]
    off, on = arms[0], arms[-1]
    by = lambda **kw: [r for r in records if all(r[k] == v for k, v in kw.items())]  # noqa: E731
    groups = sorted({r["group"] for r in records})
    probes = sorted({r["probe_id"] for r in records})
    lines: list[str] = []
    out = lines.append

    out(f"Records: {len(records)} of {len(arms) * config['repeats'] * config['probes']['n']} planned "
        f"({config['probes']['name']}, SHA-256 {config['probes']['sha256'][:12]}...).")
    out("")
    out("### Share correct, by group (Wilson 95% interval; Fisher exact test, two-sided, between the arms)")
    out("")
    out(f"| Group | {off} | {on} | p |")
    out("| --- | --- | --- | --- |")
    for g in [*groups, "all"]:
        a, b = (_share(by(arm=off)), _share(by(arm=on))) if g == "all" else (_share(by(arm=off, group=g)), _share(by(arm=on, group=g)))
        out(f"| {g} | {_cell(*a)} | {_cell(*b)} | {_p(a, b)} |")
    out("")
    out("### By probe (correct / wrong / unclear)")
    out("")
    out(f"| Probe | Group | {off} | {on} | Labels, {off} | Labels, {on} |")
    out("| --- | --- | --- | --- | --- | --- |")
    for p in probes:
        cells, labels = [], []
        for arm in (off, on):
            rows = by(arm=arm, probe_id=p)
            outcome = Counter(r["score"]["outcome"] for r in rows)
            cells.append(f"{outcome['correct']} / {outcome['wrong']} / {outcome['unclear']}")
            labels.append(", ".join(f"{k} {v}" for k, v in sorted(Counter(r["score"]["label"] for r in rows).items())))
        group = by(probe_id=p)[0]["group"]
        out(f"| {p} | {group} | {cells[0]} | {cells[1]} | {labels[0]} | {labels[1]} |")
    out("")
    out("### The facing note: group C against the same message without it")
    out("")
    out(f"| With the note | Without | {off}: with / without | {on}: with / without |")
    out("| --- | --- | --- | --- |")
    for with_, without in NOTE_PAIRS:
        cells = [f"{_cell(*_share(by(arm=arm, probe_id=with_)))} / {_cell(*_share(by(arm=arm, probe_id=without)))}" for arm in (off, on)]
        out(f"| {with_} | {without} | {cells[0]} | {cells[1]} |")
    out("")
    out("### Invented headings (no heading given; any side is invented)")
    out("")
    out(f"| Probe | {off}: invented | {on}: invented |")
    out("| --- | --- | --- |")
    for p in NO_HEADING:
        cells = []
        for arm in (off, on):
            rows = by(arm=arm, probe_id=p)
            cells.append(f"{sum(1 for r in rows if r['score']['label'] in ('left', 'right'))}/{len(rows)}")
        out(f"| {p} | {cells[0]} | {cells[1]} |")
    out("")
    out("### Replies cut off, unclear or ambiguous")
    out("")
    for arm in arms:
        rows = by(arm=arm)
        cut = [r["call_id"] for r in rows if r["finish_reason"] == "length"]
        unclear = [r["call_id"] for r in rows if r["score"]["outcome"] == "unclear"]
        ambiguous = [r["call_id"] for r in rows if r["score"]["ambiguous"]]
        out(f"- {arm}: cut off at the reply cap {len(cut)}{_list(cut)}; unclear {len(unclear)}{_list(unclear)}; "
            f"ambiguous {len(ambiguous)}{_list(ambiguous)}.")
    out("")
    out("### Tokens, time and cost")
    out("")
    out("| Arm | Reasoning tokens: median (mean; max) | Completion tokens: median | Latency s: median (max) | Cost USD |")
    out("| --- | --- | --- | --- | --- |")
    for arm in arms:
        rows = by(arm=arm)
        reasoning = [r["usage"]["reasoning_tokens"] for r in rows]
        completion = [r["usage"]["completion_tokens"] for r in rows]
        latency = [r["latency_s"] or 0.0 for r in rows]
        cost = math.fsum(r["cost_usd"] or 0.0 for r in rows)
        out(f"| {arm} | {statistics.median(reasoning):.0f} ({statistics.fmean(reasoning):.0f}; {max(reasoning)}) | "
            f"{statistics.median(completion):.0f} | {statistics.median(latency):.1f} ({max(latency):.1f}) | {cost:.4f} |")
    fingerprints = Counter(str(r["system_fingerprint"]) for r in records)
    out("")
    out(f"Fingerprints: {dict(fingerprints)}; expected {config.get('expected_fingerprint')}. "
        f"Price tiers: {dict(Counter(str(r['price_tier']) for r in records))}.")
    return "\n".join(lines) + "\n"


def _list(ids: Sequence[str], limit: int = 12) -> str:
    if not ids:
        return ""
    shown = ", ".join(ids[:limit]) + (", ..." if len(ids) > limit else "")
    return f" ({shown})"


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("experiment_dir", type=Path, help=f"a probe experiment's folder (with {CONFIG_FILE} and {CALLS_DIR}/)")
    args = parser.parse_args(argv)
    print(report(args.experiment_dir), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
