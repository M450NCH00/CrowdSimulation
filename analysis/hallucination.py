"""Hallucinated decisions (issue #134, RF-45; the supervisor's point 6, SV12): the share of
replies that rest on something not in the agent's input, or choose something not possible.

**The definition, agreed with the user on 2026-11-25 before anything was counted**
(``WORK_LOG-134.md``). A decision point is flagged in a category when its reply:

1. **misperceived the other**: says the other did something (signalled, spoke, stopped, slowed,
   moved aside) or has a trait (cane, suitcase, phone, older age) that the view does not show,
   or puts them on the wrong side. Misreading the side of a heard message is tagged
   ``misread_heard_side`` (RF-40's E3);
2. **misremembered itself**: says it already moved to a side, is on a side, signalled or spoke,
   when the history its prompt repeats (or the wall distances) say otherwise;
3. **says one thing, plans another**: RF-8's intent-against-plan mismatch (``analysis.intent``);
4. **says a side it does not take**: RF-40's coding of a message against the speaker's own move
   (``analysis.turn_taking.words_match_move``);
5. **not an available action**: the reply is unreadable after the retry (``parse_error``);
6. **made-up source**: not recounted here; RF-14's count is quoted in the report;
7. **misstated the setting**: says there is no room, or that a wall is right beside it, when the
   widths and wall distances given say otherwise (added by the user from RF-44).

The **headline share** is the decision points flagged in 1, 2, 5 or 7, of all decision points.
3 and 4 are reported beside it as **self-contradiction**. Every category is also reported alone.

**The input** is that decision point's prompt only: each call is fresh, and the model sees no
earlier prompt except the history lines this one repeats. A claim is supported when the view's
structured fields show it (``seen``: signal, motion, changes, factor lines, age, bearing;
``heard``; ``history``; ``place``; ``me``).

**How claims are found:** the keyword codebook ``codebooks/hallucination_v1.json`` (frozen; a
change is ``_v2``) on the reply's reason and intent (and its message, where a rule says so). A
match preceded in its sentence by a hedge or negation ("if he waves", "he didn't stop") is
skipped. The patterns are the assistant's coding choices: their precision and recall come from
the hand check (``hand_check_judgements.json``), reported beside every share.

    python -m analysis.hallucination llm_negotiation/runs/rf39_round1_head_on_sidestep_reprompt \\
        llm_negotiation/runs/rf40_round1_head_on_turn_taking --out llm_negotiation/runs/rf45_hallucination
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import re
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional, Sequence

from .intent import OTHER as INTENT_OTHER
from .intent import code_intent, code_plan, load_codebook as load_intent_codebook
from .sidestep_reprompt import WALLS, fisher_exact
from .turn_taking import OTHER_SIDE, OWN, YOURS, frame_of, words_match_move

CODEBOOKS = Path(__file__).resolve().parent / "codebooks"
CODEBOOK = "hallucination_v1"
HEADLINE = ("1", "2", "5", "7")
CONTRADICTION = ("3", "4")
CATEGORIES = ("1", "2", "3", "4", "5", "7")
SIDES = ("left", "right")
TRAIT_WORDS = {"cane": "cane", "suitcase": "suitcase", "phone": "phone"}
SIGNAL_WORDS = {"waved": "wave_on", "nodded": "nod", "made eye contact": "eye_contact",
                "held up my hand": "hold_up_hand", "raised my hand": "hold_up_hand"}
PASSAGE = re.compile(r"passage ([\d.]+) m wide")
SENTENCE_END = re.compile(r"[.!?;]\s")


@lru_cache(maxsize=None)
def load_codebook(name: str = CODEBOOK) -> dict[str, Any]:
    """The codebook with every pattern compiled (``{other}`` and ``{link}`` filled in)."""
    data = json.loads((CODEBOOKS / f"{name}.json").read_text(encoding="utf-8"))
    compiled = {}
    for number, category in data["categories"].items():
        for rule_name, rule in category["rules"].items():
            if "patterns" not in rule:
                continue
            patterns = [re.compile(p.replace("{other}", data["other"]).replace("{link}", data["link"]), re.IGNORECASE)
                        for p in rule["patterns"]]
            compiled[(number, rule_name)] = {**rule, "compiled": patterns}
    data["compiled"] = compiled
    data["skip"] = re.compile(data["skip_before"], re.IGNORECASE)
    return data


def wilson(k: int, n: int, z: float = 1.959964) -> tuple[Optional[float], Optional[float]]:
    """The Wilson score interval of k in n (None when n is 0)."""
    if n == 0:
        return (None, None)
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (max(0.0, centre - half), min(1.0, centre + half))


# --- one decision point -------------------------------------------------------------------------

def _sentence_before(text: str, start: int) -> str:
    """The part of the claim's sentence before the claim."""
    head = text[:start]
    ends = [m.end() for m in SENTENCE_END.finditer(head)]
    return head[ends[-1]:] if ends else head


