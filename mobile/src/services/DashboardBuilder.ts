import {
  getBaselineStatus,
  latestMetricValue,
  metricAverage,
  recentMetricValues,
} from "../analytics/baseline";

import {
  describeRelationship,
  getRelationshipData,
} from "../analytics/relationships";

import {
  analyzeTrend,
} from "../analytics/trends";

import {
  DashboardData,
  DailyHealthRecord,
  HealthMetricSnapshot,
  MetricKey,
  MetricTone,
  ViewWindow,
} from "../models/health";


type DashboardBuilderOptions = {
  sourceLabel: string;
  cardSource: string;
  lastUpdatedLabel?: string;
};


function toneFromStatus(
  metric: MetricKey,
  level: ReturnType<
    typeof getBaselineStatus
  >["level"],
): MetricTone {
  if (
    level === "neutral"
  ) {
    return "neutral";
  }

  if (
    metric === "sleep_hours"
    || metric === "deep_sleep_hours"
    || metric === "rem_sleep_hours"
  ) {
    return "pink";
  }

  if (
    level === "watch"
    || level === "unusual"
  ) {
    return "warning";
  }

  return "good";
}


function formatValue(
  metric: MetricKey,
  value: number | null,
): string {
  if (
    value === null
  ) {
    return "No data";
  }

  switch (
    metric
  ) {
    case "resting_hr":
      return `${value.toFixed(0)} bpm`;

    case "hrv":
      return `${value.toFixed(0)} ms`;

    case "systolic_bp":
    case "diastolic_bp":
    case "pulse_pressure":
    case "map":
      return `${value.toFixed(0)} mmHg`;

    case "glucose":
      return `${value.toFixed(0)} mg/dL`;

    case "oxygen_saturation":
      return `${value.toFixed(1)}%`;

    case "respiratory_rate":
      return `${value.toFixed(1)} / min`;

    case "wrist_temperature":
      return (
        value >= 0
          ? `+${value.toFixed(2)} °F`
          : `${value.toFixed(2)} °F`
      );

    case "sleep_hours":
    case "deep_sleep_hours":
    case "rem_sleep_hours":
      return `${value.toFixed(1)} h`;

    default:
      return value.toFixed(
        1
      );
  }
}


function makeMetric(
  data: DailyHealthRecord[],
  metric: MetricKey,
  icon: string,
  title: string,
  windowDays: ViewWindow,
  source: string,
): HealthMetricSnapshot {
  const latest = latestMetricValue(
    data,
    metric,
  );

  const average = metricAverage(
    data,
    metric,
    windowDays,
  );

  const status = getBaselineStatus(
    data,
    metric,
    windowDays,
  );

  return {
    id: metric,
    icon,
    title,
    value: formatValue(
      metric,
      latest,
    ),
    detail: (
      average === null
        ? "No recent baseline data"
        : (
          `${windowDays}-day average: `
          + formatValue(
            metric,
            average,
          )
        )
    ),
    status: status.label,
    tone: toneFromStatus(
      metric,
      status.level,
    ),
    source,
  };
}


