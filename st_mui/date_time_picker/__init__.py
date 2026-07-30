"""MUI X DateTimePicker component for Streamlit."""

from __future__ import annotations

from datetime import datetime
from typing import Callable

from st_mui._compat import component
from st_mui._datetime import parse_datetime, serialize_datetime

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

    Returns
    -------
    datetime or None
        The selected timezone-naive wall-clock datetime, or None.
    """
    def _noop():
        pass

    result = _component(
        key=key,
        default={"selected_datetime": serialize_datetime(value)},
        data={
            "label": label,
            "value": serialize_datetime(value),
            "minDatetime": serialize_datetime(min_datetime),
            "maxDatetime": serialize_datetime(max_datetime),
            "ampm": ampm,
            "disabled": disabled,
        },
        on_selected_datetime_change=on_change or _noop,
    )

    selected = result.get("selected_datetime") if result else None
    return parse_datetime(selected)
