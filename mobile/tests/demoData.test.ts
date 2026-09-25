import {
  describe,
  expect,
  it,
} from "vitest";

import {
  generateDemoHealthData,
} from "../src/data/demoGenerator";

import {
  generateDemoIntradayData,
} from "../src/data/demoIntradayGenerator";


describe(
  "synthetic demo data",
  () => {
    it(
      "is deterministic for the same seed",
      () => {
        const first = generateDemoHealthData(
          10,
          42,
        );

        const second = generateDemoHealthData(
          10,
          42,
        );

        expect(
          first
        ).toEqual(
          second
        );
      }
    );


    it(
      "generates derived blood-pressure metrics",
      () => {
        const data = generateDemoHealthData(
          10,
          42,
        );

        for (
          const row of data
        ) {
          expect(
            row.pulse_pressure
          ).toBeCloseTo(
            (
              row.systolic_bp ?? 0
            )
            - (
              row.diastolic_bp ?? 0
            ),
            8,
          );

          expect(
            row.map
          ).toBeCloseTo(
            (
              row.diastolic_bp ?? 0
            )
            + (
              row.pulse_pressure ?? 0
            )
            / 3,
            8,
          );
        }
      }
    );


    it(
      "generates bounded intraday samples",
      () => {
        const daily = generateDemoHealthData(
          10,
          42,
        );

        const intraday = generateDemoIntradayData(
          daily[
            daily.length - 1
          ],
          15,
          84,
        );

        expect(
          intraday.length
        ).toBeGreaterThan(
          0
        );

        for (
          const row of intraday
        ) {
          expect(
            row.heart_rate
          ).toBeGreaterThanOrEqual(
            48
          );

          expect(
            row.heart_rate
          ).toBeLessThanOrEqual(
            130
          );

          expect(
            row.oxygen_saturation
          ).toBeGreaterThanOrEqual(
            92
          );

          expect(
            row.oxygen_saturation
          ).toBeLessThanOrEqual(
            100
          );
        }
      }
    );
  }
);
