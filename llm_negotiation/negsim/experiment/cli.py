"""Run an experiment from a config file.

    python run_experiment.py configs/experiments/c0_no_llm.yaml
    python run_experiment.py configs/experiments/c1_smoke.yaml --plan
    python run_experiment.py configs/experiments/c1_smoke.yaml --client mock
    python run_experiment.py configs/experiments/c1_smoke.yaml --client deepseek
    python run_experiment.py configs/avoidance/si1_head_on_side_preference.yaml

``--client mock`` rehearses the experiment with the deterministic mock model: no network,
no cost, output under ``runs_mock/`` (not committed). ``--client deepseek`` makes paid API
calls, each one checked against the budget cap in the config, with output under ``runs/``.
Without ``--client`` the config's own ``llm.client`` is used.

A config that says ``layer: avoidance`` is an avoidance experiment (ORCA under directives).
It calls no model at all, so ``--client`` does not apply to it and it costs nothing; its
output goes under ``runs/``.

Run it from the ``llm_negotiation`` folder. Paths inside configs are relative to that folder.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

from ..configutil import ConfigError, load_yaml, resolve_path
from ..llm import LLMError
from .avoidance import AvoidanceExperiment, is_avoidance_config, run_avoidance_experiment
from .batch import make_client, run_experiment, worst_case_cost
from .config import ExperimentConfig


def run_avoidance(args: argparse.Namespace) -> int:
    """An avoidance experiment: no model, no client, no cost."""
    if args.client:
        raise ConfigError(
            f"{args.config} is an avoidance experiment, which calls no model; --client does not apply to it"
        )
    config = AvoidanceExperiment.load(args.config)
    plans = config.plans()[: args.limit] if args.limit else config.plans()
    print(f"{config.experiment_name}: avoidance layer, {len(plans)} run(s), no model calls, cost USD 0")
    if args.plan:
        for plan in plans:
            print(f"  {plan.run_id}  (seed {plan.seed})")
        return 0
    result = run_avoidance_experiment(config, out_root=args.out, limit=args.limit, overwrite=args.overwrite)
    print(f"done: {len(result.executed)} run(s) executed, {len(result.skipped)} skipped, cost USD 0")
    print(f"logs: {result.experiment_dir}")
    print(f"summary: {result.summary_path}")
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("config", help="experiment config, e.g. configs/experiments/c1_smoke.yaml")
    parser.add_argument("--client", choices=("mock", "deepseek"), help="override the config's llm.client")
    parser.add_argument("--out", type=Path, help="output root (default: runs/, or runs_mock/ for the mock client)")
    parser.add_argument("--limit", type=int, help="run only the first N runs of the design")
    parser.add_argument("--overwrite", action="store_true", help="redo runs that already have an outcome")
    parser.add_argument("--plan", action="store_true", help="list the runs and the worst-case cost, then stop")
    args = parser.parse_args(argv)

    try:
        if is_avoidance_config(load_yaml(resolve_path(args.config))):
            return run_avoidance(args)

        config = ExperimentConfig.load(args.config)
        plans = config.plans()[: args.limit] if args.limit else config.plans()
        client_name = args.client or config.llm["client"]

        print(f"{config.experiment_name}: condition {config.condition}, {len(plans)} run(s)")
        if config.negotiation["enabled"]:
            print(
                f"  client {client_name}, model {config.llm['model']}, temperature {config.llm['temperature']}, "
                f"template {config.negotiation['template']}, timing {config.negotiation['timing']['mode']}"
            )
        if args.plan:
            for plan in plans:
                print(f"  {plan.run_id}  (seed {plan.seed})")
            if config.negotiation["enabled"]:
                bound = worst_case_cost(config, plans, sends_per_call=3)
                print(
                    f"  worst-case cost with the deepseek client: USD {bound:.4f} "
                    f"(cap USD {config.budget['cap_usd']:.2f}); a typical run costs a small fraction of this"
                )
            return 0

        client = make_client(config, args.client)
        result = run_experiment(config, client=client, out_root=args.out, limit=args.limit, overwrite=args.overwrite)
    except (ConfigError, LLMError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(
        f"done: {len(result.executed)} run(s) executed, {len(result.skipped)} skipped, "
        f"estimated cost of this invocation USD {result.cost_usd:.6f}"
    )
    print(f"logs: {result.experiment_dir}")
    print(f"summary: {result.summary_path}")
    if result.aborted:
        print(f"stopped early: {result.aborted}", file=sys.stderr)
        return 3
    return 0
