"""MUI X Community Data Grid component for Streamlit."""

from __future__ import annotations

import json
import math
from collections.abc import Callable, Mapping, Sequence
from typing import Any

from st_mui._compat import component

_component = component(
    "st-mui.data_grid",
    js="index-*.js",
    html='<div class="react-root"></div>',
)

_COLUMN_ALIASES = {
    "header_name": "headerName",
    "header_align": "headerAlign",
    "min_width": "minWidth",
    "max_width": "maxWidth",
    "value_options": "valueOptions",
}
_COLUMN_KEYS = {
    "field",
    "headerName",
    "description",
    "width",
    "minWidth",
    "maxWidth",
    "flex",
    "type",
    "align",
    "headerAlign",
    "sortable",
    "filterable",
    "resizable",
    "valueOptions",
}
_COLUMN_TYPES = {"string", "number", "boolean", "singleSelect"}
_DENSITIES = {"compact", "standard", "comfortable"}
_ALIGNMENTS = {"left", "center", "right"}
_FILTER_KEYS = {
    "items",
    "logicOperator",
    "quickFilterValues",
    "quickFilterLogicOperator",
    "quickFilterExcludeHiddenColumns",
}
_FILTER_ITEM_KEYS = {"id", "field", "operator", "value"}
_LOGIC_OPERATORS = {"and", "or"}
_MAX_SAFE_INTEGER = 2**53 - 1


def _json_safe(value: Any, *, field: str) -> Any:
    try:
        json.dumps(value, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"{field} must contain only JSON-safe values") from exc
    _validate_json_precision(value, field=field)
    return value


def _validate_json_precision(value: Any, *, field: str) -> None:
    """Reject values that JSON accepts but JavaScript cannot preserve safely."""
    if value is None or isinstance(value, (str, bool)):
        return
    if isinstance(value, int):
        if abs(value) > _MAX_SAFE_INTEGER:
            raise ValueError(
                f"{field} contains an integer outside JavaScript's safe range"
            )
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"{field} contains a non-finite number")
        return
    if isinstance(value, Mapping):
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError(f"{field} contains a non-string object key")
            _validate_json_precision(item, field=field)
        return
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for item in value:
            _validate_json_precision(item, field=field)


def _normalize_row_id(value: Any, *, field: str) -> str | int | float:
    if (
        isinstance(value, bool)
        or not isinstance(value, (str, int, float))
        or value == ""
    ):
        raise TypeError(f"{field} must be a string or number")
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError(f"{field} must be finite")
    if isinstance(value, int) and abs(value) > _MAX_SAFE_INTEGER:
        raise ValueError(f"{field} exceeds JavaScript's safe integer range")
    return value


def _row_id_key(
    value: str | int | float,
) -> tuple[str, str | int | float]:
    return ("number", value) if isinstance(value, (int, float)) else ("string", value)


def _normalize_rows(
    rows: Sequence[Mapping[str, Any]] | Any | None,
    *,
    id_field: str,
) -> list[dict[str, Any]]:
    if rows is None:
        return []
    if hasattr(rows, "to_dict") and not isinstance(rows, Mapping):
        try:
            rows = rows.to_dict(orient="records")
        except TypeError:
            rows = rows.to_dict("records")
    if isinstance(rows, (str, bytes)) or not isinstance(rows, Sequence):
        raise TypeError("rows must be a sequence of mappings or a DataFrame")

    normalized: list[dict[str, Any]] = []
    seen_ids: set[tuple[str, str | int | float]] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            raise TypeError(f"rows[{index}] must be a mapping")
        copied = dict(row)
        if id_field not in copied:
            raise ValueError(f"rows[{index}] is missing id field {id_field!r}")
        row_id = _normalize_row_id(
            copied[id_field], field=f"rows[{index}][{id_field!r}]"
        )
        key = _row_id_key(row_id)
        if key in seen_ids:
            raise ValueError(f"rows contains duplicate id {row_id!r}")
        seen_ids.add(key)
        _json_safe(copied, field=f"rows[{index}]")
        normalized.append(copied)
    return normalized


