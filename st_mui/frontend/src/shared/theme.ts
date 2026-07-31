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
import { createTheme, Theme } from "@mui/material/styles";

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

function isDarkBackground(bgColor: string): boolean {
  // Parse rgb/rgba or hex
  let r = 0,
    g = 0,
    b = 0;

  const rgbMatch = bgColor.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
  if (rgbMatch) {
    r = parseInt(rgbMatch[1]);
    g = parseInt(rgbMatch[2]);
    b = parseInt(rgbMatch[3]);
  } else if (bgColor.startsWith("#")) {
    const hex = bgColor.replace("#", "");
    const fullHex =
      hex.length === 3
        ? hex
            .split("")
            .map((c) => c + c)
            .join("")
        : hex;
    r = parseInt(fullHex.slice(0, 2), 16);
    g = parseInt(fullHex.slice(2, 4), 16);
    b = parseInt(fullHex.slice(4, 6), 16);
  } else {
    return false;
  }

  // Relative luminance (WCAG)
  const toLinear = (c: number) => {
    const v = c / 255;
    return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
  };
  const lum =
    0.2126 * toLinear(r) + 0.7152 * toLinear(g) + 0.0722 * toLinear(b);
  return lum < 0.5;
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
  const primary = getCSSVar(styles, "--st-primary-color", "#FF4B4B");
  const bgColor = getCSSVar(styles, "--st-background-color", "");
  const isDark = detectDarkMode(styles);

  // Read Streamlit's actual theme values
  const secondaryBg = getCSSVar(
    styles,
    "--st-secondary-background-color",
    isDark ? "#262730" : "#f0f2f6",
  );
  const textColor = getCSSVar(
    styles,
    "--st-text-color",
    isDark ? "#fafafa" : "#262730",
  );
  const grayColor = getCSSVar(styles, "--st-gray-color", "#808495");
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
      borderRadius: parseInt(borderRadius, 10) || 8,
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
            // Popover/dropdown paper should have a solid background
            backgroundColor: isDark ? "#262730" : "#ffffff",
          },
        },
      },
    },
  });

  return cachedTheme;
}
