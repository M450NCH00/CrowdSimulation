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

(The work is done in ``negsim/experiment/cli.py``, where the tests can reach it.)
"""

from __future__ import annotations

from negsim.experiment.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
