import {
  DailyHealthRecord,
  MetricKey,
  ViewWindow,
} from "../models/health";

import {
  latestMetricValue,
  metricAverage,
} from "./baseline";

import {
  describePeriodComparison,
} from "./comparisons";

import {
  describeRelationship,
  strongestRelationships,
} from "./relationships";

import {
  analyzeTrend,
  describeTrend,
  FRIENDLY_NAMES,
  UNITS,
} from "./trends";


const METRIC_ALIASES: Array<{
  phrase: string;
  metric: MetricKey;
}> = [
  {
    phrase: "resting heart rate",
    metric: "resting_hr",
  },
  {
    phrase: "resting hr",
    metric: "resting_hr",
  },
  {
    phrase: "heart rate variability",
    metric: "hrv",
  },
  {
    phrase: "heart-rate variability",
    metric: "hrv",
  },
  {
    phrase: "heart rate",
    metric: "resting_hr",
  },
  {
    phrase: "hrv",
    metric: "hrv",
  },
  {
    phrase: "systolic blood pressure",
    metric: "systolic_bp",
  },
  {
    phrase: "systolic pressure",
    metric: "systolic_bp",
  },
  {
    phrase: "systolic",
    metric: "systolic_bp",
  },
  {
    phrase: "diastolic blood pressure",
    metric: "diastolic_bp",
  },
  {
    phrase: "diastolic pressure",
    metric: "diastolic_bp",
  },
  {
    phrase: "diastolic",
    metric: "diastolic_bp",
  },
  {
    phrase: "blood pressure",
    metric: "systolic_bp",
  },
  {
    phrase: "bp",
    metric: "systolic_bp",
  },
  {
    phrase: "blood sugar",
    metric: "glucose",
  },
  {
    phrase: "glucose",
    metric: "glucose",
  },
  {
    phrase: "oxygen saturation",
    metric: "oxygen_saturation",
  },
  {
    phrase: "blood oxygen",
    metric: "oxygen_saturation",
  },
  {
    phrase: "spo2",
    metric: "oxygen_saturation",
  },
  {
    phrase: "respiratory rate",
    metric: "respiratory_rate",
  },
  {
    phrase: "breathing rate",
    metric: "respiratory_rate",
  },
  {
    phrase: "breathing",
    metric: "respiratory_rate",
  },
  {
    phrase: "wrist temperature",
    metric: "wrist_temperature",
  },
  {
    phrase: "temperature",
    metric: "wrist_temperature",
  },
  {
    phrase: "temp",
    metric: "wrist_temperature",
  },
  {
    phrase: "sleep duration",
    metric: "sleep_hours",
  },
  {
    phrase: "sleep",
    metric: "sleep_hours",
  },
];


const RELATIONSHIP_PHRASES = [
  "related",
  "relationship",
  "correlated",
  "correlation",
  "associated",
  "association",
  "linked",
  "move together",
  "affect",
];


const TREND_PHRASES = [
  "trend",
  "trending",
  "over time",
  "increasing",
  "decreasing",
  "going up",
  "going down",
  "rising",
  "falling",
  "changing",
  "changed",
  "change over",
  "direction",
];


const COMPARISON_PHRASES = [
  "compare",
  "compared",
  "versus",
  "vs",
  "this week",
  "last week",
  "previous week",
];


const AVERAGE_PHRASES = [
  "average",
  "mean",
  "usually",
  "typical value",
];


function extractMetrics(
  question: string,
): MetricKey[] {
  const lowered = question.toLowerCase();

  const ordered = [
    ...METRIC_ALIASES,
  ].sort(
    (
      a,
      b,
    ) => (
      b.phrase.length
      - a.phrase.length
    )
  );

  const matches: Array<{
    index: number;
    end: number;
    metric: MetricKey;
  }> = [];

  for (
    const alias of ordered
  ) {
    let start = 0;

    while (
      start < lowered.length
    ) {
      const index = lowered.indexOf(
        alias.phrase,
        start,
      );

      if (
        index < 0
      ) {
        break;
      }

      const end = (
        index
        + alias.phrase.length
      );

      const overlaps = matches.some(
        (
          match
        ) => (
          index < match.end
          && end > match.index
        )
      );

      if (
        !overlaps
      ) {
        matches.push(
          {
            index,
            end,
            metric: alias.metric,
          }
        );
      }

      start = end;
    }
  }

  return matches
    .sort(
      (
        a,
        b,
      ) => (
        a.index - b.index
      )
    )
    .map(
      (
        match
      ) => match.metric
    )
    .filter(
      (
        metric,
        index,
        values,
      ) => (
        values.indexOf(
          metric
        ) === index
      )
    );
}


