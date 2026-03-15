import { FC, useCallback, useMemo, useState } from "react";
import { FrontendRendererArgs } from "@streamlit/component-v2-lib";
import dayjs, { Dayjs } from "dayjs";
import Box from "@mui/material/Box";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { DateRangePicker as MuiDateRangePicker } from "@mui/x-date-pickers-pro/DateRangePicker";
import { DateRange } from "@mui/x-date-pickers-pro/models";
import { applyMuiLicense } from "../shared/license";

export type DateRangePickerState = {
  start_date: string | null;
  end_date: string | null;
};

export type DateRangePickerData = {
  label: string;
  startValue: string | null;
  endValue: string | null;
  minDate: string | null;
  maxDate: string | null;
  calendars: number;
  disabled: boolean;
  licenseKey: string | null;
};

type Props = {
  data: DateRangePickerData;
  setStateValue: FrontendRendererArgs<
    DateRangePickerState,
    DateRangePickerData
  >["setStateValue"];
};

const DateRangePickerComponent: FC<Props> = ({ data, setStateValue }) => {
  const {
    label,
    startValue,
    endValue,
    minDate,
    maxDate,
    calendars,
    disabled,
    licenseKey,
  } = data;

  applyMuiLicense(licenseKey);

  const initialValue = useMemo<DateRange<Dayjs>>(
    () => [
      startValue ? dayjs(startValue) : null,
      endValue ? dayjs(endValue) : null,
    ],
    [startValue, endValue]
  );
  const [selected, setSelected] = useState<DateRange<Dayjs>>(initialValue);

  const handleChange = useCallback(
    (newValue: DateRange<Dayjs>) => {
      setSelected(newValue);
      const [start, end] = newValue;
      setStateValue(
        "start_date",
        start?.isValid() ? start.format("YYYY-MM-DD") : null
      );
      setStateValue(
        "end_date",
        end?.isValid() ? end.format("YYYY-MM-DD") : null
      );
    },
    [setStateValue]
  );

  const minDayjs = useMemo(
    () => (minDate ? dayjs(minDate) : undefined),
    [minDate]
  );
  const maxDayjs = useMemo(
    () => (maxDate ? dayjs(maxDate) : undefined),
    [maxDate]
  );

  return (
    <Box sx={{ width: "100%", py: 0.5 }}>
      <LocalizationProvider dateAdapter={AdapterDayjs}>
        <MuiDateRangePicker
          localeText={{ start: label ? `${label} (start)` : "Start", end: label ? `${label} (end)` : "End" }}
          value={selected}
          onChange={handleChange}
          disabled={disabled}
          minDate={minDayjs}
          maxDate={maxDayjs}
          calendars={calendars as 1 | 2 | 3}
          slotProps={{
            textField: {
              fullWidth: true,
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

export default DateRangePickerComponent;
