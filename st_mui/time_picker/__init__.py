"""MUI X TimePicker component for Streamlit."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from datetime import time

from st_mui._compat import component
from st_mui._picker import (
    is_minute_aligned,
    normalize_bool,
    normalize_minutes_step,
    normalize_optional_text,
    normalize_time_value,
    normalize_views,
)

_component = component(
    "st-mui.time_picker",
    js="index-*.js",
    html='<div class="react-root"></div>',
)


def time_picker(
    label: str = "Select a time",
    value: time | str | None = None,
    ampm: bool = True,
    min_time: time | str | None = None,
    max_time: time | str | None = None,
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
) -> time | None:
    """A rich time picker powered by MUI X.

    Parameters
    ----------
    label : str
        Label displayed above the picker.
    value : time or str or None
        Default time value. Accepts time object or HH:MM string.
    ampm : bool
        Whether to use 12-hour format with AM/PM.
    min_time : time or str or None
        Minimum selectable time.
    max_time : time or str or None
        Maximum selectable time.
    disabled : bool
        Whether the picker is disabled.
    on_change : callable or None
        Callback when the selected time changes.
    key : str or None
        Unique widget key.
    helper_text : str or None
        Supporting text displayed below the input.
    clearable : bool
        Whether the selected value can be cleared.
    read_only : bool
        Whether the value can be viewed but not changed.
    disable_past, disable_future : bool
        Prevent selecting times before or after the current time.
    open_to : {"hours", "minutes", "seconds"} or None
        View displayed when the picker first opens.
    views : sequence of {"hours", "minutes", "seconds"} or None
        Clock views users can navigate through.
    minutes_step : int
        Minute increment between 1 and 60. ``value`` must sit on the same
        grid; a minute that is not a multiple of ``minutes_step`` renders as
        a validation error.
    format : str or None
        Optional MUI display format. ``None`` uses the locale default.

    Returns
    -------
    time or None
        The selected time, or None if nothing selected.
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
        allowed=("hours", "minutes", "seconds"),
        default=("hours", "minutes"),
        open_to=open_to,
    )
    minutes_step = normalize_minutes_step(minutes_step)

    def _noop():
        pass

    serialized_value, parsed_value = normalize_time_value(value, field="value")
    min_value, parsed_min = normalize_time_value(min_time, field="min_time")
    max_value, parsed_max = normalize_time_value(max_time, field="max_time")
    result = _component(
        key=key,
        default={"selected_time": serialized_value},
        data={
            "label": label,
            "value": serialized_value,
            "ampm": ampm,
            "minTime": min_value,
            "maxTime": max_value,
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
        on_selected_time_change=on_change or _noop,
    )

    if not isinstance(result, Mapping) or "selected_time" not in result:
        return parsed_value
    selected = result.get("selected_time")
    if selected is None:
        return None if clearable else parsed_value
    try:
        _, parsed_selected = normalize_time_value(
            selected, field="selected_time", reject_timezone=True
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
