"""Minimal .env loader (no dependency).

Reads CrowdSimulation/.env and puts any keys not already in os.environ into it.
Real environment variables always win, so CI / shell exports override the file.
"""

from __future__ import annotations

import os
from pathlib import Path

_ENV_PATH = Path(__file__).resolve().parents[1] / ".env"


def load(path: Path | None = None) -> dict:
    path = path or _ENV_PATH
    loaded = {}
    if not path.exists():
        return loaded
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key, val = key.strip(), val.strip().strip('"').strip("'")
        loaded[key] = val
        os.environ.setdefault(key, val)
    return loaded