def claims(text: str, patterns: Iterable[re.Pattern], skip: re.Pattern) -> list[re.Match]:
    """Every match that is a claim: not preceded in its sentence by a hedge or a negation."""
    found = []
    for pattern in patterns:
        for match in pattern.finditer(text or ""):
            if not skip.search(_sentence_before(text, match.start())):
                found.append(match)
    return found


def _side_of(match: re.Match) -> Optional[str]:
    side = match.groupdict().get("side")
    return side.lower() if side else None


def _bearing_side(seen: Mapping[str, Any], ahead_deg: float) -> Optional[str]:
    """Where the description puts the other: ``left``, ``right`` or None (straight ahead)."""
    bearing = seen.get("bearing_rad")
    if bearing is None or abs(math.degrees(bearing)) <= ahead_deg:
        return None
    return "left" if bearing > 0 else "right"


def _walls(place: Sequence[str]) -> tuple[Optional[float], Optional[float], Optional[float]]:
    """The passage width and the distances to the left and right walls (from the body's centre)."""
    width = left = right = None
    for line in place or []:
        found = WALLS.search(line)
        if found:
            left, right = float(found.group(1)), float(found.group(2))
        found = PASSAGE.search(line)
        if found:
            width = float(found.group(1))
    return width, left, right


def heard_expected_side(heard: Sequence[Mapping[str, Any]]) -> Optional[str]:
    """For the last heard message naming one side: that side as the listener should restate it in
    its own frame ("your right" stays right; "I'll keep left", facing, is the listener's right)."""
    for entry in reversed(list(heard or [])):
        message = entry.get("message") or ""
        frame = frame_of(message)
        if frame == "yours":
            sides = {m.group(1).lower() for m in YOURS.finditer(message)}
            if len(sides) == 1:
                return sides.pop()
        elif frame == "own":
            sides = {(m.group(1) or m.group(2)).lower() for m in OWN.finditer(message)}
            if len(sides) == 1 and entry.get("frame") in (None, "facing"):
                return OTHER_SIDE[sides.pop()]
    return None


