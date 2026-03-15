import { createMuiRenderer } from "../shared/renderer";
import DateTimeRangePickerComponent, {
  DateTimeRangePickerState,
  DateTimeRangePickerData,
} from "./DateTimeRangePicker";

export default createMuiRenderer<
  DateTimeRangePickerState,
  DateTimeRangePickerData
>(DateTimeRangePickerComponent);
