import { createElement } from "react";
import { act, create, type ReactTestRenderer } from "react-test-renderer";
import type { RichTreeViewProps } from "@mui/x-tree-view/RichTreeView";
import { afterEach, describe, expect, it, vi } from "vitest";
import TreeViewComponent, {
  type TreeViewData,
} from "../src/tree_view/TreeView";

type TreeProps = RichTreeViewProps<TreeViewData["items"][number], boolean>;

vi.mock("@mui/x-tree-view/RichTreeView", () => ({
  RichTreeView: (_props: TreeProps) => null,
}));

import { RichTreeView } from "@mui/x-tree-view/RichTreeView";

const renderers: ReactTestRenderer[] = [];

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
  let renderer!: ReactTestRenderer;
  act(() => {
    renderer = create(
      createElement(TreeViewComponent, { data, setStateValue }),
    );
  });
  renderers.push(renderer);
  return {
    get props(): TreeProps {
      return renderer.root.findByType(RichTreeView).props as TreeProps;
    },
    renderer,
    setStateValue,
    update(overrides: Partial<TreeViewData>) {
      data = { ...data, ...overrides };
      act(() => {
        renderer.update(
          createElement(TreeViewComponent, { data, setStateValue }),
        );
      });
    },
  };
}

afterEach(() => {
  act(() => {
    for (const renderer of renderers.splice(0)) renderer.unmount();
  });
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

  it("preserves existing duplicate-ID behavior in multi-selection", () => {
    const tree = renderTree({ multiSelect: true });
    act(() => tree.props.onSelectedItemsChange!(null, ["a", "a"]));
    expect(tree.props.selectedItems).toEqual(["a", "a"]);
    expect(tree.setStateValue).toHaveBeenCalledExactlyOnceWith(
      "selected_items",
      ["a", "a"],
    );
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

  it("renders the empty state without mounting a MUI tree", () => {
    const tree = renderTree({ items: [] });
    expect(tree.renderer.root.findAllByType(RichTreeView)).toHaveLength(0);
    expect(JSON.stringify(tree.renderer.toJSON())).toContain("No items");
    expect(tree.setStateValue).not.toHaveBeenCalled();
  });
});
