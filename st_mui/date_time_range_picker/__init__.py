"""MIT-licensed paired MUI X DateTimePicker fields for Streamlit."""

from __future__ import annotations

import warnings
from collections.abc import Callable, Mapping, Sequence
from datetime import datetime
from typing import Any

from st_mui._compat import component
from st_mui._datetime import parse_datetime, serialize_datetime
from st_mui._picker import (
    normalize_bool,
    normalize_minutes_step,
    normalize_optional_text,
    normalize_views,
)

_component = component(
    "st-mui.date_time_range_picker",
    js="index-*.js",
    html='<div class="react-root"></div>',
)

_DATETIME_VIEWS = ("year", "month", "day", "hours", "minutes", "seconds")
_DEFAULT_DATETIME_VIEWS = ("year", "day", "hours", "minutes")


def _normalize_datetime(
    value: Any, *, field: str
) -> tuple[str | None, datetime | None]:
    if value is None:
        return None, None
    if not isinstance(value, (datetime, str)):
        raise TypeError(f"{field} must be a datetime, ISO datetime string, or None")
    parsed = value if isinstance(value, datetime) else parse_datetime(value)
    if parsed is None:
        raise ValueError(f"{field} must be a valid ISO datetime string")
    parsed = parsed.replace(tzinfo=None)
    return serialize_datetime(parsed), parsed


def _normalize_range(
    value: Sequence[datetime | str | None] | None,
) -> tuple[tuple[str | None, str | None], tuple[datetime | None, datetime | None]]:
    if value is None:
        return (None, None), (None, None)
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise TypeError("value must be a two-item sequence or None")
    if len(value) != 2:
        raise ValueError("value must contain exactly two datetimes")
    start_serialized, start = _normalize_datetime(value[0], field="value[0]")
    end_serialized, end = _normalize_datetime(value[1], field="value[1]")
    if start is not None and end is not None and start > end:
        raise ValueError("range start must not exceed its end")
    return (start_serialized, end_serialized), (start, end)


def _returned_range(
    result: Any,
    *,
    fallback: tuple[datetime | None, datetime | None],
    min_datetime: datetime | None,
    max_datetime: datetime | None,
) -> tuple[datetime | None, datetime | None]:
    if not isinstance(result, Mapping):
        return fallback
    if "start_datetime" not in result or "end_datetime" not in result:
        return fallback
    try:
        _, start = _normalize_datetime(
            result.get("start_datetime"), field="start_datetime"
        )
        _, end = _normalize_datetime(result.get("end_datetime"), field="end_datetime")
    except (TypeError, ValueError):
        return fallback
    if start is not None and end is not None and start > end:
        return fallback
    if min_datetime is not None and any(
        item is not None and item < min_datetime for item in (start, end)
    ):
        return fallback
    if max_datetime is not None and any(
        item is not None and item > max_datetime for item in (start, end)
    ):
        return fallback
    return start, end


def date_time_range_picker(
    label: str = "Select date & time range",
    value: tuple[datetime | str | None, datetime | str | None] | None = None,
    min_datetime: datetime | str | None = None,
    max_datetime: datetime | str | None = None,
    ampm: bool = True,
    disabled: bool = False,
    license_key: str | None = None,
    on_change: Callable | None = None,
    key: str | None = None,
    *,
    start_label: str | None = None,
    end_label: str | None = None,
    format: str | None = None,
    helper_text: str | None = None,
    clearable: bool = False,
    read_only: bool = False,
    disable_past: bool = False,
    disable_future: bool = False,
    open_to: str | None = None,
    views: Sequence[str] | None = None,
    minutes_step: int = 1,
) -> tuple[datetime | None, datetime | None]:
    """Select a datetime range with two MIT MUI X Community fields.

    ``license_key`` remains accepted for backward compatibility but is
    deprecated and ignored. The original parameters through ``key`` retain
    their positional API; new controls are keyword-only. Returned datetimes
    remain timezone-naive wall-clock values.

    Both ``value`` datetimes must sit on the ``minutes_step`` grid; a minute
    that is not a multiple of ``minutes_step`` renders as a validation error.
    """
    if not isinstance(label, str):
        raise TypeError("label must be a string")
    normalize_optional_text(start_label, field="start_label")
    normalize_optional_text(end_label, field="end_label")
    normalize_optional_text(format, field="format")
    normalize_optional_text(helper_text, field="helper_text")
    if format == "":
        raise ValueError("format must not be empty")
    for field, option in (
        ("ampm", ampm),
        ("disabled", disabled),
        ("clearable", clearable),
        ("read_only", read_only),
        ("disable_past", disable_past),
        ("disable_future", disable_future),
    ):
        normalize_bool(option, field=field)
    if on_change is not None and not callable(on_change):
        raise TypeError("on_change must be callable or None")
    normalized_views, open_to = normalize_views(
        views,
        allowed=_DATETIME_VIEWS,
        default=_DEFAULT_DATETIME_VIEWS,
        open_to=open_to,
    )
    minutes_step = normalize_minutes_step(minutes_step)

    (start_value, end_value), default_range = _normalize_range(value)
    min_value, parsed_min = _normalize_datetime(min_datetime, field="min_datetime")
    max_value, parsed_max = _normalize_datetime(max_datetime, field="max_datetime")
    if parsed_min is not None and parsed_max is not None and parsed_min > parsed_max:
        raise ValueError("min_datetime must not exceed max_datetime")
    if parsed_min is not None and any(
        item is not None and item < parsed_min for item in default_range
    ):
        raise ValueError("value must not be earlier than min_datetime")
    if parsed_max is not None and any(
        item is not None and item > parsed_max for item in default_range
    ):
        raise ValueError("value must not be later than max_datetime")

    if license_key is not None:
        warnings.warn(
            "license_key is deprecated and ignored; date_time_range_picker now "
            "uses MUI X Community",
            DeprecationWarning,
            stacklevel=2,
        )

    def _noop():
        pass

    result = _component(
        key=key,
        default={"start_datetime": start_value, "end_datetime": end_value},
        data={
            "label": label,
            "startLabel": start_label,
            "endLabel": end_label,
            "startValue": start_value,
            "endValue": end_value,
            "minDatetime": min_value,
            "maxDatetime": max_value,
            "ampm": ampm,
            "format": format,
            "helperText": helper_text,
            "clearable": clearable,
            "readOnly": read_only,
            "disablePast": disable_past,
            "disableFuture": disable_future,
            "openTo": open_to,
            "views": normalized_views,
            "minutesStep": minutes_step,
            "disabled": disabled,
        },
        on_start_datetime_change=_noop,
        on_end_datetime_change=_noop,
        on_range_change=on_change if on_change is not None else _noop,
    )
    return _returned_range(
        result,
        fallback=default_range,
        min_datetime=parsed_min,
        max_datetime=parsed_max,
    )
