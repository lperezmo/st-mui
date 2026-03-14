import { createMuiRenderer } from "../shared/renderer";
import DateTimePickerComponent, {
  DateTimePickerState,
  DateTimePickerData,
} from "./DateTimePicker";

export default createMuiRenderer<DateTimePickerState, DateTimePickerData>(
  DateTimePickerComponent
);
