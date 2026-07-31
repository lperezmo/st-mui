import dayjs from "dayjs";
import { describe, expect, it, vi } from "vitest";

import {
  nextDatePickerStateValue,
  reconcileDatePickerValue,
  serializeDatePickerValue,
  syncExternalDatePickerValue,
} from "../src/date_picker/DatePicker";
import {
  nextTimePickerStateValue,
  parseTimePickerValue,
  reconcileTimePickerValue,
  serializeTimePickerValue,
  syncExternalTimePickerValue,
} from "../src/time_picker/TimePicker";
import {
  nextDateTimePickerStateValue,
  reconcileDateTimePickerValue,
  syncExternalDateTimePickerValue,
} from "../src/date_time_picker/DateTimePicker";
import { createPickerId } from "../src/shared/id";
import { resolveTimeSteps } from "../src/shared/timeSteps";

describe("picker accessibility IDs", () => {
  it("creates stable-prefix IDs that remain unique across independent roots", () => {
    const ids = new Set(
      Array.from({ length: 25 }, () => createPickerId("date-picker")),
    );

    expect(ids.size).toBe(25);
    for (const id of ids) {
      expect(id).toMatch(/^st-mui-date-picker-/);
    }
  });
});

describe("picker value serialization", () => {
  it("serializes dates, times, and wall-clock datetimes without timezone drift", () => {
    expect(serializeDatePickerValue(dayjs("2026-08-03T22:10:00"))).toBe(
      "2026-08-03",
    );
    expect(serializeTimePickerValue(dayjs("2000-01-01T09:05:07"))).toBe(
      "09:05:07",
    );
    expect(
      nextDateTimePickerStateValue(
        dayjs("2026-08-03T09:05:07.123"),
        "2026-08-03T08:00:00.000",
        { interactive: true, clearable: true },
      ),
    ).toBe("2026-08-03T09:05:07.123");
  });

  it("anchors time-only values to today for past/future validation", () => {
    vi.useFakeTimers();
    try {
      vi.setSystemTime(new Date("2026-08-03T12:00:00"));
      const parsed = parseTimePickerValue("09:05:07");

      expect(parsed?.format("YYYY-MM-DD")).toBe("2026-08-03");
      expect(parsed?.format("HH:mm:ss")).toBe("09:05:07");
    } finally {
      vi.useRealTimers();
    }
  });

  it("emits null for a deliberate clear", () => {
    expect(
      nextDatePickerStateValue(null, "2026-08-03", {
        interactive: true,
        clearable: true,
      }),
    ).toBeNull();
    expect(
      nextTimePickerStateValue(null, "09:05:00", {
        interactive: true,
        clearable: true,
      }),
    ).toBeNull();
    expect(
      nextDateTimePickerStateValue(null, "2026-08-03T09:05:00.000", {
        interactive: true,
        clearable: true,
      }),
    ).toBeNull();
  });
});

describe("external picker value synchronization", () => {
  it("updates both the displayed single-picker value and Streamlit state", () => {
    const setDateState = vi.fn();
    const setTimeState = vi.fn();
    const setDateTimeState = vi.fn();

    expect(
      syncExternalDatePickerValue("2026-08-04", setDateState)?.format(
        "YYYY-MM-DD",
      ),
    ).toBe("2026-08-04");
    expect(setDateState).toHaveBeenCalledWith("selected_date", "2026-08-04");

    expect(
      syncExternalTimePickerValue("10:30:00", setTimeState)?.format("HH:mm:ss"),
    ).toBe("10:30:00");
    expect(setTimeState).toHaveBeenCalledWith("selected_time", "10:30:00");

    expect(
      syncExternalDateTimePickerValue(
        "2026-08-04T10:30:00.000",
        setDateTimeState,
      )?.format("YYYY-MM-DDTHH:mm:ss.SSS"),
    ).toBe("2026-08-04T10:30:00.000");
    expect(setDateTimeState).toHaveBeenCalledWith(
      "selected_datetime",
      "2026-08-04T10:30:00.000",
    );
  });
});

