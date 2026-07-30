import { describe, expect, it } from "vitest";
import {
  dedupeAutocompleteSelection,
  reconcileAutocompleteSelection,
  resolveAutocompleteSelection,
  sameAutocompleteDataValue,
  sameAutocompleteValue,
  serializeAutocompleteSelection,
  type AutocompleteOption,
} from "../src/autocomplete/Autocomplete";

const options: AutocompleteOption[] = [
  { label: "Numeric one", value: 1, disabled: false },
  { label: "String one", value: "1", disabled: false },
  { label: "Enabled", value: true, disabled: false },
];

describe("autocomplete state helpers", () => {
  it("preserves scalar types when matching options", () => {
    expect(sameAutocompleteValue(1, "1")).toBe(false);
    expect(sameAutocompleteDataValue([1, "1"], [1, "1"])).toBe(true);
    expect(sameAutocompleteDataValue([1, "1"], ["1", 1])).toBe(false);
    expect(resolveAutocompleteSelection(1, options, false, false)).toBe(
      options[0],
    );
    expect(resolveAutocompleteSelection("1", options, false, false)).toBe(
      options[1],
    );
  });

  it("resolves and serializes multiple option and free-solo values", () => {
    const selected = resolveAutocompleteSelection(
      [1, "custom"],
      options,
      true,
      true,
    );
    expect(selected).toEqual([options[0], "custom"]);
    expect(serializeAutocompleteSelection(selected, true)).toEqual([
      1,
      "custom",
    ]);
  });

  it("deduplicates repeated free-solo and option values", () => {
    const selection = [options[0], "custom", "custom", options[0]];
    expect(dedupeAutocompleteSelection(selection, true)).toEqual([
      options[0],
      "custom",
    ]);
    expect(serializeAutocompleteSelection(selection, true)).toEqual([
      1,
      "custom",
    ]);
  });

  it("uses empty values for invalid selections", () => {
    expect(resolveAutocompleteSelection("missing", options, false, false)).toBe(
      null,
    );
    expect(serializeAutocompleteSelection(null, false)).toBe(null);
    expect(serializeAutocompleteSelection(null, true)).toEqual([]);
  });

  it("preserves user state across equivalent Streamlit defaults", () => {
    const refreshedOptions = options.map((option) => ({ ...option }));
    const selected = reconcileAutocompleteSelection(
      1,
      "1",
      "1",
      refreshedOptions,
      false,
      false,
    );
    expect(selected).toBe(refreshedOptions[0]);
  });

  it("honors changed defaults and component mode", () => {
    expect(
      reconcileAutocompleteSelection(1, "1", true, options, false, false),
    ).toBe(options[2]);
    expect(
      reconcileAutocompleteSelection(
        [1],
        [1],
        "1",
        options,
        false,
        false,
        true,
      ),
    ).toBe(options[1]);
  });

  it("drops selections removed from the latest options", () => {
    expect(
      reconcileAutocompleteSelection(
        1,
        null,
        null,
        options.slice(1),
        false,
        false,
      ),
    ).toBe(null);
  });
});
