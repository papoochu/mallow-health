import {
  describe,
  expect,
  it,
} from "vitest";

import {
  calculateCorrelation,
  describeRelationship,
  strongestRelationships,
} from "../src/analytics/relationships";

import {
  DailyHealthRecord,
} from "../src/models/health";


const records: DailyHealthRecord[] = Array.from(
  {
    length: 12,
  },
  (
    _,
    index,
  ) => {
    const sleep = (
      6
      + index * 0.1
    );

    return {
      date: `2026-09-${String(index + 1).padStart(2, "0")}`,
      sleep_hours: sleep,
      hrv: (
        30
        + sleep * 4
      ),
      resting_hr: (
        90
        - sleep * 3
      ),
    };
  }
);


describe(
  "relationship analytics",
  () => {
    it(
      "calculates positive relationships",
      () => {
        const correlation = calculateCorrelation(
          records,
          "sleep_hours",
          "hrv",
          30,
        );

        expect(
          correlation
        ).not.toBeNull();

        expect(
          correlation ?? 0
        ).toBeGreaterThan(
          0.99
        );
      }
    );


    it(
      "describes correlation without claiming causation",
      () => {
        const text = describeRelationship(
          records,
          "sleep_hours",
          "hrv",
          30,
        );

        expect(
          text
        ).toContain(
          "association"
        );

        expect(
          text
        ).toContain(
          "does not show"
        );
      }
    );


    it(
      "ranks strongest relationships by absolute correlation",
      () => {
        const results = strongestRelationships(
          records,
          "sleep_hours",
          30,
          3,
        );

        expect(
          results.length
        ).toBeGreaterThanOrEqual(
          2
        );

        expect(
          Math.abs(
            results[
              0
            ].correlation
          )
        ).toBeGreaterThanOrEqual(
          Math.abs(
            results[
              1
            ].correlation
          )
        );
      }
    );
  }
);
