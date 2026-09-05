"""Configuration for the DeepSeek prompting pipeline.

EDIT THIS FILE before running estimate_cost.py or the generator.
Every value marked `VERIFY` is an assumption, not a confirmed fact.
"""

from pathlib import Path

# ----------------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]          # .../CrowdSimulation
DATASET_DIR = ROOT / "dataset"
PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"
OUT_DIR = DATASET_DIR / "generated"                  # raw/ and behaviour_records.* go here

SCENARIOS_YAML = DATASET_DIR / "scenarios.yaml"
PERSONAS_YAML = DATASET_DIR / "personas.yaml"
ACTION_SPACE_YAML = DATASET_DIR / "action_space.yaml"

# ----------------------------------------------------------------------------
# Budget
# ----------------------------------------------------------------------------
BUDGET_USD = 2.00           # total DeepSeek credit available
ALREADY_SPENT_USD = 0.10    # run01 (2026-09-04) cost $0.097; update as you spend

# ----------------------------------------------------------------------------
# Generation shape
# ----------------------------------------------------------------------------
MODEL = "deepseek-chat"     # or "deepseek-reasoner" (more expensive; see PRICING)
REPEATS = 3                 # identical prompts per (scenario x persona) cell, for consistency checks
TEMPERATURE = 1.0           # DeepSeek recommends ~1.0-1.3 for this kind of open description
MAX_OUTPUT_TOKENS = 1200    # hard cap sent as max_tokens; also used for the worst-case row

# ----------------------------------------------------------------------------
# Pricing — USD per 1,000,000 tokens.
# VERIFY at https://api-docs.deepseek.com/quick_start/pricing  (rates change!)
# `AS_OF` is when these numbers were last believed correct.
# ----------------------------------------------------------------------------
PRICING = {
    "deepseek-chat@2025-09-v3.2": {
        "AS_OF": "2025-09",
        "input_cache_miss": 0.28,
        "input_cache_hit": 0.028,
        "output": 0.42,
    },
    "deepseek-chat@2025-02": {          # older, higher — used as a conservative upper bound
        "AS_OF": "2025-02",
        "input_cache_miss": 0.27,
        "input_cache_hit": 0.07,
        "output": 1.10,
    },
    "deepseek-reasoner@2025-02": {
        "AS_OF": "2025-02",
        "input_cache_miss": 0.55,
        "input_cache_hit": 0.14,
        "output": 2.19,
    },
}
ACTIVE_PRICING = "deepseek-chat@2025-09-v3.2"   # the profile the pass/fail verdict uses
UPPER_BOUND_PRICING = "deepseek-chat@2025-02"   # also always shown for comparison

# ----------------------------------------------------------------------------
# Prompt caching (DeepSeek context caching is automatic and on by default).
# The system prompt is identical for every call; the user prompt is identical
# across the REPEATS of a given cell. So most input tokens after the first pass
# are billed at the cache-hit rate.
# ----------------------------------------------------------------------------
ASSUME_PREFIX_CACHED = True

# ----------------------------------------------------------------------------
# Token estimation knobs (only used when tiktoken is unavailable, plus safety).
# ----------------------------------------------------------------------------
TOKENIZER = "auto"                 # "auto" -> tiktoken cl100k_base if importable, else "heuristic"
HEURISTIC_TOKENS_PER_CHAR = 0.30   # DeepSeek rule of thumb for English text
CHAT_OVERHEAD_TOKENS_PER_MSG = 4   # role wrappers etc.
CHAT_OVERHEAD_TOKENS_PER_CALL = 3  # assistant priming
OUTPUT_FILL_FACTOR = 2.2           # filled JSON vs the skeleton in output_contract.json
INFLATE_FACTOR = 1.15              # applied to the final projected cost as a safety margin
