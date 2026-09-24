from __future__ import annotations

from collections import defaultdict
from contextlib import contextmanager
from io import BytesIO
from pathlib import Path
import math
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
import pandas as pd


APPLE_TYPES = {
    "resting_hr": "HKQuantityTypeIdentifierRestingHeartRate",
    "hrv": "HKQuantityTypeIdentifierHeartRateVariabilitySDNN",
    "systolic_bp": "HKQuantityTypeIdentifierBloodPressureSystolic",
    "diastolic_bp": "HKQuantityTypeIdentifierBloodPressureDiastolic",
    "glucose": "HKQuantityTypeIdentifierBloodGlucose",
    "oxygen_saturation": "HKQuantityTypeIdentifierOxygenSaturation",
    "respiratory_rate": "HKQuantityTypeIdentifierRespiratoryRate",
    "wrist_temperature_absolute": (
        "HKQuantityTypeIdentifierAppleSleepingWristTemperature"
    ),
    "sleep": "HKCategoryTypeIdentifierSleepAnalysis",
}


FRIENDLY_NAMES = {
    "resting_hr": "Resting heart rate",
    "hrv": "HRV",
    "systolic_bp": "Systolic blood pressure",
    "diastolic_bp": "Diastolic blood pressure",
    "glucose": "Blood glucose",
    "oxygen_saturation": "Oxygen saturation",
    "respiratory_rate": "Respiratory rate",
    "wrist_temperature": "Wrist temperature deviation",
    "sleep_hours": "Sleep duration",
    "deep_sleep_hours": "Deep sleep",
    "rem_sleep_hours": "REM sleep",
}


DAILY_COLUMNS = [
    "date",
    "resting_hr",
    "hrv",
    "systolic_bp",
    "diastolic_bp",
    "glucose",
    "oxygen_saturation",
    "respiratory_rate",
    "wrist_temperature",
    "sleep_hours",
    "deep_sleep_hours",
    "rem_sleep_hours",
    "pulse_pressure",
    "map",
]


ASLEEP_VALUES = {
    "HKCategoryValueSleepAnalysisAsleep",
    "HKCategoryValueSleepAnalysisAsleepCore",
    "HKCategoryValueSleepAnalysisAsleepDeep",
    "HKCategoryValueSleepAnalysisAsleepREM",
}


DEEP_SLEEP_VALUES = {
    "HKCategoryValueSleepAnalysisAsleepDeep",
}


REM_SLEEP_VALUES = {
    "HKCategoryValueSleepAnalysisAsleepREM",
}


def _clean_unit(unit):
    return (
        str(unit or "")
        .strip()
        .lower()
        .replace(" ", "")
    )


