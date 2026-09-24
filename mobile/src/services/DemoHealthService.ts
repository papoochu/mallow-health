import {
  askMallow,
} from "../analytics/assistant";

import {
  generateDemoHealthData,
} from "../data/demoGenerator";

import {
  DashboardData,
  HealthDataService,
  ViewWindow,
} from "../models/health";

import {
  buildDashboard,
} from "./DashboardBuilder";


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
