# Token estimates for describing 2, 5 and 10 nearby people (Q6)

> For issue [#52](https://github.com/M450NCH00/CrowdSimulation/issues/52). **Offline estimates**:
> no LLM was called, paid or local. Supports [verdict.md](verdict.md). The formats compared are
> **design proposals**, not negsim templates; no file in `llm_negotiation/` was changed.

## Method

- **What is counted:** the *situation block* of a first-person prompt only: "ABOUT YOU", "WHERE YOU
  ARE" and the people. The rest of a negsim prompt (system text, glossary, output format) is the
  same whatever the format, so it is left out; real prompts are longer by that fixed amount.
- **Wording:** the lines of the `situation` block of
  `llm_negotiation/negsim/negotiation/templates/rulegen_negotiate_v2.yaml` (`self_*`, `place_*`,
  `other_*`), filled with example values at negsim's rounding (0.1 m along, 0.01 m across, 0.01 m/s,
  whole degrees). The people are generated with a fixed seed (7), so the counts are reproducible.
- **Tokenizer:** DeepSeek-V3's `tokenizer.json` from
  https://huggingface.co/deepseek-ai/DeepSeek-V3 (SHA-256 `621ac2e3…6b517fb41`), run locally with the
  Hugging Face `tokenizers` library 0.23.3, no special tokens. `[assumption]` The project's model is
  `deepseek-chat` (`pipeline/config.py`); DeepSeek does not state that the hosted model uses exactly
  this file, so treat the counts as close estimates, not billing figures.
- **Price used for the cost line:** $0.28 per million input tokens (cache miss), the
  `deepseek-chat@2025-09-v3.2` profile in `pipeline/config.py`, which says to verify current rates.

## Formats

| Format | What it does with N nearby people |
|---|---|
| **A. negsim today** | One person in full (the nearest), plus "Other people are walking around you as well." |
| **B. Prose, everyone in full** | negsim's five `other_*` lines repeated for each person, nearest first, under "Person k:" |
| **C. Hybrid** (after [Durupinar-AffectCrowd]) | One summary line for everyone within 8 m, the three nearest in full, then one line for the rest |
| **D. JSON line per person** (after [Martorell-TextToSpace]) | One JSON object per person: egocentric x (ahead) and y (left) in metres, speed, heading, closing, width, apparent age and gender |

## Results (DeepSeek-V3 tokenizer)

The fixed "ABOUT YOU" + "WHERE YOU ARE" part is **131 tokens** in every format.

| Format | N = 2 | N = 5 | N = 10 | Added per person (5 → 10) |
|---|---|---|---|---|
| A. negsim today | 220 | 220 | 220 | 0 (the others are not described) |
| B. Prose, everyone in full | 301 | 545 | 940 | 79 |
| C. Hybrid, 3 nearest in full | 333 | 448 | 448 | 0 beyond the third person |
| D. JSON line per person | 282 | 479 | 805 | 65 |

**Cost per call, situation block only**, at $0.28 per million input tokens: format B at N = 10 is
about $0.00026 (940 tokens); format C at any N ≥ 3 about $0.00013 (448 tokens). Per 1,000 calls:
about $0.26 and $0.13. `[inference]` The block is small next to a whole prompt; what scales cost in a
simulation is the number of calls (one per agent per decision), not this block.

Readings:
- JSON is about 18% shorter than the prose per person (65 against 79 tokens), not dramatically, because
  the JSON keys repeat on every line.
- The hybrid costs more than full prose at N = 2 (its summary line is overhead) and stops growing
  after the third person.

## Example: format C, N = 5

```text
PEOPLE NEAR YOU
- There are 5 people within 8 m of you; 2 of them are getting closer. Their average walking speed is 0.62 m/s.
Nearest person 1:
- They are 1.3 m away, behind you and 60° to your right.
- They are walking at 0.11 m/s, in the same direction as you, and the distance between you is not shrinking.
- Their body is 0.41 m wide.
- They look about 80 years old.
- They look like a woman.
Nearest person 2:
- They are 1.7 m away, ahead of you and 15° to your left.
...
- 2 other people are further away, between 3.3 m and 7.6 m.
```

Format D, the same first person:
`{"ahead_m": -0.6, "left_m": -1.1, "speed_mps": 0.11, "heading": "same", "closing": false, "width_m": 0.41, "looks_age": 80, "looks": "woman"}`

`[inference]` The example people are random, not checked against any perceivability rule (person 1
stands behind, outside a 200° field of view). A real renderer would apply the rule first.

## Script

Run with `uv run --no-project --with tokenizers python token_estimate.py tokenizer.json [--show N]`.
Kept here rather than as a file, since this issue adds no code to the repository.

