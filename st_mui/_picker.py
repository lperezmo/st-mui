"""Validation helpers shared by the MUI date and time pickers."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date, datetime, time
from typing import Any


def normalize_date_value(value: Any, *, field: str) -> tuple[str | None, date | None]:
    """Normalize a date prop without accepting datetime subclasses."""
    if value is None:
        return None, None
    if isinstance(value, datetime):
        raise TypeError(f"{field} must be a date, ISO date string, or None")
    if isinstance(value, date):
        parsed = value
    elif isinstance(value, str):
        try:
            parsed = date.fromisoformat(value)
        except ValueError as exc:
            raise ValueError(
                f"{field} must be an ISO date string (YYYY-MM-DD)"
            ) from exc
    else:
        raise TypeError(f"{field} must be a date, ISO date string, or None")
    return parsed.isoformat(), parsed


def normalize_time_value(
    value: Any,
    *,
    field: str,
    reject_timezone: bool = False,
) -> tuple[str | None, time | None]:
    """Normalize a wall-clock time prop or untrusted component result."""
    if value is None:
        return None, None
    if isinstance(value, time):
        parsed = value
    elif isinstance(value, str):
        try:
            parsed = time.fromisoformat(value)
        except ValueError as exc:
            raise ValueError(f"{field} must be a valid ISO time string") from exc
    else:
        raise TypeError(f"{field} must be a time, ISO time string, or None")
    if reject_timezone and parsed.tzinfo is not None:
        raise ValueError(f"{field} must be timezone-naive")
    parsed = parsed.replace(tzinfo=None)
    return parsed.isoformat(), parsed


def is_minute_aligned(value: time | datetime, minutes_step: int) -> bool:
    """Return whether a time-like value lies on the configured minute grid."""
    return value.minute % minutes_step == 0


def normalize_optional_text(value: Any, *, field: str) -> str | None:
    """Validate an optional text prop."""
    if value is not None and not isinstance(value, str):
        raise TypeError(f"{field} must be a string or None")
    return value


def normalize_bool(value: Any, *, field: str) -> bool:
    """Validate a strict boolean prop."""
    if not isinstance(value, bool):
        raise TypeError(f"{field} must be a boolean")
    return value


def normalize_views(
    views: Sequence[str] | None,
    *,
    allowed: tuple[str, ...],
    default: tuple[str, ...],
    open_to: str | None,
) -> tuple[list[str] | None, str | None]:
    """Validate picker views and ensure ``open_to`` can actually be displayed."""
    if views is None:
        normalized_views = None
        effective_views = default
    else:
        if isinstance(views, (str, bytes)) or not isinstance(views, Sequence):
            raise TypeError("views must be a sequence of strings or None")
        if not views:
            raise ValueError("views must not be empty")

        normalized_views = []
        for index, view in enumerate(views):
            if not isinstance(view, str):
                raise TypeError(f"views[{index}] must be a string")
            if view not in allowed:
                choices = ", ".join(repr(item) for item in allowed)
                raise ValueError(f"views[{index}] must be one of {choices}")
            if view in normalized_views:
                raise ValueError(f"views contains duplicate view {view!r}")
            normalized_views.append(view)
        effective_views = tuple(normalized_views)

    if open_to is not None:
        if not isinstance(open_to, str):
            raise TypeError("open_to must be a string or None")
        if open_to not in allowed:
            choices = ", ".join(repr(item) for item in allowed)
            raise ValueError(f"open_to must be one of {choices}")
        if open_to not in effective_views:
            raise ValueError("open_to must be included in views")

    return normalized_views, open_to


def normalize_minutes_step(value: Any) -> int:
    """Validate a useful MUI minute increment."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("minutes_step must be an integer")
    if not 1 <= value <= 60:
        raise ValueError("minutes_step must be between 1 and 60")
    return value
