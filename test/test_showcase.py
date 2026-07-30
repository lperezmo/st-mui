"""Keep the Streamlit showcase comprehensive as components evolve."""

from __future__ import annotations

import ast
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOWCASE = ROOT / "examples" / "showcase.py"

COMPONENTS = {
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

NEW_COMPONENT_FEATURES = {
    "autocomplete": {
        "label",
        "value",
        "multiple",
        "free_solo",
        "placeholder",
        "helper_text",
        "clearable",
        "disabled",
        "on_change",
        "key",
    },
    "slider": {
        "min_value",
        "max_value",
        "step",
        "marks",
        "value_label_display",
        "disabled",
        "on_change",
        "key",
    },
    "rating": {
        "value",
        "max_value",
        "precision",
        "size",
        "disabled",
        "read_only",
        "clearable",
        "on_change",
        "key",
    },
    "data_grid": {
        "rows",
        "columns",
        "id_field",
        "selected_rows",
        "sort_model",
        "filter_model",
        "page_size",
        "page_size_options",
        "height",
        "checkbox_selection",
        "density",
        "disabled",
        "on_change",
        "key",
    },
}


def _component_calls() -> dict[str, list[ast.Call]]:
    tree = ast.parse(SHOWCASE.read_text(encoding="utf-8"), filename=str(SHOWCASE))
    calls: dict[str, list[ast.Call]] = defaultdict(list)
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in COMPONENTS
        ):
            calls[node.func.id].append(node)
    return calls


def test_showcase_renders_every_public_component():
    calls = _component_calls()

    assert set(calls) == COMPONENTS
    assert all(
        any(
            keyword.arg == "disabled"
            for call in component_calls
            for keyword in call.keywords
        )
        for component_calls in calls.values()
    )


def test_showcase_exercises_every_new_component_option():
    calls = _component_calls()

    for component_name, expected_keywords in NEW_COMPONENT_FEATURES.items():
        actual_keywords = {
            keyword.arg
            for call in calls[component_name]
            for keyword in call.keywords
            if keyword.arg is not None
        }
        assert expected_keywords <= actual_keywords, (
            f"{component_name} showcase is missing options: "
            f"{sorted(expected_keywords - actual_keywords)}"
        )


def test_showcase_has_multiple_meaningful_new_component_scenarios():
    calls = _component_calls()
    counts = Counter(
        {name: len(component_calls) for name, component_calls in calls.items()}
    )

    assert counts["autocomplete"] >= 3
    assert counts["slider"] >= 3
    assert counts["rating"] >= 5
    assert counts["data_grid"] >= 2

    grid_keyword_sets = [
        {keyword.arg for keyword in call.keywords if keyword.arg is not None}
        for call in calls["data_grid"]
    ]
    assert any("columns" in keywords for keywords in grid_keyword_sets)
    assert any("columns" not in keywords for keywords in grid_keyword_sets)
