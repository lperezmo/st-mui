import { FC, useCallback, useMemo, useState } from "react";
import { FrontendRendererArgs } from "@streamlit/component-v2-lib";
import dayjs, { Dayjs } from "dayjs";
import Box from "@mui/material/Box";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { TimePicker as MuiTimePicker } from "@mui/x-date-pickers/TimePicker";

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
};

type Props = {
  data: TimePickerData;
  setStateValue: FrontendRendererArgs<
    TimePickerState,
    TimePickerData
  >["setStateValue"];
};

function parseTime(val: string | null): Dayjs | null {
  if (!val) return null;
  const d = dayjs(`2000-01-01T${val}`);
  return d.isValid() ? d : null;
}

const TimePickerComponent: FC<Props> = ({ data, setStateValue }) => {
  const { label, value, ampm, minTime, maxTime, disabled } = data;

  const initialValue = useMemo(() => parseTime(value), [value]);
  const [selected, setSelected] = useState<Dayjs | null>(initialValue);

  const handleChange = useCallback(
    (newValue: Dayjs | null) => {
      setSelected(newValue);
      setStateValue(
        "selected_time",
        newValue?.isValid() ? newValue.format("HH:mm:ss") : null
      );
    },
    [setStateValue]
  );

  const minTimeDayjs = useMemo(() => parseTime(minTime), [minTime]);
  const maxTimeDayjs = useMemo(() => parseTime(maxTime), [maxTime]);

  return (
    <Box sx={{ width: "100%", py: 0.5 }}>
      <LocalizationProvider dateAdapter={AdapterDayjs}>
        <MuiTimePicker
          label={label}
          value={selected}
          onChange={handleChange}
          ampm={ampm}
          disabled={disabled}
          minTime={minTimeDayjs ?? undefined}
          maxTime={maxTimeDayjs ?? undefined}
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

export default TimePickerComponent;
