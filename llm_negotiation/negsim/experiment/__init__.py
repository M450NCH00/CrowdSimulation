"""Experiments: config and design expansion, the single-run loop, and the batch runner.

(Not in the issue's suggested layout: the run loop has to live somewhere importable so
that the tests can drive it, and ``run_experiment.py`` stays a thin command-line wrapper.)
"""

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
    "MOCK_RUNS_DIR",
    "RUNS_DIR",
    "ExperimentConfig",
    "ExperimentResult",
    "RunAborted",
    "RunPlan",
    "SlotSpec",
    "TaskTable",
    "execute_run",
    "git_state",
    "make_client",
    "run_experiment",
    "summary_row",
    "worst_case_cost",
]
