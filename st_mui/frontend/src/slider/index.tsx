import { createMuiRenderer } from "../shared/renderer";
import SliderComponent from "./Slider";
import type { SliderData, SliderState } from "./Slider";

export default createMuiRenderer<SliderState, SliderData>(SliderComponent, {
  emotionKey: "st-mui-slider",
});
