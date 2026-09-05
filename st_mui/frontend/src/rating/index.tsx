import { createMuiRenderer } from "../shared/renderer";
import RatingComponent from "./Rating";
import type { RatingData, RatingState } from "./Rating";

export default createMuiRenderer<RatingState, RatingData>(RatingComponent, {
  emotionKey: "st-mui-rating",
});
