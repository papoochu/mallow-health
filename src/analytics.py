import pandas as pd


def get_latest_values(data):
    """
    Return the most recent health measurements.
    """

    latest = data.iloc[-1]

    return {
        "date": latest["date"],
        "resting_hr": latest["resting_hr"],
        "hrv": latest["hrv"],
        "systolic_bp": latest["systolic_bp"],
        "diastolic_bp": latest["diastolic_bp"],
        "pulse_pressure": latest["pulse_pressure"],
        "map": latest["map"],
        "glucose": latest["glucose"],
        "oxygen_saturation": latest["oxygen_saturation"],
        "respiratory_rate": latest["respiratory_rate"],
        "wrist_temperature": latest["wrist_temperature"],
        "sleep_hours": latest["sleep_hours"],
        "deep_sleep_hours": latest["deep_sleep_hours"],
        "rem_sleep_hours": latest["rem_sleep_hours"],
    }


def get_baseline(data, days=30):
    """
    Calculate a rolling personal baseline using the most recent
    number of days.
    """

    recent = data.tail(days)

    numeric_columns = recent.select_dtypes(
        include="number"
    )

    return numeric_columns.mean()


def get_standard_deviation(data, days=30):
    """
    Calculate variation in each health measurement over the
    baseline period.
    """

    recent = data.tail(days)

    numeric_columns = recent.select_dtypes(
        include="number"
    )

    return numeric_columns.std()


def get_deviation_from_baseline(
    data,
    metric,
    days=30,
):
    """
    Compare the latest measurement against its recent baseline.
    """

    latest = data.iloc[-1][metric]

    baseline = data.tail(days)[metric].mean()

    return latest - baseline


def get_percent_change_from_baseline(
    data,
    metric,
    days=30,
):
    """
    Calculate the percent difference between today's value
    and the recent baseline.
    """

    latest = data.iloc[-1][metric]

    baseline = data.tail(days)[metric].mean()

    if baseline == 0:
        return 0

    return (
        (latest - baseline)
        / baseline
        * 100
    )


def get_z_score(
    data,
    metric,
    days=30,
):
    """
    Measure how unusual the latest value is compared with
    the person's recent history.

    A z-score near 0 means the value is close to baseline.
    Larger positive or negative values indicate greater
    deviation.
    """

    recent = data.tail(days)

    latest = recent.iloc[-1][metric]

    baseline = recent[metric].mean()

    std = recent[metric].std()

    if std == 0:
        return 0

    return (
        latest - baseline
    ) / std


def get_health_summary(
    data,
    baseline_days=30,
):
    """
    Build a compact summary for the dashboard and,
    eventually, the Mallow assistant.
    """

    latest = get_latest_values(data)

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
        summary["deviations"][metric] = (
            get_deviation_from_baseline(
                data,
                metric,
                baseline_days,
            )
        )

        summary["z_scores"][metric] = (
            get_z_score(
                data,
                metric,
                baseline_days,
            )
        )

    return summary

def get_baseline_status(
    data,
    metric,
    days=30,
):
    """
    Describe how different the latest measurement is from
    the person's recent baseline.

    This is a personal-baseline comparison only.
    It is not a clinical interpretation.
    """

    z_score = get_z_score(
        data,
        metric,
        days,
    )

    if abs(z_score) < 1:
        return {
            "label": "Near your usual range",
            "level": "typical",
            "z_score": z_score,
        }

    if abs(z_score) < 2:
        direction = (
            "above"
            if z_score > 0
            else "below"
        )

        return {
            "label": f"Somewhat {direction} your baseline",
            "level": "watch",
            "z_score": z_score,
        }

    direction = (
        "above"
        if z_score > 0
        else "below"
    )

    return {
        "label": f"Unusually {direction} your baseline",
        "level": "unusual",
        "z_score": z_score,
    }