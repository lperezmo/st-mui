import { afterEach, describe, expect, it, vi } from "vitest";
import { getStreamlitMuiTheme } from "../src/shared/theme";

describe("Streamlit MUI theme", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("uses a concrete background color that DataGrid can decompose", () => {
    const cssVariables: Record<string, string> = {
      "--st-background-color": "#123456",
      "--st-primary-color": "#ff4b4b",
      "--st-secondary-background-color": "#f0f2f6",
      "--st-text-color": "#fafafa",
      "--st-gray-color": "#808495",
      "--st-base-radius": "8px",
    };

    vi.stubGlobal("document", {
      documentElement: {},
      body: {},
    });
    vi.stubGlobal("getComputedStyle", () => ({
      backgroundColor: "rgb(18, 52, 86)",
      getPropertyValue: (name: string) => cssVariables[name] ?? "",
    }));
    vi.stubGlobal("window", {
      matchMedia: () => ({ matches: false }),
    });

    const theme = getStreamlitMuiTheme();

    expect(theme.palette.background.default).toBe("#123456");
    expect(theme.palette.background.default).not.toBe("transparent");
  });
});
