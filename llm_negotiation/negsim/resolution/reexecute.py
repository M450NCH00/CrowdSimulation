"""An experiment's sessions carried out again under another execution (issue #101; the user's
decision of 2026-10-25), with no LLM call.

A session's plans are recorded (D13), and its replays are rebuilt from the record alone
(``negsim.resolution.replay``). When **every decision point came at the encounter's trigger**,
before any plan had moved anyone, nothing an agent was told depended on how plans are carried out;
so the same plans can be replayed under another ``protocol.execution`` and the result is exactly
what that execution would have made of them. In the independent condition of a two-person case
this holds (one decision point per agent, both at the trigger). A session where it does not hold
is refused: its later decisions saw a world the other execution would have changed.

It writes a new experiment folder beside the source:

- ``sessions/``: each record copied, with ``protocol.execution`` set and ``reexecuted_from`` naming
  the source; nothing else changed (prompts, replies, tokens and cost are the source's);
- ``replay/``: both replays rebuilt under the new execution, and plain ORCA;
- ``outcomes.csv`` and ``outcomes.jsonl``, built as the source's were; ``design.jsonl`` filtered;
- ``config.json``: the source's, its ``experiment_name`` changed and a ``reexecution`` block
  added; and ``NOTE.md``.

    python -m negsim.resolution.reexecute runs/rf29_round1_head_on_sidestep --execution keep_line
        [--condition independent] [--out runs] [--name NAME]
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

from ..configutil import ConfigError, resolve_path
from ..rulegen.cases import CaseStore
from .execute import EXECUTIONS
from .experiment import (
    CONFIG_FILE, DESIGN_FILE, OUTCOMES_CSV, OUTCOMES_JSONL, SESSIONS_DIR, outcome_row, outcomes_csv, replay_record,
)
from .protocol import SESSION_COMPLETED

NOTE_FILE = "NOTE.md"
_EPS = 1e-9


class ReexecuteError(ValueError):
    """A source that cannot be carried out again exactly."""


def decided_at_trigger(record: Mapping[str, Any]) -> bool:
    """Whether every decision point of the session came at its encounter's trigger."""
    trigger = ((record.get("encounter") or {}).get("trigger") or {}).get("time_s")
    points = record.get("decision_points") or []
    return trigger is not None and all(point["time_s"] <= trigger + _EPS for point in points)


def reexecuted(record: Mapping[str, Any], execution: str, source: str, orca_within_groups: bool = False) -> dict[str, Any]:
    """The record with ``protocol.execution`` set (and, issue #110, ``orca_within_groups`` switched
    on), and where it came from."""
    out = copy.deepcopy(dict(record))
    was = (out.get("protocol") or {}).get("execution", "rf4")
    out.setdefault("protocol", {})["execution"] = execution
    out["reexecuted_from"] = {"experiment": source, "execution": was}
    if orca_within_groups:  # only when asked, so that every earlier re-execution is written as before
        out["reexecuted_from"]["orca_within_groups"] = bool(out["protocol"].get("orca_within_groups", False))
        out["protocol"]["orca_within_groups"] = True
    return out


