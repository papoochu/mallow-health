import numpy as np
import pandas as pd


SUMMARY_METRICS = [
    "resting_hr",
    "hrv",
    "systolic_bp",
    "diastolic_bp",
    "pulse_pressure",
    "map",
    "glucose",
    "oxygen_saturation",
    "respiratory_rate",
    "wrist_temperature",
    "sleep_hours",
    "deep_sleep_hours",
    "rem_sleep_hours",
]


def _latest_nonmissing_value(
    data,
    metric,
):
    if (
        metric not in data.columns
        or data.empty
    ):
        return np.nan

    values = data[
        metric
    ].dropna()

    if values.empty:
        return np.nan

    return values.iloc[
        -1
    ]


def get_latest_values(data):
    if data.empty:
        return {
            "date": None,
            **{
                metric: np.nan
                for metric in SUMMARY_METRICS
            },
        }

    latest = {
        "date": data.iloc[
            -1
        ].get(
            "date"
        ),
    }

    for metric in SUMMARY_METRICS:
        latest[
            metric
        ] = _latest_nonmissing_value(
            data,
            metric,
        )

    return latest


def get_baseline(
    data,
    days=30,
):
    recent = data.tail(
        days
    )

    numeric_columns = recent.select_dtypes(
        include="number"
    )

    return numeric_columns.mean()


def get_standard_deviation(
    data,
    days=30,
):
    recent = data.tail(
        days
    )

    numeric_columns = recent.select_dtypes(
        include="number"
    )

    return numeric_columns.std()


def get_deviation_from_baseline(
    data,
    metric,
    days=30,
):
    if (
        metric not in data.columns
        or data.empty
    ):
        return np.nan

    recent = (
        data.tail(
            days
        )[
            metric
        ]
        .dropna()
    )

    if recent.empty:
        return np.nan

    latest = recent.iloc[
        -1
    ]

    baseline = recent.mean()

    return (
        latest
        - baseline
    )


def get_percent_change_from_baseline(
    data,
    metric,
    days=30,
):
    deviation = (
        get_deviation_from_baseline(
            data,
            metric,
            days=days,
        )
    )

    if pd.isna(
        deviation
    ):
        return np.nan

    recent = (
        data.tail(
            days
        )[
            metric
        ]
        .dropna()
    )

    if recent.empty:
        return np.nan

    baseline = recent.mean()

    if baseline == 0:
        return 0.0

    return (
        deviation
        / baseline
        * 100
    )


def get_z_score(
    data,
    metric,
    days=30,
):
    if (
        metric not in data.columns
        or data.empty
    ):
        return np.nan

    recent = (
        data.tail(
            days
        )[
            metric
        ]
        .dropna()
        .astype(
            float
        )
    )

    if recent.empty:
        return np.nan

    latest = recent.iloc[
        -1
    ]

    baseline = recent.mean()
    std = recent.std()

    if (
        len(
            recent
        ) < 2
        or pd.isna(
            std
        )
        or std == 0
    ):
        return 0.0

    return (
        latest
        - baseline
    ) / std


def get_health_summary(
    data,
    baseline_days=30,
):
    latest = get_latest_values(
        data
    )

    baseline = get_baseline(
        data,
        days=baseline_days,
    )

    summary = {
        "latest": latest,
        "baseline": baseline.to_dict(),
        "deviations": {},
        "z_scores": {},
    }

    metrics = [
        "resting_hr",
        "hrv",
        "systolic_bp",
        "diastolic_bp",
        "glucose",
        "oxygen_saturation",
        "respiratory_rate",
        "wrist_temperature",
        "sleep_hours",
    ]

    for metric in metrics:
        summary[
            "deviations"
        ][
            metric
        ] = get_deviation_from_baseline(
            data,
            metric,
            baseline_days,
        )

        summary[
            "z_scores"
        ][
            metric
        ] = get_z_score(
            data,
            metric,
            baseline_days,
        )

    return summary


def get_baseline_status(
    data,
    metric,
    days=30,
):
    """
    Describe how different the latest available measurement is
    from the person's recent statistical baseline.

    Missing data is reported explicitly rather than interpreted.
    This is not a clinical interpretation.
    """

    if (
        metric not in data.columns
        or data[
            metric
        ].dropna().empty
    ):
        return {
            "label": "No data",
            "level": "neutral",
            "z_score": np.nan,
        }

    if days < 2:
        return {
            "label": "Single-day view",
            "level": "neutral",
            "z_score": 0.0,
        }

    z_score = get_z_score(
        data,
        metric,
        days,
    )

    if pd.isna(
        z_score
    ):
        return {
            "label": "No data",
            "level": "neutral",
            "z_score": np.nan,
        }

    if abs(
        z_score
    ) < 1:
        return {
            "label": "Near your usual range",
            "level": "typical",
            "z_score": z_score,
        }

    if abs(
        z_score
    ) < 2:
        direction = (
            "above"
            if z_score > 0
            else "below"
        )

        return {
            "label": (
                f"Somewhat {direction} "
                "your baseline"
            ),
            "level": "watch",
            "z_score": z_score,
        }

    direction = (
        "above"
        if z_score > 0
        else "below"
    )

    return {
        "label": (
            f"Unusually {direction} "
            "your baseline"
        ),
        "level": "unusual",
        "z_score": z_score,
    }
