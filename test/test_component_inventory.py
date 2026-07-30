"""Keep every component inventory in sync with the source of truth."""

from __future__ import annotations

import re
from pathlib import Path

import st_mui

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "autocomplete",
    "data_grid",
    "date_picker",
    "date_range_picker",
    "date_time_picker",
    "date_time_range_picker",
    "rating",
    "slider",
    "time_picker",
    "tree_view",
}


def test_component_inventories_match():
    manifest = (ROOT / "st_mui" / "pyproject.toml").read_text(encoding="utf-8")
    build_script = (ROOT / "st_mui" / "frontend" / "build.mjs").read_text(
        encoding="utf-8"
    )
    project = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    source_manifest = (ROOT / "MANIFEST.in").read_text(encoding="utf-8")
    production_guard = (ROOT / "scripts" / "assert_prod_build.sh").read_text(
        encoding="utf-8"
    )
    guard_array = re.search(r"COMPONENTS=\(\s*(.*?)\s*\)", production_guard, re.DOTALL)
    assert guard_array is not None

    inventories = {
        "public exports": set(st_mui.__all__),
        "lazy imports": set(st_mui._COMPONENT_IMPORTS),
        "Streamlit manifest": set(
            re.findall(
                r"\[\[tool\.streamlit\.component\.components\]\]\s+"
                r'name = "([^"]+)"',
                manifest,
            )
        ),
        "frontend builds": set(re.findall(r'name:\s*"([^"]+)"', build_script)),
        "wheel package data": set(
            re.findall(r'"st_mui\.([^"]+)" = \["frontend/build/\*\*/\*"\]', project)
        ),
        "source distribution": set(
            re.findall(
                r"recursive-include st_mui/([^/]+)/frontend/build \*",
                source_manifest,
            )
        ),
        "production build guard": set(
            re.findall(r"^\s*([a-z][a-z0-9_]*)\s*$", guard_array.group(1), re.MULTILINE)
        ),
    }

    for inventory_name, component_names in inventories.items():
        assert component_names == EXPECTED, (
            f"{inventory_name} drifted: expected {sorted(EXPECTED)}, "
            f"got {sorted(component_names)}"
        )
        for component_name in component_names:
            assert (ROOT / "st_mui" / component_name / "__init__.py").is_file()
            assert (
                ROOT / "st_mui" / "frontend" / "src" / component_name / "index.tsx"
            ).is_file()
