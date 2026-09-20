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
import { DateTimePicker as MuiDateTimePicker } from "@mui/x-date-pickers/DateTimePicker";
import type {
  DateOrTimeView,
  DateTimeValidationError,
  PickerChangeHandlerContext,
} from "@mui/x-date-pickers/models";
import { serializeWallClockDateTime } from "../shared/datetime";
import { usePickerId } from "../shared/id";
import { resolveTimeSteps } from "../shared/timeSteps";

export type DateTimeRangePickerState = {
  start_datetime: string | null;
  end_datetime: string | null;
  range: {
    start_datetime: string | null;
    end_datetime: string | null;
  };
};

export type DateTimeRangePickerData = {
  label: string;
  startLabel: string | null;
  endLabel: string | null;
  startValue: string | null;
  endValue: string | null;
  minDatetime: string | null;
  maxDatetime: string | null;
  ampm: boolean;
  format: string | null;
  helperText: string | null;
  clearable: boolean;
  readOnly: boolean;
  disablePast: boolean;
  disableFuture: boolean;
  openTo: DateOrTimeView | null;
  views: DateOrTimeView[] | null;
  minutesStep: number;
  disabled: boolean;
};

type Props = {
  data: DateTimeRangePickerData;
  setStateValue: FrontendRendererArgs<
    DateTimeRangePickerState,
    DateTimeRangePickerData
  >["setStateValue"];
  setTriggerValue: FrontendRendererArgs<
    DateTimeRangePickerState,
    DateTimeRangePickerData
  >["setTriggerValue"];
};

type DateTimePair = [Dayjs | null, Dayjs | null];
type SerializedDateTimePair = {
  start_datetime: string | null;
  end_datetime: string | null;
};

function serializeDateTimePair(
  newValue: DateTimePair,
): SerializedDateTimePair | null {
  if (
    (newValue[0] !== null && !newValue[0].isValid()) ||
    (newValue[1] !== null && !newValue[1].isValid()) ||
    (newValue[0] !== null &&
      newValue[1] !== null &&
      newValue[0].isAfter(newValue[1]))
  ) {
    return null;
  }
  return {
    start_datetime: serializeWallClockDateTime(newValue[0]),
    end_datetime: serializeWallClockDateTime(newValue[1]),
  };
}

function sameDateTimePair(
  left: SerializedDateTimePair,
  right: SerializedDateTimePair,
): boolean {
  return (
    left.start_datetime === right.start_datetime &&
    left.end_datetime === right.end_datetime
  );
}

export function updateDateTimeRangeState(
  newValue: DateTimePair,
  setStateValue: Props["setStateValue"],
  setTriggerValue: Props["setTriggerValue"],
  previousValue?: SerializedDateTimePair,
): boolean {
  const serialized = serializeDateTimePair(newValue);
  if (
    serialized === null ||
    (previousValue !== undefined && sameDateTimePair(serialized, previousValue))
  ) {
    return false;
  }

  setStateValue("start_datetime", serialized.start_datetime);
  setStateValue("end_datetime", serialized.end_datetime);
  setTriggerValue("range", serialized);
  return true;
}

function parseDateTime(value: string | null): Dayjs | null {
  if (!value) return null;
  const parsed = dayjs(value);
  return parsed.isValid() ? parsed : null;
}

export function syncExternalDateTimeRangeValue(
  incoming: SerializedDateTimePair,
  setStateValue: Props["setStateValue"],
): DateTimePair {
  setStateValue("start_datetime", incoming.start_datetime);
  setStateValue("end_datetime", incoming.end_datetime);
  return [
    parseDateTime(incoming.start_datetime),
    parseDateTime(incoming.end_datetime),
  ];
}

function earlierDateTime(
  left: Dayjs | undefined,
  right: Dayjs | null,
): Dayjs | undefined {
  if (right === null || !right.isValid()) {
    return left;
  }
  return left === undefined || right.isBefore(left) ? right : left;
}

function laterDateTime(
  left: Dayjs | undefined,
  right: Dayjs | null,
): Dayjs | undefined {
  if (right === null || !right.isValid()) {
    return left;
  }
  return left === undefined || right.isAfter(left) ? right : left;
}

