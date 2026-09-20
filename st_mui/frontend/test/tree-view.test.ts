// @vitest-environment jsdom
import { createElement } from "react";
import { act, cleanup, render, screen } from "@testing-library/react";
import type { RichTreeViewProps } from "@mui/x-tree-view/RichTreeView";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import TreeViewComponent, {
  type TreeViewData,
} from "../src/tree_view/TreeView";

type TreeProps = RichTreeViewProps<TreeViewData["items"][number], boolean>;

const { richTreeView } = vi.hoisted(() => ({
  richTreeView: vi.fn<(props: unknown) => null>(() => null),
}));

vi.mock("@mui/x-tree-view/RichTreeView", () => ({
  RichTreeView: richTreeView,
}));

function renderTree(overrides: Partial<TreeViewData> = {}) {
  let data: TreeViewData = {
    items: [
      { id: "a", label: "A" },
      { id: "b", label: "B" },
    ],
    label: "Tree",
    multiSelect: false,
    checkboxSelection: false,
    defaultExpanded: [],
    defaultSelected: [],
    disabled: false,
    ...overrides,
  };
  const setStateValue = vi.fn();
  const view = render(
    createElement(TreeViewComponent, { data, setStateValue }),
  );
  return {
    get props(): TreeProps {
      const call = richTreeView.mock.calls.at(-1);
      if (!call) throw new Error("RichTreeView was never rendered");
      return call[0] as TreeProps;
    },
    get mountCount(): number {
      return richTreeView.mock.calls.length;
    },
    setStateValue,
    update(next: Partial<TreeViewData>) {
      data = { ...data, ...next };
      view.rerender(createElement(TreeViewComponent, { data, setStateValue }));
    },
  };
}

beforeEach(() => {
  richTreeView.mockClear();
});

afterEach(() => {
  cleanup();
});

