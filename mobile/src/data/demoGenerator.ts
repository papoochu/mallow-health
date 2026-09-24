import {
  DailyHealthRecord,
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


function isoDateDaysAgo(
  daysAgo: number,
) {
  const date = new Date();

  date.setHours(
    12,
    0,
    0,
    0,
  );

  date.setDate(
    date.getDate()
    - daysAgo
  );

  return date
    .toISOString()
    .slice(
      0,
      10,
    );
}


export function generateDemoHealthData(
  days = 90,
  seed = 42,
): DailyHealthRecord[] {
  const random = new SeededRandom(
    seed
  );

  const records: DailyHealthRecord[] = [];

  for (
    let index = 0;
    index < days;
    index += 1
  ) {
    const daysAgo = (
      days - 1 - index
    );

    const sleepHours = clamp(
      random.normal(
        7.1,
        0.7,
      ),
      4,
      10,
    );

    const sleepDeviation = (
      sleepHours - 7.1
    );

    const slowFitnessDrift = (
      index
      / Math.max(
        days - 1,
        1
      )
    );

    const restingHr = clamp(
      (
        63
        - 2.5 * sleepDeviation
        - 1.4 * slowFitnessDrift
        + random.normal(
            0,
            1.8,
          )
      ),
      45,
      100,
    );

    const hrv = clamp(
      (
        45
        + 5.0 * sleepDeviation
        + 4.0 * slowFitnessDrift
        + random.normal(
            0,
            3.5,
          )
      ),
      15,
      100,
    );

    const systolic = clamp(
      (
        118
        - 1.5 * sleepDeviation
        + random.normal(
            0,
            5.5,
          )
      ),
      90,
      160,
    );

    const diastolic = clamp(
      (
        74
        - 0.8 * sleepDeviation
        + random.normal(
            0,
            3.5,
          )
      ),
      55,
      110,
    );

    const glucose = clamp(
      (
        98
        - 2.5 * sleepDeviation
        + random.normal(
            0,
            6,
          )
      ),
      65,
      180,
    );

    const oxygenSaturation = clamp(
      random.normal(
        97.5,
        0.7,
      ),
      90,
      100,
    );

    const respiratoryRate = clamp(
      random.normal(
        14.5,
        1,
      ),
      8,
      25,
    );

    const wristTemperature = clamp(
      random.normal(
        0,
        0.25,
      ),
      -2,
      2,
    );

    const deepFraction = random.normal(
      0.17,
      0.02,
    );

    const remFraction = random.normal(
      0.22,
      0.025,
    );

    const deepSleep = clamp(
      sleepHours
      * deepFraction,
      0,
      sleepHours,
    );

    const remSleep = clamp(
      sleepHours
      * remFraction,
      0,
      sleepHours,
    );

    const pulsePressure = (
      systolic
      - diastolic
    );

    const meanArterialPressure = (
      diastolic
      + pulsePressure / 3
    );

    records.push(
      {
        date: isoDateDaysAgo(
          daysAgo
        ),
        resting_hr: restingHr,
        hrv,
        systolic_bp: systolic,
        diastolic_bp: diastolic,
        glucose,
        oxygen_saturation: oxygenSaturation,
        respiratory_rate: respiratoryRate,
        wrist_temperature: wristTemperature,
        sleep_hours: sleepHours,
        deep_sleep_hours: deepSleep,
        rem_sleep_hours: remSleep,
        pulse_pressure: pulsePressure,
        map: meanArterialPressure,
      }
    );
  }

  return records;
}
