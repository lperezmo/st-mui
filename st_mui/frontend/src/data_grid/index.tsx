import { createMuiRenderer } from "../shared/renderer";
import DataGridComponent, {
  type DataGridData,
  type DataGridState,
} from "./DataGrid";

export default createMuiRenderer<DataGridState, DataGridData>(
  DataGridComponent,
  { emotionKey: "st-mui-data-grid" },
);