export function buildDashboard(
  data: DailyHealthRecord[],
  windowDays: ViewWindow,
  options: DashboardBuilderOptions,
): DashboardData {
  const source = options.cardSource;

  const restingHr = makeMetric(
    data,
    "resting_hr",
    "❤️",
    "Resting heart rate",
    windowDays,
    source,
  );

  const hrv = makeMetric(
    data,
    "hrv",
    "🫀",
    "HRV",
    windowDays,
    source,
  );

  const sleep = makeMetric(
    data,
    "sleep_hours",
    "🌙",
    "Sleep",
    windowDays,
    source,
  );

  const respiratory = makeMetric(
    data,
    "respiratory_rate",
    "🫁",
    "Respiratory rate",
    windowDays,
    source,
  );

  const oxygen = makeMetric(
    data,
    "oxygen_saturation",
    "🫁",
    "Oxygen saturation",
    windowDays,
    source,
  );

  const glucose = makeMetric(
    data,
    "glucose",
    "🍬",
    "Blood glucose",
    windowDays,
    source,
  );

  const deepSleep = makeMetric(
    data,
    "deep_sleep_hours",
    "💤",
    "Deep sleep",
    windowDays,
    source,
  );

  const remSleep = makeMetric(
    data,
    "rem_sleep_hours",
    "✨",
    "REM sleep",
    windowDays,
    source,
  );

  const systolic = latestMetricValue(
    data,
    "systolic_bp",
  );

  const diastolic = latestMetricValue(
    data,
    "diastolic_bp",
  );

  const systolicStatus = getBaselineStatus(
    data,
    "systolic_bp",
    windowDays,
  );

  const bloodPressure: HealthMetricSnapshot = {
    id: "blood_pressure",
    icon: "🩸",
    title: "Blood pressure",
    value: (
      systolic === null
      || diastolic === null
        ? "No data"
        : (
          `${systolic.toFixed(0)} / `
          + `${diastolic.toFixed(0)} mmHg`
        )
    ),
    detail: "Compared with your recent personal baseline",
    status: (
      systolic === null
      || diastolic === null
        ? "No data"
        : systolicStatus.label
    ),
    tone: (
      systolic === null
      || diastolic === null
        ? "neutral"
        : toneFromStatus(
          "systolic_bp",
          systolicStatus.level,
        )
    ),
    source,
  };

  const hrvTrend = analyzeTrend(
    data,
    "hrv",
    windowDays,
  );

  const sleepTrend = analyzeTrend(
    data,
    "sleep_hours",
    windowDays,
  );

  const hrvPoints = recentMetricValues(
    data,
    "hrv",
    windowDays,
  ).slice(
    -12
  );

  const sleepPoints = recentMetricValues(
    data,
    "sleep_hours",
    windowDays,
  ).slice(
    -12
  );

  const pairedSleepHrv = getRelationshipData(
    data,
    "sleep_hours",
    "hrv",
    windowDays,
  );

  const relationshipText = describeRelationship(
    data,
    "sleep_hours",
    "hrv",
    windowDays,
  );

  const hrvTitle = (
    hrvTrend === null
      ? "Not enough HRV data for a recent trend yet."
      : hrvTrend.direction === "up"
        ? "Your HRV has been trending upward."
        : hrvTrend.direction === "down"
          ? "Your HRV has been trending downward."
          : "Your HRV does not show a clear recent trend."
  );

  const sleepTitle = (
    sleepTrend === null
      ? "Not enough sleep data for a recent trend yet."
      : sleepTrend.direction === "up"
        ? "Your sleep duration has been trending upward."
        : sleepTrend.direction === "down"
          ? "Your sleep duration has been trending downward."
          : "Your sleep duration has been fairly steady."
  );

  const relationshipSupport = (
    pairedSleepHrv.length >= 30
      ? "High data support"
      : pairedSleepHrv.length >= 14
        ? "Good data support"
        : pairedSleepHrv.length >= 7
          ? "Moderate data support"
          : "Limited data support"
  );

  return {
    sourceLabel: options.sourceLabel,
    lastUpdatedLabel:
      options.lastUpdatedLabel ?? "Calculated locally",

    overviewMetrics: [
      restingHr,
      hrv,
      sleep,
      respiratory,
    ],

    healthMetrics: [
      restingHr,
      hrv,
      bloodPressure,
      glucose,
      oxygen,
    ],

    sleepMetrics: [
      sleep,
      deepSleep,
      remSleep,
      respiratory,
    ],

    hrvTrend: {
      id: "hrv_trend",
      title: "HRV trend",
      value: formatValue(
        "hrv",
        latestMetricValue(
          data,
          "hrv",
        ),
      ),
      caption: `${windowDays}-day view`,
      trendLabel: (
        hrvTrend === null
          ? "Not enough data"
          : (
            hrvTrend.direction === "up"
              ? `↗ ${hrvTrend.label}`
              : hrvTrend.direction === "down"
                ? `↘ ${hrvTrend.label}`
                : `→ ${hrvTrend.label}`
          )
      ),
      points: hrvPoints,
    },

    sleepTrend: {
      id: "sleep_trend",
      title: "Recent sleep pattern",
      value: formatValue(
        "sleep_hours",
        latestMetricValue(
          data,
          "sleep_hours",
        ),
      ),
      caption: `${windowDays}-day view`,
      trendLabel: (
        sleepTrend === null
          ? "Not enough data"
          : (
            sleepTrend.direction === "up"
              ? `↗ ${sleepTrend.label}`
              : sleepTrend.direction === "down"
                ? `↘ ${sleepTrend.label}`
                : `→ ${sleepTrend.label}`
          )
      ),
      points: sleepPoints,
    },

    overviewInsight: {
      id: "overview_insight",
      title: hrvTitle,
      body: relationshipText,
      support: relationshipSupport,
    },

    sleepInsight: {
      id: "sleep_insight",
      title: sleepTitle,
      body: (
        sleepTrend === null
          ? (
            "Mallow needs at least five usable recent sleep values "
            + "before estimating a descriptive trend."
          )
          : (
            `Across the selected window, the fitted sleep trend changed `
            + `by ${sleepTrend.change >= 0 ? "+" : ""}`
            + `${sleepTrend.change.toFixed(1)} hours. Data support is `
            + `${sleepTrend.dataSupport}. This describes the recent `
            + "pattern only and is not a prediction."
          )
      ),
      support: (
        sleepTrend === null
          ? "Limited data support"
          : (
            `${sleepTrend.dataSupport.charAt(0).toUpperCase()}`
            + `${sleepTrend.dataSupport.slice(1)} data support`
          )
      ),
    },
  };
}
