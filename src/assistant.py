from src.analytics import get_health_summary
from src.anomaly import detect_current_anomaly
from src.insights import build_anomaly_insight
from src.relationships import (
    describe_relationship,
    strongest_relationships,
    FRIENDLY_NAMES,
)


METRIC_ALIASES = {
    "resting heart rate": "resting_hr",
    "heart rate": "resting_hr",
    "hrv": "hrv",
    "heart-rate variability": "hrv",
    "heart rate variability": "hrv",
    "blood pressure": "systolic_bp",
    "systolic": "systolic_bp",
    "diastolic": "diastolic_bp",
    "blood sugar": "glucose",
    "glucose": "glucose",
    "oxygen saturation": "oxygen_saturation",
    "blood oxygen": "oxygen_saturation",
    "spo2": "oxygen_saturation",
    "respiratory rate": "respiratory_rate",
    "breathing rate": "respiratory_rate",
    "breathing": "respiratory_rate",
    "wrist temperature": "wrist_temperature",
    "temperature": "wrist_temperature",
    "sleep duration": "sleep_hours",
    "sleep": "sleep_hours",
}


RELATIONSHIP_PHRASES = [
    "related",
    "relationship",
    "correlated",
    "correlation",
    "associated",
    "association",
    "linked",
    "affect",
]


def compare_periods(data, metric, days=7):
    """
    Compare the most recent period with the period immediately before it.
    """

    if len(data) < days * 2:
        return None

    current_period = data.iloc[-days:]
    previous_period = data.iloc[-days * 2:-days]

    current_avg = current_period[metric].mean()
    previous_avg = previous_period[metric].mean()

    difference = (
        current_avg
        - previous_avg
    )

    if previous_avg == 0:
        percent_change = 0
    else:
        percent_change = (
            difference
            / previous_avg
            * 100
        )

    return {
        "current_average": current_avg,
        "previous_average": previous_avg,
        "difference": difference,
        "percent_change": percent_change,
    }


def direction_word(value):
    """
    Convert a numeric difference into simple language.
    """

    if value > 0:
        return "higher"

    if value < 0:
        return "lower"

    return "about the same"


def extract_metrics(question):
    """
    Find health metrics mentioned in a natural-language question.

    Returns unique metric names in the order they appear.
    """

    question = question.lower()

    matches = []

    aliases = sorted(
        METRIC_ALIASES.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    )

    for phrase, metric in aliases:
        position = question.find(phrase)

        if position != -1:
            matches.append(
                (
                    position,
                    metric,
                )
            )

    matches.sort(
        key=lambda item: item[0]
    )

    metrics = []

    for _, metric in matches:
        if metric not in metrics:
            metrics.append(metric)

    return metrics


def is_relationship_question(question):
    """
    Determine whether the user is asking about a relationship
    between measurements.
    """

    return any(
        phrase in question
        for phrase in RELATIONSHIP_PHRASES
    )


def describe_top_relationships(
    data,
    target_metric,
    days=30,
):
    """
    Describe the measurements most strongly associated with
    a selected metric.
    """

    relationships = strongest_relationships(
        data,
        target_metric,
        days=days,
        top_n=3,
    )

    if not relationships:
        return (
            "I don't have enough usable data to compare "
            "that measurement with the others yet."
        )

    pieces = []

    for item in relationships:
        metric = item["metric"]
        correlation = item["correlation"]

        readable_name = FRIENDLY_NAMES.get(
            metric,
            metric.replace("_", " "),
        )

        pieces.append(
            f"{readable_name} "
            f"(r = {correlation:.2f})"
        )

    target_name = FRIENDLY_NAMES.get(
        target_metric,
        target_metric.replace("_", " "),
    )

    return (
        f"The strongest statistical relationships with "
        f"{target_name} over the last {days} days are "
        + ", ".join(pieces)
        + ". These are correlations in the available data "
        + "and do not show that one measurement caused another."
    )


