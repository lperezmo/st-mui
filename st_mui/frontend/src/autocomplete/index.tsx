import { createMuiRenderer } from "../shared/renderer";
import AutocompleteComponent from "./Autocomplete";
import type {
  AutocompleteData,
  AutocompleteState,
} from "./Autocomplete";

export default createMuiRenderer<AutocompleteState, AutocompleteData>(
  AutocompleteComponent,
  { emotionKey: "st-mui-autocomplete" },
);
