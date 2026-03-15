"""MUI X DataGrid component for Streamlit."""

from __future__ import annotations

from typing import Any, Callable

import streamlit as st

_component = st.components.v2.component(
    "st-mui.data_grid",
    js="index-*.js",
    html='<div class="react-root"></div>',
    isolate_styles=False,
)


def data_grid(
    rows: list[dict[str, Any]] | None = None,
    columns: list[dict[str, Any]] | None = None,
    page_size: int = 10,
    height: int = 400,
    checkbox_selection: bool = False,
    density: str = "standard",
    disabled: bool = False,
    on_change: Callable | None = None,
    key: str | None = None,
) -> dict[str, Any]:
    """A rich data grid powered by MUI X DataGrid (Community).

    Parameters
    ----------
    rows : list of dicts
        Row data. Each dict must have an "id" field.
    columns : list of dicts
        Column definitions. Each dict should have at minimum
        "field" and "headerName" keys.
    page_size : int
        Number of rows per page.
    height : int
        Height of the grid in pixels.
    checkbox_selection : bool
        Enable row selection checkboxes.
    density : str
        Grid density: "compact", "standard", or "comfortable".
    disabled : bool
        Whether the grid is read-only.
    on_change : callable or None
        Callback when selection or sort/filter changes.
    key : str or None
        Unique widget key.

    Returns
    -------
    dict
        Dictionary with "selected_rows" (list of row ids),
        "sort_model", and "filter_model".
    """
    default = {"selected_rows": [], "sort_model": [], "filter_model": {"items": []}}

    def _noop():
        pass

    result = _component(
        key=key,
        default=default,
        height=height,
        data={
            "rows": rows or [],
            "columns": columns or [],
            "pageSize": page_size,
            "checkboxSelection": checkbox_selection,
            "density": density,
            "height": height,
            "disabled": disabled,
        },
        on_selected_rows_change=on_change or _noop,
        on_sort_model_change=_noop,
        on_filter_model_change=_noop,
    )
    return result or default
