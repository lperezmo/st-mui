/**
 * Resolve the `timeSteps` option for a picker's visible minute choices.
 *
 * MUI treats `minutesStep` as validation only, so the digital clock keeps
 * offering its default 5-minute options and a user can select a minute the
 * picker then rejects with a red error. Forwarding the step as `timeSteps`
 * keeps the offered minutes and the accepted minutes in sync.
 *
 * The default step of 1 is left alone: it accepts every minute, so MUI's own
 * default spacing is already valid, and overriding it would replace a
 * 12-entry minute column with a 60-entry one for every caller.
 */
export function resolveTimeSteps(
  minutesStep: number,
): { minutes: number } | undefined {
  return minutesStep > 1 ? { minutes: minutesStep } : undefined;
}
