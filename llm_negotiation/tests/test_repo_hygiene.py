"""Constraints on the code base itself that the issue sets."""

from __future__ import annotations

import ast
import re
from pathlib import Path

from negsim.configutil import PACKAGE_ROOT, REPO_ROOT

SOURCE_FILES = sorted(
    path
    for path in PACKAGE_ROOT.rglob("*.py")
    if not {"runs", "runs_mock", "__pycache__"} & set(path.relative_to(PACKAGE_ROOT).parts)
)
THIRD_PARTY_ALLOWED = {"yaml", "pytest", "matplotlib"}


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            modules.add(node.module.split(".")[0])
    return modules


def test_there_is_source_to_check():
    assert len(SOURCE_FILES) > 40


def test_phase_1_code_is_not_imported():
    """The Phase 1 dataset pipeline is retired: nothing here may import from it."""
    for path in SOURCE_FILES:
        assert not {"pipeline", "dataset"} & imported_modules(path), path


def test_only_pinned_third_party_packages_are_imported():
    import sys

    local = {"negsim", "helpers", "test_llm", "test_resolution", "conftest", "test_encounter_protocol", "test_perceive", "test_rulegen_validate", "test_execute"}
    for path in SOURCE_FILES:
        third_party = {
            module for module in imported_modules(path) if module not in sys.stdlib_module_names and module not in local
        }
        assert third_party <= THIRD_PARTY_ALLOWED, (path, third_party)
    pinned = (PACKAGE_ROOT / "requirements.txt").read_text(encoding="utf-8")
    assert re.search(r"^PyYAML==\S+$", pinned, re.M) and re.search(r"^pytest==\S+$", pinned, re.M)
    assert all("==" in line for line in pinned.splitlines() if line and not line.startswith("#"))


def test_no_module_shadows_the_standard_library_logging():
    assert not [path for path in PACKAGE_ROOT.rglob("logging*") if "__pycache__" not in path.parts]


def test_the_layout_the_issue_asks_for_is_there():
    for folder in ("core", "scenarios", "control", "conflict", "llm", "negotiation", "personas", "runlog", "metrics", "viz"):
        assert (PACKAGE_ROOT / "negsim" / folder / "__init__.py").is_file(), folder
    for scenario in ("doorway", "intersection", "hallway"):
        assert (PACKAGE_ROOT / "configs" / "scenarios" / f"{scenario}.yaml").is_file()
    for document in ("architecture", "gamechat-notes", "derivations", "llm-backend", "log-schema"):
        assert (PACKAGE_ROOT / "docs" / f"{document}.md").is_file(), document
    for name in ("README.md", "THIRD_PARTY_NOTICES.md", "requirements.txt", "run_experiment.py"):
        assert (PACKAGE_ROOT / name).is_file(), name


def test_nothing_that_looks_like_an_api_key_is_in_the_package():
    """DeepSeek keys start with ``sk-`` followed by a long run of hex-like characters.
    The only such strings allowed are the obvious fakes used by the tests."""
    pattern = re.compile(r"sk-[A-Za-z0-9]{20,}")
    for path in PACKAGE_ROOT.rglob("*"):
        if not path.is_file() or "__pycache__" in path.parts or path.suffix in {".png", ".pyc"}:
            continue
        for match in pattern.findall(path.read_text(encoding="utf-8", errors="ignore")):
            assert False, f"{path}: {match[:6]}... looks like a key"


def test_env_file_is_ignored_by_git():
    ignored = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert ".env" in ignored
