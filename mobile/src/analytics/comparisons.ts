import {
  DailyHealthRecord,
  MetricKey,
} from "../models/health";

import {
  finiteValues,
  mean,
} from "./statistics";

import {
  FRIENDLY_NAMES,
  UNITS,
} from "./trends";


export type PeriodComparison = {
  metric: MetricKey;
  name: string;
  unit: string;
  decimals: number;
  days: number;
  currentAverage: number;
  previousAverage: number;
  difference: number;
  absoluteDifference: number;
  percentChange: number | null;
  direction: "higher" | "lower" | "about the same";
  arrow: "↑" | "↓" | "→";
  currentCount: number;
  previousCount: number;
};


const DECIMALS: Partial<
  Record<
    MetricKey,
    number
  >
> = {
  wrist_temperature: 2,
};


export function comparePeriods(
  data: DailyHealthRecord[],
  metric: MetricKey,
  days = 7,
): PeriodComparison | null {
  if (
    days < 1
    || data.length < days * 2
  ) {
    return null;
  }

  const current = data.slice(
    -days
  );

  const previous = data.slice(
    -days * 2,
    -days,
  );

  const currentValues = finiteValues(
    current.map(
      (
        record
      ) => record[
        metric
      ]
    )
  );

  const previousValues = finiteValues(
    previous.map(
      (
        record
      ) => record[
        metric
      ]
    )
  );

  if (
    currentValues.length === 0
    || previousValues.length === 0
  ) {
    return null;
  }

  const currentAverage = mean(
    currentValues
  );

  const previousAverage = mean(
    previousValues
  );

  if (
    currentAverage === null
    || previousAverage === null
  ) {
    return null;
  }

  const difference = (
    currentAverage
    - previousAverage
  );

  const percentChange = (
    previousAverage === 0
      ? null
      : (
        difference
        / Math.abs(
          previousAverage
        )
        * 100
      )
  );

  let direction: PeriodComparison[
    "direction"
  ];

  let arrow: PeriodComparison[
    "arrow"
  ];

  if (
    difference > 0
  ) {
    direction = "higher";
    arrow = "↑";
  } else if (
    difference < 0
  ) {
    direction = "lower";
    arrow = "↓";
  } else {
    direction = "about the same";
    arrow = "→";
  }

  return {
    metric,
    name: FRIENDLY_NAMES[
      metric
    ],
    unit: UNITS[
      metric
    ],
    decimals: DECIMALS[
      metric
    ] ?? 1,
    days,
    currentAverage,
    previousAverage,
    difference,
    absoluteDifference: Math.abs(
      difference
    ),
    percentChange,
    direction,
    arrow,
    currentCount: currentValues.length,
    previousCount: previousValues.length,
  };
}


function formatAverage(
  comparison: PeriodComparison,
  value: number,
): string {
  const signed = (
    comparison.metric === "wrist_temperature"
  );

  const number = (
    signed
      ? (
        value >= 0
          ? `+${value.toFixed(comparison.decimals)}`
          : value.toFixed(
              comparison.decimals
            )
      )
      : value.toFixed(
          comparison.decimals
        )
  );

  return (
    comparison.unit
      ? `${number} ${comparison.unit}`
      : number
  );
}


function formatDifference(
  comparison: PeriodComparison,
): string {
  const value = (
    Math.abs(
      comparison.difference
    ) < 1e-12
      ? 0
      : comparison.difference
  );

  const number = (
    value > 0
      ? `+${value.toFixed(comparison.decimals)}`
      : value.toFixed(
          comparison.decimals
        )
  );

  return (
    comparison.unit
      ? `${number} ${comparison.unit}`
      : number
  );
}


export function describePeriodComparison(
  data: DailyHealthRecord[],
  metric: MetricKey,
  days = 7,
): string {
  const comparison = comparePeriods(
    data,
    metric,
    days,
  );

  if (
    comparison === null
  ) {
    return (
      "There isn't enough history to compare those two periods yet."
    );
  }

  const currentText = formatAverage(
    comparison,
    comparison.currentAverage,
  );

  const previousText = formatAverage(
    comparison,
    comparison.previousAverage,
  );

  let changeText: string;

  if (
    Math.abs(
      comparison.difference
    ) < 1e-12
  ) {
    changeText = (
      "The two period averages are essentially unchanged."
    );
  } else {
    const percentText = (
      comparison.percentChange === null
        ? ""
        : (
          ` (${Math.abs(comparison.percentChange).toFixed(1)}% `
          + `${comparison.direction})`
        )
    );

    changeText = (
      `That is ${formatDifference(comparison)} overall${percentText}.`
    );
  }

  return (
    `Your average ${comparison.name.toLowerCase()} over the most recent `
    + `${days} days was ${currentText}. In the previous ${days} days it `
    + `was ${previousText}. ${changeText} This is a descriptive comparison `
    + "and does not say whether the change is medically good or bad."
  );
}
