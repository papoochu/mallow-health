import io
import math
import unittest
import zipfile

import numpy as np

from src.apple_health import (
    load_apple_health_export,
)


def record(
    record_type,
    value,
    unit,
    start,
    end=None,
    source="Apple Watch",
):
    if end is None:
        end = start

    return (
        f'<Record type="{record_type}" '
        f'sourceName="{source}" '
        f'unit="{unit}" '
        f'value="{value}" '
        f'startDate="{start}" '
        f'endDate="{end}" />'
    )


def sleep_record(
    value,
    start,
    end,
    source="Apple Watch",
):
    return (
        '<Record '
        'type="HKCategoryTypeIdentifierSleepAnalysis" '
        f'sourceName="{source}" '
        f'value="{value}" '
        f'startDate="{start}" '
        f'endDate="{end}" />'
    )


def build_xml(
    records,
):
    body = "\n".join(
        records
    )

    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<HealthData locale="en_US">\n'
        f'{body}\n'
        '</HealthData>'
    ).encode(
        "utf-8"
    )


class AppleHealthImportTests(
    unittest.TestCase
):

    def test_parses_supported_daily_quantities(self):
        xml = build_xml(
            [
                record(
                    "HKQuantityTypeIdentifierRestingHeartRate",
                    "61",
                    "count/min",
                    "2026-09-10 12:00:00 -0700",
                ),
                record(
                    "HKQuantityTypeIdentifierHeartRateVariabilitySDNN",
                    "48",
                    "ms",
                    "2026-09-10 06:00:00 -0700",
                ),
                record(
                    "HKQuantityTypeIdentifierRespiratoryRate",
                    "14.5",
                    "count/min",
                    "2026-09-10 07:00:00 -0700",
                ),
            ]
        )

        data, info = load_apple_health_export(
            xml
        )

        self.assertEqual(
            len(data),
            1,
        )

        self.assertAlmostEqual(
            data.loc[
                0,
                "resting_hr",
            ],
            61.0,
        )

        self.assertAlmostEqual(
            data.loc[
                0,
                "hrv",
            ],
            48.0,
        )

        self.assertAlmostEqual(
            data.loc[
                0,
                "respiratory_rate",
            ],
            14.5,
        )

        self.assertIn(
            "resting_hr",
            info[
                "available_metrics"
            ],
        )

    def test_converts_glucose_mmol_to_mg_dl(self):
        xml = build_xml(
            [
                record(
                    "HKQuantityTypeIdentifierBloodGlucose",
                    "5.5",
                    "mmol/L",
                    "2026-09-10 08:00:00 -0700",
                ),
            ]
        )

        data, _ = load_apple_health_export(
            xml
        )

        self.assertAlmostEqual(
            data.loc[
                0,
                "glucose",
            ],
            5.5 * 18.0182,
            places=4,
        )

    def test_converts_fractional_oxygen_to_percent(self):
        xml = build_xml(
            [
                record(
                    "HKQuantityTypeIdentifierOxygenSaturation",
                    "0.975",
                    "%",
                    "2026-09-10 08:00:00 -0700",
                ),
            ]
        )

        data, _ = load_apple_health_export(
            xml
        )

        self.assertAlmostEqual(
            data.loc[
                0,
                "oxygen_saturation",
            ],
            97.5,
        )

    def test_blood_pressure_derives_pulse_pressure_and_map(self):
        xml = build_xml(
            [
                record(
                    "HKQuantityTypeIdentifierBloodPressureSystolic",
                    "120",
                    "mmHg",
                    "2026-09-10 08:00:00 -0700",
                ),
                record(
                    "HKQuantityTypeIdentifierBloodPressureDiastolic",
                    "75",
                    "mmHg",
                    "2026-09-10 08:00:00 -0700",
                ),
            ]
        )

        data, _ = load_apple_health_export(
            xml
        )

        self.assertAlmostEqual(
            data.loc[
                0,
                "pulse_pressure",
            ],
            45.0,
        )

        self.assertAlmostEqual(
            data.loc[
                0,
                "map",
            ],
            90.0,
        )

    def test_sleep_intervals_are_not_double_counted(self):
        xml = build_xml(
            [
                sleep_record(
                    "HKCategoryValueSleepAnalysisAsleepCore",
                    "2026-09-09 23:00:00 -0700",
                    "2026-09-10 02:00:00 -0700",
                ),
                sleep_record(
                    "HKCategoryValueSleepAnalysisAsleepDeep",
                    "2026-09-10 01:00:00 -0700",
                    "2026-09-10 02:00:00 -0700",
                ),
                sleep_record(
                    "HKCategoryValueSleepAnalysisAsleepREM",
                    "2026-09-10 02:00:00 -0700",
                    "2026-09-10 03:00:00 -0700",
                ),
            ]
        )

        data, _ = load_apple_health_export(
            xml
        )

        # The deep sample overlaps the core interval.
        # Total sleep should use the interval union: 4 hours.
        self.assertAlmostEqual(
            data.loc[
                0,
                "sleep_hours",
            ],
            4.0,
        )

        self.assertAlmostEqual(
            data.loc[
                0,
                "deep_sleep_hours",
            ],
            1.0,
        )

        self.assertAlmostEqual(
            data.loc[
                0,
                "rem_sleep_hours",
            ],
            1.0,
        )

    def test_missing_metrics_remain_missing(self):
        xml = build_xml(
            [
                record(
                    "HKQuantityTypeIdentifierRestingHeartRate",
                    "60",
                    "count/min",
                    "2026-09-10 12:00:00 -0700",
                ),
            ]
        )

        data, info = load_apple_health_export(
            xml
        )

        self.assertTrue(
            math.isnan(
                data.loc[
                    0,
                    "glucose",
                ]
            )
        )

        self.assertIn(
            "glucose",
            info[
                "unavailable_metrics"
            ],
        )

    def test_zip_export_is_supported(self):
        xml = build_xml(
            [
                record(
                    "HKQuantityTypeIdentifierRestingHeartRate",
                    "63",
                    "count/min",
                    "2026-09-10 12:00:00 -0700",
                ),
            ]
        )

        archive_bytes = io.BytesIO()

        with zipfile.ZipFile(
            archive_bytes,
            "w",
        ) as archive:
            archive.writestr(
                "apple_health_export/export.xml",
                xml,
            )

        data, info = load_apple_health_export(
            archive_bytes.getvalue()
        )

        self.assertAlmostEqual(
            data.loc[
                0,
                "resting_hr",
            ],
            63.0,
        )

        self.assertEqual(
            info[
                "export_xml_name"
            ],
            "apple_health_export/export.xml",
        )

    def test_wrist_temperature_becomes_personal_deviation(self):
        records = []

        for day in range(
            1,
            8,
        ):
            temperature = (
                95.0
                if day <= 6
                else 96.0
            )

            records.append(
                record(
                    "HKQuantityTypeIdentifierAppleSleepingWristTemperature",
                    str(
                        temperature
                    ),
                    "degF",
                    (
                        f"2026-09-{day:02d} "
                        "06:00:00 -0700"
                    ),
                )
            )

        xml = build_xml(
            records
        )

        data, _ = load_apple_health_export(
            xml,
            temperature_baseline_days=30,
        )

        self.assertTrue(
            np.isnan(
                data.loc[
                    0,
                    "wrist_temperature",
                ]
            )
        )

        self.assertAlmostEqual(
            data.loc[
                6,
                "wrist_temperature",
            ],
            1.0,
        )

    def test_archive_without_export_xml_raises(self):
        archive_bytes = io.BytesIO()

        with zipfile.ZipFile(
            archive_bytes,
            "w",
        ) as archive:
            archive.writestr(
                "readme.txt",
                "not an Apple Health export",
            )

        with self.assertRaises(
            ValueError
        ):
            load_apple_health_export(
                archive_bytes.getvalue()
            )


if __name__ == "__main__":
    unittest.main()
