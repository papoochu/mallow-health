import {
  describe,
  expect,
  it,
} from "vitest";

import {
  getBaselineStatus,
  latestMetricValue,
  metricAverage,
} from "../src/analytics/baseline";

import {
  DailyHealthRecord,
} from "../src/models/health";


const records: DailyHealthRecord[] = [
  {
    date: "2026-09-01",
    hrv: 40,
  },
  {
    date: "2026-09-02",
    hrv: 42,
  },
  {
    date: "2026-09-03",
    hrv: null,
  },
  {
    date: "2026-09-04",
    hrv: 44,
  },
  {
    date: "2026-09-05",
    hrv: 46,
  },
];


describe(
  "personal baseline analytics",
  () => {
    it(
      "uses the latest non-missing value",
      () => {
        expect(
          latestMetricValue(
            records,
            "hrv",
          )
        ).toBe(
          46
        );
      }
    );


    it(
      "ignores missing values in averages",
      () => {
        expect(
          metricAverage(
            records,
            "hrv",
            30,
          )
        ).toBeCloseTo(
          43,
          8,
        );
      }
    );


    it(
      "returns neutral No data when a metric is absent",
      () => {
        const status = getBaselineStatus(
          records,
          "glucose",
          30,
        );

        expect(
          status.label
        ).toBe(
          "No data"
        );

        expect(
          status.level
        ).toBe(
          "neutral"
        );
      }
    );
  }
);
