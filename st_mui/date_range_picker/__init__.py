"""MIT-licensed paired MUI X DatePicker fields for Streamlit."""

from __future__ import annotations

import warnings
from collections.abc import Callable, Mapping, Sequence
from datetime import date, datetime
from typing import Any

from st_mui._compat import component
from st_mui._picker import normalize_bool, normalize_optional_text, normalize_views

_component = component(
    "st-mui.date_range_picker",
    js="index-*.js",
    html='<div class="react-root"></div>',
)

_DATE_VIEWS = ("year", "month", "day")


def _normalize_date(value: Any, *, field: str) -> tuple[str | None, date | None]:
    if value is None:
        return None, None
    if isinstance(value, datetime):
        raise TypeError(f"{field} must be a date, ISO date string, or None")
    if isinstance(value, date):
        parsed = value
    elif isinstance(value, str):
        try:
            parsed = date.fromisoformat(value)
        except ValueError as exc:
            raise ValueError(
                f"{field} must be an ISO date string (YYYY-MM-DD)"
            ) from exc
    else:
        raise TypeError(f"{field} must be a date, ISO date string, or None")
    return parsed.isoformat(), parsed


def _normalize_range(
    value: Sequence[date | str | None] | None,
) -> tuple[tuple[str | None, str | None], tuple[date | None, date | None]]:
    if value is None:
        return (None, None), (None, None)
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise TypeError("value must be a two-item sequence or None")
    if len(value) != 2:
        raise ValueError("value must contain exactly two dates")
    start_serialized, start = _normalize_date(value[0], field="value[0]")
    end_serialized, end = _normalize_date(value[1], field="value[1]")
    if start is not None and end is not None and start > end:
        raise ValueError("range start must not exceed its end")
    return (start_serialized, end_serialized), (start, end)


def _returned_range(
    result: Any,
    *,
    fallback: tuple[date | None, date | None],
    min_date: date | None,
    max_date: date | None,
) -> tuple[date | None, date | None]:
    if not isinstance(result, Mapping):
        return fallback
    if "start_date" not in result or "end_date" not in result:
        return fallback
    try:
        _, start = _normalize_date(result.get("start_date"), field="start_date")
        _, end = _normalize_date(result.get("end_date"), field="end_date")
    except (TypeError, ValueError):
        return fallback
    if start is not None and end is not None and start > end:
        return fallback
    if min_date is not None and any(
        item is not None and item < min_date for item in (start, end)
    ):
        return fallback
    if max_date is not None and any(
        item is not None and item > max_date for item in (start, end)
    ):
        return fallback
    return start, end


def date_range_picker(
    label: str = "Select date range",
    value: tuple[date | str | None, date | str | None] | None = None,
    min_date: date | str | None = None,
    max_date: date | str | None = None,
    calendars: int = 2,
    disabled: bool = False,
    license_key: str | None = None,
    on_change: Callable | None = None,
    key: str | None = None,
    *,
    start_label: str | None = None,
    end_label: str | None = None,
    format: str = "MM/DD/YYYY",
    helper_text: str | None = None,
    clearable: bool = False,
    read_only: bool = False,
    disable_past: bool = False,
    disable_future: bool = False,
    open_to: str | None = None,
    views: Sequence[str] | None = None,
    display_week_number: bool = False,
) -> tuple[date | None, date | None]:
    """Select a date range with two MIT-licensed MUI X Community fields.

    ``calendars`` remains accepted for source compatibility, but paired
    Community ``DatePicker`` fields cannot control the number of simultaneously
    visible calendar panels, so the value is intentionally ignored.
    ``license_key`` is deprecated and ignored because this implementation no
    longer uses MUI X Pro.

    The original parameters through ``key`` retain their positional API. New
    display and interaction controls are keyword-only.
    """
    if not isinstance(label, str):
        raise TypeError("label must be a string")
    if not isinstance(format, str):
        raise TypeError("format must be a string")
    if not format:
        raise ValueError("format must not be empty")
    normalize_optional_text(start_label, field="start_label")
    normalize_optional_text(end_label, field="end_label")
    normalize_optional_text(helper_text, field="helper_text")
    for field, option in (
        ("disabled", disabled),
        ("clearable", clearable),
        ("read_only", read_only),
        ("disable_past", disable_past),
        ("disable_future", disable_future),
        ("display_week_number", display_week_number),
    ):
        normalize_bool(option, field=field)
    if on_change is not None and not callable(on_change):
        raise TypeError("on_change must be callable or None")
    normalized_views, open_to = normalize_views(
        views,
        allowed=_DATE_VIEWS,
        default=_DATE_VIEWS,
        open_to=open_to,
    )

    (start_value, end_value), default_range = _normalize_range(value)
    min_value, parsed_min = _normalize_date(min_date, field="min_date")
    max_value, parsed_max = _normalize_date(max_date, field="max_date")
    if parsed_min is not None and parsed_max is not None and parsed_min > parsed_max:
        raise ValueError("min_date must not exceed max_date")
    if parsed_min is not None and any(
        item is not None and item < parsed_min for item in default_range
    ):
        raise ValueError("value must not be earlier than min_date")
    if parsed_max is not None and any(
        item is not None and item > parsed_max for item in default_range
    ):
        raise ValueError("value must not be later than max_date")

    if license_key is not None:
        warnings.warn(
            "license_key is deprecated and ignored; date_range_picker now uses "
            "MUI X Community",
            DeprecationWarning,
            stacklevel=2,
        )
    # Kept intentionally to preserve calls that used this historical argument.
    del calendars

    def _noop():
        pass

    result = _component(
        key=key,
        default={"start_date": start_value, "end_date": end_value},
        data={
            "label": label,
            "startLabel": start_label,
            "endLabel": end_label,
            "startValue": start_value,
            "endValue": end_value,
            "minDate": min_value,
            "maxDate": max_value,
            "format": format,
            "helperText": helper_text,
            "clearable": clearable,
            "readOnly": read_only,
            "disablePast": disable_past,
            "disableFuture": disable_future,
            "openTo": open_to,
            "views": normalized_views,
            "displayWeekNumber": display_week_number,
            "disabled": disabled,
        },
        on_start_date_change=_noop,
        on_end_date_change=_noop,
        on_range_change=on_change if on_change is not None else _noop,
    )
    return _returned_range(
        result,
        fallback=default_range,
        min_date=parsed_min,
        max_date=parsed_max,
    )