def _to_float(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None

    if not math.isfinite(number):
        return None

    return number


def _calendar_date(value):
    """
    Preserve the calendar date written in the Apple export.

    Apple Health timestamps include their local UTC offset. Using the
    date text directly avoids accidentally moving a late-night sample
    onto a neighboring UTC date.
    """

    if not value:
        return None

    text = str(value)

    try:
        return pd.Timestamp(
            text[:10]
        ).date()
    except (TypeError, ValueError):
        return None


def _duration_timestamp(value):
    """
    Parse a timestamp for interval-duration arithmetic.

    Converting to UTC is appropriate here because elapsed duration,
    unlike the local calendar-date grouping above, should be absolute.
    """

    if not value:
        return None

    parsed = pd.to_datetime(
        value,
        errors="coerce",
        utc=True,
    )

    if pd.isna(parsed):
        return None

    return parsed


def _convert_quantity(metric, value, unit):
    """
    Convert HealthKit quantity values into Mallow's display units.
    """

    number = _to_float(
        value
    )

    if number is None:
        return None

    normalized_unit = _clean_unit(
        unit
    )

    if metric == "resting_hr":
        return number

    if metric == "hrv":
        if normalized_unit in {
            "s",
            "sec",
            "second",
            "seconds",
        }:
            return number * 1000.0

        return number

    if metric in {
        "systolic_bp",
        "diastolic_bp",
    }:
        if normalized_unit in {
            "kpa",
        }:
            return number * 7.50061683

        return number

    if metric == "glucose":
        if normalized_unit in {
            "mmol/l",
            "mmol/liter",
            "mmol/litre",
        }:
            return number * 18.0182

        return number

    if metric == "oxygen_saturation":
        # HealthKit represents oxygen saturation as a percentage
        # quantity. Some exported datasets encode it as 0-1 while
        # others contain 0-100-style percentage values.
        if number <= 1.5:
            return number * 100.0

        return number

    if metric == "respiratory_rate":
        return number

    if metric == "wrist_temperature_absolute":
        if normalized_unit in {
            "degc",
            "°c",
            "c",
            "degreecelsius",
        }:
            return (
                number
                * 9.0
                / 5.0
                + 32.0
            )

        if normalized_unit in {
            "k",
            "kelvin",
        }:
            celsius = (
                number
                - 273.15
            )

            return (
                celsius
                * 9.0
                / 5.0
                + 32.0
            )

        return number

    return number


def _merge_interval_hours(
    intervals,
):
    """
    Return total duration of the union of time intervals in hours.

    This prevents overlapping Apple Health sleep samples from being
    double-counted when multiple sources contribute to the export.
    """

    cleaned = []

    for start, end in intervals:
        if (
            start is None
            or end is None
            or end <= start
        ):
            continue

        cleaned.append(
            (
                start,
                end,
            )
        )

    if not cleaned:
        return np.nan

    cleaned.sort(
        key=lambda pair: pair[0]
    )

    merged = [
        list(
            cleaned[0]
        )
    ]

    for start, end in cleaned[1:]:
        previous = merged[-1]

        if start <= previous[1]:
            previous[1] = max(
                previous[1],
                end,
            )
        else:
            merged.append(
                [
                    start,
                    end,
                ]
            )

    total_seconds = sum(
        (
            end
            - start
        ).total_seconds()
        for start, end in merged
    )

    return (
        total_seconds
        / 3600.0
    )


def _temperature_deviation(
    absolute_temperature,
    baseline_days=30,
    minimum_baseline_days=5,
):
    """
    Convert absolute sleeping wrist temperature into a deviation
    from the preceding personal rolling mean.

    Apple Health exports the sleeping wrist-temperature quantity.
    Mallow's existing temperature metric is a personal deviation,
    so the importer derives that deviation without fabricating
    values when insufficient history exists.
    """

    previous_baseline = (
        absolute_temperature
        .shift(1)
        .rolling(
            window=baseline_days,
            min_periods=minimum_baseline_days,
        )
        .mean()
    )

    return (
        absolute_temperature
        - previous_baseline
    )


@contextmanager
def _open_export_xml(
    source,
):
    """
    Yield an Apple Health export.xml stream.

    Supported inputs:
    - path to export.xml
    - path to Apple's exported ZIP archive
    - bytes / bytearray
    - binary file-like objects such as Streamlit UploadedFile
    """

    zip_handle = None
    xml_handle = None

    try:
        if isinstance(
            source,
            (
                str,
                Path,
            ),
        ):
            path = Path(
                source
            )

            if not path.exists():
                raise FileNotFoundError(
                    f"Apple Health export not found: {path}"
                )

            if zipfile.is_zipfile(
                path
            ):
                zip_handle = zipfile.ZipFile(
                    path,
                    "r",
                )

                xml_name = _find_export_xml(
                    zip_handle.namelist()
                )

                xml_handle = zip_handle.open(
                    xml_name,
                    "r",
                )

                yield (
                    xml_handle,
                    xml_name,
                )

                return

            xml_handle = path.open(
                "rb"
            )

            yield (
                xml_handle,
                path.name,
            )

            return

        if isinstance(
            source,
            (
                bytes,
                bytearray,
            ),
        ):
            raw = BytesIO(
                source
            )
        elif hasattr(
            source,
            "read",
        ):
            raw_bytes = source.read()

            if hasattr(
                source,
                "seek",
            ):
                try:
                    source.seek(
                        0
                    )
                except (
                    OSError,
                    ValueError,
                ):
                    pass

            raw = BytesIO(
                raw_bytes
            )
        else:
            raise TypeError(
                "Apple Health source must be a path, bytes, "
                "or a binary file-like object."
            )

        if zipfile.is_zipfile(
            raw
        ):
            raw.seek(
                0
            )

            zip_handle = zipfile.ZipFile(
                raw,
                "r",
            )

            xml_name = _find_export_xml(
                zip_handle.namelist()
            )

            xml_handle = zip_handle.open(
                xml_name,
                "r",
            )

            yield (
                xml_handle,
                xml_name,
            )

            return

        raw.seek(
            0
        )

        yield (
            raw,
            "export.xml",
        )

    finally:
        if xml_handle is not None:
            try:
                xml_handle.close()
            except (
                OSError,
                ValueError,
            ):
                pass

        if zip_handle is not None:
            zip_handle.close()


def _find_export_xml(
    names,
):
    candidates = [
        name
        for name in names
        if name.lower().endswith(
            "export.xml"
        )
    ]

    if not candidates:
        raise ValueError(
            "The ZIP archive does not contain an Apple Health "
            "export.xml file."
        )

    preferred = [
        name
        for name in candidates
        if "apple_health_export/" in name.lower()
    ]

    if preferred:
        return sorted(
            preferred,
            key=len,
        )[0]

    return sorted(
        candidates,
        key=len,
    )[0]


def parse_apple_health_export(
    source,
    temperature_baseline_days=30,
):
    """
    Parse an Apple Health XML/ZIP export into Mallow's daily schema.

    Returns:
        (daily_dataframe, import_info)

    Missing health metrics remain NaN. They are never replaced by
    synthetic values.
    """

    type_to_metric = {
        identifier: metric
        for metric, identifier
        in APPLE_TYPES.items()
        if metric != "sleep"
    }

    quantity_values = defaultdict(
        lambda: defaultdict(
            list
        )
    )

    total_sleep = defaultdict(
        list
    )

    deep_sleep = defaultdict(
        list
    )

    rem_sleep = defaultdict(
        list
    )

    source_names = set()
    record_counts = defaultdict(
        int
    )

    records_seen = 0
    relevant_records = 0

    with _open_export_xml(
        source
    ) as (
        xml_stream,
        xml_name,
    ):
        try:
            iterator = ET.iterparse(
                xml_stream,
                events=(
                    "end",
                ),
            )

            for _, element in iterator:
                if element.tag != "Record":
                    element.clear()
                    continue

                records_seen += 1

                record_type = element.attrib.get(
                    "type"
                )

                source_name = element.attrib.get(
                    "sourceName"
                )

                if source_name:
                    source_names.add(
                        source_name
                    )

                if record_type == APPLE_TYPES[
                    "sleep"
                ]:
                    value = element.attrib.get(
                        "value"
                    )

                    if value not in ASLEEP_VALUES:
                        element.clear()
                        continue

                    start_text = element.attrib.get(
                        "startDate"
                    )

                    end_text = element.attrib.get(
                        "endDate"
                    )

                    sleep_day = _calendar_date(
                        end_text
                    )

                    start = _duration_timestamp(
                        start_text
                    )

                    end = _duration_timestamp(
                        end_text
                    )

                    if (
                        sleep_day is None
                        or start is None
                        or end is None
                        or end <= start
                    ):
                        element.clear()
                        continue

                    relevant_records += 1
                    record_counts[
                        "sleep_hours"
                    ] += 1

                    interval = (
                        start,
                        end,
                    )

                    total_sleep[
                        sleep_day
                    ].append(
                        interval
                    )

                    if value in DEEP_SLEEP_VALUES:
                        record_counts[
                            "deep_sleep_hours"
                        ] += 1

                        deep_sleep[
                            sleep_day
                        ].append(
                            interval
                        )

                    if value in REM_SLEEP_VALUES:
                        record_counts[
                            "rem_sleep_hours"
                        ] += 1

                        rem_sleep[
                            sleep_day
                        ].append(
                            interval
                        )

                    element.clear()
                    continue

                metric = type_to_metric.get(
                    record_type
                )

                if metric is None:
                    element.clear()
                    continue

                day = _calendar_date(
                    element.attrib.get(
                        "startDate"
                    )
                )

                converted = _convert_quantity(
                    metric,
                    element.attrib.get(
                        "value"
                    ),
                    element.attrib.get(
                        "unit"
                    ),
                )

                if (
                    day is None
                    or converted is None
                ):
                    element.clear()
                    continue

                relevant_records += 1
                record_counts[
                    metric
                ] += 1

                quantity_values[
                    metric
                ][
                    day
                ].append(
                    converted
                )

                element.clear()

        except ET.ParseError as exc:
            raise ValueError(
                "The Apple Health export XML could not be parsed."
            ) from exc

    all_dates = set()

    for metric_days in quantity_values.values():
        all_dates.update(
            metric_days.keys()
        )

    all_dates.update(
        total_sleep.keys()
    )

    if not all_dates:
        raise ValueError(
            "No supported Apple Health records were found in "
            "this export."
        )

    start_day = min(
        all_dates
    )

    end_day = max(
        all_dates
    )

    date_index = pd.date_range(
        start=start_day,
        end=end_day,
        freq="D",
    )

    daily = pd.DataFrame(
        {
            "date": date_index.date,
        }
    )

    for metric in [
        "resting_hr",
        "hrv",
        "systolic_bp",
        "diastolic_bp",
        "glucose",
        "oxygen_saturation",
        "respiratory_rate",
    ]:
        daily[metric] = [
            (
                float(
                    np.mean(
                        quantity_values[
                            metric
                        ].get(
                            day,
                            [
                                np.nan,
                            ],
                        )
                    )
                )
            )
            for day in daily[
                "date"
            ]
        ]

    absolute_temperature = pd.Series(
        [
            (
                float(
                    np.mean(
                        quantity_values[
                            "wrist_temperature_absolute"
                        ].get(
                            day,
                            [
                                np.nan,
                            ],
                        )
                    )
                )
            )
            for day in daily[
                "date"
            ]
        ],
        index=daily.index,
        dtype=float,
    )

    daily[
        "wrist_temperature"
    ] = _temperature_deviation(
        absolute_temperature,
        baseline_days=temperature_baseline_days,
    )

    daily[
        "sleep_hours"
    ] = [
        _merge_interval_hours(
            total_sleep.get(
                day,
                [],
            )
        )
        for day in daily[
            "date"
        ]
    ]

    daily[
        "deep_sleep_hours"
    ] = [
        _merge_interval_hours(
            deep_sleep.get(
                day,
                [],
            )
        )
        for day in daily[
            "date"
        ]
    ]

    daily[
        "rem_sleep_hours"
    ] = [
        _merge_interval_hours(
            rem_sleep.get(
                day,
                [],
            )
        )
        for day in daily[
            "date"
        ]
    ]

    daily[
        "pulse_pressure"
    ] = (
        daily[
            "systolic_bp"
        ]
        - daily[
            "diastolic_bp"
        ]
    )

    daily[
        "map"
    ] = (
        daily[
            "diastolic_bp"
        ]
        + daily[
            "pulse_pressure"
        ]
        / 3.0
    )

    daily = daily[
        DAILY_COLUMNS
    ].copy()

    daily = daily.replace(
        [
            np.inf,
            -np.inf,
        ],
        np.nan,
    )

    available_metrics = [
        metric
        for metric in FRIENDLY_NAMES
        if metric in daily.columns
        and daily[
            metric
        ].notna().any()
    ]

    unavailable_metrics = [
        metric
        for metric in FRIENDLY_NAMES
        if metric not in available_metrics
    ]

    info = {
        "source": "Apple Health export",
        "export_xml_name": xml_name,
        "start_date": start_day,
        "end_date": end_day,
        "calendar_days": len(
            daily
        ),
        "records_seen": records_seen,
        "relevant_records": relevant_records,
        "record_counts": dict(
            record_counts
        ),
        "available_metrics": available_metrics,
        "unavailable_metrics": unavailable_metrics,
        "available_metric_names": [
            FRIENDLY_NAMES[
                metric
            ]
            for metric in available_metrics
        ],
        "unavailable_metric_names": [
            FRIENDLY_NAMES[
                metric
            ]
            for metric in unavailable_metrics
        ],
        "source_names": sorted(
            source_names
        ),
    }

    return (
        daily,
        info,
    )


def load_apple_health_export(
    source,
    temperature_baseline_days=30,
):
    """
    Friendly public alias for parse_apple_health_export().
    """

    return parse_apple_health_export(
        source,
        temperature_baseline_days=temperature_baseline_days,
    )
