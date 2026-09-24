import numpy as np
import pandas as pd

from sklearn.ensemble import IsolationForest


FEATURES = [
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


MIN_HISTORY_DAYS = 9
MIN_FEATURE_OBSERVATIONS = 5
MIN_USABLE_FEATURES = 2


def _usable_features(
    history,
    current,
):
    usable = []

    for feature in FEATURES:
        if (
            feature not in history.columns
            or feature not in current.columns
        ):
            continue

        current_value = current.iloc[
            0
        ][
            feature
        ]

        history_count = int(
            history[
                feature
            ].notna().sum()
        )

        if (
            pd.notna(
                current_value
            )
            and history_count
            >= MIN_FEATURE_OBSERVATIONS
        ):
            usable.append(
                feature
            )

    return usable


def detect_current_anomaly(
    data,
    contamination=0.10,
):
    """
    Compare the latest day's available combination of measurements
    with historical patterns using Isolation Forest.

    Real-world Apple Health data is sparse, so only measurements
    available on the current day with enough historical observations
    are included. Historical gaps are median-imputed feature by
    feature for model fitting.

    This detects statistical unusualness only.
    It is not a medical diagnosis.
    """

    if len(
        data
    ) < (
        MIN_HISTORY_DAYS
        + 1
    ):
        raise ValueError(
            "At least 10 calendar days of data are required."
        )

    history = data.iloc[
        :-1
    ].copy()

    current = data.iloc[
        [
            -1
        ]
    ].copy()

    features = _usable_features(
        history,
        current,
    )

    if len(
        features
    ) < MIN_USABLE_FEATURES:
        raise ValueError(
            "At least two current measurements with sufficient "
            "recent history are required for anomaly detection."
        )

    X_history = (
        history[
            features
        ]
        .astype(
            float
        )
        .copy()
    )

    medians = X_history.median()

    X_history = X_history.fillna(
        medians
    )

    X_current = (
        current[
            features
        ]
        .astype(
            float
        )
        .copy()
    )

    if X_history.isna().any().any():
        raise ValueError(
            "Not enough usable historical data for anomaly detection."
        )

    model = IsolationForest(
        n_estimators=200,
        contamination=contamination,
        random_state=42,
    )

    model.fit(
        X_history
    )

    prediction = model.predict(
        X_current
    )[
        0
    ]

    decision_score = model.decision_function(
        X_current
    )[
        0
    ]

    is_anomaly = (
        prediction
        == -1
    )

    recent_history = history.tail(
        30
    )

    feature_deviations = {}

    for feature in features:
        values = (
            recent_history[
                feature
            ]
            .dropna()
            .astype(
                float
            )
        )

        current_value = float(
            current.iloc[
                0
            ][
                feature
            ]
        )

        mean = values.mean()
        std = values.std()

        if (
            len(
                values
            ) < 2
            or pd.isna(
                std
            )
            or std == 0
        ):
            z_score = 0.0
        else:
            z_score = (
                current_value
                - mean
            ) / std

        feature_deviations[
            feature
        ] = float(
            z_score
        )

    ranked_features = sorted(
        feature_deviations.items(),
        key=lambda item: abs(
            item[
                1
            ]
        ),
        reverse=True,
    )

    excluded_features = [
        feature
        for feature in FEATURES
        if feature not in features
    ]

    return {
        "is_anomaly": bool(
            is_anomaly
        ),
        "decision_score": float(
            decision_score
        ),
        "feature_deviations": feature_deviations,
        "ranked_features": ranked_features,
        "features_used": features,
        "excluded_features": excluded_features,
    }
