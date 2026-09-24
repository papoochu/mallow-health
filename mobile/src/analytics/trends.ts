import {
  DailyHealthRecord,
  MetricKey,
} from "../models/health";

import {
  classifyDataSupport,
  DataSupport,
} from "./dataQuality";

import {
  recentMetricValues,
} from "./baseline";

import {
  linearRegression,
  mean,
  sampleStandardDeviation,
} from "./statistics";


export const FRIENDLY_NAMES: Record<
  MetricKey,
  string
> = {
  resting_hr: "Resting heart rate",
  hrv: "HRV",
  systolic_bp: "Systolic blood pressure",
  diastolic_bp: "Diastolic blood pressure",
  glucose: "Blood glucose",
  oxygen_saturation: "Oxygen saturation",
  respiratory_rate: "Respiratory rate",
  wrist_temperature: "Wrist temperature",
  sleep_hours: "Sleep duration",
  deep_sleep_hours: "Deep sleep",
  rem_sleep_hours: "REM sleep",
  pulse_pressure: "Pulse pressure",
  map: "Mean arterial pressure",
};


export const UNITS: Record<
  MetricKey,
  string
> = {
  resting_hr: "bpm",
  hrv: "ms",
  systolic_bp: "mmHg",
  diastolic_bp: "mmHg",
  glucose: "mg/dL",
  oxygen_saturation: "%",
  respiratory_rate: "breaths/min",
  wrist_temperature: "°F",
  sleep_hours: "h",
  deep_sleep_hours: "h",
  rem_sleep_hours: "h",
  pulse_pressure: "mmHg",
  map: "mmHg",
};


export type TrendDirection =
  | "up"
  | "down"
  | "stable";


export type TrendResult = {
  metric: MetricKey;
  name: string;
  unit: string;
  days: number;
  sampleCount: number;
  dataSupport: DataSupport;
  direction: TrendDirection;
  label: string;
  strength: "minimal" | "gradual" | "clear";
  consistency: "low" | "moderate" | "high";
  change: number;
  slopePerDay: number;
  rSquared: number;
  latest: number;
  average: number;
};


export const MIN_TREND_SAMPLES = 5;


export function analyzeTrend(
  data: DailyHealthRecord[],
  metric: MetricKey,
  days = 30,
): TrendResult | null {
  const values = recentMetricValues(
    data,
    metric,
    days,
  );

  if (
    values.length < MIN_TREND_SAMPLES
  ) {
    return null;
  }

  const spread = sampleStandardDeviation(
    values
  );

  const average = mean(
    values
  );

  if (
    average === null
  ) {
    return null;
  }

  const support = classifyDataSupport(
    values.length,
    Math.min(
      days,
      data.length,
    ),
  );

  if (
    spread === null
    || spread < 1e-9
  ) {
    return {
      metric,
      name: FRIENDLY_NAMES[
        metric
      ],
      unit: UNITS[
        metric
      ],
      days,
      sampleCount: values.length,
      dataSupport: support,
      direction: "stable",
      label: "No clear trend",
      strength: "minimal",
      consistency: "high",
      change: 0,
      slopePerDay: 0,
      rSquared: 0,
      latest: values[
        values.length - 1
      ],
      average,
    };
  }

  const regression = linearRegression(
    values
  );

  if (
    regression === null
  ) {
    return null;
  }

  const normalizedChange = (
    Math.abs(
      regression.change
    )
    / spread
  );

  let direction: TrendDirection;
  let label: string;
  let strength: TrendResult[
    "strength"
  ];

  if (
    normalizedChange < 0.35
    || regression.rSquared < 0.15
  ) {
    direction = "stable";
    label = "No clear trend";
    strength = "minimal";
  } else if (
    regression.change > 0
  ) {
    direction = "up";

    if (
      normalizedChange >= 1
      && regression.rSquared >= 0.50
    ) {
      label = "Clearly increasing";
      strength = "clear";
    } else {
      label = "Gradually increasing";
      strength = "gradual";
    }
  } else {
    direction = "down";

    if (
      normalizedChange >= 1
      && regression.rSquared >= 0.50
    ) {
      label = "Clearly decreasing";
      strength = "clear";
    } else {
      label = "Gradually decreasing";
      strength = "gradual";
    }
  }

  let consistency: TrendResult[
    "consistency"
  ];

  if (
    regression.rSquared >= 0.60
  ) {
    consistency = "high";
  } else if (
    regression.rSquared >= 0.30
  ) {
    consistency = "moderate";
  } else {
    consistency = "low";
  }

  return {
    metric,
    name: FRIENDLY_NAMES[
      metric
    ],
    unit: UNITS[
      metric
    ],
    days,
    sampleCount: values.length,
    dataSupport: support,
    direction,
    label,
    strength,
    consistency,
    change: regression.change,
    slopePerDay: regression.slope,
    rSquared: regression.rSquared,
    latest: values[
      values.length - 1
    ],
    average,
  };
}


export function formatTrendChange(
  trend: TrendResult | null,
): string {
  if (
    trend === null
  ) {
    return "Not enough data";
  }

  const value = (
    Math.abs(
      trend.change
    ) < 0.05
      ? "0.0"
      : Math.abs(
          trend.change
        ) < 10
        ? (
          trend.change >= 0
            ? `+${trend.change.toFixed(1)}`
            : trend.change.toFixed(1)
        )
        : (
          trend.change >= 0
            ? `+${trend.change.toFixed(0)}`
            : trend.change.toFixed(0)
        )
  );

  return (
    trend.unit
      ? (
        `${value} ${trend.unit} across `
        + `${trend.sampleCount} days`
      )
      : (
        `${value} across `
        + `${trend.sampleCount} days`
      )
  );
}


export function describeTrend(
  data: DailyHealthRecord[],
  metric: MetricKey,
  days = 30,
): string {
  const trend = analyzeTrend(
    data,
    metric,
    days,
  );

  if (
    trend === null
  ) {
    return (
      "There is not enough recent data to estimate "
      + "a trend for this measurement yet."
    );
  }

  if (
    trend.direction === "stable"
  ) {
    return (
      `${trend.name} does not show a clear upward or downward trend `
      + `over the last ${days} days. Data support for this estimate `
      + `is ${trend.dataSupport}.`
    );
  }

  const directionWord = (
    trend.direction === "up"
      ? "increased"
      : "decreased"
  );

  return (
    `${trend.name} has ${directionWord} overall across the last `
    + `${days} days. The fitted trend changes by about `
    + `${formatTrendChange(trend)}. Data support for this estimate `
    + `is ${trend.dataSupport}. This describes the recent pattern `
    + "only and is not a prediction."
  );
}
