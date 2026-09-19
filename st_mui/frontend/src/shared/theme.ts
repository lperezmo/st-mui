/**
 * Shared theme bridge: Streamlit CSS custom properties → MUI theme.
 *
 * Streamlit v2 (1.55+) exposes a rich set of --st-* CSS custom properties.
 * We read these at render time and build a matching MUI theme.
 *
 * The properties are declared on a generated class on each element container,
 * not on :root, so they resolve only inside the app subtree. Reading them from
 * document.documentElement yields empty strings and silently falls back to
 * Streamlit's stock palette, which is why every caller must pass the host
 * element the component renders into.
 */
import { createTheme, type Theme } from "@mui/material/styles";

function readVars(host?: Element | null): CSSStyleDeclaration {
  return getComputedStyle(host ?? document.documentElement);
}

function getCSSVar(
  styles: CSSStyleDeclaration,
  name: string,
  fallback: string,
): string {
  const val = styles.getPropertyValue(name).trim();
  return val || fallback;
}

function parseHexColor(hex: string): [number, number, number] | null {
  const clean = hex.replace("#", "").trim();
  const full =
    clean.length === 3 || clean.length === 4
      ? clean
          .slice(0, 3)
          .split("")
          .map((c) => c + c)
          .join("")
      : clean.slice(0, 6);
  if (!/^[0-9a-fA-F]{6}$/.test(full)) return null;
  const r = parseInt(full.slice(0, 2), 16);
  const g = parseInt(full.slice(2, 4), 16);
  const b = parseInt(full.slice(4, 6), 16);
  if ([r, g, b].some((v) => Number.isNaN(v))) return null;
  return [r, g, b];
}

function parseRgbColor(color: string): [number, number, number] | null {
  // Handles comma syntax rgb(1, 2, 3) / rgba(1, 2, 3, 0.5) and space syntax
  // rgb(1 2 3) / rgb(1 2 3 / 50%) used by newer Streamlit themes.
  const match = color.match(/rgba?\(([^)]+)\)/i);
  if (!match) return null;
  const parts = match[1].split("/")[0].trim().split(/[\s,]+/).filter(Boolean);
  if (parts.length < 3) return null;
  const nums = parts.slice(0, 3).map((p) => {
    if (p.endsWith("%")) {
      const pct = parseFloat(p);
      if (!Number.isFinite(pct)) return NaN;
      return Math.round((pct / 100) * 255);
    }
    return parseFloat(p);
  });
  if (nums.some((v) => !Number.isFinite(v))) return null;
  return [nums[0], nums[1], nums[2]] as [number, number, number];
}

function hslToRgb(h: number, s: number, l: number): [number, number, number] {
  const hue = (((h % 360) + 360) % 360) / 360;
  const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
  const p = 2 * l - q;
  const channel = (t: number) => {
    let tc = t;
    if (tc < 0) tc += 1;
    if (tc > 1) tc -= 1;
    if (tc < 1 / 6) return p + (q - p) * 6 * tc;
    if (tc < 1 / 2) return q;
    if (tc < 2 / 3) return p + (q - p) * (2 / 3 - tc) * 6;
    return p;
  };
  return [
    Math.round(channel(hue + 1 / 3) * 255),
    Math.round(channel(hue) * 255),
    Math.round(channel(hue - 1 / 3) * 255),
  ];
}

function parseHslColor(color: string): [number, number, number] | null {
  const match = color.match(/hsla?\(([^)]+)\)/i);
  if (!match) return null;
  const parts = match[1].split("/")[0].trim().split(/[\s,]+/).filter(Boolean);
  if (parts.length < 3) return null;
  const h = parseFloat(parts[0]);
  const s = parseFloat(parts[1].replace("%", "")) / 100;
  const l = parseFloat(parts[2].replace("%", "")) / 100;
  if (![h, s, l].every(Number.isFinite)) return null;
  if (s < 0 || s > 1 || l < 0 || l > 1) return null;
  return hslToRgb(h, s, l);
}

export function parseCssColorToRgb(
  color: string,
): [number, number, number] | null {
  const trimmed = color.trim().toLowerCase();
  if (!trimmed || trimmed === "transparent") return null;
  if (trimmed.startsWith("#")) return parseHexColor(trimmed);
  if (trimmed.startsWith("rgb")) return parseRgbColor(trimmed);
  if (trimmed.startsWith("hsl")) return parseHslColor(trimmed);
  // Named colors, oklch(), color-mix(), etc: resolve via the browser when
  // available so custom Streamlit themes still detect dark mode correctly.
  try {
    if (typeof document !== "undefined" && typeof getComputedStyle !== "undefined") {
      const el = document.createElement("div");
      el.style.color = color;
      // Invalid assignments are dropped silently; empty means unparsable.
      if (!el.style.color) return null;
      document.body?.appendChild(el);
      try {
        const computed = getComputedStyle(el).color;
        if (computed && computed !== el.style.color) {
          const viaComputed =
            parseRgbColor(computed) ?? parseHslColor(computed);
          if (viaComputed) return viaComputed;
        }
      } finally {
        el.remove();
      }
    }
  } catch {
    return null;
  }
  return null;
}

