import { FC, useCallback } from "react";
import { FrontendRendererArgs } from "@streamlit/component-v2-lib";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import { RichTreeView } from "@mui/x-tree-view/RichTreeView";
import { TreeViewBaseItem } from "@mui/x-tree-view/models";

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

const TreeViewComponent: FC<Props> = ({ data, setStateValue }) => {
  const { items, label, multiSelect, checkboxSelection, defaultExpanded, defaultSelected } = data;

  const handleSelectedChange = useCallback(
    (_event: React.SyntheticEvent | null, itemIds: string | string[] | null) => {
      const selected = itemIds === null ? [] : Array.isArray(itemIds) ? itemIds : [itemIds];
      setStateValue("selected_items", selected);
    },
    [setStateValue]
  );

  const handleExpandedChange = useCallback(
    (_event: React.SyntheticEvent | null, itemIds: string[]) => {
      setStateValue("expanded_items", itemIds);
    },
    [setStateValue]
  );

  return (
    <Box sx={{ width: "100%", py: 0.5 }}>
      {label && (
        <Typography variant="body2" sx={{ mb: 0.5, fontWeight: 500 }}>
          {label}
        </Typography>
      )}
      <RichTreeView
        items={items}
        multiSelect={multiSelect}
        checkboxSelection={checkboxSelection}
        defaultExpandedItems={defaultExpanded}
        defaultSelectedItems={multiSelect ? defaultSelected : (defaultSelected[0] ?? undefined)}
        onSelectedItemsChange={handleSelectedChange}
        onExpandedItemsChange={handleExpandedChange}
      />
    </Box>
  );
};

export default TreeViewComponent;