function extractRequestedDays(
  question: string,
  defaultDays: number,
): number {
  const lowered = question.toLowerCase();

  const dayMatch = lowered.match(
    /(?:last|past|previous|over|for)?\s*(\d{1,3})\s*days?/
  );

  if (
    dayMatch
  ) {
    const parsed = Number(
      dayMatch[
        1
      ]
    );

    return Math.max(
      5,
      Math.min(
        parsed,
        365,
      ),
    );
  }

  if (
    [
      "three months",
      "3 months",
      "three month",
      "3 month",
      "quarter",
    ].some(
      (
        phrase
      ) => lowered.includes(
        phrase
      )
    )
  ) {
    return 90;
  }

  if (
    [
      "two months",
      "2 months",
      "two month",
      "2 month",
    ].some(
      (
        phrase
      ) => lowered.includes(
        phrase
      )
    )
  ) {
    return 60;
  }

  if (
    [
      "this month",
      "last month",
      "past month",
      "one month",
      "1 month",
      "30 days",
    ].some(
      (
        phrase
      ) => lowered.includes(
        phrase
      )
    )
  ) {
    return 30;
  }

  if (
    [
      "two weeks",
      "2 weeks",
      "two week",
      "2 week",
      "14 days",
    ].some(
      (
        phrase
      ) => lowered.includes(
        phrase
      )
    )
  ) {
    return 14;
  }

  if (
    [
      "this week",
      "last week",
      "past week",
      "one week",
      "1 week",
      "7 days",
    ].some(
      (
        phrase
      ) => lowered.includes(
        phrase
      )
    )
  ) {
    return 7;
  }

  return defaultDays;
}


function formatMetricValue(
  metric: MetricKey,
  value: number,
): string {
  const unit = UNITS[
    metric
  ];

  const decimals = (
    metric === "wrist_temperature"
      ? 2
      : 1
  );

  const number = (
    metric === "wrist_temperature"
      ? (
        value >= 0
          ? `+${value.toFixed(decimals)}`
          : value.toFixed(
              decimals
            )
      )
      : value.toFixed(
          decimals
        )
  );

  return (
    unit
      ? `${number} ${unit}`
      : number
  );
}


function describeMetricSnapshot(
  data: DailyHealthRecord[],
  metric: MetricKey,
  days: number,
): string {
  const latest = latestMetricValue(
    data,
    metric,
  );

  const average = metricAverage(
    data,
    metric,
    days,
  );

  if (
    latest === null
    || average === null
  ) {
    return (
      "I don't have enough recent data for that measurement yet."
    );
  }

  const difference = (
    latest - average
  );

  const comparison = (
    Math.abs(
      difference
    ) < 1e-9
      ? "about the same as"
      : difference > 0
        ? "higher than"
        : "lower than"
  );

  return (
    `Your latest ${FRIENDLY_NAMES[metric].toLowerCase()} is `
    + `${formatMetricValue(metric, latest)}. That is ${comparison} your `
    + `${days}-day personal average of ${formatMetricValue(metric, average)}. `
    + "This is a descriptive comparison, not a clinical interpretation."
  );
}


function describeMetricAverage(
  data: DailyHealthRecord[],
  metric: MetricKey,
  days: number,
): string {
  const average = metricAverage(
    data,
    metric,
    days,
  );

  if (
    average === null
  ) {
    return (
      "I don't have enough recent data for that measurement yet."
    );
  }

  return (
    `Your average ${FRIENDLY_NAMES[metric].toLowerCase()} over the last `
    + `${Math.min(days, data.length)} days is `
    + `${formatMetricValue(metric, average)}.`
  );
}


function describeTopRelationships(
  data: DailyHealthRecord[],
  targetMetric: MetricKey,
  days: number,
): string {
  const relationships = strongestRelationships(
    data,
    targetMetric,
    days,
    3,
  );

  if (
    relationships.length === 0
  ) {
    return (
      "I don't have enough usable data to compare that measurement "
      + "with the others yet."
    );
  }

  const pieces = relationships.map(
    (
      item
    ) => (
      `${item.metricName.toLowerCase()} `
      + `(r = ${item.correlation.toFixed(2)})`
    )
  );

  return (
    `The strongest statistical relationships with `
    + `${FRIENDLY_NAMES[targetMetric].toLowerCase()} over the last `
    + `${days} days are ${pieces.join(", ")}. These are correlations `
    + "in the available data and do not show that one measurement "
    + "caused another."
  );
}


