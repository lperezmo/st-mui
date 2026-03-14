import { FC, useCallback, useMemo } from "react";
import { FrontendRendererArgs } from "@streamlit/component-v2-lib";
import Box from "@mui/material/Box";
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
  autoHeight: boolean;
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
  const {
    rows,
    columns,
    pageSize,
    checkboxSelection,
    density,
    autoHeight,
  } = data;

  const colDefs = useMemo<GridColDef[]>(
    () =>
      columns.map((col) => ({
        flex: 1,
        ...col,
      })),
    [columns]
  );

  const handleRowSelection = useCallback(
    (model: GridRowSelectionModel) => {
      setStateValue("selected_rows", [...model.ids] as (string | number)[]);
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
    <Box sx={{ width: "100%", minHeight: autoHeight ? undefined : 400 }}>
      <MuiDataGrid
        rows={rows}
        columns={colDefs}
        density={density}
        autoHeight={autoHeight}
        pageSizeOptions={[pageSize, 25, 50, 100]}
        initialState={{
          pagination: { paginationModel: { pageSize } },
        }}
        checkboxSelection={checkboxSelection}
        disableRowSelectionOnClick
        onRowSelectionModelChange={handleRowSelection}
        onSortModelChange={handleSortChange}
        onFilterModelChange={handleFilterChange}
        sx={{
          // Ensure proper border rendering in Streamlit context
          "& .MuiDataGrid-cell": {
            borderColor: "divider",
          },
        }}
      />
    </Box>
  );
};

export default DataGridComponent;
