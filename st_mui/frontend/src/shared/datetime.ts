import type { Dayjs } from "dayjs";

/**
 * Serialize the wall-clock value displayed by a timezone-less MUI picker.
 *
 * `toISOString()` converts the selected value to UTC and emits a trailing Z.
 * That shifts the displayed wall time and Python 3.10 cannot parse the Z form.
 */
export function serializeWallClockDateTime(value: Dayjs | null): string | null {
  return value?.isValid() ? value.format("YYYY-MM-DDTHH:mm:ss.SSS") : null;
}
