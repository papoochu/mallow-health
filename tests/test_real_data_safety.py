import unittest

import numpy as np
import pandas as pd

from src.analytics import (
    get_baseline_status,
    get_health_summary,
)
from src.anomaly import (
    detect_current_anomaly,
)


class RealDataSafetyTests(
    unittest.TestCase
):

    def test_latest_summary_uses_latest_nonmissing_metric_value(self):
        data = pd.DataFrame(
            {
                "date": pd.date_range(
                    "2026-01-01",
                    periods=4,
                ).date,
                "resting_hr": [
                    60.0,
                    61.0,
                    np.nan,
                    np.nan,
                ],
                "hrv": [
                    40.0,
                    41.0,
                    42.0,
                    43.0,
                ],
                "systolic_bp": [
                    np.nan,
                ] * 4,
                "diastolic_bp": [
                    np.nan,
                ] * 4,
                "pulse_pressure": [
                    np.nan,
                ] * 4,
                "map": [
                    np.nan,
                ] * 4,
                "glucose": [
                    np.nan,
                ] * 4,
                "oxygen_saturation": [
                    np.nan,
                ] * 4,
                "respiratory_rate": [
                    np.nan,
                ] * 4,
                "wrist_temperature": [
                    np.nan,
                ] * 4,
                "sleep_hours": [
                    7.0,
                ] * 4,
                "deep_sleep_hours": [
                    np.nan,
                ] * 4,
                "rem_sleep_hours": [
                    np.nan,
                ] * 4,
            }
        )

        summary = get_health_summary(
            data
        )

        self.assertEqual(
            summary[
                "latest"
            ][
                "resting_hr"
            ],
            61.0,
        )

        self.assertEqual(
            summary[
                "latest"
            ][
                "hrv"
            ],
            43.0,
        )

    def test_missing_metric_gets_neutral_no_data_status(self):
        data = pd.DataFrame(
            {
                "date": pd.date_range(
                    "2026-01-01",
                    periods=10,
                ).date,
                "glucose": [
                    np.nan,
                ] * 10,
            }
        )

        status = get_baseline_status(
            data,
            "glucose",
        )

        self.assertEqual(
            status[
                "label"
            ],
            "No data",
        )

        self.assertEqual(
            status[
                "level"
            ],
            "neutral",
        )

    def test_anomaly_detector_can_use_sparse_real_world_features(self):
        rows = 12

        data = pd.DataFrame(
            {
                "resting_hr": [
                    60,
                    61,
                    60,
                    np.nan,
                    62,
                    61,
                    60,
                    61,
                    np.nan,
                    62,
                    60,
                    61,
                ],
                "hrv": [
                    40,
                    41,
                    39,
                    42,
                    np.nan,
                    40,
                    41,
                    39,
                    40,
                    42,
                    41,
                    40,
                ],
                "systolic_bp": [
                    np.nan,
                ] * rows,
                "diastolic_bp": [
                    np.nan,
                ] * rows,
                "glucose": [
                    np.nan,
                ] * rows,
                "oxygen_saturation": [
                    np.nan,
                ] * rows,
                "respiratory_rate": [
                    np.nan,
                ] * rows,
                "wrist_temperature": [
                    np.nan,
                ] * rows,
                "sleep_hours": [
                    7.0,
                    7.2,
                    np.nan,
                    6.8,
                    7.1,
                    7.0,
                    7.3,
                    np.nan,
                    6.9,
                    7.1,
                    7.0,
                    7.2,
                ],
            }
        )

        result = detect_current_anomaly(
            data
        )

        self.assertIn(
            "resting_hr",
            result[
                "features_used"
            ],
        )

        self.assertIn(
            "hrv",
            result[
                "features_used"
            ],
        )

        self.assertNotIn(
            "glucose",
            result[
                "features_used"
            ],
        )

    def test_anomaly_detector_rejects_too_few_usable_features(self):
        data = pd.DataFrame(
            {
                "resting_hr": list(
                    range(
                        50,
                        62,
                    )
                ),
                "hrv": [
                    np.nan,
                ] * 12,
                "systolic_bp": [
                    np.nan,
                ] * 12,
                "diastolic_bp": [
                    np.nan,
                ] * 12,
                "glucose": [
                    np.nan,
                ] * 12,
                "oxygen_saturation": [
                    np.nan,
                ] * 12,
                "respiratory_rate": [
                    np.nan,
                ] * 12,
                "wrist_temperature": [
                    np.nan,
                ] * 12,
                "sleep_hours": [
                    np.nan,
                ] * 12,
            }
        )

        with self.assertRaises(
            ValueError
        ):
            detect_current_anomaly(
                data
            )


if __name__ == "__main__":
    unittest.main()
