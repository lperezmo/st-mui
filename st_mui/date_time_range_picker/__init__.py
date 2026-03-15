"""MUI X DateTimeRangePicker component for Streamlit (Pro)."""

from __future__ import annotations

import os
from datetime import datetime
from typing import Callable

import streamlit as st

_component = st.components.v2.component(
    "st-mui.date_time_range_picker",
    js="index-*.js",
    html='<div class="react-root"></div>',
    isolate_styles=False,
)


def _get_license_key(license_key: str | None) -> str | None:
    """Resolve license key: explicit param > env var > None."""
    return license_key or os.environ.get("ST_MUI_LICENSE_KEY")


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
) -> tuple[datetime | None, datetime | None]:
    """A date-time range picker powered by MUI X (Pro).

    Works in evaluation mode without a license key (watermark shown).
    Provide a license key via the ``license_key`` parameter or the
    ``ST_MUI_LICENSE_KEY`` environment variable to remove the watermark.

    Parameters
    ----------
    label : str
        Label displayed above the picker.
    value : tuple of (datetime/str/None, datetime/str/None) or None
        Default datetime range. Accepts datetime objects or ISO strings.
    min_datetime : datetime or str or None
        Minimum selectable datetime.
    max_datetime : datetime or str or None
        Maximum selectable datetime.
    ampm : bool
        Whether to use 12-hour format with AM/PM.
    disabled : bool
        Whether the picker is disabled.
    license_key : str or None
        MUI X Pro license key. Falls back to ST_MUI_LICENSE_KEY env var.
    on_change : callable or None
        Callback when the selected datetime range changes.
    key : str or None
        Unique widget key.

    Returns
    -------
    tuple of (datetime or None, datetime or None)
        The selected start and end datetimes, or (None, None).
    """

    def _serialize_dt(dt):
        if dt is None:
            return None
        if isinstance(dt, datetime):
            return dt.isoformat()
        return str(dt)

    start_val = None
    end_val = None
    if value is not None:
        start_val = _serialize_dt(value[0])
        end_val = _serialize_dt(value[1])

    def _noop():
        pass

    result = _component(
        key=key,
        default={"start_datetime": start_val, "end_datetime": end_val},
        data={
            "label": label,
            "startValue": start_val,
            "endValue": end_val,
            "minDatetime": _serialize_dt(min_datetime),
            "maxDatetime": _serialize_dt(max_datetime),
            "ampm": ampm,
            "disabled": disabled,
            "licenseKey": _get_license_key(license_key),
        },
        on_start_datetime_change=on_change or _noop,
        on_end_datetime_change=_noop,
    )

    def _parse_dt(val):
        if not val:
            return None
        try:
            return datetime.fromisoformat(val)
        except (ValueError, TypeError):
            return None

    if result:
        return (_parse_dt(result.get("start_datetime")), _parse_dt(result.get("end_datetime")))
    return (None, None)
