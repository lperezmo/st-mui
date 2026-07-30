"""Fail CI when the resolved lock regresses known dependency security floors."""

from __future__ import annotations

import re
from pathlib import Path

import tomllib

MINIMUM_VERSIONS = {
    # Fixes Dependabot alerts #35-#44 (excluding unused #39). The newest
    # advisory in that set requires GitPython 3.1.55 or newer.
    "gitpython": (3, 1, 55),
}


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
    print(f"Dependency security floors satisfied: {checked}")


if __name__ == "__main__":
    main()
