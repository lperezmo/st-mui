import { describe, expect, it } from "vitest";
import {
  isDarkBackground,
  parseBorderRadius,
  parseCssColorToRgb,
} from "../src/shared/theme";
import {
  collectTreeIds,
  filterValidTreeIds,
  reconcileTreeIds,
  sameTreeIds,
} from "../src/tree_view/TreeView";
import { gridRowIdKey, sameGridRowIds } from "../src/data_grid/DataGrid";
import { clampSliderValue, getSliderAriaValueText } from "../src/slider/Slider";
import {
  getAutocompleteOptionLabel,
  isAutocompleteOptionDisabled,
  isAutocompleteOptionEqual,
} from "../src/autocomplete/Autocomplete";
import { createPickerId } from "../src/shared/id";

describe("theme color parsing", () => {
  it("parses hex, rgb comma/space, and hsl forms", () => {
    expect(parseCssColorToRgb("#fff")).toEqual([255, 255, 255]);
    expect(parseCssColorToRgb("#0e1117")).toEqual([14, 17, 23]);
    // 8-digit hex ignores alpha
    expect(parseCssColorToRgb("#0e1117ff")).toEqual([14, 17, 23]);
    expect(parseCssColorToRgb("rgb(255, 255, 255)")).toEqual([255, 255, 255]);
    expect(parseCssColorToRgb("rgb(14 17 23)")).toEqual([14, 17, 23]);
    expect(parseCssColorToRgb("rgba(14 17 23 / 50%)")).toEqual([14, 17, 23]);
    expect(parseCssColorToRgb("rgb(100%, 0%, 0%)")).toEqual([255, 0, 0]);
    expect(parseCssColorToRgb("hsl(0, 100%, 50%)")).toEqual([255, 0, 0]);
    expect(parseCssColorToRgb("hsl(120 100% 25%)")).toEqual([0, 128, 0]);
  });

  it("rejects invalid colors without throwing", () => {
    expect(parseCssColorToRgb("")).toBeNull();
    expect(parseCssColorToRgb("transparent")).toBeNull();
    expect(parseCssColorToRgb("not-a-color")).toBeNull();
    expect(parseCssColorToRgb("#zzz")).toBeNull();
    expect(parseCssColorToRgb("rgb(1, 2)")).toBeNull();
  });

  it("detects dark mode across formats", () => {
    expect(isDarkBackground("#0e1117")).toBe(true);
    expect(isDarkBackground("rgb(14 17 23)")).toBe(true);
    expect(isDarkBackground("#ffffff")).toBe(false);
    expect(isDarkBackground("rgb(255, 255, 255)")).toBe(false);
    // Unknown formats fall back to light instead of NaN-driven dark
    expect(isDarkBackground("not-a-color")).toBe(false);
  });

  it("parses fractional border radii", () => {
    expect(parseBorderRadius("8px")).toBe(8);
    expect(parseBorderRadius("12px")).toBe(12);
    expect(parseBorderRadius("0.5rem")).toBe(0.5);
    expect(parseBorderRadius("")).toBe(8);
    expect(parseBorderRadius("invalid")).toBe(8);
    expect(parseBorderRadius("-4px")).toBe(8);
  });
});

describe("tree reconciliation helpers", () => {
  it("compares id arrays", () => {
    expect(sameTreeIds(["a"], ["a"])).toBe(true);
    expect(sameTreeIds(["a"], ["b"])).toBe(false);
    expect(sameTreeIds(["a", "b"], ["a"])).toBe(false);
  });

  it("preserves user state when Python default is unchanged", () => {
    expect(reconcileTreeIds(["user"], ["a"], ["a"])).toEqual(["user"]);
    expect(reconcileTreeIds(["user"], ["a"], ["b"])).toEqual(["b"]);
  });

  it("filters ids to those present in items", () => {
    const valid = new Set(["a", "b"]);
    expect(filterValidTreeIds(["a", "missing"], valid)).toEqual(["a"]);
  });

  it("collects nested ids", () => {
    const ids = collectTreeIds([
      { id: "a", label: "A", children: [{ id: "b", label: "B" }] },
      { id: "c", label: "C" },
    ]);
    expect([...ids].sort()).toEqual(["a", "b", "c"]);
  });
});

describe("data grid selection helpers", () => {
  it("treats selection as order-insensitive", () => {
    expect(sameGridRowIds([1, 2], [2, 1])).toBe(true);
    expect(sameGridRowIds([1, 2], [1, 3])).toBe(false);
    expect(sameGridRowIds([1], [1, 1])).toBe(false);
    expect(sameGridRowIds([1, "1"], ["1", 1])).toBe(true);
  });

  it("builds collision-free id keys", () => {
    expect(gridRowIdKey(1)).not.toBe(gridRowIdKey("1"));
  });
});

describe("slider helpers", () => {
  it("clamps values to bounds", () => {
    expect(clampSliderValue(150, 0, 100)).toBe(100);
    expect(clampSliderValue(-5, 0, 100)).toBe(0);
    expect(clampSliderValue([-10, 150] as unknown as number[], 0, 100)).toEqual(
      [0, 100],
    );
  });

  it("formats aria value text", () => {
    expect(getSliderAriaValueText(42)).toBe("42");
  });
});

describe("autocomplete helpers", () => {
  it("labels malformed options without crashing", () => {
    expect(getAutocompleteOptionLabel("typed")).toBe("typed");
    expect(
      getAutocompleteOptionLabel({
        label: "LA",
        value: "LAX",
        disabled: false,
      }),
    ).toBe("LA");
    expect(getAutocompleteOptionLabel(null)).toBe("");
    expect(getAutocompleteOptionLabel(undefined)).toBe("");
  });

  it("disables only real options", () => {
    expect(isAutocompleteOptionDisabled("typed")).toBe(false);
    expect(
      isAutocompleteOptionDisabled({ label: "X", value: 1, disabled: true }),
    ).toBe(true);
  });

  it("matches free-solo strings by label", () => {
    const option = { label: "Los Angeles", value: "LAX", disabled: false };
    expect(isAutocompleteOptionEqual(option, "Los Angeles")).toBe(true);
    expect(isAutocompleteOptionEqual(option, "LAX")).toBe(true);
    expect(isAutocompleteOptionEqual(option, "Other")).toBe(false);
    expect(isAutocompleteOptionEqual(option, { ...option })).toBe(true);
  });
});

describe("picker ids", () => {
  it("creates unique prefixed ids", () => {
    const a = createPickerId("date-picker");
    const b = createPickerId("date-picker");
    expect(a.startsWith("st-mui-date-picker-")).toBe(true);
    expect(a).not.toBe(b);
  });
});
