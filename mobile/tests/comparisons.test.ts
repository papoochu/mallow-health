import {
  describe,
  expect,
  it,
} from "vitest";

import {
  comparePeriods,
  describePeriodComparison,
} from "../src/analytics/comparisons";

import {
  DailyHealthRecord,
} from "../src/models/health";


const records: DailyHealthRecord[] = Array.from(
  {
    length: 14,
  },
  (
    _,
    index,
  ) => ({
    date: `2026-09-${String(index + 1).padStart(2, "0")}`,
    resting_hr: (
      index < 7
        ? 70
        : 65
    ),
  })
);


describe(
  "period comparison",
  () => {
    it(
      "compares the latest period with the preceding period",
      () => {
        const result = comparePeriods(
          records,
          "resting_hr",
          7,
        );

        expect(
          result
        ).not.toBeNull();

        expect(
          result?.currentAverage
        ).toBe(
          65
        );

        expect(
          result?.previousAverage
        ).toBe(
          70
        );

        expect(
          result?.direction
        ).toBe(
          "lower"
        );
      }
    );


    it(
      "keeps the interpretation descriptive",
      () => {
        const text = describePeriodComparison(
          records,
          "resting_hr",
          7,
        );

        expect(
          text
        ).toContain(
          "descriptive comparison"
        );

        expect(
          text
        ).toContain(
          "does not say whether"
        );
      }
    );
  }
);
