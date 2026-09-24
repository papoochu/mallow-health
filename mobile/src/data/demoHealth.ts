export type MetricTone =
  | "good"
  | "pink"
  | "warning";


export type MetricData = {
  icon: string;
  title: string;
  value: string;
  detail: string;
  status: string;
  tone: MetricTone;
  source?: string;
};


export const overviewMetrics: MetricData[] = [
  {
    icon: "❤️",
    title: "Resting heart rate",
    value: "62 bpm",
    detail: "30-day average: 64 bpm",
    status: "Near your usual range",
    tone: "good",
    source: "Apple Watch",
  },
  {
    icon: "🫀",
    title: "HRV",
    value: "48 ms",
    detail: "30-day average: 43 ms",
    status: "Slightly above baseline",
    tone: "good",
    source: "Apple Watch",
  },
  {
    icon: "🌙",
    title: "Sleep",
    value: "7.4 h",
    detail: "Deep 1.4 h • REM 1.8 h",
    status: "Near your usual range",
    tone: "pink",
    source: "Apple Watch",
  },
  {
    icon: "🫁",
    title: "Respiratory rate",
    value: "14.7 / min",
    detail: "30-day average: 14.5 / min",
    status: "Near your usual range",
    tone: "good",
    source: "Apple Watch",
  },
];


export const healthMetrics: MetricData[] = [
  {
    icon: "❤️",
    title: "Resting heart rate",
    value: "62 bpm",
    detail: "30-day average: 64 bpm",
    status: "Near your usual range",
    tone: "good",
    source: "Apple Watch",
  },
  {
    icon: "🫀",
    title: "HRV",
    value: "48 ms",
    detail: "30-day average: 43 ms",
    status: "Slightly above baseline",
    tone: "good",
    source: "Apple Watch",
  },
  {
    icon: "🩸",
    title: "Blood pressure",
    value: "118 / 74",
    detail: "Recent cuff reading",
    status: "Near your usual range",
    tone: "good",
    source: "Connected cuff",
  },
  {
    icon: "🍬",
    title: "Blood glucose",
    value: "92 mg/dL",
    detail: "30-day average: 95 mg/dL",
    status: "Near your usual range",
    tone: "good",
    source: "HealthKit",
  },
  {
    icon: "🫁",
    title: "Oxygen saturation",
    value: "97.8%",
    detail: "30-day average: 97.4%",
    status: "Near your usual range",
    tone: "good",
    source: "Apple Watch",
  },
];


export const sleepMetrics: MetricData[] = [
  {
    icon: "🌙",
    title: "Sleep duration",
    value: "7.4 h",
    detail: "30-day average: 7.1 h",
    status: "Near your usual range",
    tone: "pink",
    source: "Apple Watch",
  },
  {
    icon: "💤",
    title: "Deep sleep",
    value: "1.4 h",
    detail: "19% of sleep",
    status: "Recent nightly value",
    tone: "pink",
    source: "Apple Watch",
  },
  {
    icon: "✨",
    title: "REM sleep",
    value: "1.8 h",
    detail: "24% of sleep",
    status: "Recent nightly value",
    tone: "pink",
    source: "Apple Watch",
  },
  {
    icon: "🫁",
    title: "Respiratory rate",
    value: "14.7 / min",
    detail: "30-day average: 14.5 / min",
    status: "Near your usual range",
    tone: "good",
    source: "Apple Watch",
  },
];


export const hrvTrendData = [
  44,
  52,
  49,
  58,
  61,
  56,
  64,
  69,
  63,
  71,
  74,
  72,
];


export const sleepTrendData = [
  6.8,
  7.1,
  6.5,
  7.4,
  7.0,
  7.6,
  7.2,
  7.8,
  7.3,
  7.5,
  7.1,
  7.4,
];
