"""Behavior and validation tests for the MIT component expansion."""

from __future__ import annotations

import importlib
import sys
from collections.abc import Callable
from typing import Any

import pytest

from st_mui import _compat


@pytest.fixture
def load_component(monkeypatch):
    imported: list[str] = []

    def load(name: str, renderer: Callable[..., Any]):
        module_name = f"st_mui.{name}"
        sys.modules.pop(module_name, None)

        def fake_registration(_component_name: str, **_kwargs: Any):
            return renderer

        monkeypatch.setattr(_compat, "component", fake_registration)
        imported.append(module_name)
        return importlib.import_module(module_name)

    yield load

    for module_name in imported:
        sys.modules.pop(module_name, None)


def test_autocomplete_normalizes_options_and_returns_scalar(load_component):
    calls: list[dict[str, Any]] = []

    def renderer(**kwargs):
        calls.append(kwargs)
        return {"selected_value": 2}

    module = load_component("autocomplete", renderer)
    selected = module.autocomplete(
        ["one", {"label": "Two", "value": 2, "disabled": True}],
        value=2,
        label="Pick",
        placeholder="Search",
        helper_text="Choose carefully",
        clearable=False,
        disabled=True,
        key="auto",
    )

    assert selected == 2
    assert calls[0]["default"] == {"selected_value": 2}
    assert calls[0]["data"] == {
        "options": [
            {"label": "one", "value": "one", "disabled": False},
            {"label": "Two", "value": 2, "disabled": True},
        ],
        "label": "Pick",
        "selectedValue": 2,
        "multiple": False,
        "freeSolo": False,
        "placeholder": "Search",
        "helperText": "Choose carefully",
        "clearable": False,
        "disabled": True,
    }
    assert calls[0]["key"] == "auto"


def test_autocomplete_multiple_free_solo_round_trip_and_callback(load_component):
    calls: list[dict[str, Any]] = []

    class FalseyCallback:
        def __bool__(self):
            return False

        def __call__(self):
            pass

    callback = FalseyCallback()

    def renderer(**kwargs):
        calls.append(kwargs)
        return {"selected_value": ["known", "custom"]}

    module = load_component("autocomplete", renderer)
    selected = module.autocomplete(
        ["known"],
        value=("known", "custom"),
        multiple=True,
        free_solo=True,
        on_change=callback,
    )

    assert selected == ["known", "custom"]
    assert calls[0]["default"]["selected_value"] == ["known", "custom"]
    assert calls[0]["on_selected_value_change"] is callback


@pytest.mark.parametrize(
    ("response", "multiple", "free_solo", "expected"),
    [
        ({"selected_value": float("nan")}, False, False, None),
        ({"selected_value": "missing"}, False, False, None),
        ({"selected_value": ["known", "known"]}, True, False, []),
        ({"selected_value": [object()]}, True, True, []),
        (["not", "a", "mapping"], True, False, []),
    ],
)
def test_autocomplete_safely_rejects_invalid_frontend_state(
    load_component, response, multiple, free_solo, expected
):
    module = load_component("autocomplete", lambda **_kwargs: response)
    assert (
        module.autocomplete(
            ["known"],
            multiple=multiple,
            free_solo=free_solo,
        )
        == expected
    )


