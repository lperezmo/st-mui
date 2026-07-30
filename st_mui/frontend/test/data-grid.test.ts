import { describe, expect, it } from "vitest";
import {
  clampPaginationModel,
  idsFromSelectionModel,
  reconcileGridModel,
  sameGridModel,
  sameGridRowId,
  sameGridRowIds,
  selectionModelFromIds,
} from "../src/data_grid/DataGrid";

describe("data grid selection helpers", () => {
  it("round-trips include selection models", () => {
    const model = selectionModelFromIds([1, "two"]);
    expect(model.type).toBe("include");
    expect(idsFromSelectionModel(model, [1, "two", 3])).toEqual([1, "two"]);
  });

  it("expands exclude selection models against the current rows", () => {
    const model = { type: "exclude" as const, ids: new Set([2]) };
    expect(idsFromSelectionModel(model, [1, 2, 3])).toEqual([1, 3]);
  });
});

describe("data grid controlled-state helpers", () => {
  it("keeps numeric and string row ids distinct", () => {
    expect(sameGridRowId(1, "1")).toBe(false);
    expect(sameGridRowIds([1, "1"], [1, "1"])).toBe(true);
    expect(sameGridRowIds([1], ["1"])).toBe(false);
  });

  it("preserves user state when the Python default is unchanged", () => {
    expect(reconcileGridModel([2], [1], [1], sameGridRowIds)).toEqual([2]);
  });

  it("honors a genuinely changed Python default", () => {
    expect(reconcileGridModel([2], [1], [3], sameGridRowIds)).toEqual([3]);
  });

  it("compares nested sort and filter models structurally", () => {
    expect(
      sameGridModel(
        { items: [{ field: "name", operator: "contains", value: "A" }] },
        { items: [{ field: "name", operator: "contains", value: "A" }] },
      ),
    ).toBe(true);
    expect(sameGridModel({ items: [] }, { items: [{ field: "id" }] })).toBe(
      false,
    );
  });

  it("clamps stale pages and unsupported page sizes after data changes", () => {
    expect(
      clampPaginationModel({ page: 5, pageSize: 25 }, 12, 10, [10]),
    ).toEqual({ page: 1, pageSize: 10 });
    expect(
      clampPaginationModel({ page: -1, pageSize: 10 }, 0, 10, [10]),
    ).toEqual({ page: 0, pageSize: 10 });
  });
});
