import { describe, expect, it } from "vitest";

import { isTreeItemDisabled } from "../src/tree_view/TreeView";

describe("TreeView disabled state", () => {
  it("disables every item when the component is disabled", () => {
    expect(isTreeItemDisabled(true)).toBe(true);
    expect(isTreeItemDisabled(false)).toBe(false);
  });
});
