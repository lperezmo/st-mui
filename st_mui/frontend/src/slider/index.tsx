import { createMuiRenderer } from "../shared/renderer";
import SliderComponent, { type SliderData, type SliderState } from "./Slider";

export default createMuiRenderer<SliderState, SliderData>(SliderComponent, {
  emotionKey: "st-mui-slider",
});
