import { useId } from "react";

export function createPickerId(prefix: string): string {
  const cryptoObj = (
    globalThis as unknown as {
      crypto?: { randomUUID?: () => string };
    }
  ).crypto;
  const randomPart =
    cryptoObj?.randomUUID?.call(cryptoObj) ??
    `${Date.now().toString(36)}-${Math.random().toString(36).slice(2)}`;
  return `st-mui-${prefix}-${randomPart}`;
}

/**
 * Stable, StrictMode-safe element id. Unlike a useMemo(createPickerId())
 * value, React's useId is stable across StrictMode remounts, so
 * aria-describedby / label associations don't break in dev.
 */
export function usePickerId(prefix: string): string {
  const reactId = useId().replace(/[^a-zA-Z0-9-_]/g, "");
  return `st-mui-${prefix}-${reactId}`;
}
