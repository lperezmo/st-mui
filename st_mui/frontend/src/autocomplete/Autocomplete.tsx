import { type FC, useCallback, useEffect, useRef, useState } from "react";
import type { FrontendRendererArgs } from "@streamlit/component-v2-lib";
import MuiAutocomplete from "@mui/material/Autocomplete";
import Box from "@mui/material/Box";
import TextField from "@mui/material/TextField";

export type AutocompleteScalar = string | number | boolean;

export type AutocompleteOption = {
  label: string;
  value: AutocompleteScalar;
  disabled: boolean;
};

export type AutocompleteState = {
  selected_value: AutocompleteScalar | AutocompleteScalar[] | null;
};

export type AutocompleteData = {
  options: AutocompleteOption[];
  label: string;
  selectedValue: AutocompleteScalar | AutocompleteScalar[] | null;
  multiple: boolean;
  freeSolo: boolean;
  placeholder: string | null;
  helperText: string | null;
  clearable: boolean;
  disabled: boolean;
};

type Selection =
  | AutocompleteOption
  | string
  | (AutocompleteOption | string)[]
  | null;

type Props = {
  data: AutocompleteData;
  setStateValue: FrontendRendererArgs<
    AutocompleteState,
    AutocompleteData
  >["setStateValue"];
};

function autocompleteSelectionValue(
  item: AutocompleteOption | string,
): AutocompleteScalar {
  return typeof item === "string" ? item : item.value;
}

export function getAutocompleteOptionLabel(
  option: AutocompleteOption | string | null | undefined,
): string {
  if (option === null || option === undefined) return "";
  if (typeof option === "string") return option;
  if (typeof option.label === "string") return option.label;
  return String((option as AutocompleteOption).value ?? "");
}

export function isAutocompleteOptionDisabled(
  option: AutocompleteOption | string,
): boolean {
  return typeof option === "string" ? false : !!option.disabled;
}

export function isAutocompleteOptionEqual(
  option: AutocompleteOption,
  current: AutocompleteOption | string,
): boolean {
  if (typeof current === "string") {
    // Free-solo strings never equal an option by value identity, but match
    // when the typed text equals the option label or a string-valued option.
    return (
      option.label === current ||
      (typeof option.value === "string" && option.value === current)
    );
  }
  return sameAutocompleteValue(option.value, current.value);
}

export function sameAutocompleteValue(
  left: AutocompleteScalar,
  right: AutocompleteScalar,
): boolean {
  return typeof left === typeof right && left === right;
}

export function sameAutocompleteDataValue(
  left: AutocompleteData["selectedValue"],
  right: AutocompleteData["selectedValue"],
): boolean {
  if (Array.isArray(left) || Array.isArray(right)) {
    return (
      Array.isArray(left) &&
      Array.isArray(right) &&
      left.length === right.length &&
      left.every((item, index) => sameAutocompleteValue(item, right[index]))
    );
  }
  if (left === null || right === null) return left === right;
  return sameAutocompleteValue(left, right);
}

export function dedupeAutocompleteSelection(
  selection: Selection,
  multiple: boolean,
): Selection {
  if (!multiple || !Array.isArray(selection)) return selection;

  const unique: (AutocompleteOption | string)[] = [];
  for (const item of selection) {
    const value = autocompleteSelectionValue(item);
    if (
      !unique.some((candidate) =>
        sameAutocompleteValue(autocompleteSelectionValue(candidate), value),
      )
    ) {
      unique.push(item);
    }
  }
  return unique;
}

export function serializeAutocompleteSelection(
  selection: Selection,
  multiple: boolean,
): AutocompleteScalar | AutocompleteScalar[] | null {
  selection = dedupeAutocompleteSelection(selection, multiple);

  if (multiple) {
    return Array.isArray(selection)
      ? selection.map(autocompleteSelectionValue)
      : [];
  }
  if (selection === null || Array.isArray(selection)) {
    return null;
  }
  return autocompleteSelectionValue(selection);
}

