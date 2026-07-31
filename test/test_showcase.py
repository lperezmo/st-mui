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

PICKER_FEATURES = {
    "time_picker": {
        "helper_text",
        "clearable",
        "read_only",
        "open_to",
        "views",
        "minutes_step",
        "format",
    },
    "date_time_picker": {
        "helper_text",
        "clearable",
        "read_only",
        "disable_past",
        "open_to",
        "views",
        "minutes_step",
        "format",
    },
    "date_picker": {
        "helper_text",
        "clearable",
        "read_only",
        "disable_past",
        "disable_future",
        "open_to",
        "views",
        "display_week_number",
    },
    "date_range_picker": {
        "start_label",
        "end_label",
        "format",
        "helper_text",
        "clearable",
        "read_only",
        "disable_past",
        "disable_future",
        "open_to",
        "views",
        "display_week_number",
        "on_change",
    },
    "date_time_range_picker": {
        "start_label",
        "end_label",
        "format",
        "helper_text",
        "clearable",
        "read_only",
        "disable_past",
        "disable_future",
        "open_to",
        "views",
        "minutes_step",
        "on_change",
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


def test_showcase_exercises_the_expanded_picker_apis():
    calls = _component_calls()

    for component_name, expected_keywords in PICKER_FEATURES.items():
        actual_keywords = {
            keyword.arg
            for call in calls[component_name]
            for keyword in call.keywords
            if keyword.arg is not None
        }
        assert expected_keywords <= actual_keywords, (
            f"{component_name} showcase is missing picker options: "
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
    assert all(counts[name] >= 3 for name in PICKER_FEATURES)

    grid_keyword_sets = [
        {keyword.arg for keyword in call.keywords if keyword.arg is not None}
        for call in calls["data_grid"]
    ]
    assert any("columns" in keywords for keywords in grid_keyword_sets)
    assert any("columns" not in keywords for keywords in grid_keyword_sets)


_WALL_CLOCK_CALLS = {("datetime", "now"), ("date", "today")}

_VALUE_KEYWORDS = {
    "value",
    "min_datetime",
    "max_datetime",
    "min_date",
    "max_date",
    "min_time",
    "max_time",
}


def _reads_the_wall_clock(node: ast.AST) -> bool:
    return any(
        isinstance(child, ast.Call)
        and isinstance(child.func, ast.Attribute)
        and isinstance(child.func.value, ast.Name)
        and (child.func.value.id, child.func.attr) in _WALL_CLOCK_CALLS
        for child in ast.walk(node)
    )


def test_showcase_never_derives_a_picker_default_from_the_live_clock():
    """A default recomputed per rerun overwrites the user's selection.

    Streamlit reruns the whole script on every interaction, so a component
    value derived from datetime.now() or date.today() hands the picker a newer
    controlled value each time. That clobbers an in-progress selection, and
    with minutes_step set it also drifts off the minute grid and renders the
    picker as a red validation error. Defaults must come from a session-state
    anchor instead.
    """
    tree = ast.parse(SHOWCASE.read_text(encoding="utf-8"), filename=str(SHOWCASE))

    offenders = [
        f"{node.func.id}(..., {keyword.arg}=...) on line {keyword.value.lineno}"
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id in COMPONENTS
        for keyword in node.keywords
        if keyword.arg in _VALUE_KEYWORDS and _reads_the_wall_clock(keyword.value)
    ]

    assert offenders == []


def test_showcase_anchors_the_demo_clock_once_in_session_state():
    tree = ast.parse(SHOWCASE.read_text(encoding="utf-8"), filename=str(SHOWCASE))
    module_body_calls = [node for node in tree.body if _reads_the_wall_clock(node)]

    # The anchor assignment is the only place the showcase may read the clock.
    assert len(module_body_calls) == 1
    assert isinstance(module_body_calls[0], ast.If)


def test_showcase_header_summary_is_one_compact_caption():
    source = SHOWCASE.read_text(encoding="utf-8")

    assert "metric_components" not in source
    assert "st.caption(" in source
