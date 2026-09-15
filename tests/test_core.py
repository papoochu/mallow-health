import unittest

import numpy as np
import pandas as pd

from src.assistant import (
    ask_mallow,
    extract_metrics,
    extract_requested_days,
)
from src.comparisons import compare_periods
from src.data_quality import (
    classify_data_support,
    metric_coverage,
    window_quality,
)
from src.relationships import (
    all_relationships,
    calculate_correlation,
    describe_relationship,
)
from src.trends import analyze_trend


def build_health_data(days=90):
    """Create deterministic synthetic-like daily data for unit tests."""

    x = np.arange(days, dtype=float)

    sleep = 6.0 + 0.02 * x
    resting_hr = 72.0 - 0.15 * x
    hrv = 35.0 + 0.25 * x
    glucose = 110.0 - 0.10 * x

    data = pd.DataFrame(
        {
            "date": pd.date_range(
                "2026-01-01",
                periods=days,
                freq="D",
            ),
            "resting_hr": resting_hr,
            "hrv": hrv,
            "systolic_bp": 120.0 - 0.04 * x,
            "diastolic_bp": 76.0 - 0.02 * x,
            "glucose": glucose,
            "oxygen_saturation": 97.0 + 0.05 * np.sin(x),
            "respiratory_rate": 14.0 + 0.10 * np.sin(x / 3),
            "wrist_temperature": 0.05 * np.sin(x / 4),
            "sleep_hours": sleep,
            "deep_sleep_hours": sleep * 0.18,
            "rem_sleep_hours": sleep * 0.22,
        }
    )

    data["pulse_pressure"] = (
        data["systolic_bp"]
        - data["diastolic_bp"]
    )

    data["map"] = (
        data["diastolic_bp"]
        + data["pulse_pressure"] / 3
    )

    return data


class RelationshipTests(unittest.TestCase):

    def setUp(self):
        self.data = build_health_data()

    def test_positive_correlation_is_detected(self):
        correlation = calculate_correlation(
            self.data,
            "sleep_hours",
            "hrv",
            days=30,
        )

        self.assertIsNotNone(correlation)
        self.assertGreater(correlation, 0.99)

    def test_negative_correlation_is_detected(self):
        correlation = calculate_correlation(
            self.data,
            "sleep_hours",
            "resting_hr",
            days=30,
        )

        self.assertIsNotNone(correlation)
        self.assertLess(correlation, -0.99)

    def test_constant_metric_returns_none(self):
        data = self.data.copy()
        data["hrv"] = 50.0

        correlation = calculate_correlation(
            data,
            "sleep_hours",
            "hrv",
            days=30,
        )

        self.assertIsNone(correlation)

    def test_relationship_description_is_causally_cautious(self):
        description = describe_relationship(
            self.data,
            "sleep_hours",
            "resting_hr",
            days=30,
        ).lower()

        self.assertIn("association", description)
        self.assertIn("does not show", description)
        self.assertIn("data support", description)

    def test_all_relationships_are_ranked(self):
        results = all_relationships(
            self.data,
            days=30,
        )

        self.assertGreater(len(results), 0)

        magnitudes = [
            abs(item["correlation"])
            for item in results
        ]

        self.assertEqual(
            magnitudes,
            sorted(
                magnitudes,
                reverse=True,
            ),
        )


class TrendTests(unittest.TestCase):

    def setUp(self):
        self.data = build_health_data()

    def test_increasing_trend_is_detected(self):
        trend = analyze_trend(
            self.data,
            "hrv",
            days=30,
        )

        self.assertIsNotNone(trend)
        self.assertEqual(
            trend["direction"],
            "up",
        )
        self.assertGreater(
            trend["change"],
            0,
        )

    def test_decreasing_trend_is_detected(self):
        trend = analyze_trend(
            self.data,
            "resting_hr",
            days=30,
        )

        self.assertIsNotNone(trend)
        self.assertEqual(
            trend["direction"],
            "down",
        )
        self.assertLess(
            trend["change"],
            0,
        )

    def test_flat_metric_has_no_clear_trend(self):
        data = self.data.copy()
        data["glucose"] = 100.0

        trend = analyze_trend(
            data,
            "glucose",
            days=30,
        )

        self.assertIsNotNone(trend)
        self.assertEqual(
            trend["direction"],
            "stable",
        )
        self.assertEqual(
            trend["label"],
            "No clear trend",
        )

    def test_short_window_returns_none(self):
        trend = analyze_trend(
            self.data.head(4),
            "hrv",
            days=4,
        )

        self.assertIsNone(trend)