@pytest.mark.parametrize(
    ("options", "value", "kwargs", "exception"),
    [
        ([1, 1.0], None, {}, ValueError),
        ("one", None, {}, TypeError),
        ([{"disabled": True}], None, {}, ValueError),
        ([{"label": object(), "value": "known"}], None, {}, TypeError),
        ([{"label": "Known", "value": "known", "disabled": "no"}], None, {}, TypeError),
        (["known"], "unknown", {}, ValueError),
        (["known"], 3, {"free_solo": True}, TypeError),
        (["known"], ["known"], {}, TypeError),
        (["known"], "known", {"multiple": True}, TypeError),
        (["known"], ["known", "known"], {"multiple": True}, ValueError),
        ([float("nan")], None, {}, ValueError),
        ([2**53], None, {}, ValueError),
        (["known"], None, {"label": None}, TypeError),
        (["known"], None, {"placeholder": 1}, TypeError),
        (["known"], None, {"helper_text": False}, TypeError),
        (["known"], None, {"multiple": 1}, TypeError),
        (["known"], None, {"free_solo": 1}, TypeError),
        (["known"], None, {"clearable": 1}, TypeError),
        (["known"], None, {"disabled": 1}, TypeError),
        (["known"], None, {"on_change": object()}, TypeError),
    ],
)
def test_autocomplete_rejects_ambiguous_or_invalid_values(
    load_component, options, value, kwargs, exception
):
    module = load_component("autocomplete", lambda **_kwargs: None)
    with pytest.raises(exception):
        module.autocomplete(options, value=value, **kwargs)


def test_slider_supports_single_and_range_values(load_component):
    calls: list[dict[str, Any]] = []
    responses = iter(
        [
            {"selected_value": 6},
            {"selected_value": [3, 8]},
        ]
    )

    def renderer(**kwargs):
        calls.append(kwargs)
        return next(responses)

    module = load_component("slider", renderer)
    single = module.slider(
        label="Amount",
        value=5,
        min_value=0,
        max_value=10,
        step=0.5,
        marks=[{"value": 0, "label": "Low"}, {"value": 10, "label": "High"}],
        value_label_display="on",
        disabled=True,
        key="single-slider",
    )
    selected_range = module.slider(value=(2, 7), min_value=0, max_value=10)

    assert single == 6
    assert selected_range == (3, 8)
    assert calls[0]["data"] == {
        "label": "Amount",
        "selectedValue": 5,
        "minValue": 0,
        "maxValue": 10,
        "step": 0.5,
        "marks": [
            {"value": 0, "label": "Low"},
            {"value": 10, "label": "High"},
        ],
        "valueLabelDisplay": "on",
        "disabled": True,
    }
    assert calls[0]["key"] == "single-slider"
    assert calls[1]["default"] == {"selected_value": [2, 7]}


def test_slider_wires_one_committed_change_callback(load_component):
    calls: list[dict[str, Any]] = []

    def callback():
        pass

    def renderer(**kwargs):
        calls.append(kwargs)
        return kwargs["default"]

    module = load_component("slider", renderer)
    module.slider(value=10, on_change=callback)
    assert calls[0]["on_selected_value_change"] is callback


def test_slider_discrete_marks_are_sorted_and_constrain_values(load_component):
    calls: list[dict[str, Any]] = []

    def renderer(**kwargs):
        calls.append(kwargs)
        return {"selected_value": 10}

    module = load_component("slider", renderer)
    selected = module.slider(
        step=None,
        marks=[
            {"value": 10, "label": "High"},
            {"value": 2, "label": "Low"},
        ],
    )

    assert selected == 10
    assert calls[0]["default"] == {"selected_value": 2}
    assert calls[0]["data"]["marks"] == [
        {"value": 2, "label": "Low"},
        {"value": 10, "label": "High"},
    ]

    invalid_result_module = load_component(
        "slider", lambda **_kwargs: {"selected_value": 3}
    )
    assert (
        invalid_result_module.slider(
            value=2,
            step=None,
            marks=[{"value": 2}, {"value": 10}],
        )
        == 2
    )


def test_slider_caps_implicit_marks_at_a_safe_boundary(load_component):
    calls: list[dict[str, Any]] = []

    def renderer(**kwargs):
        calls.append(kwargs)
        return kwargs["default"]

    module = load_component("slider", renderer)
    assert module.slider(max_value=999, marks=True) == 0
    assert calls[0]["data"]["marks"] is True

    with pytest.raises(ValueError, match="at most 1000 marks"):
        module.slider(max_value=1000, marks=True)


