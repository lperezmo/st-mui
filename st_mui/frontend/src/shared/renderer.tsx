/**
 * Shared renderer utilities for creating v2 component renderers with React.
 *
 * With isolate_styles=False, the component renders directly in the DOM (no
 * Shadow DOM). Emotion styles inject into document.head and MUI popovers
 * portal to document.body — both work correctly in this mode.
 */
import {
  FrontendRenderer,
  FrontendRendererArgs,
} from "@streamlit/component-v2-lib";
import { StrictMode, FC } from "react";
import { createRoot, Root } from "react-dom/client";
import { ThemeProvider } from "@mui/material/styles";
import ScopedCssBaseline from "@mui/material/ScopedCssBaseline";
import { CacheProvider } from "@emotion/react";
import createCache, { EmotionCache } from "@emotion/cache";
import { getStreamlitMuiTheme } from "./theme";

const reactRoots: WeakMap<FrontendRendererArgs["parentElement"], Root> =
  new WeakMap();

const emotionCaches: WeakMap<
  FrontendRendererArgs["parentElement"],
  EmotionCache
> = new WeakMap();

/**
 * Creates a FrontendRenderer that wraps a React component with MUI ThemeProvider.
 * Handles root management, Emotion cache scoping, theme injection, and cleanup.
 */
export function createMuiRenderer<
  TState extends Record<string, unknown>,
  TData extends Record<string, unknown>,
>(
  Component: FC<{
    data: TData;
    setStateValue: FrontendRendererArgs<TState, TData>["setStateValue"];
  }>
): FrontendRenderer<TState, TData> {
  return (args) => {
    const { data, parentElement, setStateValue } = args;

    const rootElement = parentElement.querySelector(".react-root");
    if (!rootElement) {
      throw new Error("React root element (.react-root) not found");
    }

    let reactRoot = reactRoots.get(parentElement);
    if (!reactRoot) {
      reactRoot = createRoot(rootElement);
      reactRoots.set(parentElement, reactRoot);
    }

    // Emotion cache scoped with a unique key so MUI class names
    // don't collide with Streamlit's own styles.
    let emotionCache = emotionCaches.get(parentElement);
    if (!emotionCache) {
      emotionCache = createCache({
        key: "st-mui",
        prepend: true,
      });
      emotionCaches.set(parentElement, emotionCache);
    }

    const theme = getStreamlitMuiTheme();

    reactRoot.render(
      <StrictMode>
        <CacheProvider value={emotionCache}>
          <ThemeProvider theme={theme}>
            <ScopedCssBaseline enableColorScheme>
              <Component data={data} setStateValue={setStateValue} />
            </ScopedCssBaseline>
          </ThemeProvider>
        </CacheProvider>
      </StrictMode>
    );

    return () => {
      const root = reactRoots.get(parentElement);
      if (root) {
        root.unmount();
        reactRoots.delete(parentElement);
      }
      emotionCaches.delete(parentElement);
    };
  };
}
