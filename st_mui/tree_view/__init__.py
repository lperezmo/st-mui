"""MUI X TreeView component for Streamlit."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from st_mui._compat import component

_component = component(
    "st-mui.tree_view",
    js="index-*.js",
    html='<div class="react-root"></div>',
)


def _normalize_items(
    items: list[dict[str, Any]] | None,
) -> tuple[list[dict[str, Any]], set[str]]:
    if items is None:
        return [], set()
    if not isinstance(items, list):
        raise TypeError("items must be a list of mappings or None")

    normalized: list[dict[str, Any]] = []
    allowed_ids: set[str] = set()
    active_lists = {id(items)}
    stack = [(iter(items), normalized, id(items))]

    while stack:
        iterator, target, list_id = stack[-1]
        try:
            item = next(iterator)
        except StopIteration:
            active_lists.remove(list_id)
            stack.pop()
            continue

        if not isinstance(item, Mapping):
            raise TypeError("each tree item must be a mapping")
        item_id = item.get("id")
        label = item.get("label")
        if not isinstance(item_id, str) or not item_id:
            raise ValueError("each tree item id must be a non-empty string")
        if not isinstance(label, str):
            raise TypeError("each tree item label must be a string")
        if item_id in allowed_ids:
            raise ValueError(f"items contains duplicate id {item_id!r}")
        allowed_ids.add(item_id)

        copied = dict(item)
        children = copied.get("children")
        if children is not None:
            if not isinstance(children, list):
                raise TypeError("tree item children must be a list")
            if id(children) in active_lists:
                raise ValueError("items must not contain a cycle")
            normalized_children: list[dict[str, Any]] = []
            copied["children"] = normalized_children
        target.append(copied)

        if children:
            active_lists.add(id(children))
            stack.append((iter(children), normalized_children, id(children)))

    return normalized, allowed_ids


def _normalize_ids(
    value: Any,
    *,
    field: str,
    allowed_ids: set[str],
    multi_select: bool = True,
) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise TypeError(f"{field} must be a list of strings or None")
    normalized: list[str] = []
    seen: set[str] = set()
    for item_id in value:
        if not isinstance(item_id, str):
            raise TypeError(f"{field} must contain only strings")
        if item_id not in allowed_ids:
            raise ValueError(f"{field} contains unknown id {item_id!r}")
        if item_id in seen:
            raise ValueError(f"{field} contains duplicate id {item_id!r}")
        seen.add(item_id)
        normalized.append(item_id)
    if not multi_select and len(normalized) > 1:
        raise ValueError(f"{field} may contain at most one id")
    return normalized


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
        Whether selection and expansion are disabled for every tree item.
    on_change : callable or None
        Callback when the selection changes.
    key : str or None
        Unique widget key.

    Returns
    -------
    list of str
        List of selected item IDs.
    """
    normalized_items, allowed_ids = _normalize_items(items)
    default_sel = _normalize_ids(
        default_selected,
        field="default_selected",
        allowed_ids=allowed_ids,
        multi_select=multi_select,
    )
    default_exp = _normalize_ids(
        default_expanded,
        field="default_expanded",
        allowed_ids=allowed_ids,
    )

    def _noop():
        pass

    result = _component(
        key=key,
        default={"selected_items": default_sel, "expanded_items": default_exp},
        data={
            "items": normalized_items,
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

    if not isinstance(result, Mapping) or "selected_items" not in result:
        return default_sel
    try:
        return _normalize_ids(
            result.get("selected_items"),
            field="selected_items",
            allowed_ids=allowed_ids,
            multi_select=multi_select,
        )
    except (TypeError, ValueError):
        return default_sel
