import {
  askMallow,
} from "../analytics/assistant";

import {
  generateDemoHealthData,
} from "../data/demoGenerator";

import {
  generateDemoIntradayData,
} from "../data/demoIntradayGenerator";

import {
  DashboardData,
  HealthDataService,
  TodayData,
  ViewWindow,
} from "../models/health";

import {
  buildDashboard,
} from "./DashboardBuilder";

import {
  buildTodayData,
} from "./TodayBuilder";


export class DemoHealthService implements HealthDataService {
  private readonly data = generateDemoHealthData(
    90,
    42,
  );


  async getDashboard(
    windowDays: ViewWindow,
  ): Promise<DashboardData> {
    return buildDashboard(
      this.data,
      windowDays,
      {
        sourceLabel: "Demo health data",
        cardSource: "Demo",
        lastUpdatedLabel: "Calculated locally",
      },
    );
  }


  async getToday(): Promise<TodayData> {
    const latestDaily = this.data[
      this.data.length - 1
    ];

    const intraday = generateDemoIntradayData(
      latestDaily,
      15,
      84,
    );

    return buildTodayData(
      intraday,
      "Demo intraday data",
      "Demo",
    );
  }


  async ask(
    question: string,
    windowDays: ViewWindow,
  ): Promise<string> {
    return askMallow(
      question,
      this.data,
      windowDays,
    );
  }
}
