import { FC, useCallback, useMemo, useState } from "react";
import { FrontendRendererArgs } from "@streamlit/component-v2-lib";
import dayjs, { Dayjs } from "dayjs";
import Box from "@mui/material/Box";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { DateTimeRangePicker as MuiDateTimeRangePicker } from "@mui/x-date-pickers-pro/DateTimeRangePicker";
import { DateRange } from "@mui/x-date-pickers-pro/models";
import { applyMuiLicense } from "../shared/license";

export type DateTimeRangePickerState = {
  start_datetime: string | null;
  end_datetime: string | null;
};

export type DateTimeRangePickerData = {
  label: string;
  startValue: string | null;
  endValue: string | null;
  minDatetime: string | null;
  maxDatetime: string | null;
  ampm: boolean;
  disabled: boolean;
  licenseKey: string | null;
};

type Props = {
  data: DateTimeRangePickerData;
  setStateValue: FrontendRendererArgs<
    DateTimeRangePickerState,
    DateTimeRangePickerData
  >["setStateValue"];
};

const DateTimeRangePickerComponent: FC<Props> = ({ data, setStateValue }) => {
  const {
    label,
    startValue,
    endValue,
    minDatetime,
    maxDatetime,
    ampm,
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
        "start_datetime",
        start?.isValid() ? start.toISOString() : null
      );
      setStateValue(
        "end_datetime",
        end?.isValid() ? end.toISOString() : null
      );
    },
    [setStateValue]
  );

  const minDayjs = useMemo(
    () => (minDatetime ? dayjs(minDatetime) : undefined),
    [minDatetime]
  );
  const maxDayjs = useMemo(
    () => (maxDatetime ? dayjs(maxDatetime) : undefined),
    [maxDatetime]
  );

  return (
    <Box sx={{ width: "100%", py: 0.5 }}>
      <LocalizationProvider dateAdapter={AdapterDayjs}>
        <MuiDateTimeRangePicker
          localeText={{ start: label ? `${label} (start)` : "Start", end: label ? `${label} (end)` : "End" }}
          value={selected}
          onChange={handleChange}
          ampm={ampm}
          disabled={disabled}
          minDateTime={minDayjs}
          maxDateTime={maxDayjs}
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

export default DateTimeRangePickerComponent;
