"""MUI X DatePicker component for Streamlit."""

from __future__ import annotations

from datetime import date
from typing import Callable

import streamlit as st

_component = st.components.v2.component(
    "st-mui.date_picker",
    js="index-*.js",
    html='<div class="react-root"></div>',
    isolate_styles=False,
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

    Returns
    -------
    date or None
        The selected date, or None if nothing selected.
    """
    def _serialize_date(d):
        if d is None:
            return None
        if isinstance(d, date):
            return d.isoformat()
        return str(d)

    def _noop():
        pass

    result = _component(
        key=key,
        default={"selected_date": _serialize_date(value)},
        data={
            "label": label,
            "value": _serialize_date(value),
            "minDate": _serialize_date(min_date),
            "maxDate": _serialize_date(max_date),
            "format": format,
            "disabled": disabled,
        },
        on_selected_date_change=on_change or _noop,
    )

    selected = result.get("selected_date") if result else None
    if selected:
        try:
            return date.fromisoformat(selected)
        except (ValueError, TypeError):
            return None
    return None
