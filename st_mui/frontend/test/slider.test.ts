import { describe, expect, it, vi } from "vitest";
import {
  commitSliderValue,
  getSliderAriaLabel,
  normalizeSliderValue,
  sliderValuesEqual,
} from "../src/slider/Slider";

describe("slider state helpers", () => {
  it("preserves scalar values", () => {
    expect(normalizeSliderValue(5)).toBe(5);
  });

  it("copies range values so local state cannot mutate component data", () => {
    const input = [2, 8];
    const normalized = normalizeSliderValue(input);
    expect(normalized).toEqual([2, 8]);
    expect(normalized).not.toBe(input);
  });

  it("compares recreated range props by value", () => {
    expect(sliderValuesEqual([2, 8], [2, 8])).toBe(true);
    expect(sliderValuesEqual([2, 8], [2, 9])).toBe(false);
    expect(sliderValuesEqual([2, 8], 2)).toBe(false);
  });

  it("gives range thumbs distinct accessible labels", () => {
    expect(getSliderAriaLabel("Price", [10, 50], 0)).toBe("Price minimum");
    expect(getSliderAriaLabel("Price", [10, 50], 1)).toBe("Price maximum");
    expect(getSliderAriaLabel("Volume", 25, 0)).toBe("Volume");
  });

  it("commits a cloned value under the callback state key", () => {
    const setStateValue = vi.fn();
    const range = [3, 7];

    commitSliderValue(setStateValue, range);

    expect(setStateValue).toHaveBeenCalledWith("selected_value", [3, 7]);
    expect(setStateValue.mock.calls[0][1]).not.toBe(range);
  });
});
