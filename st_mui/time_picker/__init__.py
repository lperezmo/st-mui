"""MUI X TimePicker component for Streamlit."""

from __future__ import annotations

from datetime import time
from typing import Callable

import streamlit as st

_component = st.components.v2.component(
    "st-mui.time_picker",
    js="index-*.js",
    html='<div class="react-root"></div>',
    isolate_styles=False,
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

    Returns
    -------
    time or None
        The selected time, or None if nothing selected.
    """
    def _serialize_time(t):
        if t is None:
            return None
        if isinstance(t, time):
            return t.isoformat()
        return str(t)

    def _noop():
        pass

    result = _component(
        key=key,
        default={"selected_time": _serialize_time(value)},
        data={
            "label": label,
            "value": _serialize_time(value),
            "ampm": ampm,
            "minTime": _serialize_time(min_time),
            "maxTime": _serialize_time(max_time),
            "disabled": disabled,
        },
        on_selected_time_change=on_change or _noop,
    )

    selected = result.get("selected_time") if result else None
    if selected:
        try:
            return time.fromisoformat(selected)
        except (ValueError, TypeError):
            return None
    return None
