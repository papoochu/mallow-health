import * as HealthKit from "@appeeky/expo-healthkit";

import {
  askMallow,
} from "../analytics/assistant";

import {
  DashboardData,
  DailyHealthRecord,
  HealthDataService,
  MetricKey,
  ViewWindow,
} from "../models/health";

import {
  buildDashboard,
} from "./DashboardBuilder";


type QuantitySampleLike = {
  value?: number;
  quantity?: number;
  startDate: Date | string;
  endDate: Date | string;
};


type CategorySampleLike = {
  value: number | string;
  startDate: Date | string;
  endDate: Date | string;
};


type Interval = {
  start: number;
  end: number;
};


type QuantityDefinition = {
  type: string;
  metric: MetricKey;
  unit: string;
};


const QUANTITY_DEFINITIONS: QuantityDefinition[] = [
  {
    type: HealthKit.QuantityType.restingHeartRate,
    metric: "resting_hr",
    unit: "count/min",
  },
  {
    type: HealthKit.QuantityType.heartRateVariabilitySDNN,
    metric: "hrv",
    unit: "ms",
  },
  {
    type: HealthKit.QuantityType.bloodPressureSystolic,
    metric: "systolic_bp",
    unit: "mmHg",
  },
  {
    type: HealthKit.QuantityType.bloodPressureDiastolic,
    metric: "diastolic_bp",
    unit: "mmHg",
  },
  {
    type: HealthKit.QuantityType.bloodGlucose,
    metric: "glucose",
    unit: "mg/dL",
  },
  {
    type: HealthKit.QuantityType.oxygenSaturation,
    metric: "oxygen_saturation",
    unit: "%",
  },
  {
    type: HealthKit.QuantityType.respiratoryRate,
    metric: "respiratory_rate",
    unit: "count/min",
  },
  {
    type: "HKQuantityTypeIdentifierAppleSleepingWristTemperature",
    metric: "wrist_temperature",
    unit: "degF",
  },
];


const SLEEP_TYPE = HealthKit.CategoryType.sleepAnalysis;


function localDateKey(
  value: Date | string,
): string {
  const date = new Date(
    value
  );

  const year = date.getFullYear();

  const month = String(
    date.getMonth() + 1
  ).padStart(
    2,
    "0",
  );

  const day = String(
    date.getDate()
  ).padStart(
    2,
    "0",
  );

  return `${year}-${month}-${day}`;
}


function addDays(
  date: Date,
  days: number,
) {
  const result = new Date(
    date
  );

  result.setDate(
    result.getDate()
    + days
  );

  return result;
}


function sampleNumber(
  sample: QuantitySampleLike,
): number | null {
  const value = (
    typeof sample.value === "number"
      ? sample.value
      : sample.quantity
  );

  return (
    typeof value === "number"
    && Number.isFinite(
      value
    )
      ? value
      : null
  );
}


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


function mergeIntervals(
  intervals: Interval[],
): Interval[] {
  if (
    intervals.length === 0
  ) {
    return [];
  }

  const sorted = [
    ...intervals,
  ].sort(
    (
      a,
      b,
    ) => a.start - b.start
  );

  const merged: Interval[] = [
    {
      ...sorted[
        0
      ],
    },
  ];

  for (
    const interval of sorted.slice(
      1
    )
  ) {
    const last = merged[
      merged.length - 1
    ];

    if (
      interval.start <= last.end
    ) {
      last.end = Math.max(
        last.end,
        interval.end,
      );
    } else {
      merged.push(
        {
          ...interval,
        }
      );
    }
  }

  return merged;
}


function intervalHours(
  intervals: Interval[],
): number {
  return mergeIntervals(
    intervals
  ).reduce(
    (
      total,
      interval,
    ) => (
      total
      + (
        interval.end
        - interval.start
      )
      / 3_600_000
    ),
    0,
  );
}


