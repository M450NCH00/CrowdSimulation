"""Writes the files of one run, and the per-experiment summary."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from .schema import (
    AVOIDANCE_SUMMARY_COLUMNS,
    AVOIDANCE_TRAJECTORY_COLUMNS,
    CONFIG_FILE,
    CONVERSATION_FILE,
    EVENTS_FILE,
    INTERACTIONS_FILE,
    OUTCOME_FILE,
    PAIR_INTERACTIONS_FILE,
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


def _write_jsonl(path: Path, records: Iterable[Mapping[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def _write_csv(path: Path, columns: Sequence[str], rows: Iterable[Mapping[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(columns)
        for row in rows:
            writer.writerow([_cell(row.get(column)) for column in columns])


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
    """One instance per negotiation run. ``conversation.jsonl`` is appended to as the turns
    happen, so a run that is interrupted still leaves every completed turn on disk."""

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
        _write_csv(self.run_dir / TRAJECTORY_FILE, TRAJECTORY_COLUMNS, rows)

    def write_outcome(self, outcome: Mapping[str, Any]) -> None:
        _write_json(self.run_dir / OUTCOME_FILE, outcome)

    def write_transcript(self, text: str) -> None:
        (self.run_dir / TRANSCRIPT_FILE).write_text(text, encoding="utf-8", newline="\n")


class AvoidanceRunLogger:
    """One instance per avoidance run. Such a run makes no model call and cannot be
    interrupted half-way through a paid turn, so everything is written at the end."""

    def __init__(self, run_dir: Path | str):
        self.run_dir = Path(run_dir)
        self.run_dir.mkdir(parents=True, exist_ok=True)

    def write_config(self, config: Mapping[str, Any]) -> None:
        _write_json(self.run_dir / CONFIG_FILE, config)

    def write_trajectory(self, rows: Iterable[Mapping[str, Any]]) -> None:
        _write_csv(self.run_dir / TRAJECTORY_FILE, AVOIDANCE_TRAJECTORY_COLUMNS, rows)

    def write_interactions(self, interactions: Iterable[Mapping[str, Any]]) -> None:
        _write_jsonl(self.run_dir / INTERACTIONS_FILE, interactions)

    def write_pair_interactions(self, pairs: Iterable[Mapping[str, Any]]) -> None:
        _write_jsonl(self.run_dir / PAIR_INTERACTIONS_FILE, pairs)

    def write_events(self, events: Iterable[Mapping[str, Any]]) -> None:
        _write_jsonl(self.run_dir / EVENTS_FILE, events)

    def write_outcome(self, outcome: Mapping[str, Any]) -> None:
        _write_json(self.run_dir / OUTCOME_FILE, outcome)


def write_summary(experiment_dir: Path | str, rows: Sequence[Mapping[str, Any]]) -> Path:
    """Write ``summary.csv`` of a negotiation experiment, one row per run, in the order given."""
    path = Path(experiment_dir) / SUMMARY_FILE
    _write_csv(path, SUMMARY_COLUMNS, rows)
    return path


def write_avoidance_summary(experiment_dir: Path | str, rows: Sequence[Mapping[str, Any]]) -> Path:
    """Write ``summary.csv`` of an avoidance experiment, one row per run, in the order given."""
    path = Path(experiment_dir) / SUMMARY_FILE
    _write_csv(path, AVOIDANCE_SUMMARY_COLUMNS, rows)
    return path