def _infer_column_type(value: Any) -> str:
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, (int, float)):
        return "number"
    return "string"


def _normalize_columns(
    columns: Sequence[str | Mapping[str, Any]] | None,
    *,
    rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    fields: list[str] = []
    inferred_types: dict[str, str | None] = {}
    for row in rows:
        for field, value in row.items():
            if field not in inferred_types:
                fields.append(field)
                inferred_types[field] = None
            if inferred_types[field] is None and value is not None:
                inferred_types[field] = _infer_column_type(value)

    if columns is None:
        return [
            {
                "field": field,
                "headerName": field.replace("_", " ").title(),
                "type": inferred_types[field] or "string",
                "flex": 1,
            }
            for field in fields
        ]
    if isinstance(columns, (str, bytes)) or not isinstance(columns, Sequence):
        raise TypeError("columns must be a sequence of field names or mappings")

    normalized: list[dict[str, Any]] = []
    seen_fields: set[str] = set()
    for index, column in enumerate(columns):
        if isinstance(column, str):
            raw: dict[str, Any] = {"field": column}
        elif isinstance(column, Mapping):
            raw = {}
            for key, value in column.items():
                if not isinstance(key, str):
                    raise TypeError(f"columns[{index}] keys must be strings")
                normalized_key = _COLUMN_ALIASES.get(key, key)
                if normalized_key in raw:
                    raise ValueError(
                        f"columns[{index}] repeats {normalized_key!r} via an alias"
                    )
                raw[normalized_key] = value
        else:
            raise TypeError(f"columns[{index}] must be a string or mapping")

        unknown = set(raw) - _COLUMN_KEYS
        if unknown:
            names = ", ".join(sorted(unknown))
            raise ValueError(f"columns[{index}] has unsupported keys: {names}")
        field = raw.get("field")
        if not isinstance(field, str) or not field:
            raise ValueError(f"columns[{index}].field must be a non-empty string")
        if field in seen_fields:
            raise ValueError(f"columns contains duplicate field {field!r}")
        seen_fields.add(field)

        column_type = raw.get("type", inferred_types.get(field) or "string")
        if not isinstance(column_type, str) or column_type not in _COLUMN_TYPES:
            raise ValueError(
                f"columns[{index}].type must be one of {sorted(_COLUMN_TYPES)}"
            )
        for text_key in ("headerName", "description"):
            if text_key in raw and not isinstance(raw[text_key], str):
                raise TypeError(f"columns[{index}].{text_key} must be a string")
        for number_key in ("width", "minWidth", "maxWidth", "flex"):
            if number_key in raw and (
                isinstance(raw[number_key], bool)
                or not isinstance(raw[number_key], (int, float))
                or raw[number_key] <= 0
            ):
                raise ValueError(
                    f"columns[{index}].{number_key} must be a positive number"
                )
        for alignment_key in ("align", "headerAlign"):
            if alignment_key in raw and (
                not isinstance(raw[alignment_key], str)
                or raw[alignment_key] not in _ALIGNMENTS
            ):
                raise ValueError(
                    f"columns[{index}].{alignment_key} must be one of "
                    f"{sorted(_ALIGNMENTS)}"
                )
        for bool_key in ("sortable", "filterable", "resizable"):
            if bool_key in raw and not isinstance(raw[bool_key], bool):
                raise TypeError(f"columns[{index}].{bool_key} must be a boolean")
        if "valueOptions" in raw:
            value_options = raw["valueOptions"]
            if isinstance(value_options, (str, bytes)) or not isinstance(
                value_options, Sequence
            ):
                raise TypeError(f"columns[{index}].valueOptions must be a sequence")
            if column_type != "singleSelect":
                raise ValueError(
                    f"columns[{index}].valueOptions requires type='singleSelect'"
                )
            for option_index, option in enumerate(value_options):
                if option is None or not isinstance(option, (str, int, float, bool)):
                    raise TypeError(
                        f"columns[{index}].valueOptions[{option_index}] must be "
                        "a string, number, or boolean"
                    )

        normalized_column = {
            "headerName": field.replace("_", " ").title(),
            **raw,
            "type": column_type,
        }
        if "width" not in raw and "flex" not in raw:
            normalized_column["flex"] = 1
        _json_safe(normalized_column, field=f"columns[{index}]")
        normalized.append(normalized_column)
    return normalized


def _normalize_selected_rows(
    selected_rows: Sequence[str | int | float] | None,
    *,
    valid_ids: set[tuple[str, str | int | float]],
) -> list[str | int | float]:
    if selected_rows is None:
        return []
    if isinstance(selected_rows, (str, bytes)) or not isinstance(
        selected_rows, Sequence
    ):
        raise TypeError("selected_rows must be a sequence of row ids")

    normalized: list[str | int | float] = []
    selected_keys: set[tuple[str, str | int | float]] = set()
    for index, raw_id in enumerate(selected_rows):
        row_id = _normalize_row_id(raw_id, field=f"selected_rows[{index}]")
        row_id_key = _row_id_key(row_id)
        if row_id_key not in valid_ids:
            raise ValueError(f"selected row id {row_id!r} is not present in rows")
        if row_id_key in selected_keys:
            raise ValueError(f"selected_rows contains duplicate id {row_id!r}")
        selected_keys.add(row_id_key)
        normalized.append(row_id)
    return normalized


def _normalize_sort_model(
    sort_model: Sequence[Mapping[str, Any]] | None,
    *,
    column_fields: set[str],
) -> list[dict[str, Any]]:
    if sort_model is None:
        return []
    if isinstance(sort_model, (str, bytes)) or not isinstance(sort_model, Sequence):
        raise TypeError("sort_model must be a sequence of mappings")
    if len(sort_model) > 1:
        raise ValueError("MUI X Community supports at most one sort item")

    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(sort_model):
        if not isinstance(item, Mapping):
            raise TypeError(f"sort_model[{index}] must be a mapping")
        field = item.get("field")
        direction = item.get("sort")
        if not isinstance(field, str) or not field:
            raise ValueError(f"sort_model[{index}].field must be a non-empty string")
        if field not in column_fields:
            raise ValueError(f"sort_model[{index}].field is not present in columns")
        if direction not in {"asc", "desc", None}:
            raise ValueError(f"sort_model[{index}].sort must be 'asc', 'desc', or None")
        normalized.append({"field": field, "sort": direction})
    _json_safe(normalized, field="sort_model")
    return normalized


def _normalize_filter_model(
    filter_model: Mapping[str, Any] | None,
    *,
    column_fields: set[str],
) -> dict[str, Any]:
    if filter_model is None:
        return {"items": []}
    if not isinstance(filter_model, Mapping):
        raise TypeError("filter_model must be a mapping")
    if any(not isinstance(key, str) for key in filter_model):
        raise TypeError("filter_model keys must be strings")
    unknown = set(filter_model) - _FILTER_KEYS
    if unknown:
        raise ValueError(
            "filter_model has unsupported keys: " + ", ".join(sorted(unknown))
        )

    items = filter_model.get("items", [])
    if not isinstance(items, list):
        raise TypeError("filter_model.items must be a list")
    if len(items) > 1:
        raise ValueError("MUI X Community supports at most one filter item")

    normalized_items: list[dict[str, Any]] = []
    for index, item in enumerate(items):
        if not isinstance(item, Mapping):
            raise TypeError(f"filter_model.items[{index}] must be a mapping")
        if any(not isinstance(key, str) for key in item):
            raise TypeError(f"filter_model.items[{index}] keys must be strings")
        item_unknown = set(item) - _FILTER_ITEM_KEYS
        if item_unknown:
            raise ValueError(
                f"filter_model.items[{index}] has unsupported keys: "
                + ", ".join(sorted(item_unknown))
            )
        field = item.get("field")
        if not isinstance(field, str) or field not in column_fields:
            raise ValueError(
                f"filter_model.items[{index}].field is not present in columns"
            )
        operator = item.get("operator")
        if not isinstance(operator, str) or not operator:
            raise ValueError(
                f"filter_model.items[{index}].operator must be a non-empty string"
            )
        if "id" in item:
            _normalize_row_id(item["id"], field=f"filter_model.items[{index}].id")
        normalized_items.append(dict(item))

    normalized: dict[str, Any] = {"items": normalized_items}
    for logic_key in ("logicOperator", "quickFilterLogicOperator"):
        if logic_key in filter_model:
            value = filter_model[logic_key]
            if not isinstance(value, str) or value not in _LOGIC_OPERATORS:
                raise ValueError(
                    f"filter_model.{logic_key} must be one of "
                    f"{sorted(_LOGIC_OPERATORS)}"
                )
            normalized[logic_key] = value
    if "quickFilterValues" in filter_model:
        quick_values = filter_model["quickFilterValues"]
        if not isinstance(quick_values, list):
            raise TypeError("filter_model.quickFilterValues must be a list")
        normalized["quickFilterValues"] = list(quick_values)
    if "quickFilterExcludeHiddenColumns" in filter_model:
        exclude_hidden = filter_model["quickFilterExcludeHiddenColumns"]
        if not isinstance(exclude_hidden, bool):
            raise TypeError(
                "filter_model.quickFilterExcludeHiddenColumns must be a boolean"
            )
        normalized["quickFilterExcludeHiddenColumns"] = exclude_hidden
    _json_safe(normalized, field="filter_model")
    return normalized


def _normalize_pagination_model(
    pagination_model: Any,
    *,
    page_size_options: Sequence[int],
    row_count: int,
) -> dict[str, int]:
    if not isinstance(pagination_model, Mapping):
        raise TypeError("pagination_model must be a mapping")
    if set(pagination_model) != {"page", "pageSize"}:
        raise ValueError("pagination_model must contain only page and pageSize")
    page = pagination_model["page"]
    page_size = pagination_model["pageSize"]
    if isinstance(page, bool) or not isinstance(page, int) or page < 0:
        raise ValueError("pagination_model.page must be a non-negative integer")
    if (
        isinstance(page_size, bool)
        or not isinstance(page_size, int)
        or page_size not in page_size_options
    ):
        raise ValueError("pagination_model.pageSize must be a configured page size")
    max_page = max(0, (row_count - 1) // page_size)
    if page > max_page:
        raise ValueError("pagination_model.page exceeds the available rows")
    return {"page": page, "pageSize": page_size}


def data_grid(
    rows: Sequence[Mapping[str, Any]] | Any | None = None,
    columns: Sequence[str | Mapping[str, Any]] | None = None,
    *,
    id_field: str = "id",
    selected_rows: Sequence[str | int | float] | None = None,
    sort_model: Sequence[Mapping[str, Any]] | None = None,
    filter_model: Mapping[str, Any] | None = None,
    page_size: int = 10,
    page_size_options: Sequence[int] = (10, 25, 50, 100),
    height: int = 400,
    checkbox_selection: bool = False,
    density: str = "standard",
    disabled: bool = False,
    on_change: Callable | None = None,
    key: str | None = None,
) -> dict[str, Any]:
    """Render the MIT-licensed MUI X Community Data Grid.

    The returned dictionary contains ``selected_rows``, ``sort_model``,
    ``filter_model``, and ``pagination_model``. Rows must contain a unique
    string or numeric ``id_field``. A pandas DataFrame is accepted when its
    records contain that field; pandas is not required by st-mui.
    """
    if not isinstance(id_field, str) or not id_field:
        raise ValueError("id_field must be a non-empty string")
    normalized_rows = _normalize_rows(rows, id_field=id_field)
    normalized_columns = _normalize_columns(columns, rows=normalized_rows)

    if (
        isinstance(page_size, bool)
        or not isinstance(page_size, int)
        or not 1 <= page_size <= 100
    ):
        raise ValueError("page_size must be an integer between 1 and 100")
    if (
        isinstance(page_size_options, (str, bytes))
        or not isinstance(page_size_options, Sequence)
        or not page_size_options
    ):
        raise ValueError("page_size_options must contain positive integers")
    normalized_page_sizes: list[int] = []
    for option in page_size_options:
        if (
            isinstance(option, bool)
            or not isinstance(option, int)
            or not 1 <= option <= 100
        ):
            raise ValueError("page_size_options must contain integers from 1 to 100")
        if option not in normalized_page_sizes:
            normalized_page_sizes.append(option)
    if page_size not in normalized_page_sizes:
        normalized_page_sizes.append(page_size)
    normalized_page_sizes.sort()

    if isinstance(height, bool) or not isinstance(height, int) or height < 100:
        raise ValueError("height must be an integer of at least 100")
    if not isinstance(density, str) or density not in _DENSITIES:
        raise ValueError(f"density must be one of {sorted(_DENSITIES)}")
    if not isinstance(checkbox_selection, bool):
        raise TypeError("checkbox_selection must be a boolean")
    if not isinstance(disabled, bool):
        raise TypeError("disabled must be a boolean")
    if on_change is not None and not callable(on_change):
        raise TypeError("on_change must be callable or None")

    valid_ids = {_row_id_key(row[id_field]) for row in normalized_rows}
    column_fields = {column["field"] for column in normalized_columns}
    normalized_selected = _normalize_selected_rows(selected_rows, valid_ids=valid_ids)
    normalized_sort = _normalize_sort_model(sort_model, column_fields=column_fields)
    normalized_filter = _normalize_filter_model(
        filter_model, column_fields=column_fields
    )
    default = {
        "selected_rows": normalized_selected,
        "sort_model": normalized_sort,
        "filter_model": normalized_filter,
        "pagination_model": {"page": 0, "pageSize": page_size},
    }

    def _noop():
        pass

    result = _component(
        key=key,
        default=default,
        data={
            "rows": normalized_rows,
            "columns": normalized_columns,
            "idField": id_field,
            "selectedRows": normalized_selected,
            "sortModel": normalized_sort,
            "filterModel": normalized_filter,
            "pageSize": page_size,
            "pageSizeOptions": normalized_page_sizes,
            "height": height,
            "checkboxSelection": checkbox_selection,
            "density": density,
            "disabled": disabled,
        },
        on_selected_rows_change=_noop,
        on_sort_model_change=_noop,
        on_filter_model_change=_noop,
        on_pagination_model_change=_noop,
        on_grid_event_change=on_change if on_change is not None else _noop,
    )
    if not isinstance(result, Mapping):
        return default

    try:
        returned_selected = _normalize_selected_rows(
            result.get("selected_rows", normalized_selected),
            valid_ids=valid_ids,
        )
    except (TypeError, ValueError):
        returned_selected = normalized_selected
    try:
        returned_sort = _normalize_sort_model(
            result.get("sort_model", normalized_sort),
            column_fields=column_fields,
        )
    except (TypeError, ValueError):
        returned_sort = normalized_sort
    try:
        returned_filter = _normalize_filter_model(
            result.get("filter_model", normalized_filter),
            column_fields=column_fields,
        )
    except (TypeError, ValueError):
        returned_filter = normalized_filter
    try:
        returned_pagination = _normalize_pagination_model(
            result.get("pagination_model", default["pagination_model"]),
            page_size_options=normalized_page_sizes,
            row_count=len(normalized_rows),
        )
    except (TypeError, ValueError):
        returned_pagination = default["pagination_model"]

    return {
        "selected_rows": returned_selected,
        "sort_model": returned_sort,
        "filter_model": returned_filter,
        "pagination_model": returned_pagination,
    }
