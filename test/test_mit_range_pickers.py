"""Regression tests for the MIT Community range-picker wrappers."""

# Range pickers intentionally preserve naive local wall-clock datetimes.
# ruff: noqa: DTZ001

from __future__ import annotations

import importlib
import inspect
import sys
from collections.abc import Callable
from datetime import date, datetime
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


@pytest.mark.parametrize(
    ("module_name", "function_name"),
    [
        ("date_range_picker", "date_range_picker"),
        ("date_time_range_picker", "date_time_range_picker"),
    ],
)
def test_new_options_are_keyword_only(load_component, module_name, function_name):
    module = load_component(module_name, lambda **kwargs: kwargs["default"])
    parameters = inspect.signature(getattr(module, function_name)).parameters

    assert parameters["key"].kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert parameters["start_label"].kind is inspect.Parameter.KEYWORD_ONLY
    assert parameters["views"].kind is inspect.Parameter.KEYWORD_ONLY


def test_date_range_maps_all_community_props_and_ignores_pro_args(load_component):
    calls: list[dict[str, Any]] = []

    def renderer(**kwargs: Any):
        calls.append(kwargs)
        return kwargs["default"]

    module = load_component("date_range_picker", renderer)
    with pytest.warns(DeprecationWarning, match="ignored"):
        selected = module.date_range_picker(
            "Trip",
            (date(2026, 8, 1), "2026-08-05"),
            "2026-07-01",
            date(2026, 9, 1),
            3,
            False,
            "old-pro-key",
            None,
            "trip",
            start_label="Depart",
            end_label="Return",
            format="DD MMM YYYY",
            helper_text="Local dates",
            clearable=True,
            read_only=True,
            disable_past=True,
            disable_future=False,
            open_to="month",
            views=("year", "month", "day"),
            display_week_number=True,
        )

    assert selected == (date(2026, 8, 1), date(2026, 8, 5))
    assert calls[0]["key"] == "trip"
    assert calls[0]["data"] == {
        "label": "Trip",
        "startLabel": "Depart",
        "endLabel": "Return",
        "startValue": "2026-08-01",
        "endValue": "2026-08-05",
        "minDate": "2026-07-01",
        "maxDate": "2026-09-01",
        "format": "DD MMM YYYY",
        "helperText": "Local dates",
        "clearable": True,
        "readOnly": True,
        "disablePast": True,
        "disableFuture": False,
        "openTo": "month",
        "views": ["year", "month", "day"],
        "displayWeekNumber": True,
        "disabled": False,
    }
    assert "licenseKey" not in calls[0]["data"]
    assert "calendars" not in calls[0]["data"]


def test_datetime_range_maps_all_community_props(load_component):
    calls: list[dict[str, Any]] = []

    def renderer(**kwargs: Any):
        calls.append(kwargs)
        return {
            "start_datetime": "2026-08-01T09:15:00.000",
            "end_datetime": "2026-08-01T10:45:00.000",
        }

    module = load_component("date_time_range_picker", renderer)
    selected = module.date_time_range_picker(
        value=("2026-08-01T08:00:00+04:00", datetime(2026, 8, 1, 11)),
        min_datetime=datetime(2026, 8, 1, 7),
        max_datetime="2026-08-01T12:00:00",
        ampm=False,
        start_label="Opens",
        end_label="Closes",
        format="YYYY-MM-DD HH:mm",
        helper_text="Office time",
        clearable=True,
        read_only=True,
        disable_past=False,
        disable_future=True,
        open_to="hours",
        views=("day", "hours", "minutes"),
        minutes_step=15,
    )

    assert selected == (
        datetime(2026, 8, 1, 9, 15),
        datetime(2026, 8, 1, 10, 45),
    )
    assert calls[0]["data"] == {
        "label": "Select date & time range",
        "startLabel": "Opens",
        "endLabel": "Closes",
        "startValue": "2026-08-01T08:00:00",
        "endValue": "2026-08-01T11:00:00",
        "minDatetime": "2026-08-01T07:00:00",
        "maxDatetime": "2026-08-01T12:00:00",
        "ampm": False,
        "format": "YYYY-MM-DD HH:mm",
        "helperText": "Office time",
        "clearable": True,
        "readOnly": True,
        "disablePast": False,
        "disableFuture": True,
        "openTo": "hours",
        "views": ["day", "hours", "minutes"],
        "minutesStep": 15,
        "disabled": False,
    }
    assert "licenseKey" not in calls[0]["data"]


