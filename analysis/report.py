"""``report.md``: every part of RF-8's analysis, for reading (issue #63, task 11).

Rendered from :class:`analysis.cli.Results` alone. Each section says what it measures and how to
read it, so that the report can be quoted without this code beside it.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any, Optional, Sequence

import pandas as pd

from .effects import ALL, OK
from .load import AGENT_OUTCOMES, SESSION_OUTCOMES
from .noise import COMPONENTS

if TYPE_CHECKING:
    from .cli import Results

MAPPING_ROWS = 25
EXAMPLES = 5
FAMILY_WORDS = {
    "report": "every term of every model in this report (the chance of any false positive in it is at most alpha)",
    "subset": "the terms of all models of one subset (one condition, or all together)",
    "model": "the terms of one model",
}


def _cell(value: Any, digits: int = 3) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "-"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, float):
        return str(int(value)) if value.is_integer() else f"{value:.{digits}f}"
    return str(value).replace("|", "\\|").replace("\n", " ")


def table(frame: pd.DataFrame, columns: Sequence[str], headers: Optional[Sequence[str]] = None, digits: int = 3) -> list[str]:
    """A Markdown table of ``frame``'s ``columns``."""
    if frame is None or frame.empty:
        return ["(none)"]
    headers = list(headers or columns)
    lines = ["| " + " | ".join(headers) + " |", "|" + " --- |" * len(headers)]
    for row in frame[list(columns)].itertuples(index=False):
        lines.append("| " + " | ".join(_cell(value, digits) for value in row) + " |")
    return lines


def _p(value: float) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "-"
    return "< 0.001" if value < 0.001 else f"{value:.3f}"


def _estimate(term: dict) -> str:
    if "odds_ratio" in term and not pd.isna(term.get("odds_ratio")):
        return f"OR {term['odds_ratio']:.2f} [{term['or_low']:.2f}, {term['or_high']:.2f}]"
    return f"{term['estimate']:+.3f} [{term['ci_low']:+.3f}, {term['ci_high']:+.3f}]"


def render(results: "Results") -> str:
    lines: list[str] = ["# Factor analysis of a resolution experiment (RF-8)", ""]
    if "mock" in results.clients:
        lines += ["> **Made with the mock client.** Its replies are scripted and do not read the prompt: these numbers "
                  "test the pipeline and are not a finding about any model.", ""]
    lines += _inputs(results)
    lines += _effects(results)
    lines += _tree(results)
    lines += _noise(results)
    lines += _stability(results)
    lines += _mapping(results)
    lines += _stated(results)
    lines += _intent(results)
    lines += _ethnicity(results)
    lines += _reading(results)
    return "\n".join(lines).rstrip() + "\n"


def _inputs(r: "Results") -> list[str]:
    o = r.options
    by_condition = r.sessions["condition"].value_counts().sort_index()
    lines = ["## Inputs", ""]
    lines += [f"- `{path}`" for path in r.paths]
    lines += [
        "",
        f"- Sessions analysed (completed): **{len(r.sessions)}** ({', '.join(f'{k}: {v}' for k, v in by_condition.items())}); "
        f"left out: {', '.join(f'{k}: {v}' for k, v in r.left_out.items()) or 'none'}.",
        f"- Rows, one per agent per session: **{len(r.agents)}**.",
        f"- Physical outcomes of mode **`{o.mode}`**" + (" (the Step 1 measure)." if o.mode == "plan_only" else "."),
        f"- Client: {', '.join(sorted(r.clients)) or 'unknown (no config.json beside the file)'}.",
        f"- Predictors that vary: {', '.join(f'`{p}`' for p in r.varied_predictors) or 'none'}; constant, left out: "
        f"{', '.join(f'`{p}`' for p in r.predictors if p not in r.varied_predictors) or 'none'}.",
        f"- Holm's correction at alpha = {o.alpha}, over {FAMILY_WORDS[o.holm_family]}; seed {o.seed}; codebooks "
        f"`{o.intent_codebook}` and `{o.reasons_codebook}`.",
        "",
        "**The other's factors are as the agent was told them.** A factor of the other person counts only if it was "
        "printed to the agent at one or more of its decision points (`analysis/load.py`).",
        "",
    ]
    return lines


