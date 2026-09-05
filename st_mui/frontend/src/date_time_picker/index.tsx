import { createMuiRenderer } from "../shared/renderer";
import DateTimePickerComponent from "./DateTimePicker";
import type {
  DateTimePickerState,
  DateTimePickerData,
} from "./DateTimePicker";

export default createMuiRenderer<DateTimePickerState, DateTimePickerData>(
  DateTimePickerComponent,
  { emotionKey: "st-mui-date-time-picker" },
);
