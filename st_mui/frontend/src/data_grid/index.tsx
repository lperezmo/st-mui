import { createMuiRenderer } from "../shared/renderer";
import DataGridComponent, { DataGridData, DataGridState } from "./DataGrid";

export default createMuiRenderer<DataGridState, DataGridData>(
  DataGridComponent,
  { emotionKey: "st-mui-data-grid" },
);
