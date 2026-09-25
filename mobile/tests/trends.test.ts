import {
  describe,
  expect,
  it,
} from "vitest";

import {
  analyzeTrend,
  describeTrend,
} from "../src/analytics/trends";

import {
  DailyHealthRecord,
} from "../src/models/health";


function makeRecords(
  values: number[],
): DailyHealthRecord[] {
  return values.map(
    (
      value,
      index,
    ) => ({
      date: `2026-09-${String(index + 1).padStart(2, "0")}`,
      hrv: value,
    })
  );
}


describe(
  "trend analytics",
  () => {
    it(
      "identifies a clear upward trend",
      () => {
        const result = analyzeTrend(
          makeRecords(
            [
              30,
              32,
              34,
              36,
              38,
              40,
              42,
              44,
            ]
          ),
          "hrv",
          30,
        );

        expect(
          result
        ).not.toBeNull();

        expect(
          result?.direction
        ).toBe(
          "up"
        );

        expect(
          result?.rSquared
        ).toBeGreaterThan(
          0.9
        );
      }
    );


    it(
      "does not invent a direction for flat data",
      () => {
        const result = analyzeTrend(
          makeRecords(
            [
              50,
              50,
              50,
              50,
              50,
              50,
            ]
          ),
          "hrv",
          30,
        );

        expect(
          result?.direction
        ).toBe(
          "stable"
        );
      }
    );


    it(
      "requires enough observations",
      () => {
        expect(
          analyzeTrend(
            makeRecords(
              [
                40,
                41,
                42,
                43,
              ]
            ),
            "hrv",
            30,
          )
        ).toBeNull();

        expect(
          describeTrend(
            makeRecords(
              [
                40,
                41,
                42,
                43,
              ]
            ),
            "hrv",
            30,
          )
        ).toContain(
          "not enough"
        );
      }
    );
  }
);