def _effects(r: "Results") -> list[str]:
    lines = ["## 1. Factor effects", "",
             "Logistic regression per binary outcome (odds ratios, OR, with 95% intervals), linear regression for a "
             "continuous one (coefficients). Per-agent models cluster standard errors by session; per-session models "
             f"use HC1. Holm's correction runs over {FAMILY_WORDS[r.options.holm_family]}. `all` is every condition together, with "
             "condition as a factor. A model whose outcome is separated by the predictors has no finite estimate and "
             "is listed as `separation`, never read as an effect.", ""]
    terms = [t for m in r.fitted for t in m.terms]
    significant = sorted((t for t in terms if t["significant"]), key=lambda t: (t["level"], t["outcome"], t["subset"], t["p_holm"]))
    lines += ["### Significant after Holm's correction", ""]
    if significant:
        frame = pd.DataFrame([{**t, "effect": _estimate(t), "p_": _p(t["p"]), "holm": _p(t["p_holm"])} for t in significant])
        lines += table(frame, ["outcome", "subset", "term", "effect", "p_", "holm", "n"], ["Outcome", "Subset", "Term", "Effect [95% CI]", "p", "Holm p", "n"])
    else:
        lines.append("None.")
    lines += ["", "### Every model", ""]
    models = pd.DataFrame([{"outcome": m.outcome, "level": m.level, "subset": m.subset, "status": m.status, "n": m.n,
                            "events": m.events, "clusters": m.clusters, "note": m.note} for m in r.fitted])
    lines += table(models, ["outcome", "level", "subset", "status", "n", "events", "clusters", "note"])
    lines += ["", "### Each outcome, all conditions together", "",
              "Per outcome: what it is, and every term of the pooled model (the per-condition terms are in `effects_terms.csv`).", ""]
    for outcome in (*AGENT_OUTCOMES, *SESSION_OUTCOMES):
        model = next((m for m in r.fitted if m.outcome == outcome.name and m.subset == ALL), None)
        if model is None:
            continue
        lines.append(f"**`{outcome.name}`** ({outcome.level}): {outcome.meaning}. Status: {model.status}, n = {model.n}"
                     + (f", events = {model.events}" if model.events is not None else "") + ".")
        if model.status == OK and model.terms:
            frame = pd.DataFrame([{**t, "effect": _estimate(t), "p_": _p(t["p"]), "holm": _p(t["p_holm"])} for t in model.terms])
            lines += [""] + table(frame, ["term", "effect", "p_", "holm"], ["Term", "Effect [95% CI]", "p", "Holm p"])
        if model.dropped:
            lines += ["", f"Left out of the model: {'; '.join(model.dropped)}."]
        lines.append("")
    return lines


def _tree(r: "Results") -> list[str]:
    t = r.tree
    lines = ["## 2. Decision tree", "", f"Predicts **`{t.outcome}`** per agent, depth at most {r.options.tree_depth}, on {t.n} rows "
             "(the predictors that vary, with condition and geometry). Figure: `tree.png`.", ""]
    if t.model is None:
        return lines + [t.note, ""]
    lines += [f"- Accuracy on the rows it was grown on: {t.accuracy:.3f}; always guessing the commoner outcome: {t.majority:.3f}.",
              f"- Accuracy on held-out sessions ({t.cv_folds}-fold, grouped by session): "
              + (f"{t.cv_accuracy:.3f}." if t.cv_accuracy is not None else "not computed (too few sessions)."),
              f"- Splits on: {', '.join(f'`{c}`' for c in t.used) or 'nothing (a single leaf)'}.",
              "", "A tree no better on held-out sessions than the commoner outcome has found no usable pattern.", "",
              "```", t.text.rstrip(), "```", ""]
    return lines


