import { FC, useCallback, useEffect, useId, useRef, useState } from "react";
import { FrontendRendererArgs } from "@streamlit/component-v2-lib";
import Box from "@mui/material/Box";
import MuiRating from "@mui/material/Rating";
import Typography from "@mui/material/Typography";

export type RatingState = {
  selected_value: number | null;
};

export type RatingData = {
  label: string;
  selectedValue: number | null;
  maxValue: number;
  precision: number;
  size: "small" | "medium" | "large";
  disabled: boolean;
  readOnly: boolean;
  clearable: boolean;
};

type Props = {
  data: RatingData;
  setStateValue: FrontendRendererArgs<RatingState, RatingData>["setStateValue"];
};

export function nextRatingValue(
  current: number | null,
  candidate: number | null,
  {
    clearable,
    disabled,
    readOnly,
  }: Pick<RatingData, "clearable" | "disabled" | "readOnly">,
): number | null {
  if (disabled || readOnly) return current;
  return candidate === null && !clearable ? current : candidate;
}

export function ratingLabelText(
  ratingValue: number | null,
  maxValue: number,
): string {
  if (ratingValue === null) return "No rating";
  return `${ratingValue} of ${maxValue} ${maxValue === 1 ? "star" : "stars"}`;
}

const RatingComponent: FC<Props> = ({ data, setStateValue }) => {
  const {
    label,
    selectedValue,
    maxValue,
    precision,
    size,
    disabled,
    readOnly,
    clearable,
  } = data;
  const name = useId();
  const [selected, setSelected] = useState<number | null>(selectedValue);
  const previousExternalRef = useRef<number | null>(selectedValue);

  useEffect(() => {
    if (previousExternalRef.current !== selectedValue) {
      previousExternalRef.current = selectedValue;
      setSelected((current) => (current === selectedValue ? current : selectedValue));
    }
  }, [selectedValue]);

  const handleChange = useCallback(
    (_event: React.SyntheticEvent, newValue: number | null) => {
      const next = nextRatingValue(selected, newValue, {
        clearable,
        disabled,
        readOnly,
      });
      if (next === selected) return;
      setSelected(next);
      setStateValue("selected_value", next);
    },
    [clearable, disabled, readOnly, selected, setStateValue],
  );

  const hasLabel = label.trim() !== "";

  return (
    <Box
      component="fieldset"
      sx={{ width: "100%", border: 0, m: 0, minWidth: 0, p: 0, py: 0.5 }}
    >
      {hasLabel && (
        <Typography component="legend" variant="body2" sx={{ mb: 0.5 }}>
          {label}
        </Typography>
      )}
      <MuiRating
        name={name}
        value={selected}
        max={maxValue}
        precision={precision}
        size={size}
        disabled={disabled}
        readOnly={readOnly}
        emptyLabelText="No rating"
        getLabelText={(ratingValue) => ratingLabelText(ratingValue, maxValue)}
        onChange={handleChange}
      />
    </Box>
  );
};

export default RatingComponent;
