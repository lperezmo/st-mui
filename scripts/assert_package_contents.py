"""Verify built wheel and sdist artifacts contain every frontend bundle."""

from __future__ import annotations

import re
import tarfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"


def _components() -> list[str]:
    manifest = (ROOT / "st_mui" / "pyproject.toml").read_text(encoding="utf-8")
    return re.findall(
        r"\[\[tool\.streamlit\.component\.components\]\]\s+"
        r'name = "([^"]+)"',
        manifest,
    )


def _assert_archive(names: list[str], *, archive_name: str) -> None:
    for component_name in _components():
        suffix_pattern = re.compile(
            rf"(?:^|/)st_mui/{re.escape(component_name)}/frontend/build/"
            r"index-[^/]+\.js$"
        )
        entries = [name for name in names if suffix_pattern.search(name)]
        assert len(entries) == 1, (
            f"{archive_name}: expected one production bundle for "
            f"{component_name}, found {entries}"
        )
        assert not any(
            name.endswith(".js.map")
            and f"/st_mui/{component_name}/frontend/build/" in f"/{name}"
            for name in names
        ), f"{archive_name}: source map found for {component_name}"

    assert any(
        name == "st_mui/pyproject.toml" or name.endswith("/st_mui/pyproject.toml")
        for name in names
    ), f"{archive_name}: Streamlit component manifest is missing"


def main() -> None:
    wheels = list(DIST.glob("*.whl"))
    sdists = list(DIST.glob("*.tar.gz"))
    assert len(wheels) == 1, f"expected one wheel, found {wheels}"
    assert len(sdists) == 1, f"expected one sdist, found {sdists}"

    with zipfile.ZipFile(wheels[0]) as wheel:
        _assert_archive(wheel.namelist(), archive_name=wheels[0].name)
    with tarfile.open(sdists[0], mode="r:gz") as sdist:
        _assert_archive(sdist.getnames(), archive_name=sdists[0].name)

    print(
        f"OK: wheel and sdist contain one production bundle for each of "
        f"{len(_components())} components"
    )


if __name__ == "__main__":
    main()
