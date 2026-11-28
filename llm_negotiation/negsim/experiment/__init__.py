"""Experiments: config and design expansion, the single-run loop, and the batch runner.

(Not in the issue's suggested layout: the run loop has to live somewhere importable so
that the tests can drive it, and ``run_experiment.py`` stays a thin command-line wrapper.)

There are two kinds of experiment. A negotiation experiment (issue #24) is read by
``config``, run by ``runner`` and ``batch``. An avoidance experiment (issue #26), marked by
``layer: avoidance`` in its config, is read and run by ``avoidance``.
"""

from .avoidance import (
    LAYER_AVOIDANCE,
    AvoidanceExperiment,
    AvoidanceExperimentResult,
    AvoidanceRunPlan,
    avoidance_summary_row,
    execute_avoidance_run,
    is_avoidance_config,
    run_avoidance_experiment,
)
from .batch import (
    MOCK_RUNS_DIR,
    RUNS_DIR,
    ExperimentResult,
    git_state,
    make_client,
    run_experiment,
    summary_row,
    worst_case_cost,
)
from .config import CONDITIONS, ExperimentConfig, RunPlan, SlotSpec, TaskTable
from .runner import RunAborted, execute_run

__all__ = [
    "CONDITIONS",
    "LAYER_AVOIDANCE",
    "MOCK_RUNS_DIR",
    "RUNS_DIR",
    "AvoidanceExperiment",
    "AvoidanceExperimentResult",
    "AvoidanceRunPlan",
    "ExperimentConfig",
    "ExperimentResult",
    "RunAborted",
    "RunPlan",
    "SlotSpec",
    "TaskTable",
    "avoidance_summary_row",
    "execute_avoidance_run",
    "execute_run",
    "git_state",
    "is_avoidance_config",
    "make_client",
    "run_avoidance_experiment",
    "run_experiment",
    "summary_row",
    "worst_case_cost",
]
