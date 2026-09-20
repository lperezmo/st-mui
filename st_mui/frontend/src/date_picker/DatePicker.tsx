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
import { DatePicker as MuiDatePicker } from "@mui/x-date-pickers/DatePicker";
import { usePickerId } from "../shared/id";
import type {
  DateValidationError,
  DateView,
  PickerChangeHandlerContext,
} from "@mui/x-date-pickers/models";

export type DatePickerState = {
  selected_date: string | null;
};

export type DatePickerData = {
  label: string;
  value: string | null;
  minDate: string | null;
  maxDate: string | null;
  format: string;
  disabled: boolean;
  helperText: string | null;
  clearable: boolean;
  readOnly: boolean;
  disablePast: boolean;
  disableFuture: boolean;
  openTo: DateView | null;
  views: DateView[] | null;
  displayWeekNumber: boolean;
};

type Props = {
  data: DatePickerData;
  setStateValue: FrontendRendererArgs<
    DatePickerState,
    DatePickerData
  >["setStateValue"];
};

export function parseDatePickerValue(value: string | null): Dayjs | null {
  if (!value) return null;
  const parsed = dayjs(value);
  return parsed.isValid() ? parsed : null;
}

export function serializeDatePickerValue(value: Dayjs | null): string | null {
  if (value === null) return null;
  return value.isValid() ? value.format("YYYY-MM-DD") : null;
}

export function reconcileDatePickerValue(
  currentValue: Dayjs | null,
  previousExternalValue: string | null,
  nextExternalValue: string | null,
): Dayjs | null {
  return previousExternalValue === nextExternalValue
    ? currentValue
    : parseDatePickerValue(nextExternalValue);
}

export function syncExternalDatePickerValue(
  nextExternalValue: string | null,
  setStateValue: Props["setStateValue"],
): Dayjs | null {
  const parsed = parseDatePickerValue(nextExternalValue);
  setStateValue("selected_date", serializeDatePickerValue(parsed));
  return parsed;
}

export function nextDatePickerStateValue(
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
  const serialized = serializeDatePickerValue(newValue);
  return serialized === currentValue ? undefined : serialized;
}

const DatePickerComponent: FC<Props> = ({ data, setStateValue }) => {
  const {
    label,
    value,
    minDate,
    maxDate,
    format,
    disabled,
    helperText,
    clearable,
    readOnly,
    disablePast,
    disableFuture,
    openTo,
    views,
    displayWeekNumber,
  } = data;

  const [selected, setSelected] = useState<Dayjs | null>(() =>
    parseDatePickerValue(value),
  );
  const selectedValueRef = useRef<string | null>(
    serializeDatePickerValue(parseDatePickerValue(value)),
  );
  const previousExternalValueRef = useRef(value);
  const inputId = usePickerId("date-picker");

  useEffect(() => {
    if (previousExternalValueRef.current !== value) {
      const synced = syncExternalDatePickerValue(value, setStateValue);
      selectedValueRef.current = serializeDatePickerValue(synced);
      setSelected(synced);
    }
    previousExternalValueRef.current = value;
  }, [value, setStateValue]);

  const handleChange = useCallback(
    (
      newValue: Dayjs | null,
      context: PickerChangeHandlerContext<DateValidationError>,
    ) => {
      const nextValue = nextDatePickerStateValue(
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
      setStateValue("selected_date", nextValue);
    },
    [clearable, disabled, readOnly, setStateValue],
  );

  const minDateDayjs = useMemo(
    () => parseDatePickerValue(minDate) ?? undefined,
    [minDate],
  );
  const maxDateDayjs = useMemo(
    () => parseDatePickerValue(maxDate) ?? undefined,
    [maxDate],
  );

  return (
    <Box sx={{ width: "100%", py: 0.5 }}>
      <LocalizationProvider dateAdapter={AdapterDayjs}>
        <MuiDatePicker
          label={label}
          value={selected}
          onChange={handleChange}
          format={format}
          disabled={disabled}
          readOnly={readOnly}
          disablePast={disablePast}
          disableFuture={disableFuture}
          minDate={minDateDayjs}
          maxDate={maxDateDayjs}
          openTo={openTo ?? undefined}
          views={views ?? undefined}
          displayWeekNumber={displayWeekNumber}
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

export default DatePickerComponent;