@pytest.mark.parametrize(
    ("response", "expected"),
    [
        ({"selected_value": True}, 4),
        ({"selected_value": float("nan")}, 4),
        ({"selected_value": 11}, 4),
        ({"selected_value": "5"}, 4),
        (["not", "a", "mapping"], 4),
    ],
)
def test_slider_rejects_malformed_single_values_from_frontend(
    load_component, response, expected
):
    module = load_component("slider", lambda **_kwargs: response)
    assert module.slider(value=4, min_value=0, max_value=10) == expected


@pytest.mark.parametrize(
    "response",
    [
        {"selected_value": [2]},
        {"selected_value": [2, 11]},
        {"selected_value": [8, 2]},
        {"selected_value": [True, 8]},
        {"selected_value": [2, float("inf")]},
        {"selected_value": "2,8"},
    ],
)
def test_slider_rejects_malformed_range_values_from_frontend(load_component, response):
    module = load_component("slider", lambda **_kwargs: response)
    assert module.slider(value=(2, 8), min_value=0, max_value=10) == (2, 8)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"min_value": 1, "max_value": 1},
        {"min_value": True},
        {"max_value": float("inf")},
        {"step": 0},
        {"step": True},
        {"value": (8, 2)},
        {"value": (1, 2, 3)},
        {"value": True},
        {"value": float("nan")},
        {"value": 101},
        {"step": None, "marks": False},
        {"step": None, "marks": []},
        {"step": None, "marks": [{"value": 2}], "value": 3},
        {"marks": [{"value": 1}, {"value": 1.0}]},
        {"marks": [{"label": "missing value"}]},
        {"marks": "not-marks"},
        {"marks": [{"value": 101}]},
        {"label": {"not": "renderable"}},
        {"min_value": -(1 << 53), "max_value": 100},
        {"value_label_display": "sometimes"},
        {"disabled": 1},
        {"on_change": "not-callable"},
    ],
)
def test_slider_validates_its_contract(load_component, kwargs):
    module = load_component("slider", lambda **_kwargs: None)
    with pytest.raises((TypeError, ValueError)):
        module.slider(**kwargs)


def test_rating_round_trips_and_wires_callback(load_component):
    calls: list[dict[str, Any]] = []

    def callback():
        pass

    def renderer(**kwargs):
        calls.append(kwargs)
        return {"selected_value": 3.5}

    module = load_component("rating", renderer)
    selected = module.rating(
        "Score",
        2.5,
        max_value=10,
        precision=0.5,
        size="large",
        disabled=True,
        read_only=True,
        clearable=False,
        on_change=callback,
    )

    assert selected == 3.5
    assert calls[0]["default"] == {"selected_value": 2.5}
    assert calls[0]["data"] == {
        "label": "Score",
        "selectedValue": 2.5,
        "maxValue": 10,
        "precision": 0.5,
        "size": "large",
        "disabled": True,
        "readOnly": True,
        "clearable": False,
    }
    assert calls[0]["on_selected_value_change"] is callback


def test_rating_preserves_a_falsey_callable_callback(load_component):
    calls: list[dict[str, Any]] = []

    class FalseyCallback:
        def __bool__(self):
            return False

        def __call__(self):
            pass

    callback = FalseyCallback()

    def renderer(**kwargs):
        calls.append(kwargs)
        return kwargs["default"]

    module = load_component("rating", renderer)
    module.rating(on_change=callback)

    assert calls[0]["on_selected_value_change"] is callback


@pytest.mark.parametrize(
    ("returned", "expected"),
    [
        (None, 2.5),
        ({}, 2.5),
        ({"selected_value": "invalid"}, 2.5),
        ({"selected_value": True}, 2.5),
        ({"selected_value": float("inf")}, 2.5),
        ({"selected_value": 6}, 2.5),
        ({"selected_value": 2.25}, 2.5),
        ({"selected_value": None}, None),
    ],
)
def test_rating_rejects_invalid_frontend_state(load_component, returned, expected):
    module = load_component("rating", lambda **_kwargs: returned)
    assert module.rating(value=2.5, precision=0.5) == expected