function sleepStage(
  value: number | string,
):
  | "asleep"
  | "deep"
  | "rem"
  | "ignore" {
  if (
    typeof value === "number"
  ) {
    if (
      value === 4
    ) {
      return "deep";
    }

    if (
      value === 5
    ) {
      return "rem";
    }

    if (
      value === 1
      || value === 3
    ) {
      return "asleep";
    }

    return "ignore";
  }

  const lowered = value.toLowerCase();

  if (
    lowered.includes(
      "deep"
    )
  ) {
    return "deep";
  }

  if (
    lowered.includes(
      "rem"
    )
  ) {
    return "rem";
  }

  if (
    lowered.includes(
      "asleep"
    )
    || lowered.includes(
      "core"
    )
  ) {
    return "asleep";
  }

  return "ignore";
}


export class DeviceHealthService implements HealthDataService {
  private authorized = false;

  private data: DailyHealthRecord[] = [];


  async isAvailable(): Promise<boolean> {
    try {
      return HealthKit.isAvailable();
    } catch {
      return false;
    }
  }


  async authorize(): Promise<void> {
    const available = await this.isAvailable();

    if (
      !available
    ) {
      throw new Error(
        "Device health data is not available in this environment."
      );
    }

    await HealthKit.requestAuthorization(
      {
        toRead: [
          ...QUANTITY_DEFINITIONS.map(
            (
              definition
            ) => definition.type
          ),
          SLEEP_TYPE,
        ],

        toShare: [],
      }
    );

    this.authorized = true;
  }


  async getDashboard(
    windowDays: ViewWindow,
  ): Promise<DashboardData> {
    await this.ensureData();

    return buildDashboard(
      this.data,
      windowDays,
      {
        sourceLabel: "Device health data",
        cardSource: "Health",
        lastUpdatedLabel: "Read from device",
      },
    );
  }


  async ask(
    question: string,
    windowDays: ViewWindow,
  ): Promise<string> {
    await this.ensureData();

    return askMallow(
      question,
      this.data,
      windowDays,
    );
  }


  private async ensureData() {
    if (
      !this.authorized
    ) {
      throw new Error(
        "Connect device health data before reading measurements."
      );
    }

    this.data = await this.loadDailyData(
      90
    );
  }


  private async loadDailyData(
    days: number,
  ): Promise<DailyHealthRecord[]> {
    const end = new Date();

    const start = addDays(
      end,
      -Math.max(
        days + 2,
        32,
      ),
    );

    const dateKeys: string[] = [];

    for (
      let offset = days - 1;
      offset >= 0;
      offset -= 1
    ) {
      dateKeys.push(
        localDateKey(
          addDays(
            end,
            -offset,
          )
        )
      );
    }

    const records = new Map<
      string,
      DailyHealthRecord
    >();

    const valueBuckets = new Map<
      string,
      Partial<
        Record<
          MetricKey,
          number[]
        >
      >
    >();

    for (
      const key of dateKeys
    ) {
      records.set(
        key,
        {
          date: key,
        }
      );

      valueBuckets.set(
        key,
        {}
      );
    }


    await Promise.all(
      QUANTITY_DEFINITIONS.map(
        async (
          definition
        ) => {
          try {
            const samples = await HealthKit.queryQuantitySamples(
              {
                type: definition.type,
                unit: definition.unit,
                from: start,
                to: end,
                ascending: true,
              }
            ) as readonly QuantitySampleLike[];

            for (
              const sample of samples
            ) {
              const value = sampleNumber(
                sample
              );

              if (
                value === null
              ) {
                continue;
              }

              const key = localDateKey(
                sample.endDate
              );

              const bucket = valueBuckets.get(
                key
              );

              if (
                bucket === undefined
              ) {
                continue;
              }

              const current = bucket[
                definition.metric
              ] ?? [];

              current.push(
                value
              );

              bucket[
                definition.metric
              ] = current;
            }
          } catch {
            // HealthKit intentionally makes denied read access look like
            // missing data. Mallow keeps that metric missing.
          }
        }
      )
    );


    for (
      const [
        key,
        bucket,
      ] of valueBuckets
    ) {
      const record = records.get(
        key
      );

      if (
        record === undefined
      ) {
        continue;
      }

      for (
        const definition of QUANTITY_DEFINITIONS
      ) {
        const values = bucket[
          definition.metric
        ] ?? [];

        const average = mean(
          values
        );

        if (
          average !== null
        ) {
          record[
            definition.metric
          ] = average;
        }
      }
    }


    await this.addSleepData(
      records,
      start,
      end,
    );

    this.convertWristTemperatureToDeviation(
      records,
    );

    this.addDerivedBloodPressureMetrics(
      records
    );

    return dateKeys
      .map(
        (
          key
        ) => records.get(
          key
        )
      )
      .filter(
        (
          record
        ): record is DailyHealthRecord => (
          record !== undefined
        )
      );
  }


