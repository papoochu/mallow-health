CORE_METRICS = [
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


FRIENDLY_NAMES = {
    "resting_hr": "Resting heart rate",
    "hrv": "HRV",
    "systolic_bp": "Systolic blood pressure",
    "diastolic_bp": "Diastolic blood pressure",
    "glucose": "Blood glucose",
    "oxygen_saturation": "Oxygen saturation",
    "respiratory_rate": "Respiratory rate",
    "wrist_temperature": "Wrist temperature",
    "sleep_hours": "Sleep duration",
}


def classify_data_support(
    sample_count,
    requested_days,
    minimum_samples=5,
):
    """
    Describe how much usable data supports an analysis.

    This is a data-availability label, not a statistical
    confidence interval and not a clinical confidence score.
    """

    if requested_days <= 0:
        return "limited"

    coverage = (
        sample_count
        / requested_days
    )

    if sample_count < minimum_samples:
        return "limited"

    if (
        sample_count >= 30
        and coverage >= 0.80
    ):
        return "high"

    if (
        sample_count >= 14
        and coverage >= 0.65
    ):
        return "good"

    if (
        sample_count >= 7
        and coverage >= 0.60
    ):
        return "moderate"

    return "limited"


def support_explanation(
    support,
):
    """
    Convert a data-support label into a short explanation.
    """

    explanations = {
        "high": (
            "A substantial amount of the selected window "
            "contains usable data."
        ),
        "good": (
            "Most of the selected window contains usable data."
        ),
        "moderate": (
            "The pattern has a useful but still fairly small "
            "amount of supporting data."
        ),
        "limited": (
            "The pattern is based on a small or incomplete "
            "amount of usable data."
        ),
    }

    return explanations.get(
        support,
        explanations["limited"],
    )


def metric_coverage(
    data,
    metric,
    days=30,
):
    """
    Measure usable daily coverage for one metric.
    """

    if metric not in data.columns:
        return None

    window = data.tail(
        days
    )

    requested_days = min(
        days,
        len(data),
    )

    if requested_days <= 0:
        return None

    usable_count = int(
        window[metric]
        .notna()
        .sum()
    )

    coverage = (
        usable_count
        / requested_days
    )

    support = classify_data_support(
        usable_count,
        requested_days,
    )

    return {
        "metric": metric,
        "name": FRIENDLY_NAMES.get(
            metric,
            metric.replace(
                "_",
                " ",
            ).title(),
        ),
        "requested_days": requested_days,
        "usable_count": usable_count,
        "missing_count": (
            requested_days
            - usable_count
        ),
        "coverage": coverage,
        "coverage_percent": (
            coverage
            * 100
        ),
        "support": support,
    }


def window_quality(
    data,
    metrics=None,
    days=30,
):
    """
    Summarize data completeness across a selected daily window.
    """

    if metrics is None:
        metrics = CORE_METRICS

    available_metrics = [
        metric
        for metric in metrics
        if metric in data.columns
    ]

    requested_days = min(
        days,
        len(data),
    )

    if (
        requested_days <= 0
        or not available_metrics
    ):
        return {
            "requested_days": requested_days,
            "metric_count": 0,
            "average_coverage": 0.0,
            "coverage_percent": 0.0,
            "total_usable": 0,
            "total_expected": 0,
            "support": "limited",
            "metrics": [],
        }

    metric_results = []

    for metric in available_metrics:
        result = metric_coverage(
            data,
            metric,
            days=days,
        )

        if result is not None:
            metric_results.append(
                result
            )

    total_expected = (
        requested_days
        * len(metric_results)
    )

    total_usable = sum(
        result[
            "usable_count"
        ]
        for result in metric_results
    )

    if total_expected == 0:
        average_coverage = 0.0
    else:
        average_coverage = (
            total_usable
            / total_expected
        )

    equivalent_complete_days = int(
        round(
            average_coverage
            * requested_days
        )
    )

    support = classify_data_support(
        equivalent_complete_days,
        requested_days,
    )

    return {
        "requested_days": requested_days,
        "metric_count": len(
            metric_results
        ),
        "average_coverage": (
            average_coverage
        ),
        "coverage_percent": (
            average_coverage
            * 100
        ),
        "total_usable": total_usable,
        "total_expected": total_expected,
        "support": support,
        "metrics": metric_results,
    }


def intraday_quality(
    intraday_data,
    metrics=None,
):
    """
    Summarize completeness of the available intraday timeline.
    """

    if intraday_data is None:
        return {
            "sample_count": 0,
            "metric_count": 0,
            "coverage_percent": 0.0,
            "support": "limited",
        }

    if metrics is None:
        metrics = [
            "heart_rate",
            "hrv",
            "glucose",
            "oxygen_saturation",
            "respiratory_rate",
            "wrist_temperature",
        ]

    available_metrics = [
        metric
        for metric in metrics
        if metric in intraday_data.columns
    ]

    sample_count = len(
        intraday_data
    )

    if (
        sample_count == 0
        or not available_metrics
    ):
        return {
            "sample_count": sample_count,
            "metric_count": len(
                available_metrics
            ),
            "coverage_percent": 0.0,
            "support": "limited",
        }

    total_expected = (
        sample_count
        * len(
            available_metrics
        )
    )

    total_usable = sum(
        int(
            intraday_data[
                metric
            ]
            .notna()
            .sum()
        )
        for metric in available_metrics
    )

    coverage = (
        total_usable
        / total_expected
    )

    if (
        coverage >= 0.90
        and sample_count >= 12
    ):
        support = "high"
    elif (
        coverage >= 0.75
        and sample_count >= 8
    ):
        support = "good"
    elif sample_count >= 4:
        support = "moderate"
    else:
        support = "limited"

    return {
        "sample_count": sample_count,
        "metric_count": len(
            available_metrics
        ),
        "coverage_percent": (
            coverage
            * 100
        ),
        "support": support,
    }