class ComparisonTests(unittest.TestCase):

    def test_adjacent_periods_are_compared_correctly(self):
        data = build_health_data(days=20)

        comparison = compare_periods(
            data,
            "sleep_hours",
            days=7,
        )

        self.assertIsNotNone(comparison)
        self.assertGreater(
            comparison["current_average"],
            comparison["previous_average"],
        )
        self.assertEqual(
            comparison["direction"],
            "higher",
        )

    def test_insufficient_history_returns_none(self):
        data = build_health_data(days=10)

        comparison = compare_periods(
            data,
            "sleep_hours",
            days=7,
        )

        self.assertIsNone(comparison)


class DataQualityTests(unittest.TestCase):

    def test_full_30_day_window_has_high_support(self):
        self.assertEqual(
            classify_data_support(
                sample_count=30,
                requested_days=30,
            ),
            "high",
        )

    def test_small_sample_has_limited_support(self):
        self.assertEqual(
            classify_data_support(
                sample_count=4,
                requested_days=30,
            ),
            "limited",
        )

    def test_metric_coverage_counts_missing_values(self):
        data = build_health_data(days=30)
        data.loc[
            data.index[-5:],
            "hrv",
        ] = np.nan

        quality = metric_coverage(
            data,
            "hrv",
            days=30,
        )

        self.assertEqual(
            quality["usable_count"],
            25,
        )
        self.assertEqual(
            quality["missing_count"],
            5,
        )
        self.assertAlmostEqual(
            quality["coverage_percent"],
            83.33333333333334,
        )

    def test_window_quality_reports_incomplete_data(self):
        data = build_health_data(days=30)
        data.loc[
            data.index[-10:],
            "glucose",
        ] = np.nan

        quality = window_quality(
            data,
            metrics=[
                "glucose",
                "hrv",
            ],
            days=30,
        )

        self.assertLess(
            quality["coverage_percent"],
            100.0,
        )
        self.assertGreater(
            quality["coverage_percent"],
            0.0,
        )


class AssistantTests(unittest.TestCase):

    def setUp(self):
        self.data = build_health_data()

    def test_hrv_phrase_is_not_misread_as_heart_rate(self):
        metrics = extract_metrics(
            "How is my heart rate variability trending?"
        )

        self.assertEqual(
            metrics,
            ["hrv"],
        )

    def test_explicit_day_window_is_extracted(self):
        days = extract_requested_days(
            "What was my average glucose over the last 14 days?",
            default_days=30,
        )

        self.assertEqual(
            days,
            14,
        )

    def test_named_month_window_is_extracted(self):
        days = extract_requested_days(
            "How has my sleep changed over the last three months?",
            default_days=30,
        )

        self.assertEqual(
            days,
            90,
        )

    def test_trend_question_uses_trend_engine(self):
        answer = ask_mallow(
            "How is my HRV trending over the last 30 days?",
            self.data,
            analysis_days=30,
        ).lower()

        self.assertIn(
            "hrv",
            answer,
        )
        self.assertIn(
            "data support",
            answer,
        )

    def test_relationship_question_is_causally_cautious(self):
        answer = ask_mallow(
            "Is my sleep related to my resting heart rate?",
            self.data,
            analysis_days=30,
        ).lower()

        self.assertIn(
            "association",
            answer,
        )
        self.assertIn(
            "does not show",
            answer,
        )

    def test_average_question_respects_requested_window(self):
        answer = ask_mallow(
            "What was my average glucose over the last 7 days?",
            self.data,
            analysis_days=30,
        ).lower()

        self.assertIn(
            "last 7 days",
            answer,
        )
        self.assertIn(
            "mg/dl",
            answer,
        )


if __name__ == "__main__":
    unittest.main()
