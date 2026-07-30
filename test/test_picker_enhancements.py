"""Regression coverage for the Community picker enhancement APIs."""

from __future__ import annotations

import importlib
import inspect
import sys
from collections.abc import Callable
from datetime import date, datetime, time
from typing import Any

import pytest

from st_mui import _compat


@pytest.fixture
def load_picker(monkeypatch):
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


@pytest.mark.parametrize(
    ("module_name", "function_name", "positional_names"),
    [
        (
            "date_picker",
            "date_picker",
            [
                "label",
                "value",
                "min_date",
                "max_date",
                "format",
                "disabled",
                "on_change",
                "key",
            ],
        ),
        (
            "time_picker",
            "time_picker",
            [
                "label",
                "value",
                "ampm",
                "min_time",
                "max_time",
                "disabled",
                "on_change",
                "key",
            ],
        ),
        (
            "date_time_picker",
            "date_time_picker",
            [
                "label",
                "value",
                "min_datetime",
                "max_datetime",
                "ampm",
                "disabled",
                "on_change",
                "key",
            ],
        ),
    ],
)
def test_existing_picker_parameters_remain_positional(
    load_picker,
    module_name: str,
    function_name: str,
    positional_names: list[str],
):
    module = load_picker(module_name, lambda **kwargs: kwargs["default"])
    parameters = list(
        inspect.signature(getattr(module, function_name)).parameters.values()
    )

    assert [parameter.name for parameter in parameters[:8]] == positional_names
    assert all(
        parameter.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
        for parameter in parameters[:8]
    )
    assert all(
        parameter.kind is inspect.Parameter.KEYWORD_ONLY for parameter in parameters[8:]
    )


def test_date_picker_forwards_enhancement_props_and_callback(load_picker):
    calls: list[dict[str, Any]] = []

    def renderer(**kwargs: Any):
        calls.append(kwargs)
        return {"selected_date": "2026-08-03"}

    callback = lambda: None
    module = load_picker("date_picker", renderer)
    selected = module.date_picker(
        value=date(2026, 8, 1),
        helper_text="Choose a workday",
        clearable=False,
        read_only=True,
        disable_past=True,
        disable_future=False,
        open_to="month",
        views=("year", "month"),
        display_week_number=True,
        on_change=callback,
    )

    assert selected == date(2026, 8, 3)
    assert calls[0]["data"] == {
        "label": "Select a date",
        "value": "2026-08-01",
        "minDate": None,
        "maxDate": None,
        "format": "MM/DD/YYYY",
        "disabled": False,
        "helperText": "Choose a workday",
        "clearable": False,
        "readOnly": True,
        "disablePast": True,
        "disableFuture": False,
        "openTo": "month",
        "views": ["year", "month"],
        "displayWeekNumber": True,
    }
    assert calls[0]["on_selected_date_change"] is callback


@pytest.mark.parametrize(
    ("module_name", "function_name", "value", "state_name", "expected_data"),
    [
        (
            "time_picker",
            "time_picker",
            time(9, 30),
            "selected_time",
            {
                "openTo": "seconds",
                "views": ["hours", "minutes", "seconds"],
                "minutesStep": 15,
                "format": "HH:mm",
            },
        ),
        (
            "date_time_picker",
            "date_time_picker",
            datetime.fromisoformat("2026-08-01T09:30:00"),
            "selected_datetime",
            {
                "openTo": "minutes",
                "views": ["day", "hours", "minutes"],
                "minutesStep": 15,
                "format": "MM/DD/YYYY HH:mm",
            },
        ),
    ],
)
def test_time_based_pickers_forward_enhancement_props(
    load_picker,
    module_name: str,
    function_name: str,
    value: time | datetime,
    state_name: str,
    expected_data: dict[str, Any],
):
    calls: list[dict[str, Any]] = []

    def renderer(**kwargs: Any):
        calls.append(kwargs)
        return kwargs["default"]

    callback = lambda: None
    module = load_picker(module_name, renderer)
    selected = getattr(module, function_name)(
        value=value,
        helper_text="Quarter hours",
        clearable=False,
        read_only=True,
        disable_past=True,
        disable_future=False,
        open_to=expected_data["openTo"],
        views=expected_data["views"],
        minutes_step=15,
        format=expected_data["format"],
        on_change=callback,
    )

    assert selected == value
    data = calls[0]["data"]
    assert {
        "openTo": data["openTo"],
        "views": data["views"],
        "minutesStep": data["minutesStep"],
        "format": data["format"],
    } == expected_data
    assert data["helperText"] == "Quarter hours"
    assert data["clearable"] is False
    assert data["readOnly"] is True
    assert data["disablePast"] is True
    assert data["disableFuture"] is False
    assert calls[0][f"on_{state_name}_change"] is callback


