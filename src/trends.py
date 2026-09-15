import numpy as np

from src.data_quality import classify_data_support


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
    "sleep_hours": "h",
}


MIN_TREND_SAMPLES = 5


def analyze_trend(
    data,
    metric,
    days=30,
):
    """
    Estimate the direction and consistency of a recent metric trend.

    A simple least-squares line is used only to summarize direction.
    The result is descriptive and should not be treated as a clinical
    interpretation or prediction.
    """

    if metric not in data.columns:
        return None

    recent = (
        data.tail(days)[metric]
        .dropna()
        .astype(float)
    )

    if len(recent) < MIN_TREND_SAMPLES:
        return None

    values = recent.to_numpy()
    x = np.arange(
        len(values),
        dtype=float,
    )

    spread = float(
        np.std(
            values,
            ddof=1,
        )
    )

    mean_value = float(
        np.mean(values)
    )

    if (
        not np.isfinite(spread)
        or spread < 1e-9
    ):
        return {
            "metric": metric,
            "name": FRIENDLY_NAMES.get(
                metric,
                metric.replace("_", " ").title(),
            ),
            "unit": UNITS.get(metric, ""),
            "days": days,
            "sample_count": len(values),
            "data_support": classify_data_support(
                len(values),
                min(
                    days,
                    len(data),
                ),
            ),
            "direction": "stable",
            "label": "No clear trend",
            "strength": "minimal",
            "consistency": "high",
            "change": 0.0,
            "slope_per_day": 0.0,
            "r_squared": 0.0,
            "latest": float(values[-1]),
            "average": mean_value,
        }

    slope, intercept = np.polyfit(
        x,
        values,
        1,
    )

    fitted = (
        slope * x
        + intercept
    )

    change = float(
        fitted[-1]
        - fitted[0]
    )

    normalized_change = abs(
        change
    ) / spread

    correlation = np.corrcoef(
        x,
        values,
    )[0, 1]

    if np.isfinite(correlation):
        r_squared = float(
            correlation ** 2
        )
    else:
        r_squared = 0.0

    if (
        normalized_change < 0.35
        or r_squared < 0.15
    ):
        direction = "stable"
        label = "No clear trend"
        strength = "minimal"

    elif change > 0:
        direction = "up"

        if (
            normalized_change >= 1.0
            and r_squared >= 0.50
        ):
            label = "Clearly increasing"
            strength = "clear"
        else:
            label = "Gradually increasing"
            strength = "gradual"

    else:
        direction = "down"

        if (
            normalized_change >= 1.0
            and r_squared >= 0.50
        ):
            label = "Clearly decreasing"
            strength = "clear"
        else:
            label = "Gradually decreasing"
            strength = "gradual"

    if r_squared >= 0.60:
        consistency = "high"
    elif r_squared >= 0.30:
        consistency = "moderate"
    else:
        consistency = "low"

    return {
        "metric": metric,
        "name": FRIENDLY_NAMES.get(
            metric,
            metric.replace("_", " ").title(),
        ),
        "unit": UNITS.get(metric, ""),
        "days": days,
        "sample_count": len(values),
        "data_support": classify_data_support(
            len(values),
            min(
                days,
                len(data),
            ),
        ),
        "direction": direction,
        "label": label,
        "strength": strength,
        "consistency": consistency,
        "change": change,
        "slope_per_day": float(slope),
        "r_squared": r_squared,
        "latest": float(values[-1]),
        "average": mean_value,
    }


def format_trend_change(
    trend,
):
    """
    Format the fitted change across the selected window.
    """

    if trend is None:
        return "Not enough data"

    change = trend["change"]
    unit = trend["unit"]

    if abs(change) < 0.05:
        value = "0.0"
    elif abs(change) < 10:
        value = f"{change:+.1f}"
    else:
        value = f"{change:+.0f}"

    if unit:
        return (
            f"{value} {unit} across "
            f"{trend['sample_count']} days"
        )

    return (
        f"{value} across "
        f"{trend['sample_count']} days"
    )


def describe_trend(
    data,
    metric,
    days=30,
):
    """
    Return a short plain-language trend summary.
    """

    trend = analyze_trend(
        data,
        metric,
        days=days,
    )

    if trend is None:
        return (
            "There is not enough recent data to estimate "
            "a trend for this measurement yet."
        )

    if trend["direction"] == "stable":
        return (
            f"{trend['name']} does not show a clear "
            f"upward or downward trend over the last "
            f"{days} days. Data support for this estimate "
            f"is {trend['data_support']}."
        )

    direction_word = (
        "increased"
        if trend["direction"] == "up"
        else "decreased"
    )

    change_text = format_trend_change(
        trend
    )

    return (
        f"{trend['name']} has {direction_word} overall "
        f"across the last {days} days. The fitted trend "
        f"changes by about {change_text}. Data support for "
        f"this estimate is {trend['data_support']}. This "
        f"describes the recent pattern only and is not a "
        f"prediction."
    )
