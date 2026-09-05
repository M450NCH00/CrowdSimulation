"""Step 5 — run the DeepSeek prompting pipeline.

DO NOT run this until estimate_cost.py has been reviewed and the design decisions
in ../README.md have supervisor sign-off.

    export DEEPSEEK_API_KEY=sk-...
    python pipeline/generate.py --limit 4      # smoke test: 4 cells only
    python pipeline/generate.py                # full run (gated by the budget check)

Behaviour:
  * refuses to start if the projected spend exceeds the remaining budget
    (config.BUDGET_USD - config.ALREADY_SPENT_USD) unless --force;
  * writes one JSON line per API call to dataset/generated/raw/<run_id>.jsonl;
  * is resumable — re-running skips cells already present in that file;
  * tracks real spend from each response's `usage` and stops if it would exceed
    the budget mid-run.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import sys
import time
import uuid

import config
import env
import render
from estimate_cost import estimate, get_counter

env.load()  # pull CrowdSimulation/.env into os.environ (shell vars still win)


def _sha1(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()


def _utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def _price(usage: dict, pricing_key: str) -> float:
    r = config.PRICING[pricing_key]
    miss = usage.get("prompt_cache_miss_tokens")
    hit = usage.get("prompt_cache_hit_tokens")
    if miss is None or hit is None:                      # API did not split it
        miss, hit = usage.get("prompt_tokens", 0), 0
    out = usage.get("completion_tokens", 0)
    return miss / 1e6 * r["input_cache_miss"] + hit / 1e6 * r["input_cache_hit"] + out / 1e6 * r["output"]


def _load_done(path) -> set:
    done = set()
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    done.add(json.loads(line)["raw_id"])
                except Exception:
                    pass
    return done


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None, help="only process the first N cells")
    ap.add_argument("--dry-run", action="store_true", help="render + gate, but make no API calls")
    ap.add_argument("--force", action="store_true", help="ignore the budget gate")
    ap.add_argument("--run-id", default=None)
    args = ap.parse_args()

    tok_name, count = get_counter()
    remaining = config.BUDGET_USD - config.ALREADY_SPENT_USD

    # --- budget gate -------------------------------------------------------
    contract_tokens = count(render.load_all()["output_contract"])
    est_output = min(int(contract_tokens * config.OUTPUT_FILL_FACTOR), config.MAX_OUTPUT_TOKENS)
    proj = estimate(count, config.REPEATS, config.ACTIVE_PRICING,
                    cache=config.ASSUME_PREFIX_CACHED, output_tokens_per_call=est_output)
    print(f"[gate] tokeniser={tok_name}  projected=${proj['cost']:.2f}  remaining=${remaining:.2f}")
    if proj["cost"] > remaining and not args.force:
        print("[gate] ABORT: projected spend exceeds remaining budget. Use --force to override.")
        return 1

    cells = list(render.cells())
    if args.limit:
        cells = cells[: args.limit]
    total_calls = len(cells) * config.REPEATS
    print(f"[plan] {len(cells)} cells x {config.REPEATS} repeats = {total_calls} calls")

    run_id = args.run_id or dt.datetime.now().strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:6]
    config.OUT_DIR.joinpath("raw").mkdir(parents=True, exist_ok=True)
    raw_path = config.OUT_DIR / "raw" / f"{run_id}.jsonl"
    done = _load_done(raw_path)
    if done:
        print(f"[resume] {len(done)} calls already in {raw_path.name}, will skip them")

    if args.dry_run:
        print("[dry-run] not calling the API. Example rendered prompt for the first cell:")
        sc, ag, g = cells[0]
        print("-" * 60)
        print(render.render_user_prompt(sc, ag, g)[:1200])
        print("-" * 60)
        return 0

    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("[error] DEEPSEEK_API_KEY not found (checked shell env and CrowdSimulation/.env)")
        return 2
    base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    from openai import OpenAI
    client = OpenAI(api_key=api_key, base_url=base_url)

    spent = 0.0
    fout = open(raw_path, "a", encoding="utf-8")
    try:
        for ci, (sc, ag, g) in enumerate(cells):
            messages = render.build_messages(sc, ag, g)
            sys_sha = _sha1(messages[0]["content"])
            for rep in range(config.REPEATS):
                raw_id = f"{run_id}__{sc['id']}__{ag['id']}__{g['id']}__r{rep}"
                if raw_id in done:
                    continue

                rec = {
                    "raw_id": raw_id, "schema_version": 1, "run_id": run_id,
                    "scenario_id": sc["id"], "age_group": ag["id"], "gender": g["id"],
                    "repeat_index": rep,
                    "request": {
                        "model": config.MODEL, "prompt_version": "v1",
                        "system_prompt_sha1": sys_sha, "messages": messages,
                        "params": {"temperature": config.TEMPERATURE,
                                   "max_tokens": config.MAX_OUTPUT_TOKENS,
                                   "response_format": {"type": "json_object"}},
                    },
                    "response": {"raw_text": "", "parsed_ok": False, "parsed": None},
                    "status": "api_error", "error": None, "timestamp_utc": _utc(),
                }

                text, usage, err = "", {}, None
                for attempt in range(5):
                    try:
                        resp = client.chat.completions.create(
                            model=config.MODEL, messages=messages,
                            temperature=config.TEMPERATURE,
                            max_tokens=config.MAX_OUTPUT_TOKENS,
                            response_format={"type": "json_object"},
                        )
                        text = resp.choices[0].message.content or ""
                        usage = resp.usage.model_dump() if resp.usage else {}
                        err = None
                        break
                    except Exception as e:                       # noqa: BLE001
                        err = f"{type(e).__name__}: {e}"
                        time.sleep(2 ** attempt)

                rec["response"]["raw_text"] = text
                rec["response"]["usage"] = usage
                if err is None:
                    try:
                        rec["response"]["parsed"] = json.loads(text)
                        rec["response"]["parsed_ok"] = True
                        rec["status"] = "ok"
                    except Exception as e:                       # noqa: BLE001
                        rec["status"] = "parse_error"
                        rec["error"] = f"json: {e}"
                    call_cost = _price(usage, config.ACTIVE_PRICING)
                    rec["response"]["cost_usd"] = round(call_cost, 6)
                    spent += call_cost
                else:
                    rec["status"] = "retry_exhausted"
                    rec["error"] = err

                fout.write(json.dumps(rec, ensure_ascii=False) + "\n")
                fout.flush()

                if config.ALREADY_SPENT_USD + spent > config.BUDGET_USD and not args.force:
                    print(f"[stop] real spend ${spent:.3f} would exceed budget. Halting cleanly.")
                    return 1

            if (ci + 1) % 10 == 0:
                print(f"[progress] {ci + 1}/{len(cells)} cells, spent ~${spent:.3f}")
    finally:
        fout.close()

    print(f"[done] run_id={run_id}  calls_written -> {raw_path}")
    print(f"[done] estimated real spend this run: ${spent:.3f}  "
          f"(update ALREADY_SPENT_USD in config.py)")
    print("[next] python pipeline/aggregate.py --run-id " + run_id)
    return 0


if __name__ == "__main__":
    sys.exit(main())
