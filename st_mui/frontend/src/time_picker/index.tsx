import { createMuiRenderer } from "../shared/renderer";
import TimePickerComponent, {
  type TimePickerState,
  type TimePickerData,
} from "./TimePicker";

export default createMuiRenderer<TimePickerState, TimePickerData>(
  TimePickerComponent,
  { emotionKey: "st-mui-time-picker" },
);
