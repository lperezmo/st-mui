import { createMuiRenderer } from "../shared/renderer";
import TreeViewComponent from "./TreeView";
import type {
  TreeViewState,
  TreeViewData,
} from "./TreeView";

export default createMuiRenderer<TreeViewState, TreeViewData>(
  TreeViewComponent,
  { emotionKey: "st-mui-tree-view" },
);
