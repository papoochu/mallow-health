import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from textwrap import dedent

from src.data import generate_health_data
from src.analytics import (
    get_health_summary,
    get_baseline_status,
)
from src.anomaly import detect_current_anomaly
from src.insights import build_anomaly_insight
from src.assistant import ask_mallow
from src.relationships import calculate_correlation


st.set_page_config(
    page_title="Mallow",
    page_icon="🌿",
    layout="wide",
)


# Load synthetic health data
health_data = generate_health_data(
    days=90,
    seed=42,
)

health_summary = get_health_summary(
    health_data,
    baseline_days=30,
)

latest = health_summary["latest"]
baseline = health_summary["baseline"]
z_scores = health_summary["z_scores"]


# Run anomaly analysis
anomaly_result = detect_current_anomaly(
    health_data
)

mallow_insight = build_anomaly_insight(
    anomaly_result
)


# Personal baseline helpers
def status_for(metric):
    return get_baseline_status(
        health_data,
        metric,
        days=30,
    )


def status_style(metric):
    level = status_for(metric)["level"]

    if level == "typical":
        return "good"

    if level == "watch":
        return "watch"

    return "unusual"


def combined_bp_status():
    systolic = status_for(
        "systolic_bp"
    )

    diastolic = status_for(
        "diastolic_bp"
    )

    max_z = max(
        abs(systolic["z_score"]),
        abs(diastolic["z_score"]),
    )

    if max_z < 1:
        return {
            "label": "Near your usual range",
            "level": "typical",
        }

    if max_z < 2:
        return {
            "label": "Somewhat different from baseline",
            "level": "watch",
        }

    return {
        "label": "Unusual for your baseline",
        "level": "unusual",
    }


bp_status = combined_bp_status()

bp_style = (
    "good"
    if bp_status["level"] == "typical"
    else bp_status["level"]
)


# Sidebar
with st.sidebar:
    st.markdown("## Mallow 🌿")

    st.caption(
        "your gentle personal health companion"
    )

    dark_mode = st.toggle(
        "🌙 Dark mode",
        value=False,
    )

    st.divider()

    st.caption(
        "Prototype using synthetic health data."
    )


# Theme colors
if dark_mode:
    colors = {
        "background": "#171C18",
        "card": "#202720",
        "text": "#E8EEE9",
        "heading": "#C1D7C5",
        "muted": "#98A69B",
        "border": "#344238",
        "welcome": "#202C23",
        "welcome_border": "#3A4C3E",
        "insight": "#29242B",
        "insight_border": "#493D47",
        "good_bg": "#27362B",
        "good_text": "#AED0B6",
        "watch_bg": "#3A3426",
        "watch_text": "#D8C597",
        "unusual_bg": "#3B292B",
        "unusual_text": "#E1AFB3",
        "neutral_bg": "#393329",
        "neutral_text": "#D7C7A4",
        "chart_bg": "#202720",
        "chart_grid": "#354139",
        "chart_line": "#A5C4AA",
        "chart_average": "#C6A8B8",
        "input": "#202720",
        "input_text": "#FFFFFF",
        "input_placeholder": "#A9B6AC",
        "input_focus": "#7EA189",
    }

else:
    colors = {
        "background": "#F8F5F0",
        "card": "#FFFFFF",
        "text": "#404A43",
        "heading": "#536B5A",
        "muted": "#7B877E",
        "border": "#E6DED5",
        "welcome": "#EDF3EA",
        "welcome_border": "#D6E2D2",
        "insight": "#F2ECEF",
        "insight_border": "#E5D9DF",
        "good_bg": "#EDF5EF",
        "good_text": "#63856D",
        "watch_bg": "#F4EEDF",
        "watch_text": "#8B7852",
        "unusual_bg": "#F5E7E8",
        "unusual_text": "#97656A",
        "neutral_bg": "#F5F0E6",
        "neutral_text": "#81765F",
        "chart_bg": "#FFFFFF",
        "chart_grid": "#EEE9E3",
        "chart_line": "#7F9D87",
        "chart_average": "#C9B3BE",

        # Keep Ask Mallow dark even in light mode
        "input": "#566B5D",
        "input_text": "#FFFFFF",
        "input_placeholder": "#D5DFD8",
        "input_focus": "#789583",
    }


