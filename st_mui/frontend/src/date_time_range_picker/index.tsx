import { createMuiRenderer } from "../shared/renderer";
import DateTimeRangePickerComponent, {
  type DateTimeRangePickerState,
  type DateTimeRangePickerData,
} from "./DateTimeRangePicker";

export default createMuiRenderer<
  DateTimeRangePickerState,
  DateTimeRangePickerData
>(DateTimeRangePickerComponent, { emotionKey: "st-mui-date-time-range" });
