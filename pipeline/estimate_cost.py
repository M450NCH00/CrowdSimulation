"""Offline token + cost estimate for the DeepSeek generation run.

Makes NO API calls. Renders every prompt that would be sent, counts tokens, and
applies the rates in config.py. Prints a projection and a sensitivity table, and
exits non-zero if the active-pricing projection exceeds the remaining budget.

    python pipeline/estimate_cost.py
"""

from __future__ import annotations

import math
import sys

import config
import render


# ----------------------------------------------------------------------------
# Tokeniser
# ----------------------------------------------------------------------------
def get_counter():
    mode = config.TOKENIZER
    if mode in ("auto", "tiktoken"):
        try:
            import tiktoken
            enc = tiktoken.get_encoding("cl100k_base")
            return ("tiktoken:cl100k_base", lambda s: len(enc.encode(s)))
        except Exception:
            if mode == "tiktoken":
                raise
    tpc = config.HEURISTIC_TOKENS_PER_CHAR
    return (f"heuristic:{tpc}/char", lambda s: max(1, math.ceil(len(s) * tpc)))


# ----------------------------------------------------------------------------
# Core estimate
# ----------------------------------------------------------------------------
def estimate(count, repeats, pricing_key, *, cache, output_tokens_per_call):
    """`count` is the token-counter callable from get_counter()."""
    rates = config.PRICING[pricing_key]
    per_msg = config.CHAT_OVERHEAD_TOKENS_PER_MSG
    per_call = config.CHAT_OVERHEAD_TOKENS_PER_CALL

    data = render.load_all()
    system_tokens = count(data["system_prompt"]) + per_msg

    user_tokens = []
    for sc, ag, g in render.cells():
        u = count(render.render_user_prompt(sc, ag, g)) + per_msg
        user_tokens.append(u)

    n_cells = len(user_tokens)                     # unique prompts (140)
    total_calls = n_cells * repeats
    sum_user = sum(user_tokens)

    # input tokens across ALL calls (before cache accounting)
    input_all = repeats * (n_cells * system_tokens + sum_user) + total_calls * per_call

    if cache:
        # system paid at miss once; each unique user prompt paid at miss once;
        # everything else (repeat passes, shared system prefix) is a cache hit.
        miss_input = system_tokens + sum_user + per_call
        hit_input = input_all - miss_input
    else:
        miss_input = input_all
        hit_input = 0

    output_all = total_calls * output_tokens_per_call

    cost = (
        miss_input / 1e6 * rates["input_cache_miss"]
        + hit_input / 1e6 * rates["input_cache_hit"]
        + output_all / 1e6 * rates["output"]
    )
    cost_inflated = cost * config.INFLATE_FACTOR

    return {
        "pricing_key": pricing_key,
        "as_of": rates["AS_OF"],
        "repeats": repeats,
        "n_cells": n_cells,
        "total_calls": total_calls,
        "system_tokens": system_tokens,
        "avg_user_tokens": sum_user / n_cells,
        "output_tokens_per_call": output_tokens_per_call,
        "miss_input": miss_input,
        "hit_input": hit_input,
        "output_all": output_all,
        "cost_raw": cost,
        "cost": cost_inflated,
        "cache": cache,
    }


def main():
    tok_name, count = get_counter()
    data = render.load_all()

    # output tokens per call
    contract_tokens = count(data["output_contract"])
    est_output = min(
        int(contract_tokens * config.OUTPUT_FILL_FACTOR),
        config.MAX_OUTPUT_TOKENS,
    )

    remaining = config.BUDGET_USD - config.ALREADY_SPENT_USD

    print("=" * 72)
    print("DeepSeek generation — offline cost estimate")
    print("=" * 72)
    print(f"tokeniser              : {tok_name}")
    print(f"model                  : {config.MODEL}")
    print(f"active pricing profile : {config.ACTIVE_PRICING}  (rates AS_OF "
          f"{config.PRICING[config.ACTIVE_PRICING]['AS_OF']}, VERIFY before trusting)")
    print(f"prefix caching assumed : {config.ASSUME_PREFIX_CACHED}")
    print(f"repeats per cell       : {config.REPEATS}")
    print(f"budget remaining       : ${remaining:.2f}  "
          f"(${config.BUDGET_USD:.2f} total - ${config.ALREADY_SPENT_USD:.2f} spent)")
    print()

    base = estimate(
        count, config.REPEATS, config.ACTIVE_PRICING,
        cache=config.ASSUME_PREFIX_CACHED, output_tokens_per_call=est_output,
    )

    print(f"cells (scenarios x ages x genders) : {base['n_cells']}")
    print(f"total API calls  (cells x repeats) : {base['total_calls']}")
    print()
    print(f"system prompt tokens              : {base['system_tokens']:>8,}")
    print(f"avg user prompt tokens            : {base['avg_user_tokens']:>8,.0f}")
    print(f"est output tokens / call          : {base['output_tokens_per_call']:>8,}  "
          f"(contract {contract_tokens} x {config.OUTPUT_FILL_FACTOR}, capped {config.MAX_OUTPUT_TOKENS})")
    print()
    print(f"input tokens @ cache-MISS         : {base['miss_input']:>10,.0f}")
    print(f"input tokens @ cache-HIT          : {base['hit_input']:>10,.0f}")
    print(f"output tokens (all calls)         : {base['output_all']:>10,.0f}")
    print()
    print(f"raw cost                          : ${base['cost_raw']:.4f}")
    print(f"cost x {config.INFLATE_FACTOR} safety inflation      : ${base['cost']:.4f}")
    print()

    verdict = "OK  (within budget)" if base["cost"] <= remaining else "OVER BUDGET"
    print(f">>> projected spend for this run  : ${base['cost']:.2f}   [{verdict}]")
    print(f">>> would leave                   : ${remaining - base['cost']:.2f}")
    print()

    # ---- sensitivity table --------------------------------------------------
    print("-" * 72)
    print("Sensitivity (cost after safety inflation, USD)")
    print("-" * 72)
    print(f"{'repeats':>7} | {'calls':>6} | {config.ACTIVE_PRICING:>26} | "
          f"{config.UPPER_BOUND_PRICING:>22}")
    for r in (1, 2, 3, 5):
        a = estimate(count, r, config.ACTIVE_PRICING,
                     cache=config.ASSUME_PREFIX_CACHED, output_tokens_per_call=est_output)
        b = estimate(count, r, config.UPPER_BOUND_PRICING,
                     cache=config.ASSUME_PREFIX_CACHED, output_tokens_per_call=est_output)
        print(f"{r:>7} | {a['total_calls']:>6} | ${a['cost']:>24.3f} | ${b['cost']:>20.3f}")

    print()
    worst = estimate(count, config.REPEATS, config.UPPER_BOUND_PRICING,
                     cache=False, output_tokens_per_call=config.MAX_OUTPUT_TOKENS)
    print(f"worst case (repeats={config.REPEATS}, NO caching, max output {config.MAX_OUTPUT_TOKENS}, "
          f"{config.UPPER_BOUND_PRICING} rates): ${worst['cost']:.2f}")
    print("=" * 72)

    return 0 if base["cost"] <= remaining else 1


if __name__ == "__main__":
    sys.exit(main())
