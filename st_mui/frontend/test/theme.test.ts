import { afterEach, describe, expect, it, vi } from "vitest";
import { getStreamlitMuiTheme } from "../src/shared/theme";

/**
 * Streamlit declares its --st-* custom properties on a generated class on the
 * element container, so they resolve only inside the app subtree. These stubs
 * reproduce that: the document root sees nothing, the host element sees the
 * app's configured values.
 */
function stubScopedTheme(
  hostVars: Record<string, string>,
  hostBackground = "rgb(255, 255, 255)",
) {
  const host = { __host: true } as unknown as Element;
  const documentElement = { __root: true };

  vi.stubGlobal("document", { documentElement, body: {} });
  vi.stubGlobal("getComputedStyle", (el: unknown) => {
    const scoped = el === host;
    return {
      backgroundColor: scoped ? hostBackground : "rgba(0, 0, 0, 0)",
      getPropertyValue: (name: string) =>
        scoped ? (hostVars[name] ?? "") : "",
    };
  });
  vi.stubGlobal("window", { matchMedia: () => ({ matches: false }) });

  return host;
}

describe("Streamlit MUI theme", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("uses a concrete background color that DataGrid can decompose", () => {
    const host = stubScopedTheme(
      {
        "--st-background-color": "#123456",
        "--st-primary-color": "#ff4b4b",
        "--st-secondary-background-color": "#f0f2f6",
        "--st-text-color": "#fafafa",
        "--st-gray-color": "#808495",
        "--st-base-radius": "8px",
      },
      "rgb(18, 52, 86)",
    );

    const theme = getStreamlitMuiTheme(host);

    expect(theme.palette.background.default).toBe("#123456");
    expect(theme.palette.background.default).not.toBe("transparent");
  });

  it("reads the app's configured palette from the host element", () => {
    const host = stubScopedTheme({
      "--st-primary-color": "#6366f1",
      "--st-background-color": "#ffffff",
      "--st-secondary-background-color": "#f8fafc",
      "--st-text-color": "#0f172a",
      "--st-gray-color": "#64748b",
      "--st-base-radius": "8px",
    });

    const theme = getStreamlitMuiTheme(host);

    // Reading the document root instead would silently yield Streamlit's
    // stock red, which is the bug this guards.
    expect(theme.palette.primary.main).toBe("#6366f1");
    expect(theme.palette.primary.main).not.toBe("#FF4B4B");
    expect(theme.palette.text.primary).toBe("#0f172a");
    expect(theme.palette.background.paper).toBe("#f8fafc");
  });

  it("falls back to the stock palette when no host is given", () => {
    stubScopedTheme({ "--st-primary-color": "#6366f1" });

    const theme = getStreamlitMuiTheme();

    expect(theme.palette.primary.main).toBe("#FF4B4B");
  });

  it("does not serve a stale cached theme when only the text color changes", () => {
    const base = {
      "--st-primary-color": "#6366f1",
      "--st-background-color": "#ffffff",
      "--st-secondary-background-color": "#f8fafc",
      "--st-gray-color": "#64748b",
      "--st-base-radius": "8px",
    };

    const first = getStreamlitMuiTheme(
      stubScopedTheme({ ...base, "--st-text-color": "#0f172a" }),
    );
    expect(first.palette.text.primary).toBe("#0f172a");

    vi.unstubAllGlobals();
    const second = getStreamlitMuiTheme(
      stubScopedTheme({ ...base, "--st-text-color": "#334155" }),
    );
    expect(second.palette.text.primary).toBe("#334155");
  });

  it("detects dark mode from the host background", () => {
    const host = stubScopedTheme({
      "--st-primary-color": "#818cf8",
      "--st-background-color": "#0f172a",
      "--st-text-color": "#f1f5f9",
    });

    const theme = getStreamlitMuiTheme(host);

    expect(theme.palette.mode).toBe("dark");
    expect(theme.palette.primary.main).toBe("#818cf8");
  });
});