export function isDarkBackground(bgColor: string): boolean {
  const rgb = parseCssColorToRgb(bgColor);
  if (!rgb) return false;
  const [r, g, b] = rgb;
  // Relative luminance (WCAG)
  const toLinear = (c: number) => {
    const v = c / 255;
    return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
  };
  const lum =
    0.2126 * toLinear(r) + 0.7152 * toLinear(g) + 0.0722 * toLinear(b);
  return lum < 0.5;
}

export function parseBorderRadius(value: string, fallback = 8): number {
  // getComputedStyle resolves rem/em to px, so parseFloat suffices. parseInt
  // truncates "0.5rem" to 0 and silently falls back; keep fractional radii.
  const parsed = parseFloat(value);
  if (!Number.isFinite(parsed) || parsed < 0) return fallback;
  return parsed;
}

function isValidCssColor(value: string): boolean {
  if (!value.trim()) return false;
  try {
    if (typeof CSS !== "undefined" && typeof CSS.supports === "function") {
      return CSS.supports("color", value);
    }
  } catch {
    return false;
  }
  // Without CSS.supports (jsdom/happy-dom), accept anything our parser or the
  // browser can resolve; otherwise fall back to the stock palette.
  return (
    parseCssColorToRgb(value) !== null || value.startsWith("var(")
  );
}

function validCssColorOr(value: string, fallback: string): string {
  return isValidCssColor(value) ? value : fallback;
}

function detectDarkMode(styles: CSSStyleDeclaration): boolean {
  const bgVar = getCSSVar(styles, "--st-background-color", "");
  if (bgVar) return isDarkBackground(bgVar);

  // Fallback: read computed body background
  const bgComputed = getComputedStyle(document.body).backgroundColor;
  if (bgComputed && bgComputed !== "rgba(0, 0, 0, 0)") {
    return isDarkBackground(bgComputed);
  }

  return window.matchMedia("(prefers-color-scheme: dark)").matches;
}

let cachedTheme: Theme | null = null;
let lastKey = "";

/**
 * Creates (or returns cached) MUI theme from Streamlit CSS vars.
 *
 * ``host`` must be an element inside the app subtree, normally the element the
 * component renders into. The custom properties are inherited, so any
 * descendant resolves them; the document root does not.
 */
export function getStreamlitMuiTheme(host?: Element | null): Theme {
  const styles = readVars(host);
  const rawPrimary = getCSSVar(styles, "--st-primary-color", "#FF4B4B");
  const primary = validCssColorOr(rawPrimary, "#FF4B4B");
  const bgColor = getCSSVar(styles, "--st-background-color", "");
  const isDark = detectDarkMode(styles);

  // Read Streamlit's actual theme values
  const rawSecondaryBg = getCSSVar(
    styles,
    "--st-secondary-background-color",
    isDark ? "#262730" : "#f0f2f6",
  );
  const secondaryBg = validCssColorOr(
    rawSecondaryBg,
    isDark ? "#262730" : "#f0f2f6",
  );
  const rawTextColor = getCSSVar(
    styles,
    "--st-text-color",
    isDark ? "#fafafa" : "#262730",
  );
  const textColor = validCssColorOr(
    rawTextColor,
    isDark ? "#fafafa" : "#262730",
  );
  const rawGray = getCSSVar(styles, "--st-gray-color", "#808495");
  const grayColor = validCssColorOr(rawGray, "#808495");
  const font = getCSSVar(
    styles,
    "--st-font",
    '"Source Sans Pro", "Source Sans 3", system-ui, -apple-system, sans-serif',
  );
  const borderRadius = getCSSVar(styles, "--st-base-radius", "8px");
  const background = bgColor || (isDark ? "#0e1117" : "#ffffff");

  // Key the cache on every value the theme is built from. Keying on a subset
  // returns a stale theme when only one of the others changes.
  const key = [
    primary,
    bgColor,
    String(isDark),
    secondaryBg,
    textColor,
    grayColor,
    font,
    borderRadius,
  ].join("|");
  if (cachedTheme && key === lastKey) {
    return cachedTheme;
  }
  lastKey = key;

  cachedTheme = createTheme({
    palette: {
      mode: isDark ? "dark" : "light",
      primary: { main: primary },
      secondary: { main: grayColor },
      background: {
        // DataGrid derives CSS variables by decomposing this color. The CSS
        // keyword "transparent" is not a decomposable MUI color and crashes
        // the production grid bundle, so keep the theme color concrete while
        // ScopedCssBaseline remains visually transparent below.
        default: background,
        paper: secondaryBg,
      },
      text: {
        primary: textColor,
        secondary: grayColor,
      },
    },
    typography: {
      fontFamily: font,
      fontSize: 14,
    },
    shape: {
      borderRadius: parseBorderRadius(borderRadius, 8),
    },
    components: {
      MuiScopedCssBaseline: {
        styleOverrides: {
          root: {
            backgroundColor: "transparent",
            color: textColor,
          },
        },
      },
      MuiTextField: {
        defaultProps: {
          variant: "outlined",
        },
      },
      MuiOutlinedInput: {
        styleOverrides: {
          root: {
            backgroundColor: "transparent",
          },
        },
      },
      MuiInputLabel: {
        styleOverrides: {
          root: {
            color: grayColor,
          },
        },
      },
      MuiPaper: {
        styleOverrides: {
          root: {
            // Popover/dropdown paper should have a solid background that
            // follows the app theme instead of a hardcoded palette.
            backgroundColor: secondaryBg,
          },
        },
      },
    },
  });

  return cachedTheme;
}