# Global styling
st.markdown(
    f"""
    <style>

    .stApp {{
        background-color: {colors["background"]};
        color: {colors["text"]};
    }}

    .block-container {{
        max-width: 1500px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }}

    [data-testid="stSidebar"] {{
        background-color: {colors["card"]};
        border-right: 1px solid {colors["border"]};
    }}

    h1, h2, h3 {{
        color: {colors["heading"]} !important;
    }}

    p {{
        color: {colors["text"]};
    }}

    .mallow-header {{
        font-size: 2.8rem;
        font-weight: 700;
        color: {colors["heading"]};
        margin-bottom: 0.1rem;
    }}

    .mallow-subtitle {{
        color: {colors["muted"]};
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }}

    .welcome-card {{
        background-color: {colors["welcome"]};
        color: {colors["text"]};
        border: 1px solid {colors["welcome_border"]};
        border-radius: 20px;
        padding: 1.4rem 1.6rem;
        margin-bottom: 1.4rem;
    }}

    .metric-card {{
        background-color: {colors["card"]};
        color: {colors["text"]};
        border: 1px solid {colors["border"]};
        border-radius: 20px;
        padding: 1.2rem 1.3rem;
        min-height: 155px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.04);
    }}

    .metric-title {{
        color: {colors["muted"]};
        font-size: 0.86rem;
        font-weight: 600;
        margin-bottom: 0.55rem;
    }}

    .metric-value {{
        color: {colors["text"]};
        font-size: 1.7rem;
        font-weight: 700;
        line-height: 1.2;
        margin-bottom: 0.35rem;
    }}

    .metric-detail {{
        color: {colors["muted"]};
        font-size: 0.83rem;
        margin-bottom: 0.55rem;
    }}

    .status-good,
    .status-watch,
    .status-unusual,
    .status-neutral {{
        display: inline-block;
        border-radius: 999px;
        padding: 0.25rem 0.55rem;
        font-size: 0.74rem;
        margin-top: 0.15rem;
    }}

    .status-good {{
        background-color: {colors["good_bg"]};
        color: {colors["good_text"]};
    }}

    .status-watch {{
        background-color: {colors["watch_bg"]};
        color: {colors["watch_text"]};
    }}

    .status-unusual {{
        background-color: {colors["unusual_bg"]};
        color: {colors["unusual_text"]};
    }}

    .status-neutral {{
        background-color: {colors["neutral_bg"]};
        color: {colors["neutral_text"]};
    }}

    .source {{
        color: {colors["muted"]};
        font-size: 0.70rem;
        margin-top: 0.65rem;
    }}

    .insight-card {{
        background-color: {colors["insight"]};
        color: {colors["text"]};
        border: 1px solid {colors["insight_border"]};
        border-radius: 20px;
        padding: 1.35rem 1.5rem;
        margin-bottom: 1rem;
        line-height: 1.65;
    }}

    /* Ask Mallow input */

    [data-testid="stTextInput"] {{
        margin-top: 0.25rem;
    }}

    [data-testid="stTextInput"] div[data-baseweb="input"] {{
        background-color: {colors["input"]} !important;
        border: 1px solid {colors["input"]} !important;
        border-radius: 16px !important;
        box-shadow: none !important;
        overflow: hidden !important;
    }}

    [data-testid="stTextInput"] div[data-baseweb="input"]:hover {{
        border-color: {colors["input_focus"]} !important;
    }}

    [data-testid="stTextInput"] div[data-baseweb="input"]:focus-within {{
        border: 1px solid {colors["input_focus"]} !important;
        box-shadow: none !important;
        outline: none !important;
    }}

    [data-testid="stTextInput"] div[data-baseweb="base-input"] {{
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }}

    [data-testid="stTextInput"] input {{
        background-color: transparent !important;
        color: {colors["input_text"]} !important;
        -webkit-text-fill-color: {colors["input_text"]} !important;
        caret-color: {colors["input_text"]} !important;
        border: none !important;
        border-radius: 0 !important;
        outline: none !important;
        box-shadow: none !important;
        padding: 0.8rem 0.9rem !important;
        opacity: 1 !important;
        font-size: 1rem !important;
    }}

    [data-testid="stTextInput"] input::placeholder {{
        color: {colors["input_placeholder"]} !important;
        -webkit-text-fill-color: {colors["input_placeholder"]} !important;
        opacity: 1 !important;
    }}

    [data-testid="stTabs"] button {{
        color: {colors["muted"]};
    }}

    [data-testid="stTabs"] button[aria-selected="true"] {{
        color: {colors["heading"]};
    }}

    hr {{
        border-color: {colors["border"]};
    }}

    </style>
    """,
    unsafe_allow_html=True,
)