def ask_mallow(
    question,
    data,
    analysis_days=30,
):
    """
    Answer questions about health data using deterministic analysis.

    analysis_days controls the personal baseline and relationship
    window used by Mallow.
    """

    question = question.lower().strip()

    summary = get_health_summary(
        data,
        baseline_days=analysis_days,
    )

    latest = summary["latest"]
    baseline = summary["baseline"]

    mentioned_metrics = extract_metrics(
        question
    )

    # Relationship questions
    if is_relationship_question(question):

        if len(mentioned_metrics) >= 2:
            metric_a = mentioned_metrics[0]
            metric_b = mentioned_metrics[1]

            return describe_relationship(
                data,
                metric_a,
                metric_b,
                days=analysis_days,
            )

        if len(mentioned_metrics) == 1:
            return describe_top_relationships(
                data,
                mentioned_metrics[0],
                days=analysis_days,
            )

    # Anomaly questions
    if any(
        phrase in question
        for phrase in [
            "unusual",
            "different today",
            "weird today",
            "anything wrong",
            "what changed today",
            "anything different",
        ]
    ):
        anomaly_result = detect_current_anomaly(
            data
        )

        return build_anomaly_insight(
            anomaly_result
        )

    # Resting heart rate
    if (
        "heart rate" in question
        or "resting heart" in question
    ):
        trend = compare_periods(
            data,
            "resting_hr",
            days=7,
        )

        if trend is None:
            return (
                "I don't have enough heart-rate history "
                "to compare recent weeks yet."
            )

        direction = direction_word(
            trend["difference"]
        )

        return (
            f"Your average resting heart rate over the last "
            f"7 days was {trend['current_average']:.1f} bpm. "
            f"That is {abs(trend['difference']):.1f} bpm "
            f"{direction} than the previous 7 days. "
            f"Your {analysis_days}-day personal baseline is "
            f"{baseline['resting_hr']:.1f} bpm."
        )

    # HRV
    if "hrv" in question:
        trend = compare_periods(
            data,
            "hrv",
            days=7,
        )

        if trend is None:
            return (
                "I don't have enough HRV history "
                "to compare recent weeks yet."
            )

        direction = direction_word(
            trend["difference"]
        )

        return (
            f"Your average HRV over the last 7 days was "
            f"{trend['current_average']:.1f} ms. "
            f"That is {abs(trend['difference']):.1f} ms "
            f"{direction} than the previous 7 days. "
            f"Your {analysis_days}-day personal baseline is "
            f"{baseline['hrv']:.1f} ms."
        )

    # Sleep
    if "sleep" in question:
        trend = compare_periods(
            data,
            "sleep_hours",
            days=7,
        )

        if trend is None:
            return (
                "I don't have enough sleep history "
                "to compare recent weeks yet."
            )

        direction = direction_word(
            trend["difference"]
        )

        return (
            f"You averaged {trend['current_average']:.1f} hours "
            f"of sleep per night over the last 7 days. "
            f"That is {abs(trend['difference']):.1f} hours "
            f"{direction} than the previous week. "
            f"Your {analysis_days}-day average is "
            f"{baseline['sleep_hours']:.1f} hours."
        )

    # Glucose
    if (
        "glucose" in question
        or "blood sugar" in question
    ):
        trend = compare_periods(
            data,
            "glucose",
            days=7,
        )

        if trend is None:
            return (
                "I don't have enough glucose history "
                "to compare recent weeks yet."
            )

        direction = direction_word(
            trend["difference"]
        )

        return (
            f"Your average glucose over the last 7 days was "
            f"{trend['current_average']:.1f} mg/dL. "
            f"That is {abs(trend['difference']):.1f} mg/dL "
            f"{direction} than the previous 7 days. "
            f"Your {analysis_days}-day personal baseline is "
            f"{baseline['glucose']:.1f} mg/dL."
        )

    # Blood pressure
    if (
        "blood pressure" in question
        or "bp" in question
    ):
        systolic = compare_periods(
            data,
            "systolic_bp",
            days=7,
        )

        diastolic = compare_periods(
            data,
            "diastolic_bp",
            days=7,
        )

        if (
            systolic is None
            or diastolic is None
        ):
            return (
                "I don't have enough blood-pressure history "
                "to compare recent weeks yet."
            )

        return (
            f"Your average blood pressure over the last 7 days "
            f"was approximately "
            f"{systolic['current_average']:.0f}/"
            f"{diastolic['current_average']:.0f} mmHg. "
            f"Your {analysis_days}-day personal baseline is "
            f"approximately "
            f"{baseline['systolic_bp']:.0f}/"
            f"{baseline['diastolic_bp']:.0f} mmHg."
        )

    # Respiratory rate
    if (
        "respiratory" in question
        or "breathing" in question
    ):
        latest_value = latest[
            "respiratory_rate"
        ]

        baseline_value = baseline[
            "respiratory_rate"
        ]

        difference = (
            latest_value
            - baseline_value
        )

        direction = direction_word(
            difference
        )

        return (
            f"Your latest respiratory rate is "
            f"{latest_value:.1f} breaths per minute. "
            f"That is {abs(difference):.1f} "
            f"{direction} than your {analysis_days}-day "
            f"personal baseline of {baseline_value:.1f}."
        )

    # Oxygen saturation
    if (
        "oxygen" in question
        or "spo2" in question
    ):
        return (
            f"Your latest oxygen saturation is "
            f"{latest['oxygen_saturation']:.1f}%. "
            f"Your {analysis_days}-day personal average is "
            f"{baseline['oxygen_saturation']:.1f}%."
        )

    # Temperature
    if (
        "temperature" in question
        or "temp" in question
    ):
        baseline_value = baseline[
            "wrist_temperature"
        ]

        latest_value = latest[
            "wrist_temperature"
        ]

        difference = (
            latest_value
            - baseline_value
        )

        direction = direction_word(
            difference
        )

        return (
            f"Your latest synthetic wrist-temperature deviation "
            f"is {latest_value:+.2f} °F. "
            f"That is {abs(difference):.2f} °F "
            f"{direction} than your {analysis_days}-day "
            f"personal average."
        )

    # General summary
    if any(
        phrase in question
        for phrase in [
            "how am i",
            "summary",
            "today",
            "how do i look",
        ]
    ):
        anomaly_result = detect_current_anomaly(
            data
        )

        return build_anomaly_insight(
            anomaly_result
        )

    # Fallback
    return (
        "I can currently answer questions about heart rate, HRV, "
        "blood pressure, glucose, sleep, respiratory rate, oxygen "
        "saturation, temperature, statistical anomalies, and "
        "relationships between your measurements. 🌿"
    )