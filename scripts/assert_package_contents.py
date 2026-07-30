"""Verify built wheel and sdist artifacts contain every frontend bundle."""

from __future__ import annotations

import re
import tarfile
import zipfile
from collections.abc import Callable
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
MAX_BUNDLE_BYTES = 1_048_576
MAX_TOTAL_BUNDLE_BYTES = 6_291_456
FORBIDDEN_BUNDLE_MARKERS = (
    b"//#region node_modules/",
    b"react.development.js",
    b"sourceMappingURL",
    b"@mui/x-license",
    b"__MUI_LICENSE_INFO__",
    b"Missing license key",
)


def _components() -> list[str]:
    manifest = (ROOT / "st_mui" / "pyproject.toml").read_text(encoding="utf-8")
    return re.findall(
        r"\[\[tool\.streamlit\.component\.components\]\]\s+"
        r'name = "([^"]+)"',
        manifest,
    )


def _assert_archive(
    names: list[str],
    *,
    archive_name: str,
    read_bytes: Callable[[str], bytes],
) -> None:
    total_bundle_bytes = 0
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
        build_scripts = [
            name
            for name in names
            if re.search(
                rf"(?:^|/)st_mui/{re.escape(component_name)}/frontend/build/"
                r"[^/]+\.js$",
                name,
            )
        ]
        assert build_scripts == entries, (
            f"{archive_name}: expected the index entry to be the only JS file "
            f"for {component_name}, found {build_scripts}"
        )
        assert not any(
            name.endswith(".js.map")
            and f"/st_mui/{component_name}/frontend/build/" in f"/{name}"
            for name in names
        ), f"{archive_name}: source map found for {component_name}"

        bundle = read_bytes(entries[0])
        total_bundle_bytes += len(bundle)
        assert len(bundle) <= MAX_BUNDLE_BYTES, (
            f"{archive_name}: {entries[0]} is {len(bundle)} bytes; "
            "the frontend output is not fully minified"
        )
        for marker in FORBIDDEN_BUNDLE_MARKERS:
            assert marker not in bundle, (
                f"{archive_name}: {entries[0]} contains forbidden production "
                f"marker {marker!r}"
            )

    assert total_bundle_bytes <= MAX_TOTAL_BUNDLE_BYTES, (
        f"{archive_name}: frontend bundles total {total_bundle_bytes} bytes; "
        f"limit is {MAX_TOTAL_BUNDLE_BYTES}"
    )
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
        _assert_archive(
            wheel.namelist(),
            archive_name=wheels[0].name,
            read_bytes=wheel.read,
        )
    with tarfile.open(sdists[0], mode="r:gz") as sdist:

        def read_tar_bytes(name: str) -> bytes:
            extracted = sdist.extractfile(name)
            assert extracted is not None, f"{sdists[0].name}: cannot read {name}"
            return extracted.read()

        _assert_archive(
            sdist.getnames(),
            archive_name=sdists[0].name,
            read_bytes=read_tar_bytes,
        )

    print(
        f"OK: wheel and sdist contain one production bundle for each of "
        f"{len(_components())} components"
    )


if __name__ == "__main__":
    main()
