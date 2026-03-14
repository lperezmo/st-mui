import { createMuiRenderer } from "../shared/renderer";
import TimePickerComponent, {
  TimePickerState,
  TimePickerData,
} from "./TimePicker";

export default createMuiRenderer<TimePickerState, TimePickerData>(
  TimePickerComponent
);
