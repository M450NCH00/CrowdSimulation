"""Freeze a new prompt template version by pinning its hash in the manifest.

    python -m negsim.negotiation.freeze persona_v2 "why the wording changed"

A key that is already in the manifest cannot be frozen again: to change wording, save it
under the next version number. Record the reason in the work log as well; the note given
here is kept in ``templates/MANIFEST.json``.
"""

from __future__ import annotations

import json
import sys
from datetime import date

import yaml

from .prompts import MANIFEST_PATH, TEMPLATE_DIR, PromptTemplate, template_sha256


def freeze(key: str, note: str) -> str:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8")) if MANIFEST_PATH.is_file() else {
        "about": (
            "SHA-256 of each prompt template file, with line endings normalised to LF. "
            "negsim refuses to load a template whose file no longer matches. A template is "
            "frozen once it is listed here: new wording means a new version, never an edit."
        ),
        "templates": {},
    }
    if key in manifest["templates"]:
        raise SystemExit(f"{key} is already frozen; save the new wording as the next version")
    path = TEMPLATE_DIR / f"{key}.yaml"
    if not path.is_file():
        raise SystemExit(f"no such template file: {path}")
    digest = template_sha256(path)
    PromptTemplate(key, yaml.safe_load(path.read_text(encoding="utf-8")), digest)  # must be well-formed
    manifest["templates"][key] = {"sha256": digest, "frozen_on": date.today().isoformat(), "note": note}
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return digest


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    print(f"{sys.argv[1]} frozen: sha256 {freeze(sys.argv[1], sys.argv[2])}")