describe("TreeView callbacks and controlled state", () => {
  it.each([true, false])(
    "wires disabled=%s to the item predicate",
    (disabled) => {
      const tree = renderTree({ disabled });
      expect(tree.props.isItemDisabled!({ id: "a", label: "A" })).toBe(
        disabled,
      );
      expect(tree.props.isItemDisabled!({ id: "b", label: "B" })).toBe(
        disabled,
      );
    },
  );

  it("ignores selection and expansion callbacks while disabled", () => {
    const tree = renderTree({ disabled: true });
    act(() => {
      tree.props.onSelectedItemsChange!(null, ["a"]);
      tree.props.onExpandedItemsChange!(null, ["b"]);
    });
    expect(tree.setStateValue).not.toHaveBeenCalled();
    expect(tree.props.selectedItems).toBeNull();
    expect(tree.props.expandedItems).toEqual([]);
  });

  it.each([
    { input: "b", expected: ["b"] },
    { input: ["missing", "b", "a"], expected: ["b"] },
    { input: ["missing"], expected: [] },
    { input: [], expected: [] },
    { input: null, expected: [] },
  ])("normalizes single selection $input", ({ input, expected }) => {
    const tree = renderTree({ defaultSelected: ["a"] });
    const original = Array.isArray(input) ? [...input] : input;
    act(() => tree.props.onSelectedItemsChange!(null, input));
    expect(tree.setStateValue).toHaveBeenCalledExactlyOnceWith(
      "selected_items",
      expected,
    );
    expect(tree.props.selectedItems).toBe(expected[0] ?? null);
    expect(input).toEqual(original);
  });

  it("retains valid multi-selection order without mutating callback input", () => {
    const tree = renderTree({ multiSelect: true });
    const input = ["b", "missing", "a"];
    act(() => tree.props.onSelectedItemsChange!(null, input));
    expect(tree.setStateValue).toHaveBeenCalledExactlyOnceWith(
      "selected_items",
      ["b", "a"],
    );
    expect(tree.props.selectedItems).toEqual(["b", "a"]);
    expect(input).toEqual(["b", "missing", "a"]);
  });

  it.each([null, [] as string[]])(
    "clears multi-selection with %j only once",
    (input) => {
      const tree = renderTree({
        multiSelect: true,
        defaultSelected: ["a", "b"],
      });
      act(() => tree.props.onSelectedItemsChange!(null, input));
      act(() => tree.props.onSelectedItemsChange!(null, input));
      expect(tree.props.selectedItems).toEqual([]);
      expect(tree.setStateValue).toHaveBeenCalledExactlyOnceWith(
        "selected_items",
        [],
      );
    },
  );

  it("collapses duplicate ids to the first occurrence", () => {
    const tree = renderTree({ multiSelect: true });
    act(() => tree.props.onSelectedItemsChange!(null, ["b", "a", "b"]));
    expect(tree.props.selectedItems).toEqual(["b", "a"]);
    expect(tree.setStateValue).toHaveBeenCalledExactlyOnceWith(
      "selected_items",
      ["b", "a"],
    );
    act(() => tree.props.onExpandedItemsChange!(null, ["a", "a"]));
    expect(tree.props.expandedItems).toEqual(["a"]);
    expect(tree.setStateValue).toHaveBeenLastCalledWith("expanded_items", [
      "a",
    ]);
  });

  it("does not emit unchanged selections or repeated callbacks after rerenders", () => {
    const tree = renderTree({ defaultSelected: ["a"] });
    act(() => tree.props.onSelectedItemsChange!(null, "a"));
    expect(tree.setStateValue).not.toHaveBeenCalled();
    act(() => tree.props.onSelectedItemsChange!(null, "b"));
    act(() => tree.props.onSelectedItemsChange!(null, ["b"]));
    expect(tree.props.selectedItems).toBe("b");
    expect(tree.setStateValue).toHaveBeenCalledExactlyOnceWith(
      "selected_items",
      ["b"],
    );
  });

  it("filters expansion IDs without mutation and suppresses duplicate callbacks", () => {
    const tree = renderTree();
    const input = ["missing", "a"];
    act(() => tree.props.onExpandedItemsChange!(null, input));
    act(() => tree.props.onExpandedItemsChange!(null, ["a"]));
    expect(tree.props.expandedItems).toEqual(["a"]);
    expect(input).toEqual(["missing", "a"]);
    expect(tree.setStateValue).toHaveBeenCalledExactlyOnceWith(
      "expanded_items",
      ["a"],
    );
  });

  it("ignores unchanged initial expansion and emits clearing only once", () => {
    const tree = renderTree({ defaultExpanded: ["a"] });
    act(() => tree.props.onExpandedItemsChange!(null, ["a"]));
    expect(tree.setStateValue).not.toHaveBeenCalled();
    act(() => tree.props.onExpandedItemsChange!(null, []));
    act(() => tree.props.onExpandedItemsChange!(null, []));
    expect(tree.props.expandedItems).toEqual([]);
    expect(tree.setStateValue).toHaveBeenCalledExactlyOnceWith(
      "expanded_items",
      [],
    );
  });

  it("preserves user state for unchanged defaults and reconciles changed defaults", () => {
    const tree = renderTree({ defaultSelected: ["a"], defaultExpanded: ["a"] });
    act(() => {
      tree.props.onSelectedItemsChange!(null, "b");
      tree.props.onExpandedItemsChange!(null, ["b"]);
    });
    tree.setStateValue.mockClear();
    tree.update({ defaultSelected: ["a"], defaultExpanded: ["a"] });
    expect(tree.props.selectedItems).toBe("b");
    expect(tree.props.expandedItems).toEqual(["b"]);
    expect(tree.setStateValue).not.toHaveBeenCalled();
    tree.update({ defaultSelected: [], defaultExpanded: [] });
    expect(tree.props.selectedItems).toBeNull();
    expect(tree.props.expandedItems).toEqual([]);
    expect(tree.setStateValue.mock.calls).toEqual([
      ["selected_items", []],
      ["expanded_items", []],
    ]);
  });

  it("removes stale IDs when items change", () => {
    const tree = renderTree({ defaultSelected: ["a"], defaultExpanded: ["a"] });
    tree.update({ items: [{ id: "b", label: "B" }] });
    expect(tree.props.selectedItems).toBeNull();
    expect(tree.props.expandedItems).toEqual([]);
    expect(tree.setStateValue.mock.calls).toEqual([
      ["selected_items", []],
      ["expanded_items", []],
    ]);
  });

  it("honors disabled changes after mounting", () => {
    const tree = renderTree();
    tree.update({ disabled: true });
    act(() => tree.props.onSelectedItemsChange!(null, "a"));
    expect(tree.setStateValue).not.toHaveBeenCalled();
    expect(tree.props.isItemDisabled!({ id: "a", label: "A" })).toBe(true);
    tree.update({ disabled: false });
    act(() => tree.props.onSelectedItemsChange!(null, "a"));
    expect(tree.props.selectedItems).toBe("a");
    expect(tree.setStateValue).toHaveBeenCalledExactlyOnceWith(
      "selected_items",
      ["a"],
    );
  });

  it("forwards presentation props and renders the label", () => {
    const items = [
      { id: "a", label: "A" },
      { id: "b", label: "B" },
    ];
    const tree = renderTree({
      items,
      multiSelect: true,
      checkboxSelection: true,
      label: "Regions",
    });
    expect(tree.props.items).toBe(items);
    expect(tree.props.multiSelect).toBe(true);
    expect(tree.props.checkboxSelection).toBe(true);
    expect(tree.props["aria-label"]).toBe("Regions");
    expect(screen.getByText("Regions")).toBeTruthy();
  });

  it.each([null, "", "   "])(
    "falls back to a generic aria-label for %j",
    (label) => {
      const tree = renderTree({ label });
      expect(tree.props["aria-label"]).toBe("Tree view");
      expect(tree.props.multiSelect).toBe(false);
      expect(tree.props.checkboxSelection).toBe(false);
    },
  );

  it("renders the empty state without mounting a MUI tree", () => {
    const tree = renderTree({ items: [] });
    expect(tree.mountCount).toBe(0);
    expect(screen.getByText("No items")).toBeTruthy();
    expect(tree.setStateValue).not.toHaveBeenCalled();
  });
});
