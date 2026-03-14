import { createMuiRenderer } from "../shared/renderer";
import DataGridComponent, {
  DataGridState,
  DataGridData,
} from "./DataGrid";

export default createMuiRenderer<DataGridState, DataGridData>(
  DataGridComponent
);
