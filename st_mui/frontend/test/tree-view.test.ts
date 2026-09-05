import { describe, expect, it } from "vitest";

import { normalizeTreeSelection } from "../src/tree_view/TreeView";

describe("TreeView selection normalization", () => {
  it("keeps every id in multi-select mode", () => {
    expect(normalizeTreeSelection(["a", "b"], true)).toEqual(["a", "b"]);
  });

  it("clamps to one id in single-select mode", () => {
    expect(normalizeTreeSelection(["a", "b"], false)).toEqual(["a"]);
    expect(normalizeTreeSelection(["a"], false)).toEqual(["a"]);
    expect(normalizeTreeSelection([], false)).toEqual([]);
  });
});