# HTML helper
def render_html(content):
    clean_html = " ".join(
        line.strip()
        for line in dedent(content).strip().splitlines()
    )

    st.markdown(
        clean_html,
        unsafe_allow_html=True,
    )


# Metric card helper
def metric_card(
    icon,
    title,
    value,
    detail,
    status,
    source,
    status_type="good",
):
    return (
        f'<div class="metric-card">'
        f'<div class="metric-title">{icon} {title}</div>'
        f'<div class="metric-value">{value}</div>'
        f'<div class="metric-detail">{detail}</div>'
        f'<div class="status-{status_type}">{status}</div>'
        f'<div class="source">{source}</div>'
        f'</div>'
    )


# Header
render_html(
    """
    <div class="mallow-header">
        Mallow 🌿
    </div>
    """
)

render_html(
    """
    <div class="mallow-subtitle">
        your gentle personal health companion
    </div>
    """
)


# Welcome
render_html(
    f"""
    <div class="welcome-card">
        <b>Good morning ☀️</b>
        <br><br>
        Mallow is comparing today's synthetic measurements
        with your recent personal baseline.
        <br><br>
        <span style="color:{colors["muted"]}">
            Personal baseline comparisons are not clinical diagnoses.
        </span>
    </div>
    """
)


# Tabs
(
    overview_tab,
    heart_tab,
    metabolic_tab,
    sleep_tab,
    relationships_tab,
) = st.tabs(
    [
        "🌿 Overview",
        "❤️ Heart & circulation",
        "🩸 Blood & metabolic",
        "🌙 Sleep & respiratory",
        "📊 Relationships",
    ]
)


