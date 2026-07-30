import { createMuiRenderer } from "../shared/renderer";
import RatingComponent, { RatingData, RatingState } from "./Rating";

export default createMuiRenderer<RatingState, RatingData>(RatingComponent);
