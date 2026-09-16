import { createMuiRenderer } from "../shared/renderer";
import AutocompleteComponent, {
  type AutocompleteData,
  type AutocompleteState,
} from "./Autocomplete";

export default createMuiRenderer<AutocompleteState, AutocompleteData>(
  AutocompleteComponent,
  { emotionKey: "st-mui-autocomplete" },
);
