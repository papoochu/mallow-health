import {
  DailyHealthRecord,
  IntradayHealthRecord,
} from "../models/health";


class SeededRandom {
  private state: number;

  constructor(
    seed: number,
  ) {
    this.state = (
      seed >>> 0
    );
  }

  uniform() {
    this.state = (
      (
        1664525 * this.state
        + 1013904223
      ) >>> 0
    );

    return (
      this.state
      / 4294967296
    );
  }

  normal(
    mean = 0,
    standardDeviation = 1,
  ) {
    const first = Math.max(
      this.uniform(),
      1e-12,
    );

    const second = this.uniform();

    const standardNormal = (
      Math.sqrt(
        -2
        * Math.log(
          first
        )
      )
      * Math.cos(
        2
        * Math.PI
        * second
      )
    );

    return (
      mean
      + standardDeviation
      * standardNormal
    );
  }
}


function clamp(
  value: number,
  minimum: number,
  maximum: number,
) {
  return Math.min(
    maximum,
    Math.max(
      minimum,
      value,
    ),
  );
}


function numericOr(
  value: number | null | undefined,
  fallback: number,
) {
  return (
    typeof value === "number"
    && Number.isFinite(
      value
    )
      ? value
      : fallback
  );
}


function gaussianBump(
  hour: number,
  center: number,
  width: number,
  amplitude: number,
) {
  return (
    amplitude
    * Math.exp(
      -0.5
      * (
        (
          hour - center
        )
        / width
      ) ** 2
    )
  );
}


export function generateDemoIntradayData(
  latestDaily: DailyHealthRecord,
  intervalMinutes = 15,
  seed = 84,
): IntradayHealthRecord[] {
  const random = new SeededRandom(
    seed
  );

  const now = new Date();

  const start = new Date(
    now
  );

  start.setHours(
    0,
    0,
    0,
    0,
  );

  const restingHr = numericOr(
    latestDaily.resting_hr,
    62,
  );

  const dailyHrv = numericOr(
    latestDaily.hrv,
    48,
  );

  const dailyGlucose = numericOr(
    latestDaily.glucose,
    98,
  );

  const dailyOxygen = numericOr(
    latestDaily.oxygen_saturation,
    97.5,
  );

  const dailyRespiratory = numericOr(
    latestDaily.respiratory_rate,
    14.5,
  );

  const dailyTemperature = numericOr(
    latestDaily.wrist_temperature,
    0,
  );

  const dailySystolic = numericOr(
    latestDaily.systolic_bp,
    118,
  );

  const dailyDiastolic = numericOr(
    latestDaily.diastolic_bp,
    74,
  );

  const records: IntradayHealthRecord[] = [];

  const intervalMs = (
    intervalMinutes
    * 60
    * 1000
  );

  const sampleCount = Math.max(
    1,
    Math.floor(
      (
        now.getTime()
        - start.getTime()
      )
      / intervalMs
    )
    + 1,
  );

  for (
    let index = 0;
    index < sampleCount;
    index += 1
  ) {
    const timestamp = new Date(
      start.getTime()
      + index * intervalMs
    );

    const hour = (
      timestamp.getHours()
      + timestamp.getMinutes() / 60
    );

    const circadian = Math.sin(
      2
      * Math.PI
      * (
        hour - 8
      )
      / 24
    );

    const morningActivity = gaussianBump(
      hour,
      9,
      0.7,
      8,
    );

    const afternoonActivity = gaussianBump(
      hour,
      15.5,
      0.9,
      10,
    );

    const eveningActivity = gaussianBump(
      hour,
      19,
      0.8,
      6,
    );

    const activity = (
      morningActivity
      + afternoonActivity
      + eveningActivity
    );

    const heartRate = clamp(
      (
        restingHr
        + 8
        + 3.5 * circadian
        + activity
        + random.normal(
            0,
            2.2,
          )
      ),
      48,
      130,
    );

    const hrv = clamp(
      (
        dailyHrv
        - 0.55
        * (
          heartRate
          - (
            restingHr + 8
          )
        )
        + random.normal(
            0,
            3,
          )
      ),
      15,
      120,
    );

    const breakfast = gaussianBump(
      hour,
      8.5,
      0.8,
      14,
    );

    const lunch = gaussianBump(
      hour,
      13,
      0.9,
      18,
    );

    const dinner = gaussianBump(
      hour,
      19,
      1,
      16,
    );

    const glucose = clamp(
      (
        dailyGlucose
        - 5
        + breakfast
        + lunch
        + dinner
        + random.normal(
            0,
            2.2,
          )
      ),
      65,
      180,
    );

    const oxygen = clamp(
      (
        dailyOxygen
        + random.normal(
            0,
            0.35,
          )
      ),
      92,
      100,
    );

    const respiratory = clamp(
      (
        dailyRespiratory
        + 0.04
        * (
          heartRate
          - (
            restingHr + 8
          )
        )
        + random.normal(
            0,
            0.45,
          )
      ),
      8,
      25,
    );

    const wristTemperature = clamp(
      (
        dailyTemperature
        + 0.10 * circadian
        + random.normal(
            0,
            0.05,
          )
      ),
      -2,
      2,
    );

    const record: IntradayHealthRecord = {
      timestamp: timestamp.toISOString(),
      heart_rate: heartRate,
      hrv,
      glucose,
      oxygen_saturation: oxygen,
      respiratory_rate: respiratory,
      wrist_temperature: wristTemperature,
    };

    if (
      [
        8,
        14,
        20,
      ].includes(
        timestamp.getHours()
      )
      && timestamp.getMinutes() === 0
    ) {
      record.systolic_bp = (
        dailySystolic
        + random.normal(
          0,
          3,
        )
      );

      record.diastolic_bp = (
        dailyDiastolic
        + random.normal(
          0,
          2,
        )
      );
    }

    records.push(
      record
    );
  }

  return records;
}
