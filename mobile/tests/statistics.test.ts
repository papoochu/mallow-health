import {
  describe,
  expect,
  it,
} from "vitest";

import {
  linearRegression,
  mean,
  pearsonCorrelation,
  sampleStandardDeviation,
} from "../src/analytics/statistics";


describe(
  "statistics",
  () => {
    it(
      "calculates a mean",
      () => {
        expect(
          mean(
            [
              2,
              4,
              6,
              8,
            ]
          )
        ).toBe(
          5
        );
      }
    );


    it(
      "uses sample standard deviation",
      () => {
        expect(
          sampleStandardDeviation(
            [
              1,
              2,
              3,
            ]
          )
        ).toBeCloseTo(
          1,
          8,
        );
      }
    );


    it(
      "detects perfect positive and negative correlation",
      () => {
        expect(
          pearsonCorrelation(
            [
              1,
              2,
              3,
              4,
            ],
            [
              10,
              20,
              30,
              40,
            ],
          )
        ).toBeCloseTo(
          1,
          8,
        );

        expect(
          pearsonCorrelation(
            [
              1,
              2,
              3,
              4,
            ],
            [
              40,
              30,
              20,
              10,
            ],
          )
        ).toBeCloseTo(
          -1,
          8,
        );
      }
    );


    it(
      "fits a simple linear trend",
      () => {
        const result = linearRegression(
          [
            2,
            4,
            6,
            8,
            10,
          ]
        );

        expect(
          result
        ).not.toBeNull();

        expect(
          result?.slope
        ).toBeCloseTo(
          2,
          8,
        );

        expect(
          result?.rSquared
        ).toBeCloseTo(
          1,
          8,
        );
      }
    );
  }
);