def _noise(r: "Results") -> list[str]:
    lines = ["## 3. Counterfactual pairs against the noise floor", "",
             "The noise floor is the flip rate between repeats of one cell of the exact-repeat set (identical prompts), "
             "with a bootstrap 95% interval over cells. A pair's flip rate (Wilson 95% interval) counts as evidence only "
             "where its lower end is above the noise floor's upper end, in the same condition. Components: "
             + ", ".join(f"`{c}`" for c in COMPONENTS) + " (`behaviour` is all of them together).", "", "### The noise floor", ""]
    lines += table(r.floors, ["component", "subset", "cells", "pairs", "flips", "rate", "ci_low", "ci_high"])
    lines += ["", "### The counterfactual pairs", ""]
    if r.flips.empty:
        lines.append("No counterfactual pair in the data.")
    else:
        lines += table(r.flips, ["factor", "component", "subset", "pairs", "flips", "rate", "ci_low", "ci_high", "noise_rate", "noise_high", "verdict"])
    return lines + [""]


def _stability(r: "Results") -> list[str]:
    s = r.stability
    lines = ["## 4. Behaviour stability", "",
             "Per cell of the exact-repeat set: the share of its repeats with the commonest outcome (1: every repeat "
             f"the same). A cell whose commonest behaviour came up in fewer than {r.options.coin_flip_below:g} of its repeats "
             "is a coin flip, and RF-11 should claim no rule there.", ""]
    if s.empty:
        return lines + ["No exact-repeat set in the data.", ""]
    rows = []
    for component in COMPONENTS:
        values = s[f"stability_{component}"]
        rows.append({"component": component, "cells": len(values), "mean": values.mean(), "min": values.min(),
                     "all_the_same": int((values == 1).sum())})
    lines += table(pd.DataFrame(rows), ["component", "cells", "mean", "min", "all_the_same"], ["Component", "Cells", "Mean", "Lowest", "Cells with every repeat the same"])
    flips = s.loc[s["coin_flip"]]
    lines += ["", f"### Coin-flip cells: {len(flips)} of {len(s)}", ""]
    if not flips.empty:
        lines += table(flips, ["cell", "condition", "repeats", "stability_behaviour", "stability_who_passed_first", "commonest_behaviour"],
                       ["Cell", "Condition", "Repeats", "Stability", "Who passed first", "Commonest behaviour"])
    else:
        lines.append("None.")
    return lines + [""]


def _mapping(r: "Results") -> list[str]:
    m = r.mapping
    shown = m.sort_values("rows", ascending=False).head(MAPPING_ROWS)
    lines = ["## 5. The factor-to-decision mapping", "",
             f"Every observed combination of {', '.join(f'`{f}`' for f in r.mapping_factors) or 'no factor'}, per condition, from "
             f"the agent's point of view: **{len(m)} combinations** in `mapping.csv`, each with its rows and, per outcome, how "
             "many are known and the share that are 1. Read the counts with the shares: a combination seen once gives 0 or 1 "
             f"from one row. The {min(MAPPING_ROWS, len(m))} combinations with the most rows:", ""]
    columns = ["condition", *r.mapping_factors, "rows", "p_passed_first", "p_kept_left", "p_stopped", "p_backed_up"]
    return lines + table(shown, columns) + [""]


def _stated(r: "Results") -> list[str]:
    lines = ["## 6. Stated against measured", "",
             "How often each factor is named in the agents' private `reason` (keyword codebook "
             f"`{r.options.reasons_codebook}`), beside its strongest measured effect in the per-agent models of all conditions "
             f"together. Named often: in at least {r.options.named_often:g} of the reasons. Measured: a term significant after "
             "Holm's correction. A factor named often with no measured effect, or the reverse, is a finding.", ""]
    if not r.decisions_found:
        lines += ["No `decisions.jsonl` beside the outcomes: the reasons could not be read.", ""]
    frame = r.stated.assign(estimate=r.stated["strongest_estimate"], holm=r.stated["strongest_p_holm"].map(_p))
    lines += table(frame, ["factor", "share_of_reasons", "measured_effect", "strongest_outcome", "strongest_term", "estimate", "holm", "verdict"],
                   ["Factor", "Share of reasons naming it", "Measured effect", "Outcome", "Term", "Estimate (OR or coef.)", "Holm p", "Verdict"])
    disagree = r.stated.loc[r.stated["verdict"].isin(["named often, no measured effect", "a measured effect, rarely named"])]
    lines += ["", "**Where saying and doing disagree:** " + (", ".join(f"`{f}` ({v})" for f, v in zip(disagree["factor"], disagree["verdict"])) or "nowhere") + ".",
              "", "### The debriefs' kind of basis", "", "One per prompted agent (D8); every source is unchecked until RF-14.", ""]
    kinds = r.kinds.reset_index().rename(columns={"debrief_kind": "kind", "index": "kind"})
    lines += table(kinds, list(kinds.columns))
    return lines + [""]


