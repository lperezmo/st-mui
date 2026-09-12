"""Fail CI when the resolved lock regresses known dependency security floors."""

from __future__ import annotations

import re
from pathlib import Path

import tomllib

MINIMUM_VERSIONS = {
    "tornado": (6, 5, 8),
    # Includes GitPython advisories fixed in 3.1.58.
    "gitpython": (3, 1, 58),
    "click": (8, 3, 3),
}
PROJECT_FILES = (Path("pyproject.toml"), Path("st_mui/pyproject.toml"))


def release_tuple(version: str) -> tuple[int, ...]:
    match = re.match(r"^\d+(?:\.\d+)*", version)
    if match is None:
        raise ValueError(f"Unsupported dependency version: {version!r}")
    return tuple(int(part) for part in match.group().split("."))


def main() -> None:
    lock = tomllib.loads(Path("uv.lock").read_text(encoding="utf-8"))
    resolved = {
        package["name"].lower(): package["version"]
        for package in lock["package"]
        if "version" in package
    }

    failures = []
    project_versions = {
        path.as_posix(): tomllib.loads(path.read_text(encoding="utf-8"))["project"][
            "version"
        ]
        for path in PROJECT_FILES
    }
    locked_project_version = resolved.get("st-mui")
    expected_project_version = next(iter(project_versions.values()))
    for path, version in project_versions.items():
        if version != expected_project_version:
            failures.append(
                f"{path} version {version} does not match {expected_project_version}"
            )
    if locked_project_version != expected_project_version:
        failures.append(
            f"uv.lock st-mui version {locked_project_version!r} does not match "
            f"project version {expected_project_version}"
        )

    for package, minimum in MINIMUM_VERSIONS.items():
        version = resolved.get(package)
        if version is None:
            failures.append(f"{package} is missing from uv.lock")
        elif release_tuple(version) < minimum:
            floor = ".".join(str(part) for part in minimum)
            failures.append(f"{package} {version} is below the secure floor {floor}")

    if failures:
        raise SystemExit("\n".join(failures))

    checked = ", ".join(
        f"{package}=={resolved[package]}" for package in MINIMUM_VERSIONS
    )
    print(
        f"Lock/project versions agree at {expected_project_version}; "
        f"dependency security floors satisfied: {checked}"
    )


if __name__ == "__main__":
    main()
