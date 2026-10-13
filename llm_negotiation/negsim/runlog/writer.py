"""Writes the files of one run, and the per-experiment summary."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from .schema import (
    CONFIG_FILE,
    CONVERSATION_FILE,
    OUTCOME_FILE,
    SUMMARY_COLUMNS,
    SUMMARY_FILE,
    TRAJECTORY_COLUMNS,
    TRAJECTORY_FILE,
    TRANSCRIPT_FILE,
)


def _write_json(path: Path, data: Mapping[str, Any]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def _cell(value: Any) -> Any:
    """CSV cell: empty for None, lower-case words for booleans, short decimals for floats."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        return f"{value:.6g}"
    return value


class RunLogger:
    """One instance per run. ``conversation.jsonl`` is appended to as the turns happen,
    so a run that is interrupted still leaves every completed turn on disk."""

    def __init__(self, run_dir: Path | str):
        self.run_dir = Path(run_dir)
        self.run_dir.mkdir(parents=True, exist_ok=True)
        # Start every run with an empty conversation file: a run without negotiation
        # still has one, it is simply empty.
        (self.run_dir / CONVERSATION_FILE).write_text("", encoding="utf-8")

    def write_config(self, config: Mapping[str, Any]) -> None:
        _write_json(self.run_dir / CONFIG_FILE, config)

    def append_turn(self, turn: Mapping[str, Any]) -> None:
        with (self.run_dir / CONVERSATION_FILE).open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(turn, ensure_ascii=False) + "\n")

    def write_trajectory(self, rows: Iterable[Mapping[str, Any]]) -> None:
        with (self.run_dir / TRAJECTORY_FILE).open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(TRAJECTORY_COLUMNS)
            for row in rows:
                writer.writerow([_cell(row.get(column)) for column in TRAJECTORY_COLUMNS])

    def write_outcome(self, outcome: Mapping[str, Any]) -> None:
        _write_json(self.run_dir / OUTCOME_FILE, outcome)

    def write_transcript(self, text: str) -> None:
        (self.run_dir / TRANSCRIPT_FILE).write_text(text, encoding="utf-8", newline="\n")


def write_summary(experiment_dir: Path | str, rows: Sequence[Mapping[str, Any]]) -> Path:
    """Write ``summary.csv`` with one row per run, in the order given."""
    path = Path(experiment_dir) / SUMMARY_FILE
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(SUMMARY_COLUMNS)
        for row in rows:
            writer.writerow([_cell(row.get(column)) for column in SUMMARY_COLUMNS])
    return path
