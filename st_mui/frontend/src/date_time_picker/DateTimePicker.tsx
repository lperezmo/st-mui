import { FC, useCallback, useMemo, useState } from "react";
import { FrontendRendererArgs } from "@streamlit/component-v2-lib";
import dayjs, { Dayjs } from "dayjs";
import Box from "@mui/material/Box";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { DateTimePicker as MuiDateTimePicker } from "@mui/x-date-pickers/DateTimePicker";

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
};

type Props = {
  data: DateTimePickerData;
  setStateValue: FrontendRendererArgs<
    DateTimePickerState,
    DateTimePickerData
  >["setStateValue"];
};

const DateTimePickerComponent: FC<Props> = ({ data, setStateValue }) => {
  const { label, value, minDatetime, maxDatetime, ampm, disabled } = data;

  const initialValue = useMemo(
    () => (value ? dayjs(value) : null),
    [value]
  );
  const [selected, setSelected] = useState<Dayjs | null>(initialValue);

  const handleChange = useCallback(
    (newValue: Dayjs | null) => {
      setSelected(newValue);
      setStateValue(
        "selected_datetime",
        newValue?.isValid() ? newValue.toISOString() : null
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
        <MuiDateTimePicker
          label={label}
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

export default DateTimePickerComponent;
