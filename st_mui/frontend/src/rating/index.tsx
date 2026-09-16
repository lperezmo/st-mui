import { createMuiRenderer } from "../shared/renderer";
import RatingComponent, { type RatingData, type RatingState } from "./Rating";

export default createMuiRenderer<RatingState, RatingData>(RatingComponent, {
  emotionKey: "st-mui-rating",
});
