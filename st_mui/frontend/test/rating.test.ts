import { describe, expect, it } from "vitest";
import { nextRatingValue, ratingLabelText } from "../src/rating/Rating";

describe("rating state helpers", () => {
  it("accepts a new value", () => {
    expect(
      nextRatingValue(2, 4, {
        clearable: true,
        disabled: false,
        readOnly: false,
      }),
    ).toBe(4);
  });

  it("allows clearing only when configured", () => {
    expect(
      nextRatingValue(2, null, {
        clearable: true,
        disabled: false,
        readOnly: false,
      }),
    ).toBe(null);
    expect(
      nextRatingValue(2, null, {
        clearable: false,
        disabled: false,
        readOnly: false,
      }),
    ).toBe(2);
  });

  it("ignores changes while disabled or read-only", () => {
    expect(
      nextRatingValue(2, 4, {
        clearable: true,
        disabled: true,
        readOnly: false,
      }),
    ).toBe(2);
    expect(
      nextRatingValue(2, null, {
        clearable: true,
        disabled: false,
        readOnly: true,
      }),
    ).toBe(2);
  });

  it("provides accessible labels for values and an empty rating", () => {
    expect(ratingLabelText(null, 5)).toBe("No rating");
    expect(ratingLabelText(1, 5)).toBe("1 of 5 stars");
    expect(ratingLabelText(2.5, 5)).toBe("2.5 of 5 stars");
    expect(ratingLabelText(1, 1)).toBe("1 of 1 star");
  });
});
