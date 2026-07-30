"""Shared serialization helpers for datetime-based components."""

from __future__ import annotations

from datetime import datetime
from typing import Any


def parse_datetime(value: Any) -> datetime | None:
    """Parse an ISO datetime, including the ``Z`` form rejected by Python 3.10."""
    if not value:
        return None

    if isinstance(value, str) and value.endswith("Z"):
        value = f"{value[:-1]}+00:00"

    try:
        return datetime.fromisoformat(value)
    except (ValueError, TypeError):
        return None


def serialize_datetime(value: datetime | str | None) -> str | None:
    """Serialize a datetime as a timezone-naive wall-clock value."""
    if value is None:
        return None

    parsed = value if isinstance(value, datetime) else parse_datetime(value)
    if parsed is not None:
        return parsed.replace(tzinfo=None).isoformat()

    return str(value)
