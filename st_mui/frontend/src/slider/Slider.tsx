import { FC, useCallback, useEffect, useRef, useState } from "react";
import { FrontendRendererArgs } from "@streamlit/component-v2-lib";
import Box from "@mui/material/Box";
import MuiSlider from "@mui/material/Slider";
import Typography from "@mui/material/Typography";

export type SliderValue = number | number[];

export type SliderMark = {
  value: number;
  label?: string;
};

export type SliderState = {
  selected_value: SliderValue;
};

export type SliderData = {
  label: string;
  selectedValue: SliderValue;
  minValue: number;
  maxValue: number;
  step: number | null;
  marks: boolean | SliderMark[];
  valueLabelDisplay: "auto" | "on" | "off";
  disabled: boolean;
};

type Props = {
  data: SliderData;
  setStateValue: FrontendRendererArgs<SliderState, SliderData>["setStateValue"];
};

export function commitSliderValue(
  setStateValue: Props["setStateValue"],
  value: SliderValue,
): void {
  setStateValue("selected_value", normalizeSliderValue(value));
}

export function normalizeSliderValue(value: number | number[]): SliderValue {
  return Array.isArray(value) ? [...value] : value;
}

export function sliderValuesEqual(
  left: SliderValue,
  right: SliderValue,
): boolean {
  if (!Array.isArray(left) || !Array.isArray(right)) {
    return left === right;
  }
  return (
    left.length === right.length &&
    left.every((value, index) => value === right[index])
  );
}

export function clampSliderValue(
  value: SliderValue,
  minValue: number,
  maxValue: number,
): SliderValue {
  const clampOne = (v: number) => Math.min(maxValue, Math.max(minValue, v));
  return Array.isArray(value) ? value.map(clampOne) : clampOne(value);
}

export function getSliderAriaValueText(value: number): string {
  return `${value}`;
}

export function getSliderAriaLabel(
  label: string,
  value: SliderValue,
  index: number,
): string {
  if (!Array.isArray(value)) {
    return label;
  }
  return `${label} ${index === 0 ? "minimum" : "maximum"}`;
}

const SliderComponent: FC<Props> = ({ data, setStateValue }) => {
  const {
    label,
    selectedValue,
    minValue,
    maxValue,
    step,
    marks,
    valueLabelDisplay,
    disabled,
  } = data;
  const [displayedValue, setDisplayedValue] = useState<SliderValue>(() =>
    clampSliderValue(normalizeSliderValue(selectedValue), minValue, maxValue),
  );
  const previousSelectedValue = useRef<SliderValue>(
    normalizeSliderValue(selectedValue),
  );
  const previousBoundsRef = useRef({ minValue, maxValue });

  useEffect(() => {
    const boundsChanged =
      previousBoundsRef.current.minValue !== minValue ||
      previousBoundsRef.current.maxValue !== maxValue;
    previousBoundsRef.current = { minValue, maxValue };
    if (
      boundsChanged ||
      !sliderValuesEqual(previousSelectedValue.current, selectedValue)
    ) {
      previousSelectedValue.current = normalizeSliderValue(selectedValue);
      setDisplayedValue(
        clampSliderValue(normalizeSliderValue(selectedValue), minValue, maxValue),
      );
    }
  }, [selectedValue, minValue, maxValue]);

  const handleChange = useCallback(
    (_event: Event, newValue: number | number[]) => {
      setDisplayedValue(normalizeSliderValue(newValue));
    },
    [],
  );

  const handleCommit = useCallback(
    (_event: Event | React.SyntheticEvent, newValue: number | number[]) => {
      commitSliderValue(setStateValue, newValue);
    },
    [setStateValue],
  );

  const hasLabel = label.trim() !== "";

  return (
    <Box sx={{ width: "100%", px: 1, py: 0.5 }}>
      {hasLabel && (
        <Typography variant="body2" sx={{ mb: 0.5, fontWeight: 500 }}>
          {label}
        </Typography>
      )}
      <MuiSlider
        getAriaLabel={(index) =>
          getSliderAriaLabel(
            hasLabel ? label : "Slider",
            displayedValue,
            index,
          )
        }
        getAriaValueText={getSliderAriaValueText}
        value={displayedValue}
        min={minValue}
        max={maxValue}
        step={step}
        marks={marks}
        valueLabelDisplay={valueLabelDisplay}
        disabled={disabled}
        onChange={handleChange}
        onChangeCommitted={handleCommit}
      />
    </Box>
  );
};

export default SliderComponent;