export function resolveAutocompleteSelection(
  value: AutocompleteData["selectedValue"],
  options: AutocompleteOption[],
  multiple: boolean,
  freeSolo: boolean,
): Selection {
  const resolveOne = (
    item: AutocompleteScalar,
  ): AutocompleteOption | string | null => {
    const option = options.find((candidate) =>
      sameAutocompleteValue(candidate.value, item),
    );
    if (option) return option;
    return freeSolo && typeof item === "string" ? item : null;
  };

  if (multiple) {
    const values = Array.isArray(value) ? value : [];
    return values
      .map(resolveOne)
      .filter((item): item is AutocompleteOption | string => item !== null);
  }
  if (value === null || Array.isArray(value)) return null;
  return resolveOne(value);
}

/**
 * Keep a user's persistent component state when Streamlit rerenders with the
 * same Python default, while still honoring a genuinely changed default.
 * Re-resolving against the latest options also refreshes labels and disabled
 * flags without reverting the user's selection.
 */
export function reconcileAutocompleteSelection(
  currentValue: AutocompleteData["selectedValue"],
  previousExternalValue: AutocompleteData["selectedValue"],
  nextExternalValue: AutocompleteData["selectedValue"],
  options: AutocompleteOption[],
  multiple: boolean,
  freeSolo: boolean,
  forceExternalValue = false,
): Selection {
  const sourceValue =
    forceExternalValue ||
    !sameAutocompleteDataValue(previousExternalValue, nextExternalValue)
      ? nextExternalValue
      : currentValue;
  return resolveAutocompleteSelection(sourceValue, options, multiple, freeSolo);
}

const AutocompleteComponent: FC<Props> = ({ data, setStateValue }) => {
  const {
    options,
    label,
    selectedValue,
    multiple,
    freeSolo,
    placeholder,
    helperText,
    clearable,
    disabled,
  } = data;

  const initialSelection = resolveAutocompleteSelection(
    selectedValue,
    options,
    multiple,
    freeSolo,
  );
  const [selected, setSelected] = useState<Selection>(initialSelection);
  const selectedValueRef = useRef<AutocompleteData["selectedValue"]>(
    serializeAutocompleteSelection(initialSelection, multiple),
  );
  const previousDataRef = useRef({
    selectedValue,
    multiple,
    freeSolo,
  });

  useEffect(() => {
    const previous = previousDataRef.current;
    const nextSelection = reconcileAutocompleteSelection(
      selectedValueRef.current,
      previous.selectedValue,
      selectedValue,
      options,
      multiple,
      freeSolo,
      previous.multiple !== multiple || previous.freeSolo !== freeSolo,
    );
    const nextSerialized = serializeAutocompleteSelection(
      nextSelection,
      multiple,
    );
    previousDataRef.current = { selectedValue, multiple, freeSolo };
    // options is a new array identity on every Streamlit rerun; avoid
    // resetting user state (and extra renders) when the resolved value is
    // unchanged.
    if (sameAutocompleteDataValue(selectedValueRef.current, nextSerialized)) {
      return;
    }
    selectedValueRef.current = nextSerialized;
    setSelected(nextSelection);
  }, [selectedValue, options, multiple, freeSolo]);

  const handleChange = useCallback(
    (_event: React.SyntheticEvent, newValue: Selection) => {
      const deduplicated = dedupeAutocompleteSelection(newValue, multiple);
      const serialized = serializeAutocompleteSelection(deduplicated, multiple);
      setSelected(deduplicated);
      if (sameAutocompleteDataValue(selectedValueRef.current, serialized)) {
        return;
      }
      selectedValueRef.current = serialized;
      setStateValue("selected_value", serialized);
    },
    [multiple, setStateValue],
  );

  return (
    <Box sx={{ width: "100%", py: 0.5 }}>
      <MuiAutocomplete<AutocompleteOption, boolean, boolean, boolean>
        options={options}
        value={selected}
        multiple={multiple}
        freeSolo={freeSolo}
        disableClearable={!clearable}
        disabled={disabled}
        getOptionLabel={getAutocompleteOptionLabel}
        getOptionDisabled={isAutocompleteOptionDisabled}
        isOptionEqualToValue={isAutocompleteOptionEqual}
        onChange={handleChange}
        renderInput={(params) => (
          <TextField
            {...params}
            label={label}
            placeholder={placeholder ?? undefined}
            helperText={helperText}
          />
        )}
        slotProps={{
          popper: {
            style: { zIndex: 999999 },
          },
        }}
      />
    </Box>
  );
};

export default AutocompleteComponent;
