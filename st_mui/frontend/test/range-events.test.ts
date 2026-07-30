import dayjs from "dayjs";
import { describe, expect, it, vi } from "vitest";

import { updateDateRangeState } from "../src/date_range_picker/DateRangePicker";
import { updateDateTimeRangeState } from "../src/date_time_range_picker/DateTimeRangePicker";

describe("range change events", () => {
  it("updates both dates and emits one composite trigger", () => {
    const setStateValue = vi.fn();
    const setTriggerValue = vi.fn();

    updateDateRangeState(
      [dayjs("2026-07-30"), dayjs("2026-08-02")],
      setStateValue,
      setTriggerValue,
    );

    expect(setStateValue.mock.calls).toEqual([
      ["start_date", "2026-07-30"],
      ["end_date", "2026-08-02"],
    ]);
    expect(setTriggerValue).toHaveBeenCalledOnce();
    expect(setTriggerValue).toHaveBeenCalledWith("range", {
      start_date: "2026-07-30",
      end_date: "2026-08-02",
    });
  });

  it("updates both datetimes and emits one wall-clock trigger", () => {
    const setStateValue = vi.fn();
    const setTriggerValue = vi.fn();

    updateDateTimeRangeState(
      [dayjs("2026-07-30T09:15:00.000"), dayjs("2026-07-30T11:45:00.000")],
      setStateValue,
      setTriggerValue,
    );

    expect(setStateValue.mock.calls).toEqual([
      ["start_datetime", "2026-07-30T09:15:00.000"],
      ["end_datetime", "2026-07-30T11:45:00.000"],
    ]);
    expect(setTriggerValue).toHaveBeenCalledOnce();
    expect(setTriggerValue).toHaveBeenCalledWith("range", {
      start_datetime: "2026-07-30T09:15:00.000",
      end_datetime: "2026-07-30T11:45:00.000",
    });
  });
});
