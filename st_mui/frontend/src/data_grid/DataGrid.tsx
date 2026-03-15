import { FC, useCallback, useMemo } from "react";
import { FrontendRendererArgs } from "@streamlit/component-v2-lib";
import {
  DataGrid as MuiDataGrid,
  GridColDef,
  GridRowSelectionModel,
  GridSortModel,
  GridFilterModel,
} from "@mui/x-data-grid";

export type DataGridState = {
  selected_rows: (string | number)[];
  sort_model: GridSortModel;
  filter_model: GridFilterModel;
};

export type DataGridData = {
  rows: Record<string, unknown>[];
  columns: GridColDef[];
  pageSize: number;
  checkboxSelection: boolean;
  density: "compact" | "standard" | "comfortable";
  height: number;
  disabled: boolean;
};

type Props = {
  data: DataGridData;
  setStateValue: FrontendRendererArgs<
    DataGridState,
    DataGridData
  >["setStateValue"];
};

const DataGridComponent: FC<Props> = ({ data, setStateValue }) => {
  const rows = data.rows ?? [];
  const columns = data.columns ?? [];
  const pageSize = data.pageSize ?? 10;
  const checkboxSelection = data.checkboxSelection ?? false;
  const density = data.density ?? "standard";
  const height = data.height ?? 400;

  const colDefs = useMemo<GridColDef[]>(
    () =>
      columns.map((col) => ({
        flex: 1,
        ...col,
      })),
    [columns]
  );

  // Deduplicate page size options
  const pageSizeOptions = useMemo(
    () => [...new Set([pageSize, 25, 50, 100])].sort((a, b) => a - b),
    [pageSize]
  );

  const handleRowSelection = useCallback(
    (model: GridRowSelectionModel) => {
      // v8: model is { type: 'include'|'exclude', ids: Set<GridRowId> }
      const ids = model.ids ? [...model.ids] : [];
      setStateValue("selected_rows", ids as (string | number)[]);
    },
    [setStateValue]
  );

  const handleSortChange = useCallback(
    (model: GridSortModel) => {
      setStateValue("sort_model", model);
    },
    [setStateValue]
  );

  const handleFilterChange = useCallback(
    (model: GridFilterModel) => {
      setStateValue("filter_model", model);
    },
    [setStateValue]
  );

  return (
    <div style={{ width: "100%", height }}>
      <MuiDataGrid
        rows={rows}
        columns={colDefs}
        density={density}
        pageSizeOptions={pageSizeOptions}
        initialState={{
          pagination: { paginationModel: { pageSize, page: 0 } },
        }}
        checkboxSelection={checkboxSelection}
        disableRowSelectionOnClick
        onRowSelectionModelChange={handleRowSelection}
        onSortModelChange={handleSortChange}
        onFilterModelChange={handleFilterChange}
      />
    </div>
  );
};

export default DataGridComponent;
