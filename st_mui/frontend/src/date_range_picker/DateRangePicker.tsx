import {
  type FC,
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import type { FrontendRendererArgs } from "@streamlit/component-v2-lib";
import dayjs, { type Dayjs } from "dayjs";
import Box from "@mui/material/Box";
import FormHelperText from "@mui/material/FormHelperText";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { DatePicker as MuiDatePicker } from "@mui/x-date-pickers/DatePicker";
import type {
  DateValidationError,
  DateView,
  PickerChangeHandlerContext,
} from "@mui/x-date-pickers/models";
import { usePickerId } from "../shared/id";

export type DateRangePickerState = {
  start_date: string | null;
  end_date: string | null;
  range: {
    start_date: string | null;
    end_date: string | null;
  };
};

export type DateRangePickerData = {
  label: string;
  startLabel: string | null;
  endLabel: string | null;
  startValue: string | null;
  endValue: string | null;
  minDate: string | null;
  maxDate: string | null;
  format: string;
  helperText: string | null;
  clearable: boolean;
  readOnly: boolean;
  disablePast: boolean;
  disableFuture: boolean;
  openTo: DateView | null;
  views: DateView[] | null;
  displayWeekNumber: boolean;
  disabled: boolean;
};

type Props = {
  data: DateRangePickerData;
  setStateValue: FrontendRendererArgs<
    DateRangePickerState,
    DateRangePickerData
  >["setStateValue"];
  setTriggerValue: FrontendRendererArgs<
    DateRangePickerState,
    DateRangePickerData
  >["setTriggerValue"];
};

type DatePair = [Dayjs | null, Dayjs | null];
type SerializedDatePair = {
  start_date: string | null;
  end_date: string | null;
};

function serializeDate(value: Dayjs | null): string | null | undefined {
  if (value === null) {
    return null;
  }
  return value.isValid() ? value.format("YYYY-MM-DD") : undefined;
}

function serializeDatePair(newValue: DatePair): SerializedDatePair | null {
  const startValue = serializeDate(newValue[0]);
  const endValue = serializeDate(newValue[1]);
  if (startValue === undefined || endValue === undefined) {
    return null;
  }
  if (
    newValue[0] !== null &&
    newValue[1] !== null &&
    newValue[0].isAfter(newValue[1], "day")
  ) {
    return null;
  }
  return { start_date: startValue, end_date: endValue };
}

function sameDatePair(
  left: SerializedDatePair,
  right: SerializedDatePair,
): boolean {
  return (
    left.start_date === right.start_date && left.end_date === right.end_date
  );
}

export function updateDateRangeState(
  newValue: DatePair,
  setStateValue: Props["setStateValue"],
  setTriggerValue: Props["setTriggerValue"],
  previousValue?: SerializedDatePair,
): boolean {
  const serialized = serializeDatePair(newValue);
  if (
    serialized === null ||
    (previousValue !== undefined && sameDatePair(serialized, previousValue))
  ) {
    return false;
  }

  setStateValue("start_date", serialized.start_date);
  setStateValue("end_date", serialized.end_date);
  setTriggerValue("range", serialized);
  return true;
}

function parseDate(value: string | null): Dayjs | null {
  if (!value) return null;
  const parsed = dayjs(value);
  return parsed.isValid() ? parsed : null;
}

export function syncExternalDateRangeValue(
  incoming: SerializedDatePair,
  setStateValue: Props["setStateValue"],
): DatePair {
  setStateValue("start_date", incoming.start_date);
  setStateValue("end_date", incoming.end_date);
  return [parseDate(incoming.start_date), parseDate(incoming.end_date)];
}

function earlierDate(
  left: Dayjs | undefined,
  right: Dayjs | null,
): Dayjs | undefined {
  if (right === null || !right.isValid()) {
    return left;
  }
  return left === undefined || right.isBefore(left, "day") ? right : left;
}

function laterDate(
  left: Dayjs | undefined,
  right: Dayjs | null,
): Dayjs | undefined {
  if (right === null || !right.isValid()) {
    return left;
  }
  return left === undefined || right.isAfter(left, "day") ? right : left;
}

export function getDateRangeBounds(
  minDate: Dayjs | undefined,
  maxDate: Dayjs | undefined,
  selected: DatePair,
): { startMax: Dayjs | undefined; endMin: Dayjs | undefined } {
  return {
    startMax: earlierDate(maxDate, selected[1]),
    endMin: laterDate(minDate, selected[0]),
  };
}

export function shouldApplyDateRangeEdit(
  nextValue: DatePair,
  currentValue: DatePair,
  options: { clearable: boolean; disabled: boolean; readOnly: boolean },
): boolean {
  if (options.disabled || options.readOnly) {
    return false;
  }
  return !(
    !options.clearable &&
    ((nextValue[0] === null && currentValue[0] !== null) ||
      (nextValue[1] === null && currentValue[1] !== null))
  );
}

const DateRangePickerComponent: FC<Props> = ({
  data,
  setStateValue,
  setTriggerValue,
}) => {
  const {
    label,
    startLabel,
    endLabel,
    startValue,
    endValue,
    minDate,
    maxDate,
    format,
    helperText,
    clearable,
    readOnly,
    disablePast,
    disableFuture,
    openTo,
    views,
    displayWeekNumber,
    disabled,
  } = data;

  const [selected, setSelected] = useState<DatePair>(() => [
    parseDate(startValue),
    parseDate(endValue),
  ]);
  const latestValue = useRef<SerializedDatePair>({
    start_date: startValue,
    end_date: endValue,
  });
  const fieldIdBase = usePickerId("date-range-picker");
  const helperTextId = `${fieldIdBase}-helper`;

  useEffect(() => {
    const incoming = { start_date: startValue, end_date: endValue };
    if (!sameDatePair(incoming, latestValue.current)) {
      latestValue.current = incoming;
      setSelected(syncExternalDateRangeValue(incoming, setStateValue));
    }
  }, [startValue, endValue, setStateValue]);

  const commit = useCallback(
    (newValue: DatePair, valid: boolean) => {
      if (
        !shouldApplyDateRangeEdit(newValue, selected, {
          clearable,
          disabled,
          readOnly,
        })
      ) {
        return;
      }

      // Field typing passes through temporarily invalid Dayjs values. Keep
      // those local so the input does not snap back, but only notify Python
      // once both endpoints form a valid ordered range.
      setSelected(newValue);
      if (!valid) {
        return;
      }
      if (
        !updateDateRangeState(
          newValue,
          setStateValue,
          setTriggerValue,
          latestValue.current,
        )
      ) {
        return;
      }
      const serialized = serializeDatePair(newValue);
      if (serialized !== null) {
        latestValue.current = serialized;
      }
    },
    [clearable, disabled, readOnly, selected, setStateValue, setTriggerValue],
  );

  const minDayjs = useMemo(() => parseDate(minDate) ?? undefined, [minDate]);
  const maxDayjs = useMemo(() => parseDate(maxDate) ?? undefined, [maxDate]);
  const { startMax, endMin } = getDateRangeBounds(minDayjs, maxDayjs, selected);

  const commonProps = useMemo(
    () => ({
      format,
      disabled,
      readOnly,
      disablePast,
      disableFuture,
      openTo: openTo ?? undefined,
      views: views ?? undefined,
      displayWeekNumber,
      slotProps: {
        field: { clearable },
        textField: {
          fullWidth: true,
          InputProps: {
            "aria-describedby": helperText ? helperTextId : undefined,
          },
        },
        popper: {
          disablePortal: false,
          style: { zIndex: 999999 },
        },
      },
    }),
    [
      format,
      disabled,
      readOnly,
      disablePast,
      disableFuture,
      openTo,
      views,
      displayWeekNumber,
      clearable,
      helperText,
      helperTextId,
    ],
  );

  return (
    <Box sx={{ width: "100%", py: 0.5 }}>
      <LocalizationProvider dateAdapter={AdapterDayjs}>
        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: { xs: "1fr", sm: "1fr 1fr" },
            gap: 1.5,
          }}
        >
          <MuiDatePicker
            {...commonProps}
            slotProps={{
              ...commonProps.slotProps,
              textField: {
                ...commonProps.slotProps.textField,
                id: `${fieldIdBase}-start`,
              },
            }}
            label={startLabel ?? (label ? `${label} (start)` : "Start")}
            value={selected[0]}
            onChange={(
              newStart,
              context: PickerChangeHandlerContext<DateValidationError>,
            ) =>
              commit([newStart, selected[1]], context.validationError === null)
            }
            minDate={minDayjs}
            maxDate={startMax}
          />
          <MuiDatePicker
            {...commonProps}
            slotProps={{
              ...commonProps.slotProps,
              textField: {
                ...commonProps.slotProps.textField,
                id: `${fieldIdBase}-end`,
              },
            }}
            label={endLabel ?? (label ? `${label} (end)` : "End")}
            value={selected[1]}
            onChange={(
              newEnd,
              context: PickerChangeHandlerContext<DateValidationError>,
            ) =>
              commit([selected[0], newEnd], context.validationError === null)
            }
            minDate={endMin}
            maxDate={maxDayjs}
          />
        </Box>
        {helperText ? (
          <FormHelperText id={helperTextId}>{helperText}</FormHelperText>
        ) : null}
      </LocalizationProvider>
    </Box>
  );
};

export default DateRangePickerComponent;
