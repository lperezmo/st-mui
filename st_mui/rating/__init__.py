"""MUI Rating component for Streamlit."""

from __future__ import annotations

import math
from collections.abc import Callable

from st_mui._compat import component

_component = component(
    "st-mui.rating",
    js="index-*.js",
    html='<div class="react-root"></div>',
)

_ALIGNMENT_TOLERANCE = 1e-9
_MAX_STARS = 100
_MAX_STEPS_PER_STAR = 100


def _normalize_precision(precision: float) -> float:
    if isinstance(precision, bool) or not isinstance(precision, (int, float)):
        raise TypeError("precision must be a number")
    if not math.isfinite(precision) or precision <= 0 or precision > 1:
        raise ValueError("precision must be greater than zero and at most 1")

    raw_steps_per_star = 1 / precision
    if (
        not math.isfinite(raw_steps_per_star)
        or raw_steps_per_star > _MAX_STEPS_PER_STAR
    ):
        raise ValueError(
            f"precision must produce at most {_MAX_STEPS_PER_STAR} steps per star"
        )
    steps_per_star = round(raw_steps_per_star)
    if not math.isclose(
        raw_steps_per_star,
        steps_per_star,
        rel_tol=0,
        abs_tol=_ALIGNMENT_TOLERANCE,
    ):
        raise ValueError("precision must divide 1 into an integer number of steps")
    return 1 / steps_per_star


def _is_aligned(value: float, precision: float) -> bool:
    steps = value / precision
    return math.isclose(
        steps,
        round(steps),
        rel_tol=0,
        abs_tol=_ALIGNMENT_TOLERANCE,
    )


def rating(
    label: str = "Rating",
    value: float | None = None,
    *,
    max_value: int = 5,
    precision: float = 1.0,
    size: str = "medium",
    disabled: bool = False,
    read_only: bool = False,
    clearable: bool = True,
    on_change: Callable | None = None,
    key: str | None = None,
) -> float | None:
    """Select a star rating with configurable precision and maximum."""
    if not isinstance(label, str):
        raise TypeError("label must be a string")
    if isinstance(max_value, bool) or not isinstance(max_value, int):
        raise TypeError("max_value must be an integer")
    if max_value < 1:
        raise ValueError("max_value must be at least 1")
    if max_value > _MAX_STARS:
        raise ValueError(f"max_value must be at most {_MAX_STARS}")
    normalized_precision = _normalize_precision(precision)
    if size not in {"small", "medium", "large"}:
        raise ValueError("size must be 'small', 'medium', or 'large'")
    for name, flag in (
        ("disabled", disabled),
        ("read_only", read_only),
        ("clearable", clearable),
    ):
        if not isinstance(flag, bool):
            raise TypeError(f"{name} must be a boolean")
    if on_change is not None and not callable(on_change):
        raise TypeError("on_change must be callable or None")

    normalized_value: float | None
    if value is None:
        normalized_value = None
    else:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError("value must be a number or None")
        if not math.isfinite(value) or not 0 <= value <= max_value:
            raise ValueError("value must be between 0 and max_value")
        if not _is_aligned(value, normalized_precision):
            raise ValueError("value must align with precision")
        normalized_value = float(value)

    def _noop():
        pass

    result = _component(
        key=key,
        default={"selected_value": normalized_value},
        data={
            "label": label,
            "selectedValue": normalized_value,
            "maxValue": max_value,
            "precision": normalized_precision,
            "size": size,
            "disabled": disabled,
            "readOnly": read_only,
            "clearable": clearable,
        },
        on_selected_value_change=on_change if on_change is not None else _noop,
    )

    selected = (
        result.get("selected_value", normalized_value) if result else normalized_value
    )
    if selected is None:
        return None if clearable or normalized_value is None else normalized_value
    if isinstance(selected, bool) or not isinstance(selected, (int, float)):
        return normalized_value
    if (
        not math.isfinite(selected)
        or not 0 <= selected <= max_value
        or not _is_aligned(selected, normalized_precision)
    ):
        return normalized_value
    return float(selected)
