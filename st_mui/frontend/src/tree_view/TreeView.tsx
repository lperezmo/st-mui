import { type FC, useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { FrontendRendererArgs } from "@streamlit/component-v2-lib";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import { RichTreeView } from "@mui/x-tree-view/RichTreeView";
import type { TreeViewBaseItem } from "@mui/x-tree-view/models";

export type TreeViewState = {
  selected_items: string[];
  expanded_items: string[];
};

export type TreeViewData = {
  items: TreeViewBaseItem[];
  label: string | null;
  multiSelect: boolean;
  checkboxSelection: boolean;
  defaultExpanded: string[];
  defaultSelected: string[];
  disabled: boolean;
};

type Props = {
  data: TreeViewData;
  setStateValue: FrontendRendererArgs<
    TreeViewState,
    TreeViewData
  >["setStateValue"];
};

export function sameTreeIds(left: string[], right: string[]): boolean {
  return (
    left.length === right.length && left.every((id, index) => id === right[index])
  );
}

export function reconcileTreeIds(
  current: string[],
  previousExternal: string[],
  nextExternal: string[],
): string[] {
  return sameTreeIds(previousExternal, nextExternal) ? current : [...nextExternal];
}

// Keeps the first occurrence of each known id. Python already rejects unknown
// and duplicate ids in defaults, so this upholds the same invariant for ids
// that arrive from MUI callbacks.
export function filterValidTreeIds(ids: string[], validIds: Set<string>): string[] {
  const seen = new Set<string>();
  const result: string[] = [];
  for (const id of ids) {
    if (!validIds.has(id) || seen.has(id)) continue;
    seen.add(id);
    result.push(id);
  }
  return result;
}

export function collectTreeIds(items: TreeViewBaseItem[]): Set<string> {
  const ids = new Set<string>();
  const stack = [...items];
  while (stack.length > 0) {
    const item = stack.pop() as TreeViewBaseItem & {
      children?: TreeViewBaseItem[];
    };
    if (!item || typeof item.id !== "string") continue;
    ids.add(item.id);
    if (Array.isArray(item.children)) stack.push(...item.children);
  }
  return ids;
}

const TreeViewComponent: FC<Props> = ({ data, setStateValue }) => {
  const {
    items,
    label,
    multiSelect,
    checkboxSelection,
    defaultExpanded,
    defaultSelected,
    disabled,
  } = data;

  const validIds = useMemo(() => collectTreeIds(items), [items]);
  const initialSelected = useMemo(
    () => filterValidTreeIds(defaultSelected, validIds),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [],
  );
  const initialExpanded = useMemo(
    () => filterValidTreeIds(defaultExpanded, validIds),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [],
  );
  const [selected, setSelected] = useState<string[]>(initialSelected);
  const [expanded, setExpanded] = useState<string[]>(initialExpanded);
  const selectedRef = useRef<string[]>(initialSelected);
  const expandedRef = useRef<string[]>(initialExpanded);
  const previousSelectedRef = useRef<string[]>(defaultSelected);
  const previousExpandedRef = useRef<string[]>(defaultExpanded);

  useEffect(() => {
    const nextSelected = filterValidTreeIds(
      reconcileTreeIds(
        selectedRef.current,
        previousSelectedRef.current,
        defaultSelected,
      ),
      validIds,
    );
    previousSelectedRef.current = defaultSelected;
    if (!sameTreeIds(selectedRef.current, nextSelected)) {
      selectedRef.current = nextSelected;
      setSelected(nextSelected);
      setStateValue("selected_items", nextSelected);
    }

    const nextExpanded = filterValidTreeIds(
      reconcileTreeIds(
        expandedRef.current,
        previousExpandedRef.current,
        defaultExpanded,
      ),
      validIds,
    );
    previousExpandedRef.current = defaultExpanded;
    if (!sameTreeIds(expandedRef.current, nextExpanded)) {
      expandedRef.current = nextExpanded;
      setExpanded(nextExpanded);
      setStateValue("expanded_items", nextExpanded);
    }
  }, [defaultSelected, defaultExpanded, validIds, setStateValue]);

  const handleSelectedChange = useCallback(
    (
      _event: React.SyntheticEvent | null,
      itemIds: string | string[] | null,
    ) => {
      if (disabled) return;
      const next =
        itemIds === null ? [] : Array.isArray(itemIds) ? itemIds : [itemIds];
      const filtered = filterValidTreeIds(next, validIds);
      // Single-select mode keeps at most one id; Python already rejects
      // multi defaults, but guard here against uncontrolled MUI behavior.
      const finalIds = multiSelect ? filtered : filtered.slice(0, 1);
      if (sameTreeIds(selectedRef.current, finalIds)) return;
      selectedRef.current = finalIds;
      setSelected(finalIds);
      setStateValue("selected_items", finalIds);
    },
    [disabled, multiSelect, setStateValue, validIds],
  );

  const handleExpandedChange = useCallback(
    (_event: React.SyntheticEvent | null, itemIds: string[]) => {
      if (disabled) return;
      const filtered = filterValidTreeIds(itemIds, validIds);
      if (sameTreeIds(expandedRef.current, filtered)) return;
      expandedRef.current = filtered;
      setExpanded(filtered);
      setStateValue("expanded_items", filtered);
    },
    [disabled, setStateValue, validIds],
  );

  const hasLabel = typeof label === "string" && label.trim() !== "";

  return (
    <Box sx={{ width: "100%", py: 0.5 }}>
      {hasLabel && (
        <Typography variant="body2" sx={{ mb: 0.5, fontWeight: 500 }}>
          {label}
        </Typography>
      )}
      {items.length === 0 ? (
        <Typography variant="body2" color="text.secondary">
          No items
        </Typography>
      ) : (
        <RichTreeView
          items={items}
          aria-label={hasLabel ? (label as string) : "Tree view"}
          multiSelect={multiSelect}
          checkboxSelection={checkboxSelection}
          expandedItems={expanded}
          selectedItems={multiSelect ? selected : (selected[0] ?? null)}
          isItemDisabled={() => disabled}
          onSelectedItemsChange={handleSelectedChange}
          onExpandedItemsChange={handleExpandedChange}
        />
      )}
    </Box>
  );
};

export default TreeViewComponent;
