"""MUI X DateRangePicker component for Streamlit (Pro)."""

from __future__ import annotations

import os
from datetime import date
from typing import Callable

import streamlit as st

_component = st.components.v2.component(
    "st-mui.date_range_picker",
    js="index-*.js",
    html='<div class="react-root"></div>',
    isolate_styles=False,
)


def _get_license_key(license_key: str | None) -> str | None:
    """Resolve license key: explicit param > env var > None."""
    return license_key or os.environ.get("ST_MUI_LICENSE_KEY")


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
) -> tuple[date | None, date | None]:
    """A date range picker powered by MUI X (Pro).

    Works in evaluation mode without a license key (watermark shown).
    Provide a license key via the ``license_key`` parameter or the
    ``ST_MUI_LICENSE_KEY`` environment variable to remove the watermark.

    Parameters
    ----------
    label : str
        Label displayed above the picker.
    value : tuple of (date/str/None, date/str/None) or None
        Default date range. Accepts date objects or ISO strings.
    min_date : date or str or None
        Minimum selectable date.
    max_date : date or str or None
        Maximum selectable date.
    calendars : int
        Number of calendar panels to display (1 or 2).
    disabled : bool
        Whether the picker is disabled.
    license_key : str or None
        MUI X Pro license key. Falls back to ST_MUI_LICENSE_KEY env var.
    on_change : callable or None
        Callback when the selected date range changes.
    key : str or None
        Unique widget key.

    Returns
    -------
    tuple of (date or None, date or None)
        The selected start and end dates, or (None, None).
    """

    def _serialize_date(d):
        if d is None:
            return None
        if isinstance(d, date):
            return d.isoformat()
        return str(d)

    start_val = None
    end_val = None
    if value is not None:
        start_val = _serialize_date(value[0])
        end_val = _serialize_date(value[1])

    def _noop():
        pass

    result = _component(
        key=key,
        default={"start_date": start_val, "end_date": end_val},
        data={
            "label": label,
            "startValue": start_val,
            "endValue": end_val,
            "minDate": _serialize_date(min_date),
            "maxDate": _serialize_date(max_date),
            "calendars": calendars,
            "disabled": disabled,
            "licenseKey": _get_license_key(license_key),
        },
        on_start_date_change=on_change or _noop,
        on_end_date_change=_noop,
    )

    def _parse_date(val):
        if not val:
            return None
        try:
            return date.fromisoformat(val)
        except (ValueError, TypeError):
            return None

    if result:
        return (_parse_date(result.get("start_date")), _parse_date(result.get("end_date")))
    return (None, None)
