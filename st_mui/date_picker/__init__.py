"""MUI X DatePicker component for Streamlit."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from datetime import date

from st_mui._compat import component
from st_mui._picker import (
    normalize_bool,
    normalize_date_value,
    normalize_optional_text,
    normalize_views,
)

_component = component(
    "st-mui.date_picker",
    js="index-*.js",
    html='<div class="react-root"></div>',
)


def date_picker(
    label: str = "Select a date",
    value: date | str | None = None,
    min_date: date | str | None = None,
    max_date: date | str | None = None,
    format: str = "MM/DD/YYYY",
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
    display_week_number: bool = False,
) -> date | None:
    """A rich date picker powered by MUI X.

    Parameters
    ----------
    label : str
        Label displayed above the picker.
    value : date or str or None
        Default date value. Accepts date object or ISO string (YYYY-MM-DD).
    min_date : date or str or None
        Minimum selectable date.
    max_date : date or str or None
        Maximum selectable date.
    format : str
        Display format string (MUI format tokens).
    disabled : bool
        Whether the picker is disabled.
    on_change : callable or None
        Callback when the selected date changes.
    key : str or None
        Unique widget key.
    helper_text : str or None
        Supporting text displayed below the input.
    clearable : bool
        Whether the selected value can be cleared.
    read_only : bool
        Whether the value can be viewed but not changed.
    disable_past, disable_future : bool
        Prevent selecting dates before or after today.
    open_to : {"year", "month", "day"} or None
        View displayed when the picker first opens.
    views : sequence of {"year", "month", "day"} or None
        Views users can navigate through.
    display_week_number : bool
        Display ISO week numbers in the calendar.

    Returns
    -------
    date or None
        The selected date, or None if nothing selected.
    """
    if not isinstance(label, str):
        raise TypeError("label must be a string")
    if not isinstance(format, str):
        raise TypeError("format must be a string")
    normalize_bool(disabled, field="disabled")
    if on_change is not None and not callable(on_change):
        raise TypeError("on_change must be callable or None")
    helper_text = normalize_optional_text(helper_text, field="helper_text")
    for name, flag in (
        ("clearable", clearable),
        ("read_only", read_only),
        ("disable_past", disable_past),
        ("disable_future", disable_future),
        ("display_week_number", display_week_number),
    ):
        normalize_bool(flag, field=name)
    normalized_views, open_to = normalize_views(
        views,
        allowed=("year", "month", "day"),
        default=("year", "month", "day"),
        open_to=open_to,
    )

    def _noop():
        pass

    serialized_value, parsed_value = normalize_date_value(value, field="value")
    min_value, parsed_min = normalize_date_value(min_date, field="min_date")
    max_value, parsed_max = normalize_date_value(max_date, field="max_date")
    if parsed_min is not None and parsed_max is not None and parsed_min > parsed_max:
        raise ValueError("min_date must not exceed max_date")
    result = _component(
        key=key,
        default={"selected_date": serialized_value},
        data={
            "label": label,
            "value": serialized_value,
            "minDate": min_value,
            "maxDate": max_value,
            "format": format,
            "disabled": disabled,
            "helperText": helper_text,
            "clearable": clearable,
            "readOnly": read_only,
            "disablePast": disable_past,
            "disableFuture": disable_future,
            "openTo": open_to,
            "views": normalized_views,
            "displayWeekNumber": display_week_number,
        },
        on_selected_date_change=on_change or _noop,
    )

    if not isinstance(result, Mapping) or "selected_date" not in result:
        return parsed_value
    selected = result.get("selected_date")
    if selected is None:
        return None if clearable else parsed_value
    try:
        _, parsed_selected = normalize_date_value(selected, field="selected_date")
    except (TypeError, ValueError):
        return parsed_value
    if parsed_min is not None and parsed_selected < parsed_min:
        return parsed_value
    if parsed_max is not None and parsed_selected > parsed_max:
        return parsed_value
    return parsed_selected
