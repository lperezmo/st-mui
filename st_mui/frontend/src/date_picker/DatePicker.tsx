import { FC, useCallback, useMemo, useState } from "react";
import { FrontendRendererArgs } from "@streamlit/component-v2-lib";
import dayjs, { Dayjs } from "dayjs";
import Box from "@mui/material/Box";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { DatePicker as MuiDatePicker } from "@mui/x-date-pickers/DatePicker";

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
};

type Props = {
  data: DatePickerData;
  setStateValue: FrontendRendererArgs<
    DatePickerState,
    DatePickerData
  >["setStateValue"];
};

const DatePickerComponent: FC<Props> = ({ data, setStateValue }) => {
  const { label, value, minDate, maxDate, format, disabled } = data;

  const initialValue = useMemo(
    () => (value ? dayjs(value) : null),
    [value]
  );

  const [selected, setSelected] = useState<Dayjs | null>(initialValue);

  const handleChange = useCallback(
    (newValue: Dayjs | null) => {
      setSelected(newValue);
      setStateValue(
        "selected_date",
        newValue?.isValid() ? newValue.format("YYYY-MM-DD") : null
      );
    },
    [setStateValue]
  );

  const minDateDayjs = useMemo(
    () => (minDate ? dayjs(minDate) : undefined),
    [minDate]
  );
  const maxDateDayjs = useMemo(
    () => (maxDate ? dayjs(maxDate) : undefined),
    [maxDate]
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
          minDate={minDateDayjs}
          maxDate={maxDateDayjs}
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

export default DatePickerComponent;