describe("minute-step option wiring", () => {
  it("offers only minutes the picker will accept", () => {
    expect(resolveTimeSteps(15)).toEqual({ minutes: 15 });
    expect(resolveTimeSteps(30)).toEqual({ minutes: 30 });
  });

  it("leaves the default step on MUI's own spacing", () => {
    // minutesStep=1 accepts every minute, so MUI's 5-minute default cannot
    // offer an invalid choice. Overriding it would list all 60 minutes.
    expect(resolveTimeSteps(1)).toBeUndefined();
  });
});

describe("picker interaction guards", () => {
  it("does not clear a non-clearable picker", () => {
    expect(
      nextDatePickerStateValue(null, "2026-08-03", {
        interactive: true,
        clearable: false,
      }),
    ).toBeUndefined();
  });

  it("does not emit from disabled or read-only pickers", () => {
    expect(
      nextTimePickerStateValue(dayjs("2000-01-01T10:00:00"), "09:00:00", {
        interactive: false,
        clearable: true,
      }),
    ).toBeUndefined();
    expect(
      nextDateTimePickerStateValue(
        dayjs("2026-08-03T10:00:00"),
        "2026-08-03T09:00:00.000",
        { interactive: false, clearable: true },
      ),
    ).toBeUndefined();
  });

  it("does not emit duplicate callbacks or MUI validation failures", () => {
    expect(
      nextDatePickerStateValue(dayjs("2026-08-03"), "2026-08-03", {
        interactive: true,
        clearable: true,
      }),
    ).toBeUndefined();
    expect(
      nextTimePickerStateValue(dayjs("2000-01-01T09:07:00"), "09:00:00", {
        interactive: true,
        clearable: true,
        valid: false,
      }),
    ).toBeUndefined();
    expect(
      nextDateTimePickerStateValue(
        dayjs("2026-08-03T09:07:00"),
        "2026-08-03T09:00:00.000",
        { interactive: true, clearable: true, valid: false },
      ),
    ).toBeUndefined();
  });

  it("ignores intermediate invalid typed values", () => {
    expect(
      nextDatePickerStateValue(dayjs("not-a-date"), "2026-08-03", {
        interactive: true,
        clearable: true,
      }),
    ).toBeUndefined();
  });
});

describe("picker rerender reconciliation", () => {
  it("preserves user state when Python repeats the same default", () => {
    const currentDate = dayjs("2026-08-04");
    const currentTime = dayjs("2000-01-01T10:30:00");
    const currentDateTime = dayjs("2026-08-04T10:30:00");

    expect(
      reconcileDatePickerValue(currentDate, "2026-08-03", "2026-08-03"),
    ).toBe(currentDate);
    expect(reconcileTimePickerValue(currentTime, "09:00:00", "09:00:00")).toBe(
      currentTime,
    );
    expect(
      reconcileDateTimePickerValue(
        currentDateTime,
        "2026-08-03T09:00:00",
        "2026-08-03T09:00:00",
      ),
    ).toBe(currentDateTime);
  });

  it("synchronizes when Python supplies a genuinely changed value", () => {
    expect(
      reconcileDatePickerValue(
        dayjs("2026-08-04"),
        "2026-08-03",
        "2026-09-01",
      )?.format("YYYY-MM-DD"),
    ).toBe("2026-09-01");
    expect(
      reconcileTimePickerValue(
        dayjs("2000-01-01T10:30:00"),
        "09:00:00",
        "11:45:00",
      )?.format("HH:mm:ss"),
    ).toBe("11:45:00");
    expect(
      reconcileDateTimePickerValue(
        dayjs("2026-08-04T10:30:00"),
        "2026-08-03T09:00:00",
        "2026-09-01T11:45:00",
      )?.format("YYYY-MM-DDTHH:mm:ss"),
    ).toBe("2026-09-01T11:45:00");
  });
});
