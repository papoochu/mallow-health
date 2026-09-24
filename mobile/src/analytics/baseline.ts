import {
  DailyHealthRecord,
  MetricKey,
} from "../models/health";

import {
  finiteValues,
  mean,
  sampleStandardDeviation,
} from "./statistics";


export type BaselineLevel =
  | "typical"
  | "watch"
  | "unusual"
  | "neutral";


export type BaselineStatus = {
  label: string;
  level: BaselineLevel;
  zScore: number | null;
};


export function recentMetricValues(
  data: DailyHealthRecord[],
  metric: MetricKey,
  days = 30,
): number[] {
  const recent = data.slice(
    -days
  );

  return finiteValues(
    recent.map(
      (
        record
      ) => record[
        metric
      ]
    )
  );
}


export function latestMetricValue(
  data: DailyHealthRecord[],
  metric: MetricKey,
): number | null {
  for (
    let index = data.length - 1;
    index >= 0;
    index -= 1
  ) {
    const value = data[
      index
    ][
      metric
    ];

    if (
      typeof value === "number"
      && Number.isFinite(
        value
      )
    ) {
      return value;
    }
  }

  return null;
}


export function metricAverage(
  data: DailyHealthRecord[],
  metric: MetricKey,
  days = 30,
): number | null {
  return mean(
    recentMetricValues(
      data,
      metric,
      days,
    )
  );
}


export function metricZScore(
  data: DailyHealthRecord[],
  metric: MetricKey,
  days = 30,
): number | null {
  const values = recentMetricValues(
    data,
    metric,
    days,
  );

  if (
    values.length === 0
  ) {
    return null;
  }

  const latest = values[
    values.length - 1
  ];

  const average = mean(
    values
  );

  if (
    average === null
  ) {
    return null;
  }

  const standardDeviation = sampleStandardDeviation(
    values
  );

  if (
    values.length < 2
    || standardDeviation === null
    || standardDeviation === 0
  ) {
    return 0;
  }

  return (
    (
      latest - average
    )
    / standardDeviation
  );
}


export function getBaselineStatus(
  data: DailyHealthRecord[],
  metric: MetricKey,
  days = 30,
): BaselineStatus {
  const values = recentMetricValues(
    data,
    metric,
    days,
  );

  if (
    values.length === 0
  ) {
    return {
      label: "No data",
      level: "neutral",
      zScore: null,
    };
  }

  if (
    days < 2
  ) {
    return {
      label: "Single-day view",
      level: "neutral",
      zScore: 0,
    };
  }

  const zScore = metricZScore(
    data,
    metric,
    days,
  );

  if (
    zScore === null
  ) {
    return {
      label: "No data",
      level: "neutral",
      zScore: null,
    };
  }

  if (
    Math.abs(
      zScore
    ) < 1
  ) {
    return {
      label: "Near your usual range",
      level: "typical",
      zScore,
    };
  }

  if (
    Math.abs(
      zScore
    ) < 2
  ) {
    const direction = (
      zScore > 0
        ? "above"
        : "below"
    );

    return {
      label: (
        `Somewhat ${direction} your baseline`
      ),
      level: "watch",
      zScore,
    };
  }

  const direction = (
    zScore > 0
      ? "above"
      : "below"
  );

  return {
    label: (
      `Unusually ${direction} your baseline`
    ),
    level: "unusual",
    zScore,
  };
}
