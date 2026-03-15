import { createMuiRenderer } from "../shared/renderer";
import DateRangePickerComponent, {
  DateRangePickerState,
  DateRangePickerData,
} from "./DateRangePicker";

export default createMuiRenderer<DateRangePickerState, DateRangePickerData>(
  DateRangePickerComponent
);
