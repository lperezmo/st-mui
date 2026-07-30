import { readFileSync } from "node:fs";
import dayjs from "dayjs";
import { describe, expect, it, vi } from "vitest";

import {
  getDateRangeBounds,
  shouldApplyDateRangeEdit,
  syncExternalDateRangeValue,
  updateDateRangeState,
} from "../src/date_range_picker/DateRangePicker";
import {
  getDateTimeRangeBounds,
  shouldApplyDateTimeRangeEdit,
  syncExternalDateTimeRangeValue,
  updateDateTimeRangeState,
} from "../src/date_time_range_picker/DateTimeRangePicker";

describe("MIT Community range picker state", () => {
  it("syncs externally changed ranges without firing interaction callbacks", () => {
    const setStateValue = vi.fn();

    const dates = syncExternalDateRangeValue(
      { start_date: "2026-08-02", end_date: "2026-08-06" },
      setStateValue,
    );
    expect(dates.map((value) => value?.format("YYYY-MM-DD"))).toEqual([
      "2026-08-02",
      "2026-08-06",
    ]);
    expect(setStateValue.mock.calls).toEqual([
      ["start_date", "2026-08-02"],
      ["end_date", "2026-08-06"],
    ]);

    setStateValue.mockClear();
    const dateTimes = syncExternalDateTimeRangeValue(
      {
        start_datetime: "2026-08-02T09:00:00.000",
        end_datetime: "2026-08-02T10:00:00.000",
      },
      setStateValue,
    );
    expect(dateTimes.map((value) => value?.format("HH:mm"))).toEqual([
      "09:00",
      "10:00",
    ]);
    expect(setStateValue.mock.calls).toEqual([
      ["start_datetime", "2026-08-02T09:00:00.000"],
      ["end_datetime", "2026-08-02T10:00:00.000"],
    ]);
  });

  it("commits an ordered date edit with one composite callback", () => {
    const setStateValue = vi.fn();
    const setTriggerValue = vi.fn();

    expect(
      updateDateRangeState(
        [dayjs("2026-08-01"), dayjs("2026-08-05")],
        setStateValue,
        setTriggerValue,
      ),
    ).toBe(true);
    expect(setStateValue.mock.calls).toEqual([
      ["start_date", "2026-08-01"],
      ["end_date", "2026-08-05"],
    ]);
    expect(setTriggerValue).toHaveBeenCalledOnce();
    expect(setTriggerValue).toHaveBeenCalledWith("range", {
      start_date: "2026-08-01",
      end_date: "2026-08-05",
    });
  });

  it("supports clearing while deduplicating unchanged date edits", () => {
    const setStateValue = vi.fn();
    const setTriggerValue = vi.fn();
    const previous = {
      start_date: null,
      end_date: "2026-08-05",
    };

    expect(
      updateDateRangeState(
        [null, dayjs("2026-08-05")],
        setStateValue,
        setTriggerValue,
        previous,
      ),
    ).toBe(false);
    expect(setStateValue).not.toHaveBeenCalled();
    expect(setTriggerValue).not.toHaveBeenCalled();

    expect(
      updateDateRangeState(
        [null, null],
        setStateValue,
        setTriggerValue,
        previous,
      ),
    ).toBe(true);
    expect(setTriggerValue).toHaveBeenCalledOnce();
  });

  it("rejects invalid and reversed date edits", () => {
    const setStateValue = vi.fn();
    const setTriggerValue = vi.fn();

    expect(
      updateDateRangeState(
        [dayjs("2026-08-05"), dayjs("2026-08-01")],
        setStateValue,
        setTriggerValue,
      ),
    ).toBe(false);
    expect(
      updateDateRangeState(
        [dayjs("not-a-date"), null],
        setStateValue,
        setTriggerValue,
      ),
    ).toBe(false);
    expect(setStateValue).not.toHaveBeenCalled();
    expect(setTriggerValue).not.toHaveBeenCalled();
  });

  it("narrows each date field to the other selected endpoint", () => {
    const bounds = getDateRangeBounds(
      dayjs("2026-07-01"),
      dayjs("2026-09-01"),
      [dayjs("2026-08-01"), dayjs("2026-08-05")],
    );

    expect(bounds.startMax?.format("YYYY-MM-DD")).toBe("2026-08-05");
    expect(bounds.endMin?.format("YYYY-MM-DD")).toBe("2026-08-01");
  });

  it("preserves transient edits but rejects forbidden interaction", () => {
    const current = [dayjs("2026-08-01"), dayjs("2026-08-05")] as const;

    expect(
      shouldApplyDateRangeEdit([dayjs("bad"), current[1]], [...current], {
        clearable: false,
        disabled: false,
        readOnly: false,
      }),
    ).toBe(true);
    expect(
      shouldApplyDateRangeEdit([null, current[1]], [...current], {
        clearable: false,
        disabled: false,
        readOnly: false,
      }),
    ).toBe(false);
    expect(
      shouldApplyDateRangeEdit([...current], [...current], {
        clearable: true,
        disabled: false,
        readOnly: true,
      }),
    ).toBe(false);
  });

  it("commits wall-clock datetimes and clears them", () => {
    const setStateValue = vi.fn();
    const setTriggerValue = vi.fn();

    expect(
      updateDateTimeRangeState(
        [dayjs("2026-08-01T09:15:00"), dayjs("2026-08-01T10:45:00")],
        setStateValue,
        setTriggerValue,
      ),
    ).toBe(true);
    expect(setStateValue.mock.calls).toEqual([
      ["start_datetime", "2026-08-01T09:15:00.000"],
      ["end_datetime", "2026-08-01T10:45:00.000"],
    ]);
    expect(setTriggerValue).toHaveBeenCalledOnce();

    setStateValue.mockClear();
    setTriggerValue.mockClear();
    expect(
      updateDateTimeRangeState([null, null], setStateValue, setTriggerValue),
    ).toBe(true);
    expect(setTriggerValue).toHaveBeenCalledWith("range", {
      start_datetime: null,
      end_datetime: null,
    });
  });

  it("rejects reversed, invalid, and duplicate datetime edits", () => {
    const setStateValue = vi.fn();
    const setTriggerValue = vi.fn();
    const previous = {
      start_datetime: "2026-08-01T09:00:00.000",
      end_datetime: "2026-08-01T10:00:00.000",
    };

    expect(
      updateDateTimeRangeState(
        [dayjs("2026-08-01T10:00"), dayjs("2026-08-01T09:00")],
        setStateValue,
        setTriggerValue,
      ),
    ).toBe(false);
    expect(
      updateDateTimeRangeState(
        [dayjs("bad"), null],
        setStateValue,
        setTriggerValue,
      ),
    ).toBe(false);
    expect(
      updateDateTimeRangeState(
        [dayjs("2026-08-01T09:00"), dayjs("2026-08-01T10:00")],
        setStateValue,
        setTriggerValue,
        previous,
      ),
    ).toBe(false);
    expect(setTriggerValue).not.toHaveBeenCalled();
  });

  it("narrows each datetime field to the other endpoint", () => {
    const bounds = getDateTimeRangeBounds(
      dayjs("2026-08-01T07:00"),
      dayjs("2026-08-01T12:00"),
      [dayjs("2026-08-01T09:00"), dayjs("2026-08-01T10:00")],
    );

    expect(bounds.startMax?.format("HH:mm")).toBe("10:00");
    expect(bounds.endMin?.format("HH:mm")).toBe("09:00");
  });

  it("guards datetime clearing while allowing keyboard transition state", () => {
    const current = [
      dayjs("2026-08-01T09:00"),
      dayjs("2026-08-01T10:00"),
    ] as const;

    expect(
      shouldApplyDateTimeRangeEdit([current[0], dayjs("bad")], [...current], {
        clearable: false,
        disabled: false,
        readOnly: false,
      }),
    ).toBe(true);
    expect(
      shouldApplyDateTimeRangeEdit([current[0], null], [...current], {
        clearable: false,
        disabled: false,
        readOnly: false,
      }),
    ).toBe(false);
    expect(
      shouldApplyDateTimeRangeEdit([...current], [...current], {
        clearable: true,
        disabled: true,
        readOnly: false,
      }),
    ).toBe(false);
  });
});

