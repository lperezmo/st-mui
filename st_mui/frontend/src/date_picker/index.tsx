import { createMuiRenderer } from "../shared/renderer";
import DatePickerComponent, {
  DatePickerState,
  DatePickerData,
} from "./DatePicker";

export default createMuiRenderer<DatePickerState, DatePickerData>(
  DatePickerComponent
);