# Overview
with overview_tab:

    st.subheader("Today's vitals")

    row1 = st.columns(4)

    with row1[0]:
        heart_status = status_for(
            "resting_hr"
        )

        render_html(
            metric_card(
                "❤️",
                "Resting heart rate",
                f"{latest['resting_hr']:.0f} bpm",
                (
                    f"30-day average: "
                    f"{baseline['resting_hr']:.0f} bpm"
                ),
                heart_status["label"],
                "⌚ Apple Watch",
                status_style(
                    "resting_hr"
                ),
            )
        )

    with row1[1]:
        render_html(
            metric_card(
                "🩸",
                "Blood pressure",
                (
                    f"{latest['systolic_bp']:.0f} / "
                    f"{latest['diastolic_bp']:.0f}"
                ),
                f"MAP: {latest['map']:.0f} mmHg",
                bp_status["label"],
                "🩺 Connected cuff",
                bp_style,
            )
        )

    with row1[2]:
        glucose_status = status_for(
            "glucose"
        )

        render_html(
            metric_card(
                "🍬",
                "Blood glucose",
                f"{latest['glucose']:.0f} mg/dL",
                (
                    f"30-day average: "
                    f"{baseline['glucose']:.0f} mg/dL"
                ),
                glucose_status["label"],
                "🩸 CGM / HealthKit",
                status_style(
                    "glucose"
                ),
            )
        )

    with row1[3]:
        oxygen_status = status_for(
            "oxygen_saturation"
        )

        render_html(
            metric_card(
                "🫁",
                "Oxygen saturation",
                f"{latest['oxygen_saturation']:.1f}%",
                (
                    f"30-day average: "
                    f"{baseline['oxygen_saturation']:.1f}%"
                ),
                oxygen_status["label"],
                "⌚ Apple Watch",
                status_style(
                    "oxygen_saturation"
                ),
            )
        )

    st.write("")

    row2 = st.columns(4)

    with row2[0]:
        hrv_status = status_for(
            "hrv"
        )

        render_html(
            metric_card(
                "💓",
                "HRV",
                f"{latest['hrv']:.0f} ms",
                (
                    f"30-day average: "
                    f"{baseline['hrv']:.0f} ms"
                ),
                hrv_status["label"],
                "⌚ Apple Watch",
                status_style(
                    "hrv"
                ),
            )
        )

    with row2[1]:
        temp_status = status_for(
            "wrist_temperature"
        )

        render_html(
            metric_card(
                "🌡️",
                "Wrist temperature",
                (
                    f"{latest['wrist_temperature']:+.2f} °F"
                ),
                "Deviation from personal baseline",
                temp_status["label"],
                "⌚ Apple Watch",
                status_style(
                    "wrist_temperature"
                ),
            )
        )

    with row2[2]:
        respiratory_status = status_for(
            "respiratory_rate"
        )

        render_html(
            metric_card(
                "🌬️",
                "Respiratory rate",
                (
                    f"{latest['respiratory_rate']:.1f} / min"
                ),
                (
                    f"30-day average: "
                    f"{baseline['respiratory_rate']:.1f}"
                ),
                respiratory_status["label"],
                "⌚ Apple Watch",
                status_style(
                    "respiratory_rate"
                ),
            )
        )

    with row2[3]:
        sleep_status = status_for(
            "sleep_hours"
        )

        render_html(
            metric_card(
                "😴",
                "Sleep",
                f"{latest['sleep_hours']:.1f} h",
                (
                    f"30-day average: "
                    f"{baseline['sleep_hours']:.1f} h"
                ),
                sleep_status["label"],
                "⌚ Apple Watch",
                status_style(
                    "sleep_hours"
                ),
            )
        )

    st.write("")

    st.subheader(
        "30-day heart trend"
    )

    heart_df = (
        health_data
        .tail(30)
        .copy()
    )

    heart_df["date"] = pd.to_datetime(
        heart_df["date"]
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=heart_df["date"],
            y=heart_df["resting_hr"],
            mode="lines+markers",
            line=dict(
                color=colors["chart_line"],
                width=3,
            ),
            marker=dict(
                color=colors["chart_line"],
                size=6,
            ),
            hovertemplate=(
                "%{x|%b %d}<br>"
                "%{y:.1f} bpm"
                "<extra></extra>"
            ),
        )
    )

    fig.add_hline(
        y=baseline["resting_hr"],
        line_dash="dot",
        line_color=colors[
            "chart_average"
        ],
        annotation_text=(
            "30-day average"
        ),
        annotation_font_color=colors[
            "muted"
        ],
    )

    fig.update_layout(
        height=350,
        margin=dict(
            l=25,
            r=25,
            t=25,
            b=25,
        ),
        paper_bgcolor=colors[
            "chart_bg"
        ],
        plot_bgcolor=colors[
            "chart_bg"
        ],
        font=dict(
            color=colors["text"],
        ),
        xaxis=dict(
            title="",
            showgrid=False,
            zeroline=False,
        ),
        yaxis=dict(
            title="bpm",
            gridcolor=colors[
                "chart_grid"
            ],
            zeroline=False,
        ),
        showlegend=False,
        hoverlabel=dict(
            bgcolor=colors["card"],
            font_color=colors["text"],
        ),
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False,
        },
    )

    st.subheader(
        "Mallow noticed 🌱"
    )

    render_html(
        f"""
        <div class="insight-card">
            🌿 <b>Statistical summary</b>
            <br><br>
            {mallow_insight}
            <br><br>
            <span style="color:{colors["muted"]};">
                Mallow is describing statistical patterns only.
                This is not a diagnosis or medical interpretation.
            </span>
        </div>
        """
    )

    st.subheader(
        "Ask Mallow 💬"
    )

    question = st.text_input(
        "Ask something about your health data",
        placeholder=(
            "Does my sleep seem related to my heart rate?"
        ),
        label_visibility="collapsed",
    )

    if question:
        answer = ask_mallow(
            question,
            health_data,
        )

        render_html(
            f"""
            <div class="insight-card">
                🌿 <b>Mallow</b>
                <br><br>
                {answer}
                <br><br>
                <span style="color:{colors["muted"]};">
                    Mallow is summarizing your health data
                    and personal statistical trends.
                    This is not a diagnosis.
                </span>
            </div>
            """
        )


