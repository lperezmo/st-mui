import { type FC, useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { FrontendRendererArgs } from "@streamlit/component-v2-lib";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import {
  DataGrid as MuiDataGrid,
  type GridColDef,
  type GridFilterModel,
  type GridPaginationModel,
  type GridRowId,
  type GridRowSelectionModel,
  type GridSortModel,
  type GridValidRowModel,
} from "@mui/x-data-grid";

export type DataGridEvent = {
  type: "selection" | "sort" | "filter" | "pagination";
  value: unknown;
};

export type DataGridState = {
  selected_rows: GridRowId[];
  sort_model: GridSortModel;
  filter_model: GridFilterModel;
  pagination_model: GridPaginationModel;
  grid_event: DataGridEvent;
};

export type DataGridData = {
  rows: GridValidRowModel[];
  columns: GridColDef[];
  idField: string;
  selectedRows: GridRowId[];
  sortModel: GridSortModel;
  filterModel: GridFilterModel;
  pageSize: number;
  pageSizeOptions: number[];
  height: number;
  checkboxSelection: boolean;
  density: "compact" | "standard" | "comfortable";
  disabled: boolean;
};

type Props = {
  data: DataGridData;
  setStateValue: FrontendRendererArgs<
    DataGridState,
    DataGridData
  >["setStateValue"];
  setTriggerValue: FrontendRendererArgs<
    DataGridState,
    DataGridData
  >["setTriggerValue"];
};

export function selectionModelFromIds(ids: GridRowId[]): GridRowSelectionModel {
  return { type: "include", ids: new Set(ids) };
}

export function idsFromSelectionModel(
  model: GridRowSelectionModel,
  allRowIds: GridRowId[],
): GridRowId[] {
  if (model.type === "exclude") {
    return allRowIds.filter((id) => !model.ids.has(id));
  }
  return [...model.ids];
}

export function sameGridRowId(left: GridRowId, right: GridRowId): boolean {
  return typeof left === typeof right && left === right;
}

export function sameGridRowIds(left: GridRowId[], right: GridRowId[]): boolean {
  // Selection order is not semantically meaningful (header select-all,
  // shift-click, and Python round-trips can reorder). Compare as multisets
  // so equivalent selections don't ping-pong setStateValue.
  if (left.length !== right.length) return false;
  const remaining = [...right];
  for (const id of left) {
    const index = remaining.findIndex((candidate) =>
      sameGridRowId(candidate, id),
    );
    if (index === -1) return false;
    remaining.splice(index, 1);
  }
  return true;
}

export function gridRowIdKey(id: GridRowId): string {
  return `${typeof id}:${String(id)}`;
}

export function sameGridModel(left: unknown, right: unknown): boolean {
  if (Object.is(left, right)) return true;
  if (Array.isArray(left) || Array.isArray(right)) {
    return (
      Array.isArray(left) &&
      Array.isArray(right) &&
      left.length === right.length &&
      left.every((item, index) => sameGridModel(item, right[index]))
    );
  }
  if (
    left === null ||
    right === null ||
    typeof left !== "object" ||
    typeof right !== "object"
  ) {
    return false;
  }
  const leftRecord = left as Record<string, unknown>;
  const rightRecord = right as Record<string, unknown>;
  const leftKeys = Object.keys(leftRecord);
  const rightKeys = Object.keys(rightRecord);
  return (
    leftKeys.length === rightKeys.length &&
    leftKeys.every(
      (key) =>
        Object.prototype.hasOwnProperty.call(rightRecord, key) &&
        sameGridModel(leftRecord[key], rightRecord[key]),
    )
  );
}

export function reconcileGridModel<T>(
  current: T,
  previousExternal: T,
  nextExternal: T,
  equal: (left: T, right: T) => boolean,
): T {
  return equal(previousExternal, nextExternal) ? current : nextExternal;
}

export function clampPaginationModel(
  model: GridPaginationModel,
  rowCount: number,
  fallbackPageSize: number,
  pageSizeOptions: number[],
): GridPaginationModel {
  const pageSize = pageSizeOptions.includes(model.pageSize)
    ? model.pageSize
    : fallbackPageSize;
  const maxPage = Math.max(0, Math.ceil(rowCount / pageSize) - 1);
  return {
    page: Math.min(Math.max(0, model.page), maxPage),
    pageSize,
  };
}

const DataGridComponent: FC<Props> = ({
  data,
  setStateValue,
  setTriggerValue,
}) => {
  const {
    rows,
    columns,
    idField,
    selectedRows,
    sortModel,
    filterModel,
    pageSize,
    pageSizeOptions,
    height,
    checkboxSelection,
    density,
    disabled,
  } = data;
  const allRowIds = useMemo(
    () => rows.map((row) => row[idField] as GridRowId),
    [rows, idField],
  );
  const columnFields = useMemo(
    () => new Set(columns.map((column) => column.field)),
    [columns],
  );
  const [selection, setSelection] = useState<GridRowSelectionModel>(() =>
    selectionModelFromIds(selectedRows),
  );
  const [sort, setSort] = useState<GridSortModel>(sortModel);
  const [filter, setFilter] = useState<GridFilterModel>(filterModel);
  const [pagination, setPagination] = useState<GridPaginationModel>({
    page: 0,
    pageSize,
  });
  const selectedRowsRef = useRef<GridRowId[]>(selectedRows);
  const previousSelectedRowsRef = useRef<GridRowId[]>(selectedRows);
  const sortRef = useRef<GridSortModel>(sortModel);
  const previousSortRef = useRef<GridSortModel>(sortModel);
  const filterRef = useRef<GridFilterModel>(filterModel);
  const previousFilterRef = useRef<GridFilterModel>(filterModel);
  const paginationRef = useRef<GridPaginationModel>({ page: 0, pageSize });
  const previousPageSizeRef = useRef(pageSize);

  useEffect(() => {
    const source = reconcileGridModel(
      selectedRowsRef.current,
      previousSelectedRowsRef.current,
      selectedRows,
      sameGridRowIds,
    );
    const validIdKeys = new Set(allRowIds.map(gridRowIdKey));
    const next = source.filter((id) => validIdKeys.has(gridRowIdKey(id)));
    const stateChanged = !sameGridRowIds(selectedRowsRef.current, next);
    selectedRowsRef.current = next;
    previousSelectedRowsRef.current = selectedRows;
    setSelection(selectionModelFromIds(next));
    if (stateChanged) setStateValue("selected_rows", next);
  }, [selectedRows, allRowIds, setStateValue]);

  useEffect(() => {
    const source = reconcileGridModel(
      sortRef.current,
      previousSortRef.current,
      sortModel,
      sameGridModel,
    );
    const next = source
      .filter((item) => columnFields.has(item.field))
      .slice(0, 1);
    const stateChanged = !sameGridModel(sortRef.current, next);
    sortRef.current = next;
    previousSortRef.current = sortModel;
    setSort(next);
    if (stateChanged) setStateValue("sort_model", next);
  }, [sortModel, columnFields, setStateValue]);

  useEffect(() => {
    const source = reconcileGridModel(
      filterRef.current,
      previousFilterRef.current,
      filterModel,
      sameGridModel,
    );
    const next = {
      ...source,
      items: source.items
        .filter((item) => columnFields.has(item.field))
        .slice(0, 1),
    };
    const stateChanged = !sameGridModel(filterRef.current, next);
    filterRef.current = next;
    previousFilterRef.current = filterModel;
    setFilter(next);
    if (stateChanged) setStateValue("filter_model", next);
  }, [filterModel, columnFields, setStateValue]);

  useEffect(() => {
    const source =
      previousPageSizeRef.current === pageSize
        ? paginationRef.current
        : { page: 0, pageSize };
    const next = clampPaginationModel(
      source,
      rows.length,
      pageSize,
      pageSizeOptions,
    );
    const stateChanged = !sameGridModel(paginationRef.current, next);
    paginationRef.current = next;
    previousPageSizeRef.current = pageSize;
    setPagination(next);
    if (stateChanged) setStateValue("pagination_model", next);
  }, [pageSize, pageSizeOptions, rows.length, setStateValue]);

  const emit = useCallback(
    (event: DataGridEvent) => setTriggerValue("grid_event", event),
    [setTriggerValue],
  );

  const handleSelection = useCallback(
    (model: GridRowSelectionModel) => {
      if (disabled) return;
      const ids = idsFromSelectionModel(model, allRowIds);
      setSelection(model);
      if (sameGridRowIds(selectedRowsRef.current, ids)) return;
      selectedRowsRef.current = ids;
      setStateValue("selected_rows", ids);
      emit({ type: "selection", value: ids });
    },
    [allRowIds, disabled, emit, setStateValue],
  );

  const handleSort = useCallback(
    (model: GridSortModel) => {
      if (disabled) return;
      // Community single-sort contract: Python slices to one item, so clamp
      // locally too or the grid diverges until the next prop sync.
      const next = model.slice(0, 1);
      setSort(next);
      if (sameGridModel(sortRef.current, next)) return;
      sortRef.current = next;
      setStateValue("sort_model", next);
      emit({ type: "sort", value: next });
    },
    [disabled, emit, setStateValue],
  );

  const handleFilter = useCallback(
    (model: GridFilterModel) => {
      if (disabled) return;
      // Same single-filter contract as sorting: clamp locally.
      const next = { ...model, items: model.items.slice(0, 1) };
      setFilter(next);
      if (sameGridModel(filterRef.current, next)) return;
      filterRef.current = next;
      setStateValue("filter_model", next);
      emit({ type: "filter", value: next });
    },
    [disabled, emit, setStateValue],
  );

  const handlePagination = useCallback(
    (model: GridPaginationModel) => {
      if (disabled) return;
      const next = clampPaginationModel(
        model,
        rows.length,
        pageSize,
        pageSizeOptions,
      );
      setPagination(next);
      if (sameGridModel(paginationRef.current, next)) return;
      paginationRef.current = next;
      setStateValue("pagination_model", next);
      emit({ type: "pagination", value: next });
    },
    [disabled, emit, pageSize, pageSizeOptions, rows.length, setStateValue],
  );

  if (columns.length === 0) {
    return (
      <Box sx={{ width: "100%", height }}>
        <Typography variant="body2" color="text.secondary">
          No columns
        </Typography>
      </Box>
    );
  }

  return (
    <Box
      aria-disabled={disabled}
      sx={{
        width: "100%",
        height,
        opacity: disabled ? 0.6 : 1,
        // Keep scroll enabled when disabled so large grids remain
        // inspectable; interaction is blocked via rowSelection guards,
        // disable* props, and early returns in the handlers above.
      }}
    >
      <MuiDataGrid
        aria-label="Data grid"
        rows={rows}
        columns={columns}
        getRowId={(row) => row[idField] as GridRowId}
        density={density}
        pageSizeOptions={pageSizeOptions}
        paginationModel={pagination}
        rowSelectionModel={selection}
        sortModel={sort}
        filterModel={filter}
        checkboxSelection={checkboxSelection}
        disableRowSelectionOnClick={checkboxSelection}
        rowSelection={!disabled}
        disableColumnFilter={disabled}
        disableColumnMenu={disabled}
        disableColumnResize={disabled}
        disableColumnSorting={disabled}
        isRowSelectable={() => !disabled}
        onRowSelectionModelChange={handleSelection}
        onSortModelChange={handleSort}
        onFilterModelChange={handleFilter}
        onPaginationModelChange={handlePagination}
        slotProps={{
          baseButton: { disabled },
          baseCheckbox: { disabled },
          baseIconButton: { disabled },
          baseSelect: { disabled },
        }}
      />
    </Box>
  );
};

export default DataGridComponent;