def check_needs(needs: Mapping[str, Any], match: re.Match, text: str, point: Mapping[str, Any],
                thresholds: Mapping[str, float]) -> tuple[bool, str]:
    """Whether the view supports the claim, and the evidence for the record."""
    view = point["view"]
    seen = view.get("seen") or []
    (key, value), = needs.items()
    if key == "signal":
        shown = sorted({s.get("signal") or "none" for s in seen})
        return value in shown, f"signals shown: {shown}"
    if key == "heard":
        return bool(view.get("heard")), f"heard: {len(view.get('heard') or [])} message(s)"
    if key == "motion":
        shown = sorted({s.get("motion") or "" for s in seen})
        return value in shown, f"motion shown: {shown}"
    if key == "change":
        shown = sorted({c for s in seen for c in s.get("changes") or []})
        return value in shown, f"changes shown: {shown}"
    if key == "lateral":
        changes = {c for s in seen for c in s.get("changes") or []}
        if value == "any":
            moved = changes & {"moved_left", "moved_right", "turned"}
            return bool(moved), f"changes shown: {sorted(changes)}"
        side = _side_of(match)
        whose = (match.groupdict().get("whose") or "my").lower()
        mine = side if whose == "my" else OTHER_SIDE[side]  # facing: their left is my right
        positions = {_bearing_side(s, thresholds["straight_ahead_deg"]) for s in seen}
        ok = f"moved_{mine}" in changes or mine in positions
        return ok, f"claimed: to my {mine}; changes shown: {sorted(changes)}; position: {sorted(p or 'ahead' for p in positions)}"
    if key == "position":
        side = _side_of(match)
        positions = {_bearing_side(s, thresholds["straight_ahead_deg"]) for s in seen}
        wrong = OTHER_SIDE[side] in positions and side not in positions
        return not wrong, f"claimed: on my {side}; position: {sorted(p or 'ahead' for p in positions)}"
    if key == "trait":
        lines = [line for s in seen for line in s.get("factor_lines") or []]
        return any(TRAIT_WORDS[value] in line.lower() for line in lines), f"trait lines: {len(lines)}"
    if key == "older":
        ages = [s.get("age") for s in seen if s.get("age") is not None]
        return any(a >= thresholds["older_age"] for a in ages), f"ages shown: {ages}"
    if key == "heard_side":
        expected = heard_expected_side(view.get("heard") or [])
        if expected is None:
            return True, "no heard message naming one side: not checkable"
        side = _side_of(match)
        return side == expected, f"restated: my {side}; the heard message puts it on my {expected}"
    if key == "history_side":
        side = _side_of(match)
        history = view.get("history") or []
        moved = [h.get("sideways_m") or 0.0 for h in history]
        sign = 1 if side == "left" else -1  # sideways_m: positive is to the left
        ok = any(sign * m >= thresholds["lateral_m"] for m in moved)
        return ok, f"claimed: moved {side}; history sideways_m: {[round(m, 2) for m in moved]}"
    if key == "own_position":
        side = _side_of(match)
        _, left, right = _walls(view.get("place") or [])
        if left is None:
            return True, "walls not given"
        near, far = (left, right) if side == "left" else (right, left)
        return near <= far + thresholds["position_margin_m"], f"claimed: on my {side}; walls left {left}, right {right}"
    if key == "history_signal":
        said = match.groupdict().get("signal", "").lower()
        wanted = SIGNAL_WORDS.get(said)
        given = sorted({h.get("signal") or "none" for h in view.get("history") or []})
        return wanted in given, f"claimed: {said}; own earlier signals: {given}"
    if key == "history_message":
        given = [h.get("message") for h in view.get("history") or [] if h.get("message")]
        return bool(given), f"own earlier messages: {len(given)}"
    if key == "room":
        width, left, right = _walls(view.get("place") or [])
        me = (view.get("me") or {}).get("width_m") or 0.5
        other = max([s.get("width_m") or 0.5 for s in seen] or [0.5])
        margin = thresholds["room_margin_m"]
        sentence = text[match.start():]
        sentence = sentence[:SENTENCE_END.search(sentence).start()] if SENTENCE_END.search(sentence) else sentence
        side = re.search(r"\b(?:on|to|at) (?:my|the) (left|right)\b", _sentence_before(text, match.start()) + sentence, re.IGNORECASE)
        if side and left is not None:
            wall = left if side.group(1).lower() == "left" else right
            gap = wall - me / 2
            return gap < other + margin, f"claimed: no room on my {side.group(1).lower()}; gap {gap:.2f} m, other {other} m wide"
        if width is None:
            return True, "passage width not given"
        return width < me + other + margin, f"claimed: no room; passage {width} m, bodies {me} + {other} m"
    if key == "wall":
        _, left, right = _walls(view.get("place") or [])
        me = (view.get("me") or {}).get("width_m") or 0.5
        if left is None:
            return True, "walls not given"
        side = _side_of(match)
        gaps = {"left": left - me / 2, "right": right - me / 2}
        gap = gaps[side] if side else min(gaps.values())
        return gap <= thresholds["wall_close_m"], f"claimed: wall beside me; gaps to walls {gaps['left']:.2f} / {gaps['right']:.2f} m"
    raise ValueError(f"unknown need: {key}")


