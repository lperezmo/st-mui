import { createMuiRenderer } from "../shared/renderer";
import DateTimePickerComponent, {
  type DateTimePickerState,
  type DateTimePickerData,
} from "./DateTimePicker";

export default createMuiRenderer<DateTimePickerState, DateTimePickerData>(
  DateTimePickerComponent,
  { emotionKey: "st-mui-date-time-picker" },
);
