import {
  describe,
  expect,
  it,
} from "vitest";

import {
  buildTodayData,
} from "../src/services/TodayBuilder";

import {
  IntradayHealthRecord,
} from "../src/models/health";


const records: IntradayHealthRecord[] = [
  {
    timestamp: "2026-09-25T08:00:00-07:00",
    heart_rate: 60,
    hrv: 50,
  },
  {
    timestamp: "2026-09-25T09:00:00-07:00",
    heart_rate: 80,
    hrv: 40,
  },
  {
    timestamp: "2026-09-25T10:00:00-07:00",
    heart_rate: 70,
    hrv: 45,
  },
];


describe(
  "Today data builder",
  () => {
    it(
      "summarizes latest, average, range, and count",
      () => {
        const today = buildTodayData(
          records,
          "Test source",
          "Test",
        );

        const heartRate = today.metrics.find(
          (
            metric
          ) => metric.id === "heart_rate"
        );

        expect(
          heartRate
        ).toBeDefined();

        expect(
          heartRate?.latest
        ).toBe(
          70
        );

        expect(
          heartRate?.average
        ).toBe(
          70
        );

        expect(
          heartRate?.minimum
        ).toBe(
          60
        );

        expect(
          heartRate?.maximum
        ).toBe(
          80
        );

        expect(
          heartRate?.sampleCount
        ).toBe(
          3
        );
      }
    );


    it(
      "preserves missing metrics instead of fabricating values",
      () => {
        const today = buildTodayData(
          records,
          "Test source",
          "Test",
        );

        const glucose = today.metrics.find(
          (
            metric
          ) => metric.id === "glucose"
        );

        expect(
          glucose?.latest
        ).toBeNull();

        expect(
          glucose?.sampleCount
        ).toBe(
          0
        );
      }
    );
  }
);