# Heart & circulation
with heart_tab:

    st.subheader(
        "Heart & circulation ❤️"
    )

    row1 = st.columns(3)

    with row1[0]:
        render_html(
            metric_card(
                "❤️",
                "Resting heart rate",
                f"{latest['resting_hr']:.0f} bpm",
                (
                    f"30-day average: "
                    f"{baseline['resting_hr']:.0f} bpm"
                ),
                status_for(
                    "resting_hr"
                )["label"],
                "⌚ Apple Watch",
                status_style(
                    "resting_hr"
                ),
            )
        )

    with row1[1]:
        render_html(
            metric_card(
                "💓",
                "HRV",
                f"{latest['hrv']:.0f} ms",
                (
                    f"30-day average: "
                    f"{baseline['hrv']:.0f} ms"
                ),
                status_for(
                    "hrv"
                )["label"],
                "⌚ Apple Watch",
                status_style(
                    "hrv"
                ),
            )
        )

    with row1[2]:
        render_html(
            metric_card(
                "🫀",
                "Last ECG",
                "—",
                "No ECG demo data yet",
                "Awaiting data",
                "⌚ Apple Watch",
                "neutral",
            )
        )

    st.write("")

    row2 = st.columns(3)

    with row2[0]:
        render_html(
            metric_card(
                "🩸",
                "Blood pressure",
                (
                    f"{latest['systolic_bp']:.0f} / "
                    f"{latest['diastolic_bp']:.0f}"
                ),
                (
                    f"Pulse pressure: "
                    f"{latest['pulse_pressure']:.0f} mmHg"
                ),
                bp_status["label"],
                "🩺 Connected cuff",
                bp_style,
            )
        )

    with row2[1]:
        render_html(
            metric_card(
                "📊",
                "Mean arterial pressure",
                f"{latest['map']:.0f} mmHg",
                "Estimated from cuff measurement",
                bp_status["label"],
                "🌿 Calculated by Mallow",
                bp_style,
            )
        )

    with row2[2]:
        render_html(
            metric_card(
                "🏃",
                "Heart-rate recovery",
                "—",
                "No demo measurement yet",
                "Awaiting data",
                "⌚ Apple Watch",
                "neutral",
            )
        )

    st.write("")

    st.subheader(
        "Rhythm & monitoring"
    )

    row3 = st.columns(3)

    with row3[0]:
        render_html(
            metric_card(
                "💗",
                "Irregular rhythm alerts",
                "—",
                "No demo rhythm history yet",
                "Awaiting data",
                "⌚ Apple Watch",
                "neutral",
            )
        )

    with row3[1]:
        render_html(
            metric_card(
                "🫀",
                "AFib burden",
                "—",
                "No demo measurement",
                "Awaiting data",
                "HealthKit",
                "neutral",
            )
        )

    with row3[2]:
        render_html(
            metric_card(
                "🚶",
                "Walking heart rate",
                "—",
                "No demo measurement yet",
                "Awaiting data",
                "⌚ Apple Watch",
                "neutral",
            )
        )


# Blood & metabolic
with metabolic_tab:

    st.subheader(
        "Blood & metabolic 🩸"
    )

    row1 = st.columns(3)

    with row1[0]:
        render_html(
            metric_card(
                "🍬",
                "Current glucose",
                f"{latest['glucose']:.0f} mg/dL",
                (
                    f"30-day average: "
                    f"{baseline['glucose']:.0f} mg/dL"
                ),
                status_for(
                    "glucose"
                )["label"],
                "🩸 CGM / HealthKit",
                status_style(
                    "glucose"
                ),
            )
        )

    with row1[1]:
        glucose_std = (
            health_data
            .tail(30)["glucose"]
            .std()
        )

        glucose_mean = (
            health_data
            .tail(30)["glucose"]
            .mean()
        )

        glucose_cv = (
            glucose_std
            / glucose_mean
            * 100
        )

        render_html(
            metric_card(
                "📈",
                "Glucose variability",
                f"{glucose_cv:.1f}%",
                "30-day coefficient of variation",
                "Calculated from recent data",
                "🌿 Calculated by Mallow",
                "neutral",
            )
        )

    with row1[2]:
        render_html(
            metric_card(
                "⚖️",
                "Weight",
                "—",
                "No weight data yet",
                "Awaiting data",
                "HealthKit / smart scale",
                "neutral",
            )
        )

    st.write("")

    row2 = st.columns(3)

    with row2[0]:
        render_html(
            metric_card(
                "🩸",
                "Blood pressure",
                (
                    f"{latest['systolic_bp']:.0f} / "
                    f"{latest['diastolic_bp']:.0f}"
                ),
                (
                    f"30-day avg: "
                    f"{baseline['systolic_bp']:.0f} / "
                    f"{baseline['diastolic_bp']:.0f}"
                ),
                bp_status["label"],
                "🩺 Connected cuff",
                bp_style,
            )
        )

    with row2[1]:
        render_html(
            metric_card(
                "💉",
                "Insulin delivery",
                "—",
                "No insulin data yet",
                "Awaiting data",
                "HealthKit",
                "neutral",
            )
        )

    with row2[2]:
        render_html(
            metric_card(
                "🌿",
                "Glucose baseline",
                f"{baseline['glucose']:.0f} mg/dL",
                "Calculated over the last 30 days",
                "Personal reference",
                "Calculated by Mallow",
                "neutral",
            )
        )

    st.write("")

    st.info(
        "Blood glucose and blood-pressure measurements "
        "will come from compatible devices, HealthKit, "
        "or manual entries. Mallow does not directly "
        "measure them."
    )


