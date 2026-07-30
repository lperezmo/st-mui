"""Regression coverage for the semantic-release lock synchronization path."""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HAS_TOMLLIB = importlib.util.find_spec("tomllib") is not None


def _semantic_release_config() -> str:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(
        r"(?ms)^\[tool\.semantic_release\]\n(?P<body>.*?)(?=^\[|\Z)",
        pyproject,
    )
    assert match is not None
    return match.group("body")


def test_release_lock_command_is_exact_and_fail_fast() -> None:
    config = _semantic_release_config()
    command_match = re.search(r"(?m)^build_command = '(?P<command>[^']+)'$", config)

    assert command_match is not None
    assert command_match.group("command") == (
        'python -m pip install "uv==0.11.32"'
        ' && uv lock --upgrade-package "st-mui"'
        " && git add uv.lock"
    )


def test_release_and_ci_verify_the_tagged_lock() -> None:
    release_workflow = (ROOT / ".github/workflows/release.yml").read_text(
        encoding="utf-8"
    )
    tests_workflow = (ROOT / ".github/workflows/tests.yml").read_text(encoding="utf-8")
    manual_publish_workflow = (ROOT / ".github/workflows/publish.yml").read_text(
        encoding="utf-8"
    )

    assert "uv lock --check" in release_workflow
    assert "python scripts/assert_lock_security.py" in release_workflow
    assert "uv lock --check" in tests_workflow
    assert "python scripts/assert_lock_security.py" in tests_workflow
    assert "uv lock --check" in manual_publish_workflow
    assert "python scripts/assert_lock_security.py" in manual_publish_workflow


@pytest.mark.skipif(not HAS_TOMLLIB, reason="lock guard runs in Python 3.13 CI jobs")
def test_lock_guard_rejects_project_version_drift(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from scripts.assert_lock_security import main as assert_lock_security

    (tmp_path / "st_mui").mkdir()
    project = '[project]\nname = "st-mui"\nversion = "0.5.0"\n'
    (tmp_path / "pyproject.toml").write_text(project, encoding="utf-8")
    (tmp_path / "st_mui/pyproject.toml").write_text(project, encoding="utf-8")
    (tmp_path / "uv.lock").write_text(
        """
version = 1

[[package]]
name = "gitpython"
version = "3.1.57"

[[package]]
name = "st-mui"
version = "0.4.0"
""".lstrip(),
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    with pytest.raises(
        SystemExit,
        match=r"uv\.lock st-mui version '0\.4\.0' does not match project version 0\.5\.0",
    ):
        assert_lock_security()