```python
"""Offline token estimates for describing N nearby people (issue #52, Q6). No API calls."""
import json
import math
import random
import sys

from tokenizers import Tokenizer

SELF = """ABOUT YOU
- You are 34 years old.
- You are a woman.
- You are on your way to work.
- You are walking at 1.21 m/s. Your usual walking speed is 1.34 m/s.
- Your body is 0.46 m wide.

WHERE YOU ARE
- You are in a passage 2.40 m wide. The wall on your left is 0.82 m from you, the wall on your right 1.12 m.
- 4.0 m ahead of you, the passage narrows to 0.90 m for 1.5 m."""


def people(n, seed=7):
    rng = random.Random(seed)
    out = []
    for k in range(n):
        dist = round(rng.uniform(1.0, 8.0), 1)
        angle = rng.choice([0, 15, 30, 45, 60, 90, 120, 150, 180])
        side = rng.choice(["left", "right"])
        out.append({
            "dist": dist, "angle": angle, "side": side,
            "speed": round(rng.uniform(0.0, 1.6), 2),
            "heading": rng.choice(["same", "opposite", "across"]),
            "closing": rng.random() < 0.5,
            "width": round(rng.uniform(0.40, 0.55), 2),
            "age": rng.randint(8, 80),
            "gender": rng.choice(["a woman", "a man"]),
        })
    return sorted(out, key=lambda p: p["dist"])


def direction(p):
    if p["angle"] == 0:
        return "straight ahead of you"
    if p["angle"] == 180:
        return "straight behind you"
    if p["angle"] == 90:
        return f"to your {p['side']}"
    if p["angle"] < 90:
        return f"ahead of you and {p['angle']}° to your {p['side']}"
    return f"behind you and {180 - p['angle']}° to your {p['side']}"


def heading(p):
    other = "right" if p["side"] == "left" else "left"
    return {
        "same": "in the same direction as you",
        "opposite": "in the opposite direction to you",
        "across": f"across your direction of travel from your {p['side']} to your {other}, at 90° to it",
    }[p["heading"]]


def prose_lines(p):
    change = "and the distance between you is shrinking" if p["closing"] else "and the distance between you is not shrinking"
    return [
        f"- They are {p['dist']:.1f} m away, {direction(p)}.",
        f"- They are walking at {p['speed']:.2f} m/s, {heading(p)}, {change}.",
        f"- Their body is {p['width']:.2f} m wide.",
        f"- They look about {p['age']} years old.",
        f"- They look like {p['gender']}.",
    ]


def fmt_today(ps):
    """negsim today: one other person in full, everyone else one generic line."""
    lines = [SELF, "- Other people are walking around you as well." if len(ps) > 1 else "", "", "THE OTHER PERSON"]
    lines += prose_lines(ps[0])
    return "\n".join(l for l in lines if l is not None)


def fmt_prose_all(ps):
    """Every nearby person in full, negsim's lines repeated, nearest first."""
    lines = [SELF, "", f"PEOPLE NEAR YOU ({len(ps)}, nearest first)"]
    for k, p in enumerate(ps, 1):
        lines += [f"Person {k}:"] + prose_lines(p)
    return "\n".join(lines)


def fmt_hybrid(ps, k=3):
    """A one-line summary of everyone, then the k nearest in full (after Durupinar 2026, s3.1)."""
    toward = sum(1 for p in ps if p["closing"])
    mean = sum(p["speed"] for p in ps) / len(ps)
    lines = [SELF, "", "PEOPLE NEAR YOU",
             f"- There are {len(ps)} people within 8 m of you; {toward} of them are getting closer. Their average walking speed is {mean:.2f} m/s."]
    for i, p in enumerate(ps[:k], 1):
        lines += [f"Nearest person {i}:"] + prose_lines(p)
    rest = ps[k:]
    if rest:
        lines.append(f"- {len(rest)} other people are further away, between {rest[0]['dist']:.1f} m and {rest[-1]['dist']:.1f} m.")
    return "\n".join(lines)


def fmt_json(ps):
    """One JSON object per person, egocentric coordinates (x ahead, y to the left), nearest first."""
    rows = []
    for p in ps:
        a = math.radians(p["angle"])
        y = math.sin(a) * p["dist"] * (1 if p["side"] == "left" else -1)
        rows.append({
            "ahead_m": round(math.cos(a) * p["dist"], 1) + 0.0, "left_m": round(y, 1) + 0.0,
            "speed_mps": p["speed"], "heading": p["heading"], "closing": p["closing"],
            "width_m": p["width"], "looks_age": p["age"], "looks": p["gender"].split()[-1],
        })
    return SELF + "\n\nPEOPLE NEAR YOU (x ahead of you, y to your left, metres; nearest first)\n" + "\n".join(
        json.dumps(r, ensure_ascii=False) for r in rows)


FORMATS = {"today (1 in full + generic line)": fmt_today, "prose, everyone in full": fmt_prose_all,
           "hybrid: summary + 3 nearest in full": fmt_hybrid, "JSON line per person": fmt_json}

if __name__ == "__main__":
    tok = Tokenizer.from_file(sys.argv[1])
    count = lambda s: len(tok.encode(s, add_special_tokens=False).ids)
    print(f"fixed self + place block: {count(SELF)} tokens")
    print("format | N=2 | N=5 | N=10 | per extra person (5->10)")
    for name, f in FORMATS.items():
        c = [count(f(people(n))) for n in (2, 5, 10)]
        print(f"{name} | {c[0]} | {c[1]} | {c[2]} | {(c[2] - c[1]) / 5:.1f}")
    if "--show" in sys.argv:
        n = int(sys.argv[sys.argv.index("--show") + 1])
        for name, f in FORMATS.items():
            print(f"\n=== {name}, N={n}\n{f(people(n))}")
```
