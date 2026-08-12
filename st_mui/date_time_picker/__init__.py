"""MUI X DateTimePicker component for Streamlit."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from datetime import datetime

from st_mui._compat import component
from st_mui._datetime import normalize_datetime_value
from st_mui._picker import (
    is_minute_aligned,
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
        Minute increment between 1 and 60. ``value`` must sit on the same
        grid; a minute that is not a multiple of ``minutes_step`` renders as
        a validation error. Round dynamic defaults such as ``datetime.now()``
        up to the next boundary, and hold them in ``st.session_state`` so a
        rerun does not replace the user's in-progress selection.
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

    serialized_value, parsed_value = normalize_datetime_value(value, field="value")
    min_value, parsed_min = normalize_datetime_value(min_datetime, field="min_datetime")
    max_value, parsed_max = normalize_datetime_value(max_datetime, field="max_datetime")
    if parsed_min is not None and parsed_max is not None and parsed_min > parsed_max:
        raise ValueError("min_datetime must not exceed max_datetime")
    result = _component(
        key=key,
        default={"selected_datetime": serialized_value},
        data={
            "label": label,
            "value": serialized_value,
            "minDatetime": min_value,
            "maxDatetime": max_value,
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

    if not isinstance(result, Mapping) or "selected_datetime" not in result:
        return parsed_value
    selected = result.get("selected_datetime")
    if selected is None:
        return None if clearable else parsed_value
    try:
        _, parsed_selected = normalize_datetime_value(
            selected, field="selected_datetime", reject_timezone=True
        )
    except (TypeError, ValueError):
        return parsed_value
    if parsed_min is not None and parsed_selected < parsed_min:
        return parsed_value
    if parsed_max is not None and parsed_selected > parsed_max:
        return parsed_value
    if not is_minute_aligned(parsed_selected, minutes_step):
        return parsed_value
    return parsed_selected