# Sleep & respiratory
with sleep_tab:

    st.subheader(
        "Sleep & respiratory 🌙"
    )

    deep_percent = (
        latest["deep_sleep_hours"]
        / latest["sleep_hours"]
        * 100
    )

    rem_percent = (
        latest["rem_sleep_hours"]
        / latest["sleep_hours"]
        * 100
    )

    core_sleep = max(
        latest["sleep_hours"]
        - latest["deep_sleep_hours"]
        - latest["rem_sleep_hours"],
        0,
    )

    core_percent = (
        core_sleep
        / latest["sleep_hours"]
        * 100
    )

    row1 = st.columns(4)

    with row1[0]:
        render_html(
            metric_card(
                "😴",
                "Total sleep",
                f"{latest['sleep_hours']:.1f} h",
                (
                    f"30-day average: "
                    f"{baseline['sleep_hours']:.1f} h"
                ),
                status_for(
                    "sleep_hours"
                )["label"],
                "⌚ Apple Watch",
                status_style(
                    "sleep_hours"
                ),
            )
        )

    with row1[1]:
        render_html(
            metric_card(
                "🌙",
                "Deep sleep",
                f"{latest['deep_sleep_hours']:.1f} h",
                f"{deep_percent:.0f}% of total sleep",
                "Latest synthetic night",
                "⌚ Apple Watch",
                "neutral",
            )
        )

    with row1[2]:
        render_html(
            metric_card(
                "💭",
                "REM sleep",
                f"{latest['rem_sleep_hours']:.1f} h",
                f"{rem_percent:.0f}% of total sleep",
                "Latest synthetic night",
                "⌚ Apple Watch",
                "neutral",
            )
        )

    with row1[3]:
        render_html(
            metric_card(
                "🛏️",
                "Core sleep",
                f"{core_sleep:.1f} h",
                f"{core_percent:.0f}% of total sleep",
                "Calculated remainder",
                "🌿 Calculated by Mallow",
                "neutral",
            )
        )

    st.write("")

    row2 = st.columns(4)

    with row2[0]:
        render_html(
            metric_card(
                "🌬️",
                "Respiratory rate",
                (
                    f"{latest['respiratory_rate']:.1f} / min"
                ),
                (
                    f"30-day average: "
                    f"{baseline['respiratory_rate']:.1f}"
                ),
                status_for(
                    "respiratory_rate"
                )["label"],
                "⌚ Apple Watch",
                status_style(
                    "respiratory_rate"
                ),
            )
        )

    with row2[1]:
        render_html(
            metric_card(
                "🫁",
                "Oxygen saturation",
                (
                    f"{latest['oxygen_saturation']:.1f}%"
                ),
                (
                    f"30-day average: "
                    f"{baseline['oxygen_saturation']:.1f}%"
                ),
                status_for(
                    "oxygen_saturation"
                )["label"],
                "⌚ Apple Watch",
                status_style(
                    "oxygen_saturation"
                ),
            )
        )

    with row2[2]:
        render_html(
            metric_card(
                "🌡️",
                "Wrist temperature",
                (
                    f"{latest['wrist_temperature']:+.2f} °F"
                ),
                "Deviation from personal baseline",
                status_for(
                    "wrist_temperature"
                )["label"],
                "⌚ Apple Watch",
                status_style(
                    "wrist_temperature"
                ),
            )
        )

    with row2[3]:
        render_html(
            metric_card(
                "🌘",
                "Night awakenings",
                "—",
                "No demo measurement yet",
                "Awaiting data",
                "⌚ Apple Watch",
                "neutral",
            )
        )


