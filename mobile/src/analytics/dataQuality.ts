export type DataSupport =
  | "high"
  | "good"
  | "moderate"
  | "limited";


export function classifyDataSupport(
  sampleCount: number,
  requestedDays: number,
  minimumSamples = 5,
): DataSupport {
  if (
    requestedDays <= 0
  ) {
    return "limited";
  }

  const coverage = (
    sampleCount
    / requestedDays
  );

  if (
    sampleCount < minimumSamples
  ) {
    return "limited";
  }

  if (
    sampleCount >= 30
    && coverage >= 0.80
  ) {
    return "high";
  }

  if (
    sampleCount >= 14
    && coverage >= 0.65
  ) {
    return "good";
  }

  if (
    sampleCount >= 7
    && coverage >= 0.60
  ) {
    return "moderate";
  }

  return "limited";
}