describe("MIT Community range picker prop wiring", () => {
  it("uses two Community DatePickers and maps interaction props", () => {
    const source = readFileSync(
      new URL("../src/date_range_picker/DateRangePicker.tsx", import.meta.url),
      "utf8",
    );

    expect(source).toContain("@mui/x-date-pickers/DatePicker");
    expect(source).not.toContain("@mui/x-date-pickers-pro");
    expect(source.match(/<MuiDatePicker/g)).toHaveLength(2);
    expect(source).toContain("InputProps");
    expect(source).toContain('"aria-describedby"');
    expect(source.indexOf("setSelected(newValue);")).toBeLessThan(
      source.indexOf("updateDateRangeState(", source.indexOf("const commit")),
    );
    for (const prop of [
      "disabled",
      "readOnly",
      "clearable",
      "disablePast",
      "disableFuture",
      "displayWeekNumber",
      "openTo",
      "views",
      "format",
      "helperText",
      "context.validationError",
    ]) {
      expect(source).toContain(prop);
    }
  });

  it("uses two Community DateTimePickers and maps interaction props", () => {
    const source = readFileSync(
      new URL(
        "../src/date_time_range_picker/DateTimeRangePicker.tsx",
        import.meta.url,
      ),
      "utf8",
    );

    expect(source).toContain("@mui/x-date-pickers/DateTimePicker");
    expect(source).not.toContain("@mui/x-date-pickers-pro");
    expect(source.match(/<MuiDateTimePicker/g)).toHaveLength(2);
    expect(source).toContain("InputProps");
    expect(source).toContain('"aria-describedby"');
    expect(source.indexOf("setSelected(newValue);")).toBeLessThan(
      source.indexOf(
        "updateDateTimeRangeState(",
        source.indexOf("const commit"),
      ),
    );
    for (const prop of [
      "disabled",
      "readOnly",
      "clearable",
      "disablePast",
      "disableFuture",
      "minutesStep",
      "openTo",
      "views",
      "format",
      "helperText",
      "context.validationError",
    ]) {
      expect(source).toContain(prop);
    }
  });
});
