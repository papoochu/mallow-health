FRIENDLY_NAMES = {
    "resting_hr": "resting heart rate",
    "hrv": "heart-rate variability",
    "systolic_bp": "systolic blood pressure",
    "diastolic_bp": "diastolic blood pressure",
    "glucose": "blood glucose",
    "oxygen_saturation": "oxygen saturation",
    "respiratory_rate": "respiratory rate",
    "wrist_temperature": "wrist temperature",
    "sleep_hours": "sleep duration",
}


def describe_direction(z_score):
    if z_score > 0:
        return "higher"

    if z_score < 0:
        return "lower"

    return "close to"


def build_anomaly_insight(result, top_n=3):
    """
    Convert anomaly-detector output into a readable summary.

    This describes statistical patterns only and does not
    provide a diagnosis or clinical interpretation.
    """

    ranked = result["ranked_features"]

    notable = [
        (feature, z_score)
        for feature, z_score in ranked
        if abs(z_score) >= 1
    ]

    if result["is_anomaly"]:
        opening = (
            "Today's combination of measurements looks "
            "unusual compared with your recent pattern."
        )
    else:
        opening = (
            "Today's overall combination of measurements "
            "looks similar to your recent pattern."
        )

    if not notable:
        return (
            opening
            + " None of the monitored measurements are "
            + "far from their recent personal baselines."
        )

    notable = notable[:top_n]

    descriptions = []

    for feature, z_score in notable:
        name = FRIENDLY_NAMES.get(
            feature,
            feature.replace("_", " "),
        )

        direction = describe_direction(z_score)

        descriptions.append(
            f"{name} is {direction} than usual "
            f"({abs(z_score):.1f} SD from baseline)"
        )

    details = "; ".join(descriptions)

    return (
        f"{opening} The largest personal-baseline "
        f"differences are: {details}."
    )