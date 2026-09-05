import { createMuiRenderer } from "../shared/renderer";
import DateRangePickerComponent from "./DateRangePicker";
import type {
  DateRangePickerState,
  DateRangePickerData,
} from "./DateRangePicker";

export default createMuiRenderer<DateRangePickerState, DateRangePickerData>(
  DateRangePickerComponent,
  { emotionKey: "st-mui-date-range-picker" },
);
