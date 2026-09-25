export type ViewWindow =
  | 7
  | 30
  | 90;


export type MetricKey =
  | "resting_hr"
  | "hrv"
  | "systolic_bp"
  | "diastolic_bp"
  | "glucose"
  | "oxygen_saturation"
  | "respiratory_rate"
  | "wrist_temperature"
  | "sleep_hours"
  | "deep_sleep_hours"
  | "rem_sleep_hours"
  | "pulse_pressure"
  | "map";


export type DailyHealthRecord = {
  date: string;
} & Partial<
  Record<
    MetricKey,
    number | null
  >
>;


export type IntradayMetricKey =
  | "heart_rate"
  | "hrv"
  | "glucose"
  | "oxygen_saturation"
  | "respiratory_rate"
  | "wrist_temperature"
  | "systolic_bp"
  | "diastolic_bp";


export type IntradayHealthRecord = {
  timestamp: string;
} & Partial<
  Record<
    IntradayMetricKey,
    number | null
  >
>;


export type MetricTone =
  | "good"
  | "pink"
  | "warning"
  | "neutral";


export type HealthMetricSnapshot = {
  id: string;
  icon: string;
  title: string;
  value: string;
  detail: string;
  status: string;
  tone: MetricTone;
  source?: string;
};


export type TrendSeries = {
  id: string;
  title: string;
  value: string;
  caption: string;
  trendLabel: string;
  points: number[];
};


export type HealthInsight = {
  id: string;
  title: string;
  body: string;
  support: string;
};


export type DashboardData = {
  sourceLabel: string;
  lastUpdatedLabel: string;

  overviewMetrics: HealthMetricSnapshot[];
  healthMetrics: HealthMetricSnapshot[];
  sleepMetrics: HealthMetricSnapshot[];

  hrvTrend: TrendSeries;
  sleepTrend: TrendSeries;

  overviewInsight: HealthInsight;
  sleepInsight: HealthInsight;
};


export type IntradayPoint = {
  timestamp: string;
  value: number;
};


export type TodayMetricSummary = {
  id: IntradayMetricKey;
  icon: string;
  title: string;
  unit: string;
  decimals: number;
  latest: number | null;
  average: number | null;
  minimum: number | null;
  maximum: number | null;
  sampleCount: number;
  points: IntradayPoint[];
  source: string;
  note?: string;
};


export type TodayData = {
  sourceLabel: string;
  lastUpdatedLabel: string;
  dateLabel: string;
  totalSampleCount: number;
  metrics: TodayMetricSummary[];
};


export interface HealthDataService {
  getDashboard(
    windowDays: ViewWindow,
  ): Promise<DashboardData>;

  ask(
    question: string,
    windowDays: ViewWindow,
  ): Promise<string>;

  getToday?(): Promise<TodayData>;
}