def test_rating_cannot_be_cleared_by_frontend_when_clearable_is_false(
    load_component,
):
    module = load_component("rating", lambda **_kwargs: {"selected_value": None})
    assert module.rating(value=2.5, precision=0.5, clearable=False) == 2.5


def test_rating_canonicalizes_a_nearly_reciprocal_precision(load_component):
    calls: list[dict[str, Any]] = []

    def renderer(**kwargs):
        calls.append(kwargs)
        return kwargs["default"]

    module = load_component("rating", renderer)
    selected = module.rating(value=1 / 3, precision=0.3333333333333)

    assert selected == pytest.approx(1 / 3)
    assert calls[0]["data"]["precision"] == pytest.approx(1 / 3)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"max_value": 0},
        {"max_value": 2.5},
        {"max_value": 101},
        {"precision": 0},
        {"precision": float("inf")},
        {"precision": 2},
        {"precision": 0.3},
        {"precision": 0.001},
        {"precision": 1e-320},
        {"precision": True},
        {"value": -1},
        {"value": 6},
        {"value": 2.3, "precision": 0.5},
        {"value": True},
        {"size": "huge"},
        {"label": None},
        {"disabled": 1},
        {"read_only": "yes"},
        {"clearable": None},
        {"on_change": "not-callable"},
    ],
)
def test_rating_validates_its_contract(load_component, kwargs):
    module = load_component("rating", lambda **_kwargs: None)
    with pytest.raises((TypeError, ValueError)):
        module.rating(**kwargs)


def test_data_grid_infers_columns_and_returns_all_state(load_component):
    calls: list[dict[str, Any]] = []

    def renderer(**kwargs):
        calls.append(kwargs)
        return {
            "selected_rows": [2],
            "sort_model": [{"field": "score", "sort": "desc"}],
            "filter_model": {"items": [{"field": "active", "operator": "is"}]},
            "pagination_model": {"page": 0, "pageSize": 25},
        }

    module = load_component("data_grid", renderer)
    result = module.data_grid(
        rows=[
            {"id": 1, "name": "Ada", "score": 9.5, "active": True},
            {"id": 2, "name": "Grace", "score": 10, "active": False},
        ],
        selected_rows=[1],
        page_size=25,
        checkbox_selection=True,
        density="compact",
    )

    assert result == {
        "selected_rows": [2],
        "sort_model": [{"field": "score", "sort": "desc"}],
        "filter_model": {"items": [{"field": "active", "operator": "is"}]},
        "pagination_model": {"page": 0, "pageSize": 25},
    }
    assert calls[0]["data"]["columns"] == [
        {"field": "id", "headerName": "Id", "type": "number", "flex": 1},
        {"field": "name", "headerName": "Name", "type": "string", "flex": 1},
        {"field": "score", "headerName": "Score", "type": "number", "flex": 1},
        {"field": "active", "headerName": "Active", "type": "boolean", "flex": 1},
    ]
    assert calls[0]["data"]["pageSizeOptions"] == [10, 25, 50, 100]
    assert calls[0]["data"]["checkboxSelection"] is True
    assert calls[0]["data"]["density"] == "compact"


def test_data_grid_infers_a_stable_union_of_row_fields(load_component):
    calls: list[dict[str, Any]] = []

    def renderer(**kwargs):
        calls.append(kwargs)
        return kwargs["default"]

    module = load_component("data_grid", renderer)
    module.data_grid(
        rows=[
            {"id": 1, "name": "Ada"},
            {"id": 2, "score": 10, "name": "Grace"},
        ]
    )

    assert [column["field"] for column in calls[0]["data"]["columns"]] == [
        "id",
        "name",
        "score",
    ]
    assert calls[0]["data"]["columns"][2]["type"] == "number"


