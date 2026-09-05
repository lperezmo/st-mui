import { createMuiRenderer } from "../shared/renderer";
import TimePickerComponent from "./TimePicker";
import type {
  TimePickerState,
  TimePickerData,
} from "./TimePicker";

export default createMuiRenderer<TimePickerState, TimePickerData>(
  TimePickerComponent,
  { emotionKey: "st-mui-time-picker" },
);