function describeOverallTrends(
  data: DailyHealthRecord[],
  days: number,
): string {
  const metrics: MetricKey[] = [
    "resting_hr",
    "hrv",
    "sleep_hours",
    "glucose",
    "systolic_bp",
    "respiratory_rate",
  ];

  const trends = metrics
    .map(
      (
        metric
      ) => analyzeTrend(
        data,
        metric,
        days,
      )
    )
    .filter(
      (
        trend
      ): trend is NonNullable<
        ReturnType<
          typeof analyzeTrend
        >
      > => (
        trend !== null
        && trend.direction !== "stable"
      )
    )
    .sort(
      (
        a,
        b,
      ) => (
        b.rSquared - a.rSquared
        || Math.abs(
          b.change
        ) - Math.abs(
          a.change
        )
      )
    );

  if (
    trends.length === 0
  ) {
    return (
      `I don't see a clear upward or downward trend among the main `
      + `measurements over the last ${days} days. That does not mean `
      + "every value was unchanged—just that the data do not show a "
      + "consistent direction."
    );
  }

  const pieces = trends
    .slice(
      0,
      3,
    )
    .map(
      (
        trend
      ) => (
        `${trend.name.toLowerCase()} is trending `
        + (
          trend.direction === "up"
            ? "up"
            : "down"
        )
      )
    );

  return (
    `The clearest recent patterns over the last ${days} days are: `
    + `${pieces.join("; ")}. These are descriptive trends in your data `
    + "and are not predictions or medical conclusions."
  );
}


export function askMallow(
  question: string,
  data: DailyHealthRecord[],
  analysisDays: ViewWindow = 30,
): string {
  const clean = question
    .toLowerCase()
    .trim();

  if (
    clean.length === 0
  ) {
    return "Ask me about one of the measurements in your Mallow data.";
  }

  const requestedDays = extractRequestedDays(
    clean,
    analysisDays,
  );

  const days = Math.max(
    1,
    Math.min(
      requestedDays,
      data.length,
    ),
  );

  const metrics = extractMetrics(
    clean
  );

  const isRelationship = RELATIONSHIP_PHRASES.some(
    (
      phrase
    ) => clean.includes(
      phrase
    )
  );

  const isTrend = TREND_PHRASES.some(
    (
      phrase
    ) => clean.includes(
      phrase
    )
  );

  const isComparison = COMPARISON_PHRASES.some(
    (
      phrase
    ) => clean.includes(
      phrase
    )
  );

  const isAverage = AVERAGE_PHRASES.some(
    (
      phrase
    ) => clean.includes(
      phrase
    )
  );

  if (
    isRelationship
    && metrics.length >= 2
  ) {
    return describeRelationship(
      data,
      metrics[
        0
      ],
      metrics[
        1
      ],
      days,
    );
  }

  if (
    isRelationship
    && metrics.length === 1
  ) {
    return describeTopRelationships(
      data,
      metrics[
        0
      ],
      days,
    );
  }

  if (
    isTrend
    && metrics.length >= 1
  ) {
    return describeTrend(
      data,
      metrics[
        0
      ],
      days,
    );
  }

  if (
    isTrend
    && metrics.length === 0
  ) {
    return describeOverallTrends(
      data,
      days,
    );
  }

  if (
    isComparison
    && metrics.length >= 1
  ) {
    return describePeriodComparison(
      data,
      metrics[
        0
      ],
      days,
    );
  }

  if (
    isAverage
    && metrics.length >= 1
  ) {
    return describeMetricAverage(
      data,
      metrics[
        0
      ],
      days,
    );
  }

  if (
    metrics.length >= 1
  ) {
    return describeMetricSnapshot(
      data,
      metrics[
        0
      ],
      days,
    );
  }

  if (
    clean.includes(
      "how am i"
    )
    || clean.includes(
      "summary"
    )
    || clean.includes(
      "overall"
    )
    || clean.includes(
      "overview"
    )
  ) {
    return describeOverallTrends(
      data,
      days,
    );
  }

  return (
    "I can currently answer questions about resting heart rate, HRV, "
    + "blood pressure, glucose, oxygen saturation, respiratory rate, "
    + "wrist temperature, sleep, recent trends, period comparisons, and "
    + "relationships between measurements."
  );
}
