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
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { TimePicker as MuiTimePicker } from "@mui/x-date-pickers/TimePicker";
import { usePickerId } from "../shared/id";
import { resolveTimeSteps } from "../shared/timeSteps";
import type {
  PickerChangeHandlerContext,
  TimeValidationError,
  TimeView,
} from "@mui/x-date-pickers/models";

export type TimePickerState = {
  selected_time: string | null;
};

export type TimePickerData = {
  label: string;
  value: string | null;
  ampm: boolean;
  minTime: string | null;
  maxTime: string | null;
  disabled: boolean;
  helperText: string | null;
  clearable: boolean;
  readOnly: boolean;
  disablePast: boolean;
  disableFuture: boolean;
  openTo: TimeView | null;
  views: TimeView[] | null;
  minutesStep: number;
  format: string | null;
};

type Props = {
  data: TimePickerData;
  setStateValue: FrontendRendererArgs<
    TimePickerState,
    TimePickerData
  >["setStateValue"];
};

export function parseTimePickerValue(val: string | null): Dayjs | null {
  if (!val) return null;
  // TimePicker validation (including disablePast/disableFuture) compares the
  // complete Dayjs value with "now", so time-only values must share today's
  // date instead of an arbitrary historical anchor.
  const d = dayjs(`${dayjs().format("YYYY-MM-DD")}T${val}`);
  return d.isValid() ? d : null;
}

export function serializeTimePickerValue(value: Dayjs | null): string | null {
  if (value === null) return null;
  return value.isValid() ? value.format("HH:mm:ss") : null;
}

export function reconcileTimePickerValue(
  currentValue: Dayjs | null,
  previousExternalValue: string | null,
  nextExternalValue: string | null,
): Dayjs | null {
  return previousExternalValue === nextExternalValue
    ? currentValue
    : parseTimePickerValue(nextExternalValue);
}

export function syncExternalTimePickerValue(
  nextExternalValue: string | null,
  setStateValue: Props["setStateValue"],
): Dayjs | null {
  const parsed = parseTimePickerValue(nextExternalValue);
  setStateValue("selected_time", serializeTimePickerValue(parsed));
  return parsed;
}

export function nextTimePickerStateValue(
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
  const serialized = serializeTimePickerValue(newValue);
  return serialized === currentValue ? undefined : serialized;
}

const TimePickerComponent: FC<Props> = ({ data, setStateValue }) => {
  const {
    label,
    value,
    ampm,
    minTime,
    maxTime,
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
    parseTimePickerValue(value),
  );
  const selectedValueRef = useRef<string | null>(
    serializeTimePickerValue(parseTimePickerValue(value)),
  );
  const previousExternalValueRef = useRef(value);
  const inputId = usePickerId("time-picker");

  useEffect(() => {
    if (previousExternalValueRef.current !== value) {
      const synced = syncExternalTimePickerValue(value, setStateValue);
      selectedValueRef.current = serializeTimePickerValue(synced);
      setSelected(synced);
    }
    previousExternalValueRef.current = value;
  }, [value, setStateValue]);

  const handleChange = useCallback(
    (
      newValue: Dayjs | null,
      context: PickerChangeHandlerContext<TimeValidationError>,
    ) => {
      const nextValue = nextTimePickerStateValue(
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
      setStateValue("selected_time", nextValue);
    },
    [clearable, disabled, readOnly, setStateValue],
  );

  const minTimeDayjs = useMemo(() => parseTimePickerValue(minTime), [minTime]);
  const maxTimeDayjs = useMemo(() => parseTimePickerValue(maxTime), [maxTime]);

  return (
    <Box sx={{ width: "100%", py: 0.5 }}>
      <LocalizationProvider dateAdapter={AdapterDayjs}>
        <MuiTimePicker
          label={label}
          value={selected}
          onChange={handleChange}
          ampm={ampm}
          disabled={disabled}
          readOnly={readOnly}
          disablePast={disablePast}
          disableFuture={disableFuture}
          minTime={minTimeDayjs ?? undefined}
          maxTime={maxTimeDayjs ?? undefined}
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

export default TimePickerComponent;