def test_data_grid_normalizes_columns_dataframe_and_composite_callback(load_component):
    calls: list[dict[str, Any]] = []

    def callback():
        pass

    class FakeDataFrame:
        def to_dict(self, orient):
            assert orient == "records"
            return [{"key": "a", "status": "new"}]

    def renderer(**kwargs):
        calls.append(kwargs)
        return kwargs["default"]

    module = load_component("data_grid", renderer)
    result = module.data_grid(
        FakeDataFrame(),
        columns=[
            {"field": "key", "header_name": "Key", "min_width": 80},
            {
                "field": "status",
                "type": "singleSelect",
                "value_options": ["new", "done"],
            },
        ],
        id_field="key",
        page_size=7,
        page_size_options=(5, 7, 5),
        disabled=True,
        on_change=callback,
    )

    assert result["pagination_model"] == {"page": 0, "pageSize": 7}
    assert calls[0]["data"]["columns"] == [
        {
            "headerName": "Key",
            "field": "key",
            "minWidth": 80,
            "type": "string",
            "flex": 1,
        },
        {
            "headerName": "Status",
            "flex": 1,
            "field": "status",
            "type": "singleSelect",
            "valueOptions": ["new", "done"],
        },
    ]
    assert calls[0]["data"]["pageSizeOptions"] == [5, 7]
    assert calls[0]["data"]["disabled"] is True
    assert calls[0]["on_grid_event_change"] is callback
    assert calls[0]["on_selected_rows_change"] is not callback
    assert calls[0]["on_sort_model_change"] is not callback
    assert calls[0]["on_filter_model_change"] is not callback


def test_data_grid_normalizes_quick_filter_and_preserves_falsey_callback(
    load_component,
):
    calls: list[dict[str, Any]] = []

    class FalseyCallback:
        def __bool__(self):
            return False

        def __call__(self):
            pass

    callback = FalseyCallback()

    def renderer(**kwargs):
        calls.append(kwargs)
        return kwargs["default"]

    module = load_component("data_grid", renderer)
    module.data_grid(
        rows=[{"id": 1, "name": "Ada"}],
        filter_model={
            "quickFilterValues": ["Ada"],
            "quickFilterLogicOperator": "or",
            "quickFilterExcludeHiddenColumns": False,
        },
        on_change=callback,
    )

    assert calls[0]["data"]["filterModel"] == {
        "items": [],
        "quickFilterValues": ["Ada"],
        "quickFilterLogicOperator": "or",
        "quickFilterExcludeHiddenColumns": False,
    }
    assert calls[0]["on_grid_event_change"] is callback


def test_data_grid_rejects_malformed_frontend_state_per_field(load_component):
    module = load_component(
        "data_grid",
        lambda **_kwargs: {
            "selected_rows": [999],
            "sort_model": [{"field": "missing", "sort": "asc"}],
            "filter_model": {"items": [{"field": "name"}]},
            "pagination_model": {"page": 20, "pageSize": 10},
        },
    )

    result = module.data_grid(
        rows=[{"id": 1, "name": "Ada"}],
        selected_rows=[1],
        sort_model=[{"field": "name", "sort": "desc"}],
        filter_model={
            "items": [{"field": "name", "operator": "contains", "value": "A"}]
        },
    )

    assert result == {
        "selected_rows": [1],
        "sort_model": [{"field": "name", "sort": "desc"}],
        "filter_model": {
            "items": [{"field": "name", "operator": "contains", "value": "A"}]
        },
        "pagination_model": {"page": 0, "pageSize": 10},
    }


def test_data_grid_accepts_valid_nondefault_frontend_pagination(load_component):
    module = load_component(
        "data_grid",
        lambda **_kwargs: {
            "pagination_model": {"page": 1, "pageSize": 10},
        },
    )
    rows = [{"id": index} for index in range(11)]

    assert module.data_grid(rows=rows)["pagination_model"] == {
        "page": 1,
        "pageSize": 10,
    }


