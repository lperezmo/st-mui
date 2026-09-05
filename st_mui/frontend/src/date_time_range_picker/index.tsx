import { createMuiRenderer } from "../shared/renderer";
import DateTimeRangePickerComponent from "./DateTimeRangePicker";
import type {
  DateTimeRangePickerState,
  DateTimeRangePickerData,
} from "./DateTimeRangePicker";

export default createMuiRenderer<
  DateTimeRangePickerState,
  DateTimeRangePickerData
>(DateTimeRangePickerComponent, { emotionKey: "st-mui-date-time-range" });
