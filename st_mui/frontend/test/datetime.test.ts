import dayjs from "dayjs";
import { describe, expect, it } from "vitest";

import { serializeWallClockDateTime } from "../src/shared/datetime";

describe("serializeWallClockDateTime", () => {
  it("preserves the selected wall-clock value without a UTC suffix", () => {
    const serialized = serializeWallClockDateTime(
      dayjs("2026-07-30T09:15:42.123"),
    );

    expect(serialized).toBe("2026-07-30T09:15:42.123");
    expect(serialized).not.toMatch(/Z$/);
  });

  it("returns null for empty and invalid picker values", () => {
    expect(serializeWallClockDateTime(null)).toBeNull();
    expect(serializeWallClockDateTime(dayjs("not-a-date"))).toBeNull();
  });
});