def _intent(r: "Results") -> list[str]:
    lines = ["## 7. Intent against plan", "",
             f"Each readable intent coded by the keyword codebook `{r.options.intent_codebook}` (keep to a side, slow down, stop and wait, "
             "back up, carry on, or `other`), against the plan coded from its steps. A mismatch is an intent that says something the "
             "plan does not do. Intents coded `other` and unreadable replies are left out of the rate. A high rate means the "
             "structured plan cannot be trusted on its own (RF-11).", ""]
    if r.intent_summary is None:
        return lines + ["No `decisions.jsonl` beside the outcomes: the intents could not be read.", ""]
    lines += table(r.intent_summary, ["subset", "decision_points", "unreadable", "uncoded", "compared", "mismatches", "rate", "ci_low", "ci_high"])
    checked = r.checked
    mismatches = checked.loc[checked["status"] == "mismatch"]
    lines += ["", "### Examples of mismatches", ""]
    if mismatches.empty:
        lines.append("None.")
    else:
        examples = mismatches.groupby("condition", sort=True).head(EXAMPLES)
        lines += table(examples, ["condition", "session_id", "agent_id", "intent", "plan_categories", "plan_side", "why"])
    uncoded = checked.loc[checked["status"] == "uncoded", "intent"].value_counts().head(EXAMPLES)
    lines += ["", "### Intents the codebook could not place (the commonest)", ""]
    lines += [f"- {count} x \"{_cell(text)}\"" for text, count in uncoded.items()] or ["None."]
    return lines + [""]


def _ethnicity(r: "Results") -> list[str]:
    """Issue #92: only when the outcome rows carry real ethnicity."""
    if r.ethnicity_groups is None and r.ethnicity_weighted is None:
        return []
    lines = ["## 8. Real ethnicity", "",
             "Descriptive. A difference between groups here is the model's behaviour towards people it was told are of a group, "
             "not a fact about those groups, and no rule may read ethnicity (`llm_negotiation/docs/ethnicity.md`).", ""]
    if r.ethnicity_groups is not None and not r.ethnicity_groups.empty:
        frame = r.ethnicity_groups
        shown = [c for c in ("passed_first", "kept_left", "stopped", "backed_up", "plan_slowed", "plan_left", "plan_right") if c in frame.columns]
        lines += ["### By group, the other's as told (unweighted agent rows)", ""]
        lines += table(frame, ["own", "other_as_told", "n", *shown])
        lines += ["", "Each share is over the rows where the outcome is defined (`<outcome>_n` in `ethnicity_groups.csv`).", ""]
    if r.ethnicity_weighted is not None and not r.ethnicity_weighted.empty:
        lines += ["### Weighted back to random resident pairs", "",
                  "Each session weighted by `ethnicity_weight`, so that the sessions stand for two residents met at random (each at "
                  "the resident shares; residents only). Use the weighted rate for a population-level figure; the effective number "
                  "of sessions is what the weighting leaves.", ""]
        lines += table(r.ethnicity_weighted, ["outcome", "sessions", "unweighted", "weighted", "effective_sessions"])
        lines += [""]
    return lines


def _reading(r: "Results") -> list[str]:
    return [
        "## How to read this report", "",
        "- **An effect here is an effect on what the LLM agents did**, in this design: a screen, so main effects are "
        "estimated clear of two-factor interactions only when the design is a resolution IV fraction "
        "(`llm_negotiation/docs/screening-designs.md`, section 3).",
        "- **Separation** (an outcome predicted perfectly by some predictor) leaves a model with no finite estimate; it is "
        "listed, not reported as an effect. Rare outcomes with many factors cause it: D14 aims at about 10 events per factor.",
        "- **The mapping is sparse** when there are many factors: most combinations are seen once or twice.",
        "- **The codebooks are drafts** until RF-9's pilot (`analysis/codebooks/`): a mention or a coded intent is a keyword "
        "match, not a reading of the text.",
        "",
    ]