@pytest.mark.parametrize(
    "kwargs",
    [
        {"rows": [{"name": "missing id"}]},
        {"rows": [{"id": 1}, {"id": 1.0}]},
        {"rows": [{"id": True}]},
        {"rows": [{"id": float("inf")}]},
        {"rows": [{"id": 2**53}]},
        {"rows": [{"id": 1, "unsafe": 2**53}]},
        {"rows": [{"id": 1, 2: "non-string key"}]},
        {"rows": [{"id": 1, "bad": object()}]},
        {"rows": [{"id": 1}], "selected_rows": "1"},
        {"rows": [{"id": 1}], "selected_rows": [2]},
        {"rows": [{"id": 1}], "selected_rows": [1, 1.0]},
        {
            "rows": [{"id": 1}],
            "columns": [{"field": "id", "header_name": "A", "headerName": "B"}],
        },
        {"rows": [{"id": 1}], "columns": [{"field": "id", "render_cell": "x"}]},
        {"rows": [{"id": 1}], "columns": [{"field": "id", "editable": True}]},
        {"rows": [{"id": 1}], "columns": [{"field": "id", "type": "date"}]},
        {"rows": [{"id": 1}], "columns": [{"field": "id", "width": -1}]},
        {"rows": [{"id": 1}], "columns": [{"field": "id", "align": "middle"}]},
        {"rows": [{"id": 1}], "columns": [{"field": "id", "sortable": "yes"}]},
        {
            "rows": [{"id": 1}],
            "columns": [{"field": "id", "value_options": [1]}],
        },
        {
            "rows": [{"id": 1, "status": "new"}],
            "columns": [
                {
                    "field": "status",
                    "type": "singleSelect",
                    "value_options": [{"label": "New"}],
                }
            ],
        },
        {"rows": [{"id": 1}], "sort_model": [{"field": "id", "sort": "up"}]},
        {
            "rows": [{"id": 1, "name": "Ada"}],
            "sort_model": [
                {"field": "id", "sort": "asc"},
                {"field": "name", "sort": "desc"},
            ],
        },
        {
            "rows": [{"id": 1}],
            "columns": ["id"],
            "sort_model": [{"field": "x", "sort": "asc"}],
        },
        {"rows": [{"id": 1}], "filter_model": {"items": "not-a-list"}},
        {
            "rows": [{"id": 1}],
            "filter_model": {"items": [{"field": "id"}]},
        },
        {
            "rows": [{"id": 1}],
            "filter_model": {
                "items": [
                    {"field": "id", "operator": "="},
                    {"field": "id", "operator": "!="},
                ]
            },
        },
        {
            "rows": [{"id": 1}],
            "filter_model": {"items": [], "unsupported": True},
        },
        {
            "rows": [{"id": 1}],
            "filter_model": {"items": [], "logicOperator": "xor"},
        },
        {
            "rows": [{"id": 1}],
            "columns": ["id"],
            "filter_model": {"items": [{"field": "x", "operator": "is"}]},
        },
        {"rows": [{"id": 1}], "page_size": 0},
        {"rows": [{"id": 1}], "page_size": 101},
        {"rows": [{"id": 1}], "page_size_options": []},
        {"rows": [{"id": 1}], "page_size_options": [101]},
        {"rows": [{"id": 1}], "height": 99},
        {"rows": [{"id": 1}], "density": "tiny"},
        {"rows": [{"id": 1}], "checkbox_selection": "yes"},
        {"rows": [{"id": 1}], "disabled": 1},
        {"rows": [{"id": 1}], "on_change": "not-callable"},
    ],
)
def test_data_grid_rejects_invalid_or_ambiguous_inputs(load_component, kwargs):
    module = load_component("data_grid", lambda **_kwargs: None)
    with pytest.raises((TypeError, ValueError)):
        module.data_grid(**kwargs)
