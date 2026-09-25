import {
  describe,
  expect,
  it,
} from "vitest";

import {
  askMallow,
} from "../src/analytics/assistant";

import {
  generateDemoHealthData,
} from "../src/data/demoGenerator";


const data = generateDemoHealthData(
  90,
  42,
);


describe(
  "Ask Mallow",
  () => {
    it(
      "answers a trend question from calculated data",
      () => {
        const answer = askMallow(
          "How has my HRV changed this month?",
          data,
          30,
        );

        expect(
          answer.toLowerCase()
        ).toContain(
          "hrv"
        );

        expect(
          answer.toLowerCase()
        ).toMatch(
          /trend|increased|decreased|clear/
        );
      }
    );


    it(
      "answers a relationship question with a non-causal disclaimer",
      () => {
        const answer = askMallow(
          "What is related to my sleep?",
          data,
          30,
        );

        expect(
          answer.toLowerCase()
        ).toContain(
          "correlation"
        );

        expect(
          answer.toLowerCase()
        ).toContain(
          "do not show"
        );
      }
    );


    it(
      "answers a week-over-week comparison",
      () => {
        const answer = askMallow(
          "How does this week compare with last week for resting heart rate?",
          data,
          30,
        );

        expect(
          answer.toLowerCase()
        ).toContain(
          "previous 7 days"
        );

        expect(
          answer.toLowerCase()
        ).toContain(
          "descriptive comparison"
        );
      }
    );
  }
);
