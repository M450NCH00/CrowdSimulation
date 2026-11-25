"""Read settings from the process environment, falling back to the repository's ``.env``.

The API key lives in ``.env`` at the repository root, which git ignores. Values are
returned to the caller and never written to ``os.environ``, printed or logged.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from ..configutil import PACKAGE_ROOT, REPO_ROOT

ENV_FILE_CANDIDATES = (REPO_ROOT / ".env", PACKAGE_ROOT / ".env")


def read_env_file(path: Path) -> dict[str, str]:
    """Parse ``KEY=value`` lines; blank lines and ``#`` comments are skipped."""
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        key, separator, value = line.partition("=")
        if not separator:
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        values[key.strip()] = value
    return values


def get_setting(name: str, env_file: Optional[Path] = None) -> Optional[str]:
    """``name`` from the environment if set and non-empty, else from the ``.env`` file."""
    value = os.environ.get(name)
    if value:
        return value
    candidates = (env_file,) if env_file is not None else ENV_FILE_CANDIDATES
    for candidate in candidates:
        if candidate.is_file():
            value = read_env_file(candidate).get(name)
            if value:
                return value
    return None
