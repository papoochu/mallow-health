import re

from src.analytics import get_health_summary
from src.anomaly import detect_current_anomaly
from src.insights import build_anomaly_insight
from src.relationships import (
    describe_relationship,
    strongest_relationships,
    FRIENDLY_NAMES,
)
from src.trends import (
    analyze_trend,
    describe_trend,
)
from src.comparisons import (
    describe_period_comparison,
)


METRIC_ALIASES = {
    "resting heart rate": "resting_hr",
    "resting hr": "resting_hr",
    "heart rate": "resting_hr",
    "hrv": "hrv",
    "heart-rate variability": "hrv",
    "heart rate variability": "hrv",
    "systolic blood pressure": "systolic_bp",
    "systolic pressure": "systolic_bp",
    "systolic": "systolic_bp",
    "diastolic blood pressure": "diastolic_bp",
    "diastolic pressure": "diastolic_bp",
    "diastolic": "diastolic_bp",
    "blood pressure": "systolic_bp",
    "bp": "systolic_bp",
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
    "temp": "wrist_temperature",
    "sleep duration": "sleep_hours",
    "sleep": "sleep_hours",
}


METRIC_UNITS = {
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


RELATIONSHIP_PHRASES = [
    "related",
    "relationship",
    "correlated",
    "correlation",
    "associated",
    "association",
    "linked",
    "move together",
    "affect",
]


TREND_PHRASES = [
    "trend",
    "trending",
    "over time",
    "increasing",
    "decreasing",
    "going up",
    "going down",
    "rising",
    "falling",
    "changing",
    "change over",
    "direction",
]


ANOMALY_PHRASES = [
    "unusual",
    "different today",
    "weird today",
    "anything wrong",
    "what changed today",
    "anything different",
    "out of the ordinary",
    "abnormal for me",
]


SUMMARY_PHRASES = [
    "how am i",
    "summary",
    "how do i look",
    "overall",
    "overview",
]


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
    Longer aliases are matched first so phrases such as
    'heart rate variability' are not reduced to 'heart rate'.
    """

    question = question.lower()

    matches = []

    aliases = sorted(
        METRIC_ALIASES.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    )

    occupied_ranges = []

    for phrase, metric in aliases:
        start = 0

        while True:
            position = question.find(
                phrase,
                start,
            )

            if position == -1:
                break

            end = (
                position
                + len(phrase)
            )

            overlaps = any(
                position < used_end
                and end > used_start
                for used_start, used_end
                in occupied_ranges
            )

            if not overlaps:
                matches.append(
                    (
                        position,
                        metric,
                        phrase,
                    )
                )

                occupied_ranges.append(
                    (
                        position,
                        end,
                    )
                )

            start = end

    matches.sort(
        key=lambda item: item[0]
    )

    metrics = []

    for _, metric, _ in matches:
        if metric not in metrics:
            metrics.append(metric)

    return metrics


def extract_requested_days(
    question,
    default_days=30,
):
    """
    Extract a requested analysis window from common natural language.

    Falls back to the dashboard-selected analysis window when the
    question does not explicitly name a period.
    """

    question = question.lower()

    day_match = re.search(
        r"(?:last|past|previous|over|for)?\s*"
        r"(\d{1,3})\s*days?",
        question,
    )

    if day_match:
        days = int(
            day_match.group(1)
        )

        return max(
            5,
            min(
                days,
                365,
            ),
        )

    if any(
        phrase in question
        for phrase in [
            "three months",
            "3 months",
            "three month",
            "3 month",
            "quarter",
        ]
    ):
        return 90

    if any(
        phrase in question
        for phrase in [
            "two months",
            "2 months",
            "two month",
            "2 month",
        ]
    ):
        return 60

    if any(
        phrase in question
        for phrase in [
            "this month",
            "last month",
            "past month",
            "one month",
            "1 month",
            "30 days",
        ]
    ):
        return 30

    if any(
        phrase in question
        for phrase in [
            "two weeks",
            "2 weeks",
            "two week",
            "2 week",
            "14 days",
        ]
    ):
        return 14

    if any(
        phrase in question
        for phrase in [
            "this week",
            "last week",
            "past week",
            "one week",
            "1 week",
            "7 days",
        ]
    ):
        return 7

    return default_days


def is_relationship_question(question):
    """
    Determine whether the user is asking about a relationship
    between measurements.
    """

    return any(
        phrase in question
        for phrase in RELATIONSHIP_PHRASES
    )


def is_trend_question(question):
    """
    Determine whether the user is asking about change over time.
    """

    return any(
        phrase in question
        for phrase in TREND_PHRASES
    )


def readable_metric_name(metric):
    return FRIENDLY_NAMES.get(
        metric,
        metric.replace(
            "_",
            " ",
        ),
    )


def format_metric_value(
    metric,
    value,
):
    """
    Format a metric value with an appropriate precision and unit.
    """

    unit = METRIC_UNITS.get(
        metric,
        "",
    )

    if metric == "wrist_temperature":
        return (
            f"{value:+.2f} {unit}"
        )

    if metric in {
        "oxygen_saturation",
        "respiratory_rate",
        "sleep_hours",
    }:
        return (
            f"{value:.1f} {unit}"
        )

    if metric in {
        "resting_hr",
        "hrv",
        "systolic_bp",
        "diastolic_bp",
        "glucose",
    }:
        return (
            f"{value:.1f} {unit}"
        )

    return f"{value:.2f}"


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
        readable_name = readable_metric_name(
            item["metric"]
        )

        pieces.append(
            f"{readable_name} "
            f"(r = {item['correlation']:.2f})"
        )

    target_name = readable_metric_name(
        target_metric
    )

    return (
        f"The strongest statistical relationships with "
        f"{target_name} over the last {days} days are "
        + ", ".join(pieces)
        + ". These are correlations in the available data "
        + "and do not show that one measurement caused another."
    )


def describe_metric_snapshot(
    data,
    metric,
    days=30,
):
    """
    Describe the latest value relative to a recent personal average.
    """

    if metric not in data.columns:
        return (
            "I don't have that measurement in the current data."
        )

    recent = (
        data.tail(days)[metric]
        .dropna()
    )

    if recent.empty:
        return (
            "I don't have enough recent data for that measurement yet."
        )

    latest_value = float(
        recent.iloc[-1]
    )

    average_value = float(
        recent.mean()
    )

    difference = (
        latest_value
        - average_value
    )

    name = readable_metric_name(
        metric
    )

    latest_text = format_metric_value(
        metric,
        latest_value,
    )

    average_text = format_metric_value(
        metric,
        average_value,
    )

    if abs(difference) < 1e-9:
        comparison = (
            "about the same as"
        )
    else:
        comparison = (
            f"{direction_word(difference)} than"
        )

    return (
        f"Your latest {name} is {latest_text}. "
        f"That is {comparison} your {days}-day personal "
        f"average of {average_text}. This is a descriptive "
        f"comparison, not a clinical interpretation."
    )


def describe_metric_average(
    data,
    metric,
    days=30,
):
    """
    Return the recent average for one metric.
    """

    if metric not in data.columns:
        return (
            "I don't have that measurement in the current data."
        )

    recent = (
        data.tail(days)[metric]
        .dropna()
    )

    if recent.empty:
        return (
            "I don't have enough recent data for that measurement yet."
        )

    average_value = float(
        recent.mean()
    )

    name = readable_metric_name(
        metric
    )

    return (
        f"Your average {name} over the last {len(recent)} days "
        f"is {format_metric_value(metric, average_value)}."
    )


def describe_blood_pressure(
    data,
    days=30,
):
    """
    Describe recent systolic and diastolic pressure together.
    """

    needed = [
        "systolic_bp",
        "diastolic_bp",
    ]

    if any(
        metric not in data.columns
        for metric in needed
    ):
        return (
            "I don't have enough blood-pressure data yet."
        )

    recent = (
        data.tail(days)[needed]
        .dropna()
    )

    if recent.empty:
        return (
            "I don't have enough blood-pressure data yet."
        )

    latest = recent.iloc[-1]

    systolic_avg = float(
        recent["systolic_bp"].mean()
    )

    diastolic_avg = float(
        recent["diastolic_bp"].mean()
    )

    return (
        f"Your latest blood pressure is approximately "
        f"{latest['systolic_bp']:.0f}/"
        f"{latest['diastolic_bp']:.0f} mmHg. "
        f"Across the last {len(recent)} days, your average is "
        f"approximately {systolic_avg:.0f}/"
        f"{diastolic_avg:.0f} mmHg. "
        f"Mallow treats this as a personal data summary, "
        f"not a diagnosis."
    )


def describe_overall_trends(
    data,
    days=30,
):
    """
    Summarize the clearest recent trends across core measurements.
    """

    metrics = [
        "resting_hr",
        "hrv",
        "sleep_hours",
        "glucose",
        "systolic_bp",
        "respiratory_rate",
    ]

    trends = []

    for metric in metrics:
        trend = analyze_trend(
            data,
            metric,
            days=days,
        )

        if (
            trend is not None
            and trend["direction"] != "stable"
        ):
            trends.append(
                trend
            )

    if not trends:
        return (
            f"I don't see a clear upward or downward trend "
            f"among the main measurements over the last "
            f"{days} days. That does not mean every value was "
            f"unchanged—just that the data do not show a "
            f"consistent direction."
        )

    trends.sort(
        key=lambda item: (
            item["r_squared"],
            abs(
                item["change"]
            ),
        ),
        reverse=True,
    )

    pieces = []

    for trend in trends[:3]:
        direction = (
            "up"
            if trend["direction"] == "up"
            else "down"
        )

        pieces.append(
            f"{trend['name'].lower()} is trending {direction}"
        )

    return (
        f"The clearest recent patterns over the last {days} days are: "
        + "; ".join(pieces)
        + ". These are descriptive trends in your data and are "
        + "not predictions or medical conclusions."
    )


def ask_mallow(
    question,
    data,
    analysis_days=30,
):
    """
    Answer natural-language questions about Mallow health data.

    `analysis_days` is the default analysis window supplied by the
    dashboard. If the question explicitly names another period,
    that period takes precedence.
    """

    question = question.lower().strip()

    requested_days = extract_requested_days(
        question,
        default_days=analysis_days,
    )

    days = min(
        requested_days,
        len(data),
    )

    summary_days = min(
        max(
            days,
            5,
        ),
        len(data),
    )

    mentioned_metrics = extract_metrics(
        question
    )

    # Relationship questions.
    if is_relationship_question(
        question
    ):
        if len(mentioned_metrics) >= 2:
            return describe_relationship(
                data,
                mentioned_metrics[0],
                mentioned_metrics[1],
                days=summary_days,
            )

        if len(mentioned_metrics) == 1:
            return describe_top_relationships(
                data,
                mentioned_metrics[0],
                days=summary_days,
            )

        return (
            "Tell me which measurement you want to explore, "
            "for example: “What is related to my HRV?” or "
            "“Does sleep seem related to resting heart rate?”"
        )

    # Trend questions use the trend engine directly.
    if is_trend_question(
        question
    ):
        if mentioned_metrics:
            metric = mentioned_metrics[0]

            if (
                "blood pressure" in question
                and metric == "systolic_bp"
            ):
                systolic = describe_trend(
                    data,
                    "systolic_bp",
                    days=summary_days,
                )

                diastolic = describe_trend(
                    data,
                    "diastolic_bp",
                    days=summary_days,
                )

                return (
                    f"Systolic: {systolic} "
                    f"Diastolic: {diastolic}"
                )

            return describe_trend(
                data,
                metric,
                days=summary_days,
            )

        return describe_overall_trends(
            data,
            days=summary_days,
        )

    # Today's unusual combination / anomaly questions.
    if any(
        phrase in question
        for phrase in ANOMALY_PHRASES
    ):
        anomaly_result = detect_current_anomaly(
            data
        )

        return build_anomaly_insight(
            anomaly_result
        )

    # Explicit period-to-period comparison.
    if (
        "previous week" in question
        or "week before" in question
        or "compared with last week" in question
        or "compared to last week" in question
        or "compare this week" in question
    ):
        if mentioned_metrics:
            return describe_period_comparison(
                data,
                mentioned_metrics[0],
                days=7,
            )

    # Blood pressure is best treated as a pair.
    if (
        "blood pressure" in question
        or re.search(
            r"\bbp\b",
            question,
        )
    ):
        return describe_blood_pressure(
            data,
            days=summary_days,
        )

    # Metric-specific questions.
    if mentioned_metrics:
        metric = mentioned_metrics[0]

        if (
            "average" in question
            or "mean" in question
        ):
            return describe_metric_average(
                data,
                metric,
                days=summary_days,
            )

        return describe_metric_snapshot(
            data,
            metric,
            days=summary_days,
        )

    # General summary / anomaly summary.
    if any(
        phrase in question
        for phrase in SUMMARY_PHRASES
    ):
        anomaly_result = detect_current_anomaly(
            data
        )

        anomaly_summary = build_anomaly_insight(
            anomaly_result
        )

        trend_summary = describe_overall_trends(
            data,
            days=summary_days,
        )

        return (
            f"{anomaly_summary} {trend_summary}"
        )

    # Fallback.
    return (
        "I can answer questions about your recent values, personal "
        "averages, trends, unusual patterns, and relationships between "
        "measurements. Try asking “How is my HRV trending?”, "
        "“What is related to my sleep?”, “What was my average glucose "
        "over the last 30 days?”, or “Anything unusual today?” 🌿"
    )