export function getDateTimeRangeBounds(
  minDatetime: Dayjs | undefined,
  maxDatetime: Dayjs | undefined,
  selected: DateTimePair,
): { startMax: Dayjs | undefined; endMin: Dayjs | undefined } {
  return {
    startMax: earlierDateTime(maxDatetime, selected[1]),
    endMin: laterDateTime(minDatetime, selected[0]),
  };
}

export function shouldApplyDateTimeRangeEdit(
  nextValue: DateTimePair,
  currentValue: DateTimePair,
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

const DateTimeRangePickerComponent: FC<Props> = ({
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
    minDatetime,
    maxDatetime,
    ampm,
    format,
    helperText,
    clearable,
    readOnly,
    disablePast,
    disableFuture,
    openTo,
    views,
    minutesStep,
    disabled,
  } = data;

  const [selected, setSelected] = useState<DateTimePair>(() => [
    parseDateTime(startValue),
    parseDateTime(endValue),
  ]);
  const latestValue = useRef<SerializedDateTimePair>({
    start_datetime: startValue,
    end_datetime: endValue,
  });
  const fieldIdBase = usePickerId("date-time-range-picker");
  const helperTextId = `${fieldIdBase}-helper`;

  useEffect(() => {
    const incoming = {
      start_datetime: startValue,
      end_datetime: endValue,
    };
    if (!sameDateTimePair(incoming, latestValue.current)) {
      latestValue.current = incoming;
      setSelected(syncExternalDateTimeRangeValue(incoming, setStateValue));
    }
  }, [startValue, endValue, setStateValue]);

  const commit = useCallback(
    (newValue: DateTimePair, valid: boolean) => {
      if (
        !shouldApplyDateTimeRangeEdit(newValue, selected, {
          clearable,
          disabled,
          readOnly,
        })
      ) {
        return;
      }

      // Preserve transient keyboard edits locally. Streamlit only receives a
      // value after the pair is valid and chronologically ordered.
      setSelected(newValue);
      if (!valid) {
        return;
      }
      if (
        !updateDateTimeRangeState(
          newValue,
          setStateValue,
          setTriggerValue,
          latestValue.current,
        )
      ) {
        return;
      }
      const serialized = serializeDateTimePair(newValue);
      if (serialized !== null) {
        latestValue.current = serialized;
      }
    },
    [clearable, disabled, readOnly, selected, setStateValue, setTriggerValue],
  );

  const minDayjs = useMemo(
    () => parseDateTime(minDatetime) ?? undefined,
    [minDatetime],
  );
  const maxDayjs = useMemo(
    () => parseDateTime(maxDatetime) ?? undefined,
    [maxDatetime],
  );
  const { startMax, endMin } = getDateTimeRangeBounds(
    minDayjs,
    maxDayjs,
    selected,
  );

  const commonProps = useMemo(
    () => ({
      ampm,
      format: format ?? undefined,
      disabled,
      readOnly,
      disablePast,
      disableFuture,
      openTo: openTo ?? undefined,
      views: views ?? undefined,
      minutesStep,
      timeSteps: resolveTimeSteps(minutesStep),
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
      ampm,
      format,
      disabled,
      readOnly,
      disablePast,
      disableFuture,
      openTo,
      views,
      minutesStep,
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
          <MuiDateTimePicker
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
              context: PickerChangeHandlerContext<DateTimeValidationError>,
            ) =>
              commit([newStart, selected[1]], context.validationError === null)
            }
            minDateTime={minDayjs}
            maxDateTime={startMax}
          />
          <MuiDateTimePicker
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
              context: PickerChangeHandlerContext<DateTimeValidationError>,
            ) =>
              commit([selected[0], newEnd], context.validationError === null)
            }
            minDateTime={endMin}
            maxDateTime={maxDayjs}
          />
        </Box>
        {helperText ? (
          <FormHelperText id={helperTextId}>{helperText}</FormHelperText>
        ) : null}
      </LocalizationProvider>
    </Box>
  );
};

export default DateTimeRangePickerComponent;
