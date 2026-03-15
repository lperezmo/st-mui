import { createMuiRenderer } from "../shared/renderer";
import TreeViewComponent, {
  TreeViewState,
  TreeViewData,
} from "./TreeView";

export default createMuiRenderer<TreeViewState, TreeViewData>(
  TreeViewComponent
);
