import {
  DailyHealthRecord,
  MetricKey,
} from "../models/health";

import {
  classifyDataSupport,
  DataSupport,
} from "./dataQuality";

import {
  FRIENDLY_NAMES,
} from "./trends";

import {
  pearsonCorrelation,
} from "./statistics";


export const RELATIONSHIP_METRICS: MetricKey[] = [
  "resting_hr",
  "hrv",
  "systolic_bp",
  "diastolic_bp",
  "glucose",
  "oxygen_saturation",
  "respiratory_rate",
  "wrist_temperature",
  "sleep_hours",
];


export const MIN_CORRELATION_SAMPLES = 5;


export type RelationshipResult = {
  metric: MetricKey;
  metricName: string;
  correlation: number;
  strength: string;
  direction: "positive" | "negative" | "little clear direction";
  sampleCount: number;
  dataSupport: DataSupport;
};


export function getRelationshipData(
  data: DailyHealthRecord[],
  metricA: MetricKey,
  metricB: MetricKey,
  days = 30,
): Array<{
  a: number;
  b: number;
}> {
  const recent = data.slice(
    -days
  );

  const pairs: Array<{
    a: number;
    b: number;
  }> = [];

  for (
    const record of recent
  ) {
    const a = record[
      metricA
    ];

    const b = record[
      metricB
    ];

    if (
      typeof a === "number"
      && Number.isFinite(
        a
      )
      && typeof b === "number"
      && Number.isFinite(
        b
      )
    ) {
      pairs.push(
        {
          a,
          b,
        }
      );
    }
  }

  return pairs;
}


export function calculateCorrelation(
  data: DailyHealthRecord[],
  metricA: MetricKey,
  metricB: MetricKey,
  days = 30,
): number | null {
  const pairs = getRelationshipData(
    data,
    metricA,
    metricB,
    days,
  );

  if (
    pairs.length < MIN_CORRELATION_SAMPLES
  ) {
    return null;
  }

  const a = pairs.map(
    (
      pair
    ) => pair.a
  );

  const b = pairs.map(
    (
      pair
    ) => pair.b
  );

  if (
    new Set(
      a
    ).size < 2
    || new Set(
      b
    ).size < 2
  ) {
    return null;
  }

  return pearsonCorrelation(
    a,
    b,
  );
}


export function describeStrength(
  correlation: number,
): string {
  const value = Math.abs(
    correlation
  );

  if (
    value < 0.2
  ) {
    return "very little relationship";
  }

  if (
    value < 0.4
  ) {
    return "a weak relationship";
  }

  if (
    value < 0.6
  ) {
    return "a moderate relationship";
  }

  if (
    value < 0.8
  ) {
    return "a fairly strong relationship";
  }

  return "a strong relationship";
}


export function relationshipDirection(
  correlation: number,
): RelationshipResult[
  "direction"
] {
  if (
    Math.abs(
      correlation
    ) < 0.2
  ) {
    return "little clear direction";
  }

  return (
    correlation > 0
      ? "positive"
      : "negative"
  );
}


export function describeRelationship(
  data: DailyHealthRecord[],
  metricA: MetricKey,
  metricB: MetricKey,
  days = 30,
): string {
  const correlation = calculateCorrelation(
    data,
    metricA,
    metricB,
    days,
  );

  if (
    correlation === null
  ) {
    return (
      "There isn't enough usable variation in the recent data "
      + "to compare those measurements reliably yet."
    );
  }

  const nameA = FRIENDLY_NAMES[
    metricA
  ].toLowerCase();

  const nameB = FRIENDLY_NAMES[
    metricB
  ].toLowerCase();

  const strength = describeStrength(
    correlation
  );

  let directionText: string;

  if (
    Math.abs(
      correlation
    ) < 0.2
  ) {
    directionText = (
      `I found ${strength} between ${nameA} and ${nameB}`
    );
  } else if (
    correlation > 0
  ) {
    directionText = (
      `I found ${strength}: higher ${nameA} has tended to occur `
      + `alongside higher ${nameB}`
    );
  } else {
    directionText = (
      `I found ${strength}: higher ${nameA} has tended to occur `
      + `alongside lower ${nameB}`
    );
  }

  const pairs = getRelationshipData(
    data,
    metricA,
    metricB,
    days,
  );

  const support = classifyDataSupport(
    pairs.length,
    Math.min(
      days,
      data.length,
    ),
  );

  return (
    `${directionText} over the last ${days} days `
    + `(r = ${correlation.toFixed(2)}). Data support is ${support} `
    + `based on ${pairs.length} paired daily observations. This is an `
    + "association in your data and does not show that one measurement "
    + "caused the other."
  );
}


export function strongestRelationships(
  data: DailyHealthRecord[],
  targetMetric: MetricKey,
  days = 30,
  topN = 3,
): RelationshipResult[] {
  const results: RelationshipResult[] = [];

  for (
    const metric of RELATIONSHIP_METRICS
  ) {
    if (
      metric === targetMetric
    ) {
      continue;
    }

    const pairs = getRelationshipData(
      data,
      targetMetric,
      metric,
      days,
    );

    const correlation = calculateCorrelation(
      data,
      targetMetric,
      metric,
      days,
    );

    if (
      correlation === null
    ) {
      continue;
    }

    results.push(
      {
        metric,
        metricName: FRIENDLY_NAMES[
          metric
        ],
        correlation,
        strength: describeStrength(
          correlation
        ),
        direction: relationshipDirection(
          correlation
        ),
        sampleCount: pairs.length,
        dataSupport: classifyDataSupport(
          pairs.length,
          Math.min(
            days,
            data.length,
          ),
        ),
      }
    );
  }

  return results
    .sort(
      (
        a,
        b,
      ) => (
        Math.abs(
          b.correlation
        )
        - Math.abs(
          a.correlation
        )
      )
    )
    .slice(
      0,
      topN,
    );
}
