"""MUI Slider component for Streamlit."""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping, Sequence
from typing import Any

from st_mui._compat import component

_component = component(
    "st-mui.slider",
    js="index-*.js",
    html='<div class="react-root"></div>',
)

Number = int | float
_MAX_SAFE_INTEGER = (1 << 53) - 1
_MAX_IMPLICIT_MARKS = 1_000


def _number(value: Any, *, field: str) -> Number:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field} must be a number")
    if isinstance(value, int) and not -_MAX_SAFE_INTEGER <= value <= _MAX_SAFE_INTEGER:
        raise ValueError(f"{field} must be a JavaScript-safe integer")
    try:
        finite = math.isfinite(value)
    except OverflowError:
        finite = False
    if not finite:
        raise ValueError(f"{field} must be finite")
    return value


def _normalize_marks(
    marks: bool | Sequence[Mapping[str, Any]],
    *,
    min_value: Number,
    max_value: Number,
) -> bool | list[dict[str, Any]]:
    if isinstance(marks, bool):
        return marks
    if isinstance(marks, (str, bytes)) or not isinstance(marks, Sequence):
        raise TypeError("marks must be a boolean or a sequence of mappings")

    normalized: list[dict[str, Any]] = []
    seen: set[Number] = set()
    for index, mark in enumerate(marks):
        if not isinstance(mark, Mapping) or "value" not in mark:
            raise TypeError(f"marks[{index}] must be a mapping with a value")
        mark_value = _number(mark["value"], field=f"marks[{index}].value")
        if not min_value <= mark_value <= max_value:
            raise ValueError(f"marks[{index}].value is outside the slider bounds")
        if mark_value in seen:
            raise ValueError(f"marks contains duplicate value {mark_value!r}")
        seen.add(mark_value)
        normalized_mark: dict[str, Any] = {"value": mark_value}
        if "label" in mark:
            normalized_mark["label"] = str(mark["label"])
        normalized.append(normalized_mark)
    return sorted(normalized, key=lambda mark: mark["value"])


def _valid_selected_number(
    value: Any,
    *,
    min_value: Number,
    max_value: Number,
    allowed_values: set[Number] | None,
) -> bool:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    if not math.isfinite(value) or not min_value <= value <= max_value:
        return False
    return allowed_values is None or value in allowed_values


def slider(
    label: str = "Select a value",
    value: Number | Sequence[Number] | None = None,
    *,
    min_value: Number = 0,
    max_value: Number = 100,
    step: Number | None = 1,
    marks: bool | Sequence[Mapping[str, Any]] = False,
    value_label_display: str = "auto",
    disabled: bool = False,
    on_change: Callable | None = None,
    key: str | None = None,
) -> Number | tuple[Number, Number]:
    """Select a number or numeric range with a MUI slider.

    Passing a two-item sequence as ``value`` enables range mode. State is sent
    to Streamlit when the user commits the change, rather than on every pixel
    moved while dragging.
    """
    if not isinstance(label, str):
        raise TypeError("label must be a string")
    min_value = _number(min_value, field="min_value")
    max_value = _number(max_value, field="max_value")
    if min_value >= max_value:
        raise ValueError("min_value must be less than max_value")

    if step is not None:
        step = _number(step, field="step")
        if step <= 0:
            raise ValueError("step must be greater than zero")
    if not isinstance(disabled, bool):
        raise TypeError("disabled must be a boolean")
    if on_change is not None and not callable(on_change):
        raise TypeError("on_change must be callable or None")

    is_range = isinstance(value, Sequence) and not isinstance(value, (str, bytes))
    if is_range:
        values = list(value)
        if len(values) != 2:
            raise ValueError("range slider value must contain exactly two numbers")
        normalized_value: Number | list[Number] = [
            _number(values[0], field="value[0]"),
            _number(values[1], field="value[1]"),
        ]
        if normalized_value[0] > normalized_value[1]:
            raise ValueError("range slider start must not exceed its end")
    else:
        normalized_value = min_value if value is None else _number(value, field="value")

    selected_values = (
        normalized_value if isinstance(normalized_value, list) else [normalized_value]
    )
    if any(item < min_value or item > max_value for item in selected_values):
        raise ValueError("value must be within min_value and max_value")

    normalized_marks = _normalize_marks(marks, min_value=min_value, max_value=max_value)
    if normalized_marks is True and step is not None:
        try:
            implicit_intervals = (max_value - min_value) / step
        except OverflowError:
            implicit_intervals = math.inf
        if (
            not math.isfinite(implicit_intervals)
            or math.floor(implicit_intervals) + 1 > _MAX_IMPLICIT_MARKS
        ):
            raise ValueError(
                f"marks=True may render at most {_MAX_IMPLICIT_MARKS} marks; "
                "increase step or provide explicit marks"
            )
    allowed_values: set[Number] | None = None
    if step is None:
        if not isinstance(normalized_marks, list) or not normalized_marks:
            raise ValueError("step=None requires a non-empty explicit list of marks")
        allowed_values = {mark["value"] for mark in normalized_marks}
        if value is None:
            normalized_value = normalized_marks[0]["value"]
            selected_values = [normalized_value]
        if any(item not in allowed_values for item in selected_values):
            raise ValueError("value must match an explicit mark when step=None")
    if value_label_display not in {"auto", "on", "off"}:
        raise ValueError("value_label_display must be 'auto', 'on', or 'off'")

    def _noop():
        pass

    result = _component(
        key=key,
        default={"selected_value": normalized_value},
        data={
            "label": label,
            "selectedValue": normalized_value,
            "minValue": min_value,
            "maxValue": max_value,
            "step": step,
            "marks": normalized_marks,
            "valueLabelDisplay": value_label_display,
            "disabled": disabled,
        },
        on_selected_value_change=on_change if on_change is not None else _noop,
    )

    selected = (
        result.get("selected_value", normalized_value)
        if isinstance(result, Mapping)
        else normalized_value
    )
    if is_range:
        if (
            isinstance(selected, list)
            and len(selected) == 2
            and _valid_selected_number(
                selected[0],
                min_value=min_value,
                max_value=max_value,
                allowed_values=allowed_values,
            )
            and _valid_selected_number(
                selected[1],
                min_value=min_value,
                max_value=max_value,
                allowed_values=allowed_values,
            )
            and selected[0] <= selected[1]
        ):
            return (selected[0], selected[1])
        return (normalized_value[0], normalized_value[1])
    return (
        selected
        if _valid_selected_number(
            selected,
            min_value=min_value,
            max_value=max_value,
            allowed_values=allowed_values,
        )
        else normalized_value
    )
