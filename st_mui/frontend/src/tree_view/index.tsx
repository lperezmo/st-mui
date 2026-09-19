import { createMuiRenderer } from "../shared/renderer";
import TreeViewComponent, {
  type TreeViewState,
  type TreeViewData,
} from "./TreeView";

export default createMuiRenderer<TreeViewState, TreeViewData>(
  TreeViewComponent,
  { emotionKey: "st-mui-tree-view" },
);
