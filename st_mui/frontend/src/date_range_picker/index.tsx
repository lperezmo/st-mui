import { createMuiRenderer } from "../shared/renderer";
import DateRangePickerComponent, {
  type DateRangePickerState,
  type DateRangePickerData,
} from "./DateRangePicker";

export default createMuiRenderer<DateRangePickerState, DateRangePickerData>(
  DateRangePickerComponent,
  { emotionKey: "st-mui-date-range-picker" },
);
