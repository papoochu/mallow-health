import numpy as np


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


def calculate_correlation(
    data,
    metric_a,
    metric_b,
    days=30,
):
    """
    Calculate the Pearson correlation between two metrics
    over a recent time window.

    Correlation describes association only.
    It does not establish causation.
    """

    recent = data.tail(days)[
        [metric_a, metric_b]
    ].dropna()

    if len(recent) < 5:
        return None

    correlation = recent[
        metric_a
    ].corr(
        recent[metric_b]
    )

    if np.isnan(correlation):
        return None

    return float(correlation)


def describe_strength(correlation):
    """
    Convert a correlation coefficient into a
    plain-language strength description.
    """

    value = abs(correlation)

    if value < 0.2:
        return "very little relationship"

    if value < 0.4:
        return "a weak relationship"

    if value < 0.6:
        return "a moderate relationship"

    if value < 0.8:
        return "a fairly strong relationship"

    return "a strong relationship"


def describe_relationship(
    data,
    metric_a,
    metric_b,
    days=30,
):
    """
    Return a readable description of the recent
    relationship between two health metrics.
    """

    correlation = calculate_correlation(
        data,
        metric_a,
        metric_b,
        days,
    )

    if correlation is None:
        return (
            "There isn't enough usable data to compare "
            "those measurements yet."
        )

    name_a = FRIENDLY_NAMES.get(
        metric_a,
        metric_a.replace("_", " "),
    )

    name_b = FRIENDLY_NAMES.get(
        metric_b,
        metric_b.replace("_", " "),
    )

    strength = describe_strength(
        correlation
    )

    if abs(correlation) < 0.2:
        direction_text = (
            f"I found {strength} between "
            f"{name_a} and {name_b}"
        )

    elif correlation > 0:
        direction_text = (
            f"I found {strength}: higher {name_a} "
            f"has tended to occur alongside higher "
            f"{name_b}"
        )

    else:
        direction_text = (
            f"I found {strength}: higher {name_a} "
            f"has tended to occur alongside lower "
            f"{name_b}"
        )

    return (
        f"{direction_text} over the last {days} days "
        f"(r = {correlation:.2f}). "
        f"This is an association in your data and does "
        f"not show that one measurement caused the other."
    )


def strongest_relationships(
    data,
    target_metric,
    days=30,
    top_n=3,
):
    """
    Find which monitored metrics have the strongest
    correlations with a selected target metric.
    """

    metrics = [
        metric
        for metric in FRIENDLY_NAMES
        if metric != target_metric
        and metric in data.columns
    ]

    results = []

    for metric in metrics:
        correlation = calculate_correlation(
            data,
            target_metric,
            metric,
            days,
        )

        if correlation is not None:
            results.append(
                {
                    "metric": metric,
                    "correlation": correlation,
                }
            )

    results.sort(
        key=lambda item: abs(
            item["correlation"]
        ),
        reverse=True,
    )

    return results[:top_n]