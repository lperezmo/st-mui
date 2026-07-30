"""MUI Autocomplete component for Streamlit."""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping, Sequence
from typing import Any

from st_mui._compat import component

_component = component(
    "st-mui.autocomplete",
    js="index-*.js",
    html='<div class="react-root"></div>',
)

JsonScalar = str | int | float | bool
_MAX_SAFE_INTEGER = (1 << 53) - 1


def _normalize_scalar(value: Any, *, field: str) -> JsonScalar:
    if value is None or not isinstance(value, (str, int, float, bool)):
        raise TypeError(f"{field} must be a string, number, or boolean")
    if (
        isinstance(value, int)
        and not isinstance(value, bool)
        and not -_MAX_SAFE_INTEGER <= value <= _MAX_SAFE_INTEGER
    ):
        raise ValueError(f"{field} must be a JavaScript-safe integer")
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError(f"{field} must be finite")
    return value


def _value_key(value: JsonScalar) -> tuple[str, JsonScalar]:
    if isinstance(value, bool):
        return ("boolean", value)
    if isinstance(value, (int, float)):
        return ("number", value)
    return ("string", value)


def _normalize_options(
    options: Sequence[JsonScalar | Mapping[str, Any]] | None,
) -> list[dict[str, Any]]:
    if options is None:
        return []
    if isinstance(options, (str, bytes)) or not isinstance(options, Sequence):
        raise TypeError("options must be a sequence of scalars or mappings")

    normalized: list[dict[str, Any]] = []
    seen: set[tuple[str, JsonScalar]] = set()

    for index, option in enumerate(options):
        if isinstance(option, Mapping):
            if "value" not in option and "label" not in option:
                raise ValueError(
                    f"options[{index}] must contain a 'value' or 'label' key"
                )
            raw_value = option.get("value", option.get("label"))
            value = _normalize_scalar(raw_value, field=f"options[{index}].value")
            raw_label = option.get("label", str(value))
            if not isinstance(raw_label, str):
                raise TypeError(f"options[{index}].label must be a string")
            label = raw_label
            disabled = option.get("disabled", False)
            if not isinstance(disabled, bool):
                raise TypeError(f"options[{index}].disabled must be a boolean")
        else:
            value = _normalize_scalar(option, field=f"options[{index}]")
            label = str(value)
            disabled = False

        key = _value_key(value)
        if key in seen:
            raise ValueError(f"options contains duplicate value {value!r}")
        seen.add(key)
        normalized.append({"label": label, "value": value, "disabled": disabled})

    return normalized


def _normalize_value(
    value: JsonScalar | Sequence[JsonScalar] | None,
    *,
    multiple: bool,
) -> JsonScalar | list[JsonScalar] | None:
    if multiple:
        if value is None:
            return []
        if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
            raise TypeError("value must be a sequence when multiple=True")
        return [
            _normalize_scalar(item, field=f"value[{index}]")
            for index, item in enumerate(value)
        ]

    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        raise TypeError("value must be a scalar when multiple=False")
    if value is None:
        return None
    return _normalize_scalar(value, field="value")


def _validate_selected_values(
    value: JsonScalar | list[JsonScalar] | None,
    *,
    multiple: bool,
    free_solo: bool,
    option_keys: set[tuple[str, JsonScalar]],
) -> None:
    selected_values = (
        value if isinstance(value, list) else ([] if value is None else [value])
    )
    seen: set[tuple[str, JsonScalar]] = set()
    for selected in selected_values:
        key = _value_key(selected)
        if multiple and key in seen:
            raise ValueError(f"value contains duplicate selection {selected!r}")
        seen.add(key)
        if key not in option_keys:
            if not free_solo:
                raise ValueError(f"selected value {selected!r} is not in options")
            if not isinstance(selected, str):
                raise TypeError("free_solo values that are not options must be strings")


def _normalize_text(value: Any, *, field: str, optional: bool = False) -> str | None:
    if optional and value is None:
        return None
    if not isinstance(value, str):
        expected = "a string or None" if optional else "a string"
        raise TypeError(f"{field} must be {expected}")
    return value


def _normalize_bool(value: Any, *, field: str) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"{field} must be a boolean")
    return value


def _result_value(
    result: Any,
    *,
    multiple: bool,
    free_solo: bool,
    option_keys: set[tuple[str, JsonScalar]],
) -> JsonScalar | list[JsonScalar] | None:
    empty: JsonScalar | list[JsonScalar] | None = [] if multiple else None
    if not isinstance(result, Mapping):
        return empty

    try:
        selected = _normalize_value(
            result.get("selected_value", empty),
            multiple=multiple,
        )
        _validate_selected_values(
            selected,
            multiple=multiple,
            free_solo=free_solo,
            option_keys=option_keys,
        )
    except (TypeError, ValueError):
        return empty
    return selected


def autocomplete(
    options: Sequence[JsonScalar | Mapping[str, Any]] | None = None,
    label: str = "Select an option",
    value: JsonScalar | Sequence[JsonScalar] | None = None,
    *,
    multiple: bool = False,
    free_solo: bool = False,
    placeholder: str | None = None,
    helper_text: str | None = None,
    clearable: bool = True,
    disabled: bool = False,
    on_change: Callable | None = None,
    key: str | None = None,
) -> JsonScalar | list[JsonScalar] | None:
    """Select one or more values with searchable MUI suggestions.

    Options may be scalar values or dictionaries with ``label``, ``value``,
    and optional ``disabled`` keys. Values are limited to JSON-safe strings,
    numbers, and booleans so they round-trip without losing identity.
    """
    label = _normalize_text(label, field="label")
    placeholder = _normalize_text(placeholder, field="placeholder", optional=True)
    helper_text = _normalize_text(helper_text, field="helper_text", optional=True)
    multiple = _normalize_bool(multiple, field="multiple")
    free_solo = _normalize_bool(free_solo, field="free_solo")
    clearable = _normalize_bool(clearable, field="clearable")
    disabled = _normalize_bool(disabled, field="disabled")
    if on_change is not None and not callable(on_change):
        raise TypeError("on_change must be callable or None")

    normalized_options = _normalize_options(options)
    normalized_value = _normalize_value(value, multiple=multiple)
    option_keys = {_value_key(option["value"]) for option in normalized_options}
    _validate_selected_values(
        normalized_value,
        multiple=multiple,
        free_solo=free_solo,
        option_keys=option_keys,
    )

    def _noop():
        pass

    result = _component(
        key=key,
        default={"selected_value": normalized_value},
        data={
            "options": normalized_options,
            "label": label,
            "selectedValue": normalized_value,
            "multiple": multiple,
            "freeSolo": free_solo,
            "placeholder": placeholder,
            "helperText": helper_text,
            "clearable": clearable,
            "disabled": disabled,
        },
        on_selected_value_change=on_change if on_change is not None else _noop,
    )

    return _result_value(
        result,
        multiple=multiple,
        free_solo=free_solo,
        option_keys=option_keys,
    )
