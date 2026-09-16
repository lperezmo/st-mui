import { createMuiRenderer } from "../shared/renderer";
import DatePickerComponent, {
  type DatePickerState,
  type DatePickerData,
} from "./DatePicker";

export default createMuiRenderer<DatePickerState, DatePickerData>(
  DatePickerComponent,
  { emotionKey: "st-mui-date-picker" },
);
