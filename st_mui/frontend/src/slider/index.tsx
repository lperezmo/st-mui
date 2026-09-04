import { createMuiRenderer } from "../shared/renderer";
import SliderComponent, { SliderData, SliderState } from "./Slider";

export default createMuiRenderer<SliderState, SliderData>(SliderComponent, {
  emotionKey: "st-mui-slider",
});
