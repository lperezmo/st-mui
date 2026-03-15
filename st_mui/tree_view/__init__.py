"""MUI X TreeView component for Streamlit."""

from __future__ import annotations

from typing import Any, Callable

import streamlit as st

_component = st.components.v2.component(
    "st-mui.tree_view",
    js="index-*.js",
    html='<div class="react-root"></div>',
    isolate_styles=False,
)


def tree_view(
    items: list[dict[str, Any]] | None = None,
    label: str | None = None,
    multi_select: bool = False,
    checkbox_selection: bool = True,
    default_expanded: list[str] | None = None,
    default_selected: list[str] | None = None,
    disabled: bool = False,
    on_change: Callable | None = None,
    key: str | None = None,
) -> list[str]:
    """A hierarchical tree view powered by MUI X RichTreeView.

    Parameters
    ----------
    items : list of dicts
        Tree data. Each dict should have "id" and "label" keys, and
        optionally a "children" key with nested items of the same shape.
    label : str or None
        Optional label displayed above the tree.
    multi_select : bool
        Whether multiple items can be selected.
    checkbox_selection : bool
        Whether to show checkboxes next to each item.
    default_expanded : list of str or None
        Item IDs to expand by default.
    default_selected : list of str or None
        Item IDs to select by default.
    disabled : bool
        Whether the tree is disabled.
    on_change : callable or None
        Callback when the selection changes.
    key : str or None
        Unique widget key.

    Returns
    -------
    list of str
        List of selected item IDs.
    """
    default_sel = default_selected or []
    default_exp = default_expanded or []

    def _noop():
        pass

    result = _component(
        key=key,
        default={"selected_items": default_sel, "expanded_items": default_exp},
        data={
            "items": items or [],
            "label": label,
            "multiSelect": multi_select,
            "checkboxSelection": checkbox_selection,
            "defaultExpanded": default_exp,
            "defaultSelected": default_sel,
            "disabled": disabled,
        },
        on_selected_items_change=on_change or _noop,
        on_expanded_items_change=_noop,
    )

    if result:
        return result.get("selected_items", [])
    return []
