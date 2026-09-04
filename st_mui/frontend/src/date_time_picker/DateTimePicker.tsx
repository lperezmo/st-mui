import { FC, useCallback, useEffect, useMemo, useRef, useState } from "react";
import { FrontendRendererArgs } from "@streamlit/component-v2-lib";
import dayjs, { Dayjs } from "dayjs";
import Box from "@mui/material/Box";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { DateTimePicker as MuiDateTimePicker } from "@mui/x-date-pickers/DateTimePicker";
import { serializeWallClockDateTime } from "../shared/datetime";
import { usePickerId } from "../shared/id";
import { resolveTimeSteps } from "../shared/timeSteps";
import type {
  DateOrTimeView,
  DateTimeValidationError,
  PickerChangeHandlerContext,
} from "@mui/x-date-pickers/models";

export type DateTimePickerState = {
  selected_datetime: string | null;
};

export type DateTimePickerData = {
  label: string;
  value: string | null;
  minDatetime: string | null;
  maxDatetime: string | null;
  ampm: boolean;
  disabled: boolean;
  helperText: string | null;
  clearable: boolean;
  readOnly: boolean;
  disablePast: boolean;
  disableFuture: boolean;
  openTo: DateOrTimeView | null;
  views: DateOrTimeView[] | null;
  minutesStep: number;
  format: string | null;
};

type Props = {
  data: DateTimePickerData;
  setStateValue: FrontendRendererArgs<
    DateTimePickerState,
    DateTimePickerData
  >["setStateValue"];
};

export function parseDateTimePickerValue(value: string | null): Dayjs | null {
  if (!value) return null;
  const parsed = dayjs(value);
  return parsed.isValid() ? parsed : null;
}

export function reconcileDateTimePickerValue(
  currentValue: Dayjs | null,
  previousExternalValue: string | null,
  nextExternalValue: string | null,
): Dayjs | null {
  return previousExternalValue === nextExternalValue
    ? currentValue
    : parseDateTimePickerValue(nextExternalValue);
}

export function syncExternalDateTimePickerValue(
  nextExternalValue: string | null,
  setStateValue: Props["setStateValue"],
): Dayjs | null {
  const parsed = parseDateTimePickerValue(nextExternalValue);
  setStateValue("selected_datetime", serializeWallClockDateTime(parsed));
  return parsed;
}

export function nextDateTimePickerStateValue(
  newValue: Dayjs | null,
  currentValue: string | null,
  {
    interactive,
    clearable,
    valid = true,
  }: {
    interactive: boolean;
    clearable: boolean;
    valid?: boolean;
  },
): string | null | undefined {
  if (!interactive || !valid || (newValue === null && !clearable)) {
    return undefined;
  }
  if (newValue !== null && !newValue.isValid()) return undefined;
  const serialized = serializeWallClockDateTime(newValue);
  return serialized === currentValue ? undefined : serialized;
}

const DateTimePickerComponent: FC<Props> = ({ data, setStateValue }) => {
  const {
    label,
    value,
    minDatetime,
    maxDatetime,
    ampm,
    disabled,
    helperText,
    clearable,
    readOnly,
    disablePast,
    disableFuture,
    openTo,
    views,
    minutesStep,
    format,
  } = data;

  const [selected, setSelected] = useState<Dayjs | null>(() =>
    parseDateTimePickerValue(value),
  );
  const selectedValueRef = useRef<string | null>(
    serializeWallClockDateTime(parseDateTimePickerValue(value)),
  );
  const previousExternalValueRef = useRef(value);
  const inputId = usePickerId("date-time-picker");

  useEffect(() => {
    if (previousExternalValueRef.current !== value) {
      const synced = syncExternalDateTimePickerValue(value, setStateValue);
      selectedValueRef.current = serializeWallClockDateTime(synced);
      setSelected(synced);
    }
    previousExternalValueRef.current = value;
  }, [value, setStateValue]);

  const handleChange = useCallback(
    (
      newValue: Dayjs | null,
      context: PickerChangeHandlerContext<DateTimeValidationError>,
    ) => {
      const nextValue = nextDateTimePickerStateValue(
        newValue,
        selectedValueRef.current,
        {
          interactive: !disabled && !readOnly,
          clearable,
          valid: context.validationError === null,
        },
      );
      if (disabled || readOnly || (newValue === null && !clearable)) return;
      setSelected(newValue);
      if (nextValue === undefined) return;
      selectedValueRef.current = nextValue;
      setStateValue("selected_datetime", nextValue);
    },
    [clearable, disabled, readOnly, setStateValue],
  );

  const minDayjs = useMemo(
    () => parseDateTimePickerValue(minDatetime) ?? undefined,
    [minDatetime],
  );
  const maxDayjs = useMemo(
    () => parseDateTimePickerValue(maxDatetime) ?? undefined,
    [maxDatetime],
  );

  return (
    <Box sx={{ width: "100%", py: 0.5 }}>
      <LocalizationProvider dateAdapter={AdapterDayjs}>
        <MuiDateTimePicker
          label={label}
          value={selected}
          onChange={handleChange}
          ampm={ampm}
          disabled={disabled}
          readOnly={readOnly}
          disablePast={disablePast}
          disableFuture={disableFuture}
          minDateTime={minDayjs}
          maxDateTime={maxDayjs}
          openTo={openTo ?? undefined}
          views={views ?? undefined}
          minutesStep={minutesStep}
          timeSteps={resolveTimeSteps(minutesStep)}
          format={format ?? undefined}
          slotProps={{
            field: {
              clearable,
            },
            textField: {
              id: inputId,
              fullWidth: true,
              helperText,
            },
            popper: {
              disablePortal: false,
              style: { zIndex: 999999 },
            },
          }}
        />
      </LocalizationProvider>
    </Box>
  );
};

export default DateTimePickerComponent;
