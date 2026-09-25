import {
  IntradayHealthRecord,
  IntradayMetricKey,
  TodayData,
  TodayMetricSummary,
} from "../models/health";


type MetricDefinition = {
  id: IntradayMetricKey;
  icon: string;
  title: string;
  unit: string;
  decimals: number;
  note?: string;
};


const METRICS: MetricDefinition[] = [
  {
    id: "heart_rate",
    icon: "❤️",
    title: "Heart rate",
    unit: "bpm",
    decimals: 0,
    note: (
      "Heart rate can move substantially through the day with "
      + "activity, posture, stress, meals, and rest."
    ),
  },
  {
    id: "hrv",
    icon: "🫀",
    title: "HRV",
    unit: "ms",
    decimals: 0,
  },
  {
    id: "glucose",
    icon: "🍬",
    title: "Blood glucose",
    unit: "mg/dL",
    decimals: 0,
  },
  {
    id: "oxygen_saturation",
    icon: "🫁",
    title: "Oxygen saturation",
    unit: "%",
    decimals: 1,
  },
  {
    id: "respiratory_rate",
    icon: "🌬️",
    title: "Respiratory rate",
    unit: "/ min",
    decimals: 1,
  },
  {
    id: "wrist_temperature",
    icon: "🌡️",
    title: "Wrist temperature deviation",
    unit: "°F",
    decimals: 2,
    note: (
      "Wrist temperature is shown as a personal deviation in "
      + "Mallow rather than as a clinical body-temperature reading."
    ),
  },
];


function mean(
  values: number[],
): number | null {
  if (
    values.length === 0
  ) {
    return null;
  }

  return (
    values.reduce(
      (
        total,
        value,
      ) => total + value,
      0,
    )
    / values.length
  );
}


function formatTime(
  value: string,
) {
  const date = new Date(
    value
  );

  return date.toLocaleTimeString(
    [],
    {
      hour: "numeric",
      minute: "2-digit",
    },
  );
}


export function buildTodayData(
  records: IntradayHealthRecord[],
  sourceLabel: string,
  cardSource: string,
): TodayData {
  const ordered = [
    ...records,
  ].sort(
    (
      a,
      b,
    ) => (
      new Date(
        a.timestamp
      ).getTime()
      - new Date(
          b.timestamp
        ).getTime()
    )
  );

  const metrics: TodayMetricSummary[] = METRICS.map(
    (
      definition
    ) => {
      const points = ordered
        .map(
          (
            record
          ) => {
            const value = record[
              definition.id
            ];

            if (
              typeof value !== "number"
              || !Number.isFinite(
                value
              )
            ) {
              return null;
            }

            return {
              timestamp: record.timestamp,
              value,
            };
          }
        )
        .filter(
          (
            point
          ): point is {
            timestamp: string;
            value: number;
          } => point !== null
        );

      const values = points.map(
        (
          point
        ) => point.value
      );

      return {
        id: definition.id,
        icon: definition.icon,
        title: definition.title,
        unit: definition.unit,
        decimals: definition.decimals,
        latest: (
          values.length > 0
            ? values[
                values.length - 1
              ]
            : null
        ),
        average: mean(
          values
        ),
        minimum: (
          values.length > 0
            ? Math.min(
                ...values
              )
            : null
        ),
        maximum: (
          values.length > 0
            ? Math.max(
                ...values
              )
            : null
        ),
        sampleCount: values.length,
        points,
        source: cardSource,
        note: definition.note,
      };
    }
  );

  const latestTimestamp = (
    ordered.length > 0
      ? ordered[
          ordered.length - 1
        ].timestamp
      : null
  );

  return {
    sourceLabel,
    lastUpdatedLabel: (
      latestTimestamp === null
        ? "No samples today"
        : `Latest sample ${formatTime(latestTimestamp)}`
    ),
    dateLabel: new Date().toLocaleDateString(
      [],
      {
        weekday: "long",
        month: "long",
        day: "numeric",
      },
    ),
    totalSampleCount: ordered.length,
    metrics,
  };
}
