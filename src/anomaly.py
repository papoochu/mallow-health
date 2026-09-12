import numpy as np

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


def detect_current_anomaly(
    data,
    contamination=0.10,
):
    """
    Compare the latest day's combination of health measurements
    with historical patterns using Isolation Forest.

    The latest day is excluded from model training so the model
    does not learn from the value it is being asked to evaluate.

    This detects statistical unusualness only.
    It is not a medical diagnosis.
    """

    if len(data) < 10:
        raise ValueError(
            "At least 10 days of data are required."
        )

    history = data.iloc[:-1].copy()
    current = data.iloc[[-1]].copy()

    X_history = history[FEATURES]
    X_current = current[FEATURES]

    model = IsolationForest(
        n_estimators=200,
        contamination=contamination,
        random_state=42,
    )

    model.fit(X_history)

    prediction = model.predict(X_current)[0]

    decision_score = model.decision_function(
        X_current
    )[0]

    is_anomaly = prediction == -1

    # Explain the result using personal baseline deviations.
    # Isolation Forest itself does not tell us which individual
    # measurement caused the result.
    recent_history = history.tail(30)

    feature_deviations = {}

    for feature in FEATURES:

        mean = recent_history[feature].mean()
        std = recent_history[feature].std()

        if std == 0:
            z_score = 0.0
        else:
            z_score = (
                current.iloc[0][feature] - mean
            ) / std

        feature_deviations[feature] = float(
            z_score
        )

    # Rank measurements by how far they are from baseline.
    ranked_features = sorted(
        feature_deviations.items(),
        key=lambda item: abs(item[1]),
        reverse=True,
    )

    return {
        "is_anomaly": bool(is_anomaly),
        "decision_score": float(decision_score),
        "feature_deviations": feature_deviations,
        "ranked_features": ranked_features,
    }