  private async addSleepData(
    records: Map<
      string,
      DailyHealthRecord
    >,
    start: Date,
    end: Date,
  ) {
    let samples: readonly CategorySampleLike[];

    try {
      samples = await HealthKit.queryCategorySamples(
        {
          type: SLEEP_TYPE,
          from: start,
          to: end,
          ascending: true,
        }
      ) as readonly CategorySampleLike[];
    } catch {
      return;
    }

    const allSleep = new Map<
      string,
      Interval[]
    >();

    const deepSleep = new Map<
      string,
      Interval[]
    >();

    const remSleep = new Map<
      string,
      Interval[]
    >();


    for (
      const sample of samples
    ) {
      const stage = sleepStage(
        sample.value
      );

      if (
        stage === "ignore"
      ) {
        continue;
      }

      const startTime = new Date(
        sample.startDate
      ).getTime();

      const endTime = new Date(
        sample.endDate
      ).getTime();

      if (
        !Number.isFinite(
          startTime
        )
        || !Number.isFinite(
          endTime
        )
        || endTime <= startTime
      ) {
        continue;
      }

      const key = localDateKey(
        sample.endDate
      );

      if (
        !records.has(
          key
        )
      ) {
        continue;
      }

      const interval = {
        start: startTime,
        end: endTime,
      };

      const totalList = allSleep.get(
        key
      ) ?? [];

      totalList.push(
        interval
      );

      allSleep.set(
        key,
        totalList,
      );

      if (
        stage === "deep"
      ) {
        const list = deepSleep.get(
          key
        ) ?? [];

        list.push(
          interval
        );

        deepSleep.set(
          key,
          list,
        );
      }

      if (
        stage === "rem"
      ) {
        const list = remSleep.get(
          key
        ) ?? [];

        list.push(
          interval
        );

        remSleep.set(
          key,
          list,
        );
      }
    }


    for (
      const [
        key,
        record,
      ] of records
    ) {
      const total = intervalHours(
        allSleep.get(
          key
        ) ?? []
      );

      const deep = intervalHours(
        deepSleep.get(
          key
        ) ?? []
      );

      const rem = intervalHours(
        remSleep.get(
          key
        ) ?? []
      );

      if (
        total > 0
      ) {
        record.sleep_hours = total;
      }

      if (
        deep > 0
      ) {
        record.deep_sleep_hours = deep;
      }

      if (
        rem > 0
      ) {
        record.rem_sleep_hours = rem;
      }
    }
  }


  private convertWristTemperatureToDeviation(
    records: Map<
      string,
      DailyHealthRecord
    >,
  ) {
    const ordered = [
      ...records.values(),
    ].sort(
      (
        a,
        b,
      ) => a.date.localeCompare(
        b.date
      )
    );

    const priorValues: number[] = [];

    for (
      const record of ordered
    ) {
      const absolute = record.wrist_temperature;

      if (
        typeof absolute !== "number"
        || !Number.isFinite(
          absolute
        )
      ) {
        continue;
      }

      const baselineValues = priorValues.slice(
        -30
      );

      const baseline = mean(
        baselineValues
      );

      record.wrist_temperature = (
        baseline === null
          ? 0
          : absolute - baseline
      );

      priorValues.push(
        absolute
      );
    }
  }


  private addDerivedBloodPressureMetrics(
    records: Map<
      string,
      DailyHealthRecord
    >,
  ) {
    for (
      const record of records.values()
    ) {
      const systolic = record.systolic_bp;
      const diastolic = record.diastolic_bp;

      if (
        typeof systolic !== "number"
        || !Number.isFinite(
          systolic
        )
        || typeof diastolic !== "number"
        || !Number.isFinite(
          diastolic
        )
      ) {
        continue;
      }

      const pulsePressure = (
        systolic - diastolic
      );

      record.pulse_pressure = pulsePressure;

      record.map = (
        diastolic
        + pulsePressure / 3
      );
    }
  }
}
