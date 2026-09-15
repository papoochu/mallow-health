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


UNITS = {
    "resting_hr": "bpm",
    "hrv": "ms",
    "systolic_bp": "mmHg",
    "diastolic_bp": "mmHg",
    "glucose": "mg/dL",
    "oxygen_saturation": "%",
    "respiratory_rate": "breaths/min",
    "wrist_temperature": "°F",
    "sleep_hours": "hours",
}


DECIMALS = {
    "resting_hr": 1,
    "hrv": 1,
    "systolic_bp": 1,
    "diastolic_bp": 1,
    "glucose": 1,
    "oxygen_saturation": 1,
    "respiratory_rate": 1,
    "wrist_temperature": 2,
    "sleep_hours": 1,
}


def compare_periods(
    data,
    metric,
    days=7,
):
    """
    Compare the most recent window with the equally sized
    window immediately before it.

    The function is descriptive only. A higher or lower
    value is not labeled as medically good or bad.
    """

    if (
        metric not in data.columns
        or days < 1
        or len(data) < days * 2
    ):
        return None

    current_period = (
        data.iloc[-days:][metric]
        .dropna()
    )

    previous_period = (
        data.iloc[-days * 2:-days][metric]
        .dropna()
    )

    if (
        current_period.empty
        or previous_period.empty
    ):
        return None

    current_average = float(
        current_period.mean()
    )

    previous_average = float(
        previous_period.mean()
    )

    difference = (
        current_average
        - previous_average
    )

    if previous_average == 0:
        percent_change = None
    else:
        percent_change = (
            difference
            / abs(previous_average)
            * 100
        )

    if difference > 0:
        direction = "higher"
        arrow = "↑"
    elif difference < 0:
        direction = "lower"
        arrow = "↓"
    else:
        direction = "about the same"
        arrow = "→"

    return {
        "metric": metric,
        "name": FRIENDLY_NAMES.get(
            metric,
            metric.replace(
                "_",
                " ",
            ).title(),
        ),
        "unit": UNITS.get(
            metric,
            "",
        ),
        "decimals": DECIMALS.get(
            metric,
            1,
        ),
        "days": days,
        "current_average": current_average,
        "previous_average": previous_average,
        "difference": difference,
        "absolute_difference": abs(
            difference
        ),
        "percent_change": percent_change,
        "direction": direction,
        "arrow": arrow,
        "current_count": int(
            current_period.shape[0]
        ),
        "previous_count": int(
            previous_period.shape[0]
        ),
    }


def format_average(
    comparison,
    key,
):
    """
    Format one average stored in a comparison result.
    """

    if comparison is None:
        return "—"

    decimals = comparison[
        "decimals"
    ]

    unit = comparison[
        "unit"
    ]

    value = comparison[
        key
    ]

    if (
        comparison["metric"]
        == "wrist_temperature"
    ):
        number = (
            f"{value:+.{decimals}f}"
        )
    else:
        number = (
            f"{value:.{decimals}f}"
        )

    if unit:
        return (
            f"{number} {unit}"
        )

    return number


def format_difference(
    comparison,
):
    """
    Format the signed change between two periods.
    """

    if comparison is None:
        return "—"

    decimals = comparison[
        "decimals"
    ]

    difference = comparison[
        "difference"
    ]

    unit = comparison[
        "unit"
    ]

    if abs(difference) < 1e-12:
        number = (
            f"{0:.{decimals}f}"
        )
    else:
        number = (
            f"{difference:+.{decimals}f}"
        )

    if unit:
        return (
            f"{number} {unit}"
        )

    return number


def describe_period_comparison(
    data,
    metric,
    days=7,
):
    """
    Return a plain-language comparison of two adjacent periods.
    """

    comparison = compare_periods(
        data,
        metric,
        days=days,
    )

    if comparison is None:
        return (
            "There isn't enough history to compare "
            "those two periods yet."
        )

    current_text = format_average(
        comparison,
        "current_average",
    )

    previous_text = format_average(
        comparison,
        "previous_average",
    )

    if abs(
        comparison["difference"]
    ) < 1e-12:
        change_text = (
            "The two period averages are essentially unchanged."
        )
    else:
        if comparison[
            "percent_change"
        ] is None:
            percent_text = ""
        else:
            percent_text = (
                f" ({abs(comparison['percent_change']):.1f}% "
                f"{comparison['direction']})"
            )

        change_text = (
            f"That is {format_difference(comparison)} overall"
            f"{percent_text}."
        )

    return (
        f"Your average {comparison['name'].lower()} over "
        f"the most recent {days} days was {current_text}. "
        f"In the previous {days} days it was {previous_text}. "
        f"{change_text} This is a descriptive comparison "
        f"and does not say whether the change is medically "
        f"good or bad."
    )


def compare_metrics(
    data,
    metrics,
    days=7,
):
    """
    Compare several metrics across the same adjacent periods.
    """

    results = []

    for metric in metrics:
        comparison = compare_periods(
            data,
            metric,
            days=days,
        )

        if comparison is not None:
            results.append(
                comparison
            )

    return results
