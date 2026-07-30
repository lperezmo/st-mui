"""MUI X DateTimePicker component for Streamlit."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from datetime import datetime

from st_mui._compat import component
from st_mui._datetime import parse_datetime, serialize_datetime
from st_mui._picker import (
    normalize_bool,
    normalize_minutes_step,
    normalize_optional_text,
    normalize_views,
)

_component = component(
    "st-mui.date_time_picker",
    js="index-*.js",
    html='<div class="react-root"></div>',
)


def date_time_picker(
    label: str = "Select date & time",
    value: datetime | str | None = None,
    min_datetime: datetime | str | None = None,
    max_datetime: datetime | str | None = None,
    ampm: bool = True,
    disabled: bool = False,
    on_change: Callable | None = None,
    key: str | None = None,
    *,
    helper_text: str | None = None,
    clearable: bool = True,
    read_only: bool = False,
    disable_past: bool = False,
    disable_future: bool = False,
    open_to: str | None = None,
    views: Sequence[str] | None = None,
    minutes_step: int = 1,
    format: str | None = None,
) -> datetime | None:
    """A rich date-time picker powered by MUI X.

    Parameters
    ----------
    label : str
        Label displayed above the picker.
    value : datetime or str or None
        Default datetime value. Accepts datetime object or ISO string.
    min_datetime : datetime or str or None
        Minimum selectable datetime.
    max_datetime : datetime or str or None
        Maximum selectable datetime.
    ampm : bool
        Whether to use 12-hour format with AM/PM.
    disabled : bool
        Whether the picker is disabled.
    on_change : callable or None
        Callback when the selected datetime changes.
    key : str or None
        Unique widget key.
    helper_text : str or None
        Supporting text displayed below the input.
    clearable : bool
        Whether the selected value can be cleared.
    read_only : bool
        Whether the value can be viewed but not changed.
    disable_past, disable_future : bool
        Prevent selecting values before or after the current instant.
    open_to : {"year", "month", "day", "hours", "minutes", "seconds"} or None
        View displayed when the picker first opens.
    views : sequence of supported date/time views or None
        Views users can navigate through.
    minutes_step : int
        Minute increment between 1 and 60.
    format : str or None
        Optional MUI display format. ``None`` uses the locale default.

    Returns
    -------
    datetime or None
        The selected timezone-naive wall-clock datetime, or None.
    """
    if not isinstance(label, str):
        raise TypeError("label must be a string")
    normalize_bool(ampm, field="ampm")
    normalize_bool(disabled, field="disabled")
    if on_change is not None and not callable(on_change):
        raise TypeError("on_change must be callable or None")
    helper_text = normalize_optional_text(helper_text, field="helper_text")
    format = normalize_optional_text(format, field="format")
    for name, flag in (
        ("clearable", clearable),
        ("read_only", read_only),
        ("disable_past", disable_past),
        ("disable_future", disable_future),
    ):
        normalize_bool(flag, field=name)
    normalized_views, open_to = normalize_views(
        views,
        allowed=("year", "month", "day", "hours", "minutes", "seconds"),
        default=("year", "day", "hours", "minutes"),
        open_to=open_to,
    )
    minutes_step = normalize_minutes_step(minutes_step)

    def _noop():
        pass

    serialized_value = serialize_datetime(value)
    result = _component(
        key=key,
        default={"selected_datetime": serialized_value},
        data={
            "label": label,
            "value": serialize_datetime(value),
            "minDatetime": serialize_datetime(min_datetime),
            "maxDatetime": serialize_datetime(max_datetime),
            "ampm": ampm,
            "disabled": disabled,
            "helperText": helper_text,
            "clearable": clearable,
            "readOnly": read_only,
            "disablePast": disable_past,
            "disableFuture": disable_future,
            "openTo": open_to,
            "views": normalized_views,
            "minutesStep": minutes_step,
            "format": format,
        },
        on_selected_datetime_change=on_change or _noop,
    )

    selected = result.get("selected_datetime") if result else None
    if selected is None and not clearable and serialized_value is not None:
        selected = serialized_value
    return parse_datetime(selected)