def check_point(point: Mapping[str, Any], codebook: Mapping[str, Any], intent_codebook: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Every flag for one decision point (category, rule, tag, claim, evidence)."""
    flags = []
    if not point["readable"]:
        return [{"category": "5", "rule": "unreadable", "tag": None, "claim": "", "evidence": str(point.get("parse_error"))}]
    thresholds = codebook["thresholds"]
    for (number, rule_name), rule in codebook["compiled"].items():
        for field in rule["text"]:
            text = point["texts"].get(field) or ""
            for match in claims(text, rule["compiled"], codebook["skip"]):
                ok, evidence = check_needs(rule["needs"], match, text, point, thresholds)
                if not ok:
                    flags.append({"category": number, "rule": rule_name, "tag": rule.get("tag"),
                                  "claim": f"{field}: …{match.group(0)}…", "evidence": evidence})
    said, said_side = code_intent(point["texts"].get("intent"), intent_codebook)
    if said != {INTENT_OTHER}:
        done, done_side = code_plan(point["coded"])
        missing = sorted(said - done)
        wrong_side = said_side is not None and done_side not in (said_side, "both")
        if missing or wrong_side:
            why = [f"intent says {name}, the plan does not" for name in missing]
            if wrong_side:
                why.append(f"intent says {said_side}, the plan turns {done_side}")
            flags.append({"category": "3", "rule": "intent_against_plan", "tag": None, "claim": point["texts"].get("intent"),
                          "evidence": "; ".join(why)})
    spoken = words_match_move(point["texts"].get("message") or "", (point["coded"] or {}).get("side"))
    if spoken is not None and not spoken[1]:
        flags.append({"category": "4", "rule": spoken[0], "tag": None, "claim": point["texts"].get("message"),
                      "evidence": f"own move: {(point['coded'] or {}).get('side')}"})
    return _one_per_rule(flags)


def _one_per_rule(flags: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen, out = set(), []
    for flag in flags:
        key = (flag["category"], flag["rule"])
        if key not in seen:
            seen.add(key)
            out.append(flag)
    return out


def checkable(point: Mapping[str, Any], intent_codebook: Mapping[str, Any]) -> dict[str, bool]:
    """Which categories could be judged at this point (each category's denominator)."""
    readable = point["readable"]
    said = code_intent(point["texts"].get("intent"), intent_codebook)[0] if readable else None
    spoken = words_match_move(point["texts"].get("message") or "", (point["coded"] or {}).get("side")) if readable else None
    return {"1": readable, "2": readable, "7": readable, "5": True,
            "3": readable and said != {INTENT_OTHER}, "4": spoken is not None}


# --- runs ---------------------------------------------------------------------------------------

def load(experiment: Path) -> list[dict[str, Any]]:
    """Every decision point of every session record in the run, with its session's outcome."""
    outcomes = {}
    with (experiment / "outcomes.csv").open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            outcomes[row["session_id"]] = row
    points = []
    for path in sorted((experiment / "sessions").glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        row = outcomes.get(record["session_id"], {})
        for point in record.get("decision_points") or []:
            parsed = point.get("parsed") or {}
            readable = not point.get("parse_error") and bool(parsed)
            points.append({
                "run": experiment.name, "session_id": record["session_id"],
                "condition": record.get("condition") or row.get("condition"),
                "outcome": row.get("outcome"), "resolved": row.get("resolved_plan_only") == "True",
                "pair_id": row.get("pair_id") or None,
                "agent_id": point["agent_id"], "number": point["number"], "index": point["index"],
                "readable": readable, "parse_error": point.get("parse_error"),
                "texts": {"intent": parsed.get("intent") or "", "reason": parsed.get("reason") or "",
                          "message": parsed.get("message") or ""},
                "signal": parsed.get("signal"), "coded": point.get("coded") or {}, "view": point.get("view") or {},
            })
    return points


def key_of(point: Mapping[str, Any]) -> str:
    return f"{point['run']}/{point['session_id']}/dp{point['index']}"


def analyse(points: Sequence[dict[str, Any]], codebook_name: str = CODEBOOK) -> list[dict[str, Any]]:
    codebook, intent_codebook = load_codebook(codebook_name), load_intent_codebook()
    for point in points:
        point["flags"] = check_point(point, codebook, intent_codebook)
        point["checkable"] = checkable(point, intent_codebook)
        point["key"] = key_of(point)
    return list(points)


def _rate(k: int, n: int) -> dict[str, Any]:
    low, high = wilson(k, n)
    return {"k": k, "n": n, "rate": (k / n) if n else None, "ci": [low, high]}


def _flagged(point: Mapping[str, Any], categories: Sequence[str]) -> bool:
    return any(f["category"] in categories for f in point["flags"])


def shares(points: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Per category, the headline and self-contradiction, and the rule and tag counts."""
    out = {"decision_points": len(points), "readable": sum(p["readable"] for p in points)}
    for number in CATEGORIES:
        judged = [p for p in points if p["checkable"][number]]
        out[f"category_{number}"] = _rate(sum(_flagged(p, (number,)) for p in judged), len(judged))
    out["headline"] = _rate(sum(_flagged(p, HEADLINE) for p in points), len(points))
    readable = [p for p in points if p["readable"]]
    out["self_contradiction"] = _rate(sum(_flagged(p, CONTRADICTION) for p in readable), len(readable))
    out["rules"] = dict(sorted(Counter(f"{f['category']}:{f['rule']}" for p in points for f in p["flags"]).items()))
    out["tags"] = dict(Counter(f["tag"] for p in points for f in p["flags"] if f["tag"]))
    return out


def summarise(points: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Per run: in all, by condition, by decision number; and flagged sessions against resolved."""
    summary = {}
    for run in sorted({p["run"] for p in points}):
        mine = [p for p in points if p["run"] == run]
        by_condition = {c: shares([p for p in mine if p["condition"] == c]) for c in sorted({p["condition"] for p in mine})}
        by_number = {str(n): shares([p for p in mine if p["number"] == n]) for n in sorted({p["number"] for p in mine})}
        sessions = defaultdict(lambda: {"flagged": False, "resolved": False, "completed": False})
        for p in mine:
            if p["pair_id"]:
                continue
            s = sessions[p["session_id"]]
            s["flagged"] |= _flagged(p, HEADLINE)
            s["resolved"] = p["resolved"]
            s["completed"] = p["outcome"] == "completed"
        done = [s for s in sessions.values() if s["completed"]]
        a = sum(s["flagged"] and s["resolved"] for s in done)
        b = sum(s["flagged"] and not s["resolved"] for s in done)
        c = sum(not s["flagged"] and s["resolved"] for s in done)
        d = sum(not s["flagged"] and not s["resolved"] for s in done)
        summary[run] = {"all": shares(mine), "by_condition": by_condition, "by_decision_number": by_number,
                        "sessions_vs_resolved": {"flagged_resolved": a, "flagged_not": b, "clean_resolved": c, "clean_not": d,
                                                 "fisher_p": fisher_exact(a, b, c, d)}}
    return summary


# --- the hand check -----------------------------------------------------------------------------

def hand_check_sample(points: Sequence[Mapping[str, Any]], n: int = 150, seed: int = 134, small: int = 30) -> dict[str, list[str]]:
    """A seeded random sample of ``n`` decision points, and every flag of any rule with fewer than
    ``small`` flags in all."""
    rng = random.Random(seed)
    keys = sorted(p["key"] for p in points)
    sample = sorted(rng.sample(keys, min(n, len(keys))))
    per_rule = Counter(f"{f['category']}:{f['rule']}" for p in points for f in p["flags"])
    rare = sorted({p["key"] for p in points for f in p["flags"]
                   if per_rule[f"{f['category']}:{f['rule']}"] < small and p["key"] not in sample})
    return {"sample": sample, "small_rules": rare}


def _facts(point: Mapping[str, Any]) -> list[str]:
    view = point["view"]
    lines = []
    for s in view.get("seen") or []:
        lines.append(f"seen: {math.degrees(s.get('bearing_rad') or 0):+.0f}° (+ left), {s.get('distance_m', 0):.1f} m, "
                     f"{s.get('motion')}, signal {s.get('signal')}, changes {s.get('changes')}, age {s.get('age')}, "
                     f"width {s.get('width_m')}, traits {[l for l in s.get('factor_lines') or [] if 'look ' not in l]}")
    if not view.get("seen"):
        lines.append("seen: nobody")
    for h in view.get("heard") or []:
        lines.append(f"heard: \"{h.get('message')}\" (frame {h.get('frame')})")
    for h in view.get("history") or []:
        lines.append(f"history: {h.get('ago_s', 0):.1f} s ago \"{h.get('intent')}\", signal {h.get('signal')}, "
                     f"message \"{h.get('message')}\", sideways {h.get('sideways_m', 0):+.2f} m (+ left)")
    lines += [f"place: {line}" for line in view.get("place") or [] if "passage" in line]
    return lines


def hand_check_sheet(points: Sequence[Mapping[str, Any]], chosen: Mapping[str, list[str]]) -> str:
    by_key = {p["key"]: p for p in points}
    out = ["# RF-45 hand check sheet (issue #134)", "",
           "Each entry: what the prompt showed (the view's fields), the reply, and the coder's flags. "
           "Judgements are in `hand_check_judgements.json`.", ""]
    for part, keys in (("Random sample", chosen["sample"]), ("Every flag of a small rule", chosen["small_rules"])):
        out += [f"## {part} ({len(keys)})", ""]
        for key in keys:
            p = by_key[key]
            out.append(f"### {key} ({p['condition']}, agent {p['agent_id']}, decision {p['number']})")
            out += [f"- {line}" for line in _facts(p)]
            if p["readable"]:
                for field in ("intent", "reason", "message"):
                    if p["texts"][field]:
                        out.append(f"- **{field}:** {p['texts'][field]}")
                out.append(f"- **signal:** {p['signal']}; **coded:** side {p['coded'].get('side')}, slowed {p['coded'].get('slowed')}, "
                           f"stopped {p['coded'].get('stopped')}, backed up {p['coded'].get('backed_up')}")
            else:
                out.append(f"- **unreadable:** {p['parse_error']}")
            flags = "; ".join(f"{f['category']}:{f['rule']} ({f['evidence']})" for f in p["flags"]) or "none"
            out += [f"- **flags:** {flags}", ""]
    return "\n".join(out) + "\n"


def score_hand_check(points: Sequence[Mapping[str, Any]], chosen: Mapping[str, list[str]],
                     judgements: Mapping[str, Any]) -> dict[str, Any]:
    """Precision per category (flags judged right, of flags judged), and recall on the random
    sample (true flags, of true flags plus misses)."""
    by_key = {p["key"]: p for p in points}
    right, judged, missed, hits = Counter(), Counter(), Counter(), Counter()
    for key, entry in judgements.items():
        point = by_key.get(key)
        if point is None:
            continue
        verdicts = entry.get("flags") or {}
        for flag in point["flags"]:
            name = f"{flag['category']}:{flag['rule']}"
            if name in verdicts:
                judged[flag["category"]] += 1
                right[flag["category"]] += bool(verdicts[name])
                if key in chosen["sample"] and verdicts[name]:
                    hits[flag["category"]] += 1
        if key in chosen["sample"]:
            for category in entry.get("missed") or []:
                missed[str(category)] += 1
    out = {}
    for number in CATEGORIES:
        out[number] = {"precision": _rate(right[number], judged[number]),
                       "recall_on_sample": _rate(hits[number], hits[number] + missed[number])}
    out["judged_points"] = len(judgements)
    return out


# --- output -------------------------------------------------------------------------------------

def _pct(rate: Mapping[str, Any]) -> str:
    if not rate["n"]:
        return "–"
    low, high = rate["ci"]
    return f"{rate['k']} / {rate['n']} ({100 * rate['rate']:.1f}%, {100 * low:.1f} to {100 * high:.1f})"


NAMES = {"1": "misperceived the other", "2": "misremembered itself", "3": "says one thing, plans another",
         "4": "says a side it does not take", "5": "not an available action (unreadable)", "7": "misstated the setting"}


def markdown(summary: Mapping[str, Any], hand: Optional[Mapping[str, Any]]) -> str:
    out = ["# Hallucinated decisions (RF-45): tables", "",
           "Written by `python -m analysis.hallucination`; codebook `hallucination_v1`. Shares are flagged decision points, "
           "with Wilson 95% intervals. The headline counts categories 1, 2, 5 and 7, of all decision points; "
           "self-contradiction counts 3 and 4, of readable ones. Each category's denominator is the decision points it can "
           "be judged on (3: an intent the RF-8 codebook can place; 4: a message stating the speaker's own side).", ""]
    for run, s in summary.items():
        a = s["all"]
        out += [f"## {run}", "", f"{a['decision_points']} decision points, {a['readable']} readable.", "",
                "| | All | " + " | ".join(s["by_condition"]) + " |", "| --- | --- | " + " | ".join("---" for _ in s["by_condition"]) + " |"]
        rows = [("**Headline (1, 2, 5, 7)**", "headline"), ("Self-contradiction (3, 4)", "self_contradiction")]
        rows += [(f"{n}. {NAMES[n]}", f"category_{n}") for n in CATEGORIES]
        for label, key in rows:
            out.append(f"| {label} | {_pct(a[key])} | " + " | ".join(_pct(c[key]) for c in s["by_condition"].values()) + " |")
        out += ["", "By decision number (headline):", "", "| Decision | Headline | 1 | 2 | 5 | 7 |", "| --- | --- | --- | --- | --- | --- |"]
        for number, c in s["by_decision_number"].items():
            out.append(f"| {number} | {_pct(c['headline'])} | " + " | ".join(_pct(c[f'category_{n}']) for n in ('1', '2', '5', '7')) + " |")
        v = s["sessions_vs_resolved"]
        out += ["", f"Design sessions with a headline flag: resolved {v['flagged_resolved']}, not {v['flagged_not']}; "
                    f"without: resolved {v['clean_resolved']}, not {v['clean_not']} (Fisher's exact p = {v['fisher_p']:.3g}; "
                    "an association, not a cause).", "",
                "Flags by rule: " + ", ".join(f"`{k}` {v}" for k, v in a["rules"].items()) + ".",
                f"Tags: {a['tags'] or 'none'}.", ""]
    if hand:
        out += ["## The hand check", "", f"{hand['judged_points']} decision points judged.", "",
                "| Category | Precision (flags judged right) | Recall on the random sample |", "| --- | --- | --- |"]
        for n in CATEGORIES:
            out.append(f"| {n}. {NAMES[n]} | {_pct(hand[n]['precision'])} | {_pct(hand[n]['recall_on_sample'])} |")
        out.append("")
    return "\n".join(out) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("experiments", nargs="+", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--sample", type=int, default=150)
    parser.add_argument("--seed", type=int, default=134)
    parser.add_argument("--judgements", type=Path, default=None,
                        help="hand-check judgements (default: <out>/hand_check_judgements.json, if it exists)")
    args = parser.parse_args(argv)
    points = analyse([p for experiment in args.experiments for p in load(experiment)])
    summary = summarise(points)
    chosen = hand_check_sample(points, args.sample, args.seed)
    args.out.mkdir(parents=True, exist_ok=True)
    judgements_path = args.judgements or args.out / "hand_check_judgements.json"
    hand = None
    if judgements_path.exists():
        hand = score_hand_check(points, chosen, json.loads(judgements_path.read_text(encoding="utf-8")))
    (args.out / "hallucination.json").write_text(json.dumps({"summary": summary, "hand_check": hand, "chosen": chosen}, indent=1),
                                                encoding="utf-8")
    (args.out / "hallucination.md").write_text(markdown(summary, hand), encoding="utf-8")
    (args.out / "hand_check_sheet.md").write_text(hand_check_sheet(points, chosen), encoding="utf-8")
    with (args.out / "flags.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["key", "condition", "agent_id", "number", "category", "rule", "tag", "claim", "evidence"])
        for p in points:
            for f in p["flags"]:
                writer.writerow([p["key"], p["condition"], p["agent_id"], p["number"], f["category"], f["rule"], f["tag"] or "",
                                 f["claim"], f["evidence"]])
    print(f"{len(points)} decision points; headline flagged: "
          + ", ".join(f"{run} {_pct(s['all']['headline'])}" for run, s in summary.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