def reexecute(
    source: Path, execution: str, out_root: Path, name: Optional[str] = None, condition: Optional[str] = None,
    git: Optional[Mapping[str, Any]] = None, orca_within_groups: bool = False,
) -> Path:
    """Carry out ``source``'s sessions (of ``condition``, if given) again under ``execution`` (and,
    issue #110, with ``protocol.orca_within_groups`` on, if asked)."""
    if execution not in EXECUTIONS:
        raise ConfigError(f"execution: one of {EXECUTIONS}, got {execution!r}")
    source = Path(source)
    config = json.loads((source / CONFIG_FILE).read_text(encoding="utf-8"))
    experiment = config["experiment"]
    name = name or f"{experiment['experiment_name']}_{execution}"
    target = Path(out_root) / name
    if (target / SESSIONS_DIR).is_dir() and any((target / SESSIONS_DIR).glob("*.json")):
        raise ReexecuteError(f"{target} already holds sessions; give another --name or --out")
    paths = sorted(p for p in (source / SESSIONS_DIR).glob("*.json") if ".aborted" not in p.name)
    records = [json.loads(p.read_text(encoding="utf-8")) for p in paths]
    records = [r for r in records if condition is None or r["condition"] == condition]
    if not records:
        raise ReexecuteError(f"{source}: no session" + (f" of condition {condition}" if condition else ""))
    late = [r["session_id"] for r in records if r["outcome"] == SESSION_COMPLETED and not decided_at_trigger(r)]
    if late:
        raise ReexecuteError(
            f"{len(late)} session(s) had a decision point after the trigger, so another execution would have changed "
            f"what they were told (for example {late[0]}); only sessions decided at the trigger can be carried out again"
        )
    store = CaseStore(resolve_path(experiment.get("cases", {}).get("store", "cases")))
    git = git or config.get("git") or {}
    (target / SESSIONS_DIR).mkdir(parents=True, exist_ok=True)
    rows = []
    for record in records:
        again = reexecuted(record, execution, experiment["experiment_name"], orca_within_groups)
        (target / SESSIONS_DIR / f"{record['session_id']}.json").write_text(
            json.dumps(again, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n"
        )
        case = store.get(record["case"]["case_id"], record["case"]["version"])
        physical = replay_record(again, target, name, git, store) if record["outcome"] == SESSION_COMPLETED else None
        rows.append(outcome_row(again, case, physical))
    ids = {record["session_id"] for record in records}
    design = [line for line in (source / DESIGN_FILE).read_text(encoding="utf-8").splitlines()
              if line.strip() and json.loads(line)["session_id"] in ids]
    (target / DESIGN_FILE).write_text("\n".join(design) + "\n", encoding="utf-8", newline="\n")
    with (target / OUTCOMES_JSONL).open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    (target / OUTCOMES_CSV).write_text(outcomes_csv(rows), encoding="utf-8", newline="\n")
    when = datetime.now(timezone.utc).isoformat(timespec="seconds")
    new_config = copy.deepcopy(config)
    new_config["experiment"]["experiment_name"] = name
    new_config["reexecution"] = {
        "source": experiment["experiment_name"], "source_folder": str(source), "execution": execution,
        "condition": condition, "sessions": len(records), "created_utc": when,
        **({"orca_within_groups": True} if orca_within_groups else {}),
    }
    (target / CONFIG_FILE).write_text(json.dumps(new_config, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    (target / NOTE_FILE).write_text(
        f"# {name}\n\n{experiment['experiment_name']}'s "
        + (f"{condition} " if condition else "")
        + f"sessions ({len(records)}), carried out again under `protocol.execution: {execution}`"
        + (" and `protocol.orca_within_groups: true` (issue #110)" if orca_within_groups else "")
        + " with no LLM call "
        "(`python -m negsim.resolution.reexecute`, issue #101). Every decision point came at the encounter's trigger, so "
        "the plans and everything the agents were told are the source's; only how the plans were carried out differs. "
        "Prompts, replies, tokens and cost in `sessions/` are the source's, not new spending.\n",
        encoding="utf-8", newline="\n",
    )
    return target


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m negsim.resolution.reexecute", description=__doc__.split("\n\n")[0])
    parser.add_argument("source", type=Path, help="the experiment folder to carry out again")
    parser.add_argument("--execution", required=True, choices=EXECUTIONS)
    parser.add_argument("--condition", help="only the sessions of this condition")
    parser.add_argument("--out", type=Path, help="where to put the new experiment folder (default: beside the source)")
    parser.add_argument("--name", help="the new experiment's name (default: <source name>_<execution>)")
    parser.add_argument("--orca-within-groups", action="store_true", help="also switch on protocol.orca_within_groups (issue #110)")
    args = parser.parse_args(argv)
    try:
        target = reexecute(
            args.source, args.execution, args.out or args.source.parent, args.name, args.condition, orca_within_groups=args.orca_within_groups,
        )
    except (ReexecuteError, ConfigError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"written: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
