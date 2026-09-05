import { createMuiRenderer } from "../shared/renderer";
import DatePickerComponent from "./DatePicker";
import type {
  DatePickerState,
  DatePickerData,
} from "./DatePicker";

export default createMuiRenderer<DatePickerState, DatePickerData>(
  DatePickerComponent,
  { emotionKey: "st-mui-date-picker" },
);
