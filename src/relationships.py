import numpy as np

from src.data_quality import classify_data_support


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


MIN_CORRELATION_SAMPLES = 5


def friendly_name(metric):
    """
    Return a readable display name for a metric key.
    """

    return FRIENDLY_NAMES.get(
        metric,
        metric.replace("_", " "),
    )


def get_relationship_data(
    data,
    metric_a,
    metric_b,
    days=30,
):
    """
    Return aligned, non-missing observations for two metrics.

    The most recent `days` rows are used so relationship
    analysis follows the selected dashboard window.
    """

    if (
        metric_a not in data.columns
        or metric_b not in data.columns
    ):
        return data.iloc[0:0].copy()

    return (
        data.tail(days)[
            [
                metric_a,
                metric_b,
            ]
        ]
        .dropna()
        .copy()
    )


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

    recent = get_relationship_data(
        data,
        metric_a,
        metric_b,
        days=days,
    )

    if len(recent) < MIN_CORRELATION_SAMPLES:
        return None

    if (
        recent[metric_a].nunique() < 2
        or recent[metric_b].nunique() < 2
    ):
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


def relationship_direction(
    correlation,
):
    """
    Return a plain-language direction label.
    """

    if abs(correlation) < 0.2:
        return "little clear direction"

    if correlation > 0:
        return "positive"

    if correlation < 0:
        return "negative"

    return "neutral"


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
            "There isn't enough usable variation "
            "in the recent data to compare those "
            "measurements reliably yet."
        )

    name_a = friendly_name(
        metric_a
    )

    name_b = friendly_name(
        metric_b
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

    relationship_data = get_relationship_data(
        data,
        metric_a,
        metric_b,
        days=days,
    )

    support = classify_data_support(
        len(
            relationship_data
        ),
        min(
            days,
            len(data),
        ),
    )

    return (
        f"{direction_text} over the last {days} days "
        f"(r = {correlation:.2f}). Data support is "
        f"{support} based on {len(relationship_data)} paired "
        f"daily observations. This is an association in your "
        f"data and does not show that one measurement caused "
        f"the other."
    )


def strongest_relationships(
    data,
    target_metric,
    days=30,
    top_n=3,
    minimum_strength=0.0,
):
    """
    Find which monitored metrics have the strongest
    correlations with a selected target metric.

    Results are sorted by absolute correlation so both
    strong positive and strong negative relationships
    can surface.

    `minimum_strength` can be used to hide very small
    correlations.
    """

    if target_metric not in data.columns:
        return []

    metrics = [
        metric
        for metric in FRIENDLY_NAMES
        if metric != target_metric
        and metric in data.columns
    ]

    results = []

    for metric in metrics:

        relationship_data = (
            get_relationship_data(
                data,
                target_metric,
                metric,
                days=days,
            )
        )

        correlation = (
            calculate_correlation(
                data,
                target_metric,
                metric,
                days,
            )
        )

        if correlation is None:
            continue

        if (
            abs(correlation)
            < minimum_strength
        ):
            continue

        results.append(
            {
                "metric": metric,
                "metric_name": friendly_name(
                    metric
                ),
                "correlation": correlation,
                "strength": describe_strength(
                    correlation
                ),
                "direction": (
                    relationship_direction(
                        correlation
                    )
                ),
                "sample_count": len(
                    relationship_data
                ),
                "data_support": classify_data_support(
                    len(
                        relationship_data
                    ),
                    min(
                        days,
                        len(data),
                    ),
                ),
            }
        )

    results.sort(
        key=lambda item: abs(
            item["correlation"]
        ),
        reverse=True,
    )

    return results[:top_n]


def all_relationships(
    data,
    days=30,
    minimum_strength=0.0,
):
    """
    Return every unique analyzable metric pair,
    ranked by strength.

    This supports a future automatic discovery view
    where Mallow can surface interesting relationships
    without requiring the user to choose both
    measurements first.
    """

    metrics = [
        metric
        for metric in FRIENDLY_NAMES
        if metric in data.columns
    ]

    results = []

    for index, metric_a in enumerate(
        metrics
    ):
        for metric_b in metrics[
            index + 1:
        ]:

            relationship_data = (
                get_relationship_data(
                    data,
                    metric_a,
                    metric_b,
                    days=days,
                )
            )

            correlation = (
                calculate_correlation(
                    data,
                    metric_a,
                    metric_b,
                    days=days,
                )
            )

            if correlation is None:
                continue

            if (
                abs(correlation)
                < minimum_strength
            ):
                continue

            results.append(
                {
                    "metric_a": metric_a,
                    "metric_b": metric_b,
                    "metric_a_name": (
                        friendly_name(
                            metric_a
                        )
                    ),
                    "metric_b_name": (
                        friendly_name(
                            metric_b
                        )
                    ),
                    "correlation": (
                        correlation
                    ),
                    "strength": (
                        describe_strength(
                            correlation
                        )
                    ),
                    "direction": (
                        relationship_direction(
                            correlation
                        )
                    ),
                    "sample_count": len(
                        relationship_data
                    ),
                    "data_support": classify_data_support(
                        len(
                            relationship_data
                        ),
                        min(
                            days,
                            len(data),
                        ),
                    ),
                }
            )

    results.sort(
        key=lambda item: abs(
            item["correlation"]
        ),
        reverse=True,
    )

    return results