@pytest.mark.parametrize(
    ("module_name", "function_name", "value", "state_name"),
    [
        ("date_picker", "date_picker", date(2026, 8, 1), "selected_date"),
        ("time_picker", "time_picker", time(9, 30), "selected_time"),
        (
            "date_time_picker",
            "date_time_picker",
            datetime.fromisoformat("2026-08-01T09:30:00"),
            "selected_datetime",
        ),
    ],
)
def test_non_clearable_picker_rejects_cleared_frontend_state(
    load_picker,
    module_name: str,
    function_name: str,
    value: date | time | datetime,
    state_name: str,
):
    module = load_picker(module_name, lambda **_kwargs: {state_name: None})

    assert getattr(module, function_name)(value=value, clearable=False) == value
    assert getattr(module, function_name)(value=value, clearable=True) is None


@pytest.mark.parametrize(
    ("module_name", "function_name", "kwargs", "error", "message"),
    [
        (
            "date_picker",
            "date_picker",
            {"helper_text": 3},
            TypeError,
            "helper_text must be a string or None",
        ),
        (
            "date_picker",
            "date_picker",
            {"clearable": 1},
            TypeError,
            "clearable must be a boolean",
        ),
        (
            "date_picker",
            "date_picker",
            {"views": "day"},
            TypeError,
            "views must be a sequence",
        ),
        (
            "date_picker",
            "date_picker",
            {"views": ["day", "day"]},
            ValueError,
            "duplicate view",
        ),
        (
            "date_picker",
            "date_picker",
            {"views": ["year"], "open_to": "day"},
            ValueError,
            "open_to must be included in views",
        ),
        (
            "time_picker",
            "time_picker",
            {"open_to": "seconds"},
            ValueError,
            "open_to must be included in views",
        ),
        (
            "time_picker",
            "time_picker",
            {"minutes_step": True},
            TypeError,
            "minutes_step must be an integer",
        ),
        (
            "time_picker",
            "time_picker",
            {"minutes_step": 0},
            ValueError,
            "minutes_step must be between 1 and 60",
        ),
        (
            "date_time_picker",
            "date_time_picker",
            {"minutes_step": 61},
            ValueError,
            "minutes_step must be between 1 and 60",
        ),
        (
            "date_time_picker",
            "date_time_picker",
            {"views": ["week"]},
            ValueError,
            r"views\[0\] must be one of",
        ),
        (
            "time_picker",
            "time_picker",
            {"format": 24},
            TypeError,
            "format must be a string or None",
        ),
        (
            "date_time_picker",
            "date_time_picker",
            {"read_only": "yes"},
            TypeError,
            "read_only must be a boolean",
        ),
    ],
)
def test_picker_enhancement_validation(
    load_picker,
    module_name: str,
    function_name: str,
    kwargs: dict[str, Any],
    error: type[Exception],
    message: str,
):
    module = load_picker(module_name, lambda **call: call["default"])

    with pytest.raises(error, match=message):
        getattr(module, function_name)(**kwargs)
