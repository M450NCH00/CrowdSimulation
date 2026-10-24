"""``python -m analysis <outcomes.csv> [more.csv ...]``: every analysis of RF-8, written to a folder
(issue #63).

From the repository root:

    python -m analysis llm_negotiation/runs/<experiment>/outcomes.csv

writes, by default to ``analysis/`` beside the first file:

| File | Contents |
| --- | --- |
| ``report.md`` | everything below, for reading |
| ``agents.csv`` | the reshaped table: one row per agent per session |
| ``effects_terms.csv``, ``effects_models.csv`` | every term of every model; every model's status |
| ``tree.txt``, ``tree.png`` | the decision tree |
| ``mapping.csv`` | the factor-to-decision mapping |
| ``noise_floor.csv``, ``flip_rates.csv``, ``stability.csv`` | the noise floor, the counterfactual flip rates against it, stability per cell |
| ``reason_mentions.csv``, ``debrief_kinds.csv``, ``stated_vs_measured.csv`` | stated against measured |
| ``intent_check.csv``, ``intent_summary.csv`` | the coded intents and plans; the mismatch rate |
| ``ethnicity_groups.csv``, ``ethnicity_weighted.csv`` | issue #92, with real ethnicity: outcomes by group; rates weighted back to random resident pairs |

``decisions.jsonl`` beside an ``outcomes.csv`` is read for the reasons and the intents; without
it those two parts say so. No LLM is called, and nothing outside the output folder is written.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Sequence

import pandas as pd

from . import effects, groups, intent, load, mapping, noise, report, stated, tree
from .factors import factor_of

SEED = 63


@dataclass
class Options:
    mode: str = "plan_only"
    tree_outcome: str = "passed_first"
    tree_depth: int = tree.MAX_DEPTH
    interactions: tuple[str, ...] = ()
    mapping_factors: Optional[tuple[str, ...]] = None
    alpha: float = effects.ALPHA
    holm_family: str = "report"
    coin_flip_below: float = noise.COIN_FLIP_BELOW
    named_often: float = stated.NAMED_OFTEN
    intent_codebook: str = intent.INTENT_CODEBOOK
    reasons_codebook: str = stated.REASONS_CODEBOOK
    seed: int = SEED


@dataclass
class Results:
    paths: list[str]
    options: Options
    clients: set[str]
    left_out: dict[str, int]
    sessions: pd.DataFrame
    agents: pd.DataFrame
    predictors: list[str]
    varied_predictors: list[str]
    fitted: list[effects.Fitted]
    tree: tree.Tree
    floors: pd.DataFrame
    flips: pd.DataFrame
    stability: pd.DataFrame
    mapping_factors: list[str]
    mapping: pd.DataFrame
    named: pd.DataFrame
    kinds: pd.DataFrame
    stated: pd.DataFrame
    checked: Optional[pd.DataFrame]
    intent_summary: Optional[pd.DataFrame]
    decisions_found: bool = field(default=False)
    ethnicity_groups: Optional[pd.DataFrame] = None  # issue #92
    ethnicity_weighted: Optional[pd.DataFrame] = None


def analyse(paths: Sequence[Path | str], options: Optional[Options] = None) -> Results:
    options = options or Options()
    paths = [str(path) for path in paths]
    raw = load.read_outcomes(paths)
    sessions, left_out = load.sessions_table(raw, options.mode)
    agents, predictors = load.agents_table(raw, sessions)
    known = {o.name for o in load.AGENT_OUTCOMES if o.kind == "binary"}
    if options.tree_outcome not in known:
        raise load.AnalysisError(f"--tree-outcome: one of {sorted(known)}, got {options.tree_outcome!r}")
    varied = load.varied(agents, predictors)
    fitted = effects.run_all(agents, varied, sessions, options.interactions, options.alpha, options.holm_family)
    grown = tree.grow(agents, varied, options.tree_outcome, options.tree_depth, options.seed)
    floors, flips = noise.summaries(sessions, options.seed)
    stable = noise.stability(sessions, options.coin_flip_below)
    if options.mapping_factors is not None:
        unknown = [name for name in options.mapping_factors if name not in agents.columns]
        if unknown:
            raise load.AnalysisError(f"--mapping-factors: unknown {unknown}; known: {predictors + ['geometry']}")
        factors = list(options.mapping_factors)
    else:
        factors = varied + (["geometry"] if agents["geometry"].nunique() > 1 else [])
    table = mapping.mapping_table(agents, factors)
    decisions = load.read_decisions(paths)
    named = stated.mentions(decisions, options.reasons_codebook)
    varied_factors = sorted({factor_of(p) for p in varied})
    against = stated.stated_against_measured(named, fitted, varied_factors, options.named_often)
    checked = intent.check(decisions, options.intent_codebook) if decisions is not None else None
    return Results(
        paths=paths, options=options, clients=load.client_of(paths), left_out=left_out, sessions=sessions, agents=agents,
        predictors=predictors, varied_predictors=varied, fitted=fitted, tree=grown, floors=floors, flips=flips, stability=stable,
        mapping_factors=factors, mapping=table, named=named, kinds=stated.debrief_kinds(agents), stated=against,
        checked=checked, intent_summary=intent.summary(checked) if checked is not None else None, decisions_found=decisions is not None,
        ethnicity_groups=groups.by_group(agents), ethnicity_weighted=groups.weighted(sessions),
    )


def write(results: Results, out: Path) -> list[Path]:
    """Every file of the table in this module's docstring; returns them."""
    out.mkdir(parents=True, exist_ok=True)
    written = []

    def csv(name: str, frame: Optional[pd.DataFrame], index: bool = False) -> None:
        if frame is None:
            return
        path = out / name
        frame.to_csv(path, index=index, lineterminator="\n")
        written.append(path)

    csv("agents.csv", results.agents)
    csv("effects_terms.csv", effects.terms_frame(results.fitted))
    csv("effects_models.csv", effects.models_frame(results.fitted))
    csv("mapping.csv", results.mapping)
    csv("noise_floor.csv", results.floors)
    csv("flip_rates.csv", results.flips)
    csv("stability.csv", results.stability)
    csv("reason_mentions.csv", results.named)
    csv("debrief_kinds.csv", results.kinds, index=True)
    csv("stated_vs_measured.csv", results.stated)
    csv("intent_check.csv", results.checked)
    csv("intent_summary.csv", results.intent_summary)
    csv("ethnicity_groups.csv", results.ethnicity_groups)
    csv("ethnicity_weighted.csv", results.ethnicity_weighted)
    (out / "tree.txt").write_text(results.tree.text or results.tree.note + "\n", encoding="utf-8")
    written.append(out / "tree.txt")
    if tree.save_figure(results.tree, out / "tree.png"):
        written.append(out / "tree.png")
    (out / "report.md").write_text(report.render(results), encoding="utf-8")
    written.append(out / "report.md")
    return written


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="python -m analysis", description="RF-8 (issue #63): factor effects, a decision tree, the mapping, "
                                "the noise floor, stability, stated against measured, and intent against plan.")
    p.add_argument("outcomes", nargs="+", help="one or more outcomes.csv of resolution experiments")
    p.add_argument("--out", help="the output folder (default: analysis/ beside the first file)")
    p.add_argument("--mode", default="plan_only", choices=load.MODES, help="whose physical outcomes (default: plan_only, the Step 1 measure)")
    p.add_argument("--tree-outcome", default="passed_first", help="the per-agent binary outcome the tree predicts")
    p.add_argument("--tree-depth", type=int, default=tree.MAX_DEPTH, help=f"1 to {tree.MAX_DEPTH}")
    p.add_argument("--interaction", action="append", default=[], metavar="A:B", help="a named interaction of two predictors (repeatable)")
    p.add_argument("--mapping-factors", help="comma-separated columns for the mapping (default: every predictor that varies, and geometry)")
    p.add_argument("--alpha", type=float, default=effects.ALPHA, help="for Holm's correction (default 0.05)")
    p.add_argument("--holm-family", default="report", choices=effects.FAMILIES,
                   help="the terms Holm's correction runs over: every term in the report (default), one subset's, or one model's")
    p.add_argument("--coin-flip-below", type=float, default=noise.COIN_FLIP_BELOW, help="a cell is a coin flip below this stability (default 0.75)")
    p.add_argument("--named-often", type=float, default=stated.NAMED_OFTEN, help="a factor named in at least this share of reasons is named often (default 0.10)")
    p.add_argument("--intent-codebook", default=intent.INTENT_CODEBOOK)
    p.add_argument("--reasons-codebook", default=stated.REASONS_CODEBOOK)
    p.add_argument("--seed", type=int, default=SEED, help="for the bootstrap and the tree (default 63)")
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parser().parse_args(argv)
    options = Options(
        mode=args.mode, tree_outcome=args.tree_outcome, tree_depth=args.tree_depth, interactions=tuple(args.interaction),
        mapping_factors=tuple(name.strip() for name in args.mapping_factors.split(",")) if args.mapping_factors else None,
        alpha=args.alpha, holm_family=args.holm_family, coin_flip_below=args.coin_flip_below, named_often=args.named_often,
        intent_codebook=args.intent_codebook, reasons_codebook=args.reasons_codebook, seed=args.seed,
    )
    try:
        results = analyse(args.outcomes, options)
    except (load.AnalysisError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    out = Path(args.out) if args.out else Path(args.outcomes[0]).resolve().parent / "analysis"
    for path in write(results, out):
        print(path)
    return 0
