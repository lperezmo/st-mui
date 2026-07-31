"""Behavioral regression tests for the Python component wrappers."""

# Picker values intentionally exercise timezone-naive wall-clock datetimes.
# ruff: noqa: DTZ001

from __future__ import annotations

import importlib
import sys
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any

import pytest

from st_mui import _compat
from st_mui._datetime import parse_datetime, serialize_datetime


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


def test_parse_datetime_accepts_javascript_utc_suffix():
    """Python 3.10 rejects ``Z`` natively, so normalize old frontend state."""
    assert parse_datetime("2026-07-30T16:00:00.000Z") == datetime(
        2026, 7, 30, 16, 0, tzinfo=timezone.utc
    )


def test_serialize_datetime_ignores_timezone_offsets():
    assert (
        serialize_datetime(datetime(2026, 7, 30, 9, 15, tzinfo=timezone.utc))
        == "2026-07-30T09:15:00"
    )
    assert serialize_datetime("2026-07-30T09:15:00+05:00") == "2026-07-30T09:15:00"


def test_datetime_picker_round_trips_naive_wall_clock_value(load_component):
    calls: list[dict[str, Any]] = []

    def renderer(**kwargs: Any):
        calls.append(kwargs)
        return {"selected_datetime": "2026-07-30T09:15:42.123"}

    module = load_component("date_time_picker", renderer)
    selected = module.date_time_picker(value=datetime(2026, 7, 30, 8, 0))

    assert calls[0]["data"]["value"] == "2026-07-30T08:00:00"
    assert selected == datetime(2026, 7, 30, 9, 15, 42, 123000)
    assert selected.tzinfo is None


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
def test_range_on_change_uses_single_range_event(
    load_component,
    module_name: str,
    function_name: str,
    start_callback: str,
    end_callback: str,
):
    calls: list[dict[str, Any]] = []
    callback_calls: list[None] = []

    def renderer(**kwargs: Any):
        calls.append(kwargs)
        return kwargs["default"]

    def on_change():
        callback_calls.append(None)

    module = load_component(module_name, renderer)
    getattr(module, function_name)(on_change=on_change)

    render_call = calls[0]
    assert render_call["on_range_change"] is on_change
    assert render_call[start_callback] is not on_change
    assert render_call[end_callback] is not on_change

    render_call[start_callback]()
    render_call[end_callback]()
    assert callback_calls == []

    render_call["on_range_change"]()
    assert callback_calls == [None]
