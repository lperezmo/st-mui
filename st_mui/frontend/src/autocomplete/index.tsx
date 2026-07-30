import { createMuiRenderer } from "../shared/renderer";
import AutocompleteComponent, {
  AutocompleteData,
  AutocompleteState,
} from "./Autocomplete";

export default createMuiRenderer<AutocompleteState, AutocompleteData>(
  AutocompleteComponent,
);