# Relationships
with relationships_tab:

    st.subheader(
        "Relationships 📊"
    )

    st.caption(
        "Explore statistical relationships between your recent "
        "measurements. Correlation does not mean that one measurement "
        "caused another."
    )

    available_metrics = {
        "Sleep duration": "sleep_hours",
        "Resting heart rate": "resting_hr",
        "HRV": "hrv",
        "Systolic blood pressure": "systolic_bp",
        "Diastolic blood pressure": "diastolic_bp",
        "Blood glucose": "glucose",
        "Oxygen saturation": "oxygen_saturation",
        "Respiratory rate": "respiratory_rate",
        "Wrist temperature": "wrist_temperature",
    }

    selector_columns = st.columns(2)

    with selector_columns[0]:
        metric_a_name = st.selectbox(
            "First measurement",
            list(
                available_metrics.keys()
            ),
            index=0,
        )

    with selector_columns[1]:
        metric_b_name = st.selectbox(
            "Second measurement",
            list(
                available_metrics.keys()
            ),
            index=1,
        )

    metric_a = available_metrics[
        metric_a_name
    ]

    metric_b = available_metrics[
        metric_b_name
    ]

    if metric_a == metric_b:

        st.info(
            "Choose two different measurements to compare."
        )

    else:

        relationship_data = (
            health_data
            .tail(30)
            .copy()
        )

        correlation = calculate_correlation(
            relationship_data,
            metric_a,
            metric_b,
            days=30,
        )

        x = relationship_data[
            metric_a
        ].to_numpy()

        y = relationship_data[
            metric_b
        ].to_numpy()

        slope, intercept = np.polyfit(
            x,
            y,
            1,
        )

        x_line = np.linspace(
            x.min(),
            x.max(),
            100,
        )

        y_line = (
            slope * x_line
            + intercept
        )

        fig_relationship = go.Figure()

        fig_relationship.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="markers",
                name="Daily measurements",
                marker=dict(
                    size=9,
                    color=colors[
                        "chart_line"
                    ],
                    opacity=0.75,
                ),
                hovertemplate=(
                    f"{metric_a_name}: "
                    "%{x:.2f}"
                    "<br>"
                    f"{metric_b_name}: "
                    "%{y:.2f}"
                    "<extra></extra>"
                ),
            )
        )

        fig_relationship.add_trace(
            go.Scatter(
                x=x_line,
                y=y_line,
                mode="lines",
                name="Trend",
                line=dict(
                    color=colors[
                        "chart_average"
                    ],
                    width=3,
                    dash="dot",
                ),
            )
        )

        fig_relationship.update_layout(
            height=450,
            paper_bgcolor=colors[
                "chart_bg"
            ],
            plot_bgcolor=colors[
                "chart_bg"
            ],
            font=dict(
                color=colors["text"],
            ),
            xaxis=dict(
                title=metric_a_name,
                gridcolor=colors[
                    "chart_grid"
                ],
                zeroline=False,
            ),
            yaxis=dict(
                title=metric_b_name,
                gridcolor=colors[
                    "chart_grid"
                ],
                zeroline=False,
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
            ),
            hoverlabel=dict(
                bgcolor=colors["card"],
                font_color=colors["text"],
            ),
            margin=dict(
                l=30,
                r=30,
                t=55,
                b=30,
            ),
        )

        st.plotly_chart(
            fig_relationship,
            use_container_width=True,
            config={
                "displayModeBar": False,
            },
        )

        if correlation is not None:

            if abs(correlation) < 0.2:
                strength = "very little"

            elif abs(correlation) < 0.4:
                strength = "a weak"

            elif abs(correlation) < 0.6:
                strength = "a moderate"

            elif abs(correlation) < 0.8:
                strength = "a fairly strong"

            else:
                strength = "a strong"

            if correlation > 0:
                direction = "positive"

            elif correlation < 0:
                direction = "negative"

            else:
                direction = "neutral"

            render_html(
                f"""
                <div class="insight-card">
                    🌿 <b>Mallow's observation</b>
                    <br><br>
                    Over the last 30 days, I found
                    {strength} {direction} relationship
                    between {metric_a_name.lower()} and
                    {metric_b_name.lower()}
                    (r = {correlation:.2f}).
                    <br><br>
                    <span style="color:{colors["muted"]};">
                        This describes an association in the data.
                        It does not show that one measurement caused
                        the other.
                    </span>
                </div>
                """
            )


# Footer
st.write("")
st.divider()

st.caption(
    "Mallow is a personal health-monitoring project and is not intended "
    "for diagnosis, treatment, or clinical use. "
    "Baseline labels describe statistical differences from personal "
    "history, not whether a measurement is medically normal. "
    "All measurements shown in this prototype are synthetic."
)