@pytest.mark.parametrize(
    ("module_name", "function_name", "kwargs", "error", "message"),
    [
        (
            "date_range_picker",
            "date_range_picker",
            {"value": ("2026-08-02", "2026-08-01")},
            ValueError,
            "start",
        ),
        (
            "date_range_picker",
            "date_range_picker",
            {"value": ("2026-08-01",)},
            ValueError,
            "exactly two",
        ),
        (
            "date_range_picker",
            "date_range_picker",
            {"min_date": "2026-08-02", "max_date": "2026-08-01"},
            ValueError,
            "min_date",
        ),
        (
            "date_range_picker",
            "date_range_picker",
            {"value": ("not-a-date", None)},
            ValueError,
            "ISO date",
        ),
        (
            "date_range_picker",
            "date_range_picker",
            {"open_to": "month", "views": ("year", "day")},
            ValueError,
            "included",
        ),
        (
            "date_range_picker",
            "date_range_picker",
            {"disabled": 1},
            TypeError,
            "boolean",
        ),
        (
            "date_time_range_picker",
            "date_time_range_picker",
            {"value": ("2026-08-01T10:00", "2026-08-01T09:00")},
            ValueError,
            "start",
        ),
        (
            "date_time_range_picker",
            "date_time_range_picker",
            {"minutes_step": 0},
            ValueError,
            "between",
        ),
        (
            "date_time_range_picker",
            "date_time_range_picker",
            {"views": ("day", "banana")},
            ValueError,
            "views",
        ),
        (
            "date_time_range_picker",
            "date_time_range_picker",
            {"clearable": "yes"},
            TypeError,
            "boolean",
        ),
    ],
)
def test_invalid_range_configuration_is_rejected(
    load_component, module_name, function_name, kwargs, error, message
):
    module = load_component(module_name, lambda **options: options["default"])
    with pytest.raises(error, match=message):
        getattr(module, function_name)(**kwargs)


@pytest.mark.parametrize(
    ("module_name", "function_name", "kwargs"),
    [
        (
            "date_range_picker",
            "date_range_picker",
            {
                "value": ("2026-08-02", "2026-08-03"),
                "min_date": "2026-08-01",
                "max_date": "2026-08-04",
            },
        ),
        (
            "date_time_range_picker",
            "date_time_range_picker",
            {
                "value": ("2026-08-02T09:00", "2026-08-02T10:00"),
                "min_datetime": "2026-08-02T08:00",
                "max_datetime": "2026-08-02T11:00",
            },
        ),
    ],
)
def test_malformed_or_out_of_bounds_frontend_state_falls_back(
    load_component, module_name, function_name, kwargs
):
    outputs = iter(
        [
            {"unexpected": "shape"},
            {
                "start_date": "2026-08-04",
                "end_date": "2026-08-01",
                "start_datetime": "2026-08-02T12:00",
                "end_datetime": "2026-08-02T07:00",
            },
        ]
    )

    module = load_component(module_name, lambda **_options: next(outputs))
    expected = getattr(module, function_name)(**kwargs)
    assert expected == getattr(module, function_name)(**kwargs)


@pytest.mark.parametrize(
    ("module_name", "function_name", "start_key", "end_key"),
    [
        ("date_range_picker", "date_range_picker", "start_date", "end_date"),
        (
            "date_time_range_picker",
            "date_time_range_picker",
            "start_datetime",
            "end_datetime",
        ),
    ],
)
def test_cleared_frontend_range_returns_none_pair(
    load_component, module_name, function_name, start_key, end_key
):
    module = load_component(
        module_name, lambda **_options: {start_key: None, end_key: None}
    )
    assert getattr(module, function_name)(clearable=True) == (None, None)


def test_datetime_range_rejects_off_step_frontend_state(load_component):
    module = load_component(
        "date_time_range_picker",
        lambda **_options: {
            "start_datetime": "2026-08-02T09:10:00",
            "end_datetime": "2026-08-02T10:00:00",
        },
    )

    assert module.date_time_range_picker(
        value=("2026-08-02T09:15:00", "2026-08-02T10:00:00"),
        minutes_step=15,
    ) == (
        datetime(2026, 8, 2, 9, 15),
        datetime(2026, 8, 2, 10),
    )


@pytest.mark.parametrize(
    ("module_name", "function_name", "start_callback", "end_callback"),
    [
        (
            "date_range_picker",
            "date_range_picker",
            "on_start_date_change",
            "on_end_date_change",
        ),
        (
            "date_time_range_picker",
            "date_time_range_picker",
            "on_start_datetime_change",
            "on_end_datetime_change",
        ),
    ],
)
def test_only_composite_range_trigger_receives_callback(
    load_component, module_name, function_name, start_callback, end_callback
):
    calls: list[dict[str, Any]] = []
    callback = lambda: None
    module = load_component(
        module_name,
        lambda **kwargs: calls.append(kwargs) or kwargs["default"],
    )

    getattr(module, function_name)(on_change=callback)

    assert calls[0]["on_range_change"] is callback
    assert calls[0][start_callback] is not callback
    assert calls[0][end_callback] is not callback
