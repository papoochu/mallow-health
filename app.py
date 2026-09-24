import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from textwrap import dedent

from src.data import (
    generate_health_data,
    generate_intraday_data,
)
from src.analytics import (
    get_health_summary,
    get_baseline_status,
)
from src.anomaly import detect_current_anomaly
from src.insights import build_anomaly_insight
from src.assistant import ask_mallow
from src.relationships import (
    all_relationships,
    calculate_correlation,
    describe_relationship,
    get_relationship_data,
)
from src.trends import (
    analyze_trend,
    format_trend_change,
)
from src.comparisons import (
    compare_metrics,
    format_average,
    format_difference,
)
from src.data_quality import (
    intraday_quality,
    window_quality,
)
from src.apple_health import load_apple_health_export


st.set_page_config(
    page_title="Mallow",
    page_icon="🌿",
    layout="wide",
)


def format_clock_time(timestamp):
    """
    Format a timestamp as a friendly 12-hour time.

    Avoids platform-specific strftime flags so it works
    consistently on Windows, macOS, and Linux.
    """

    if pd.isna(timestamp):
        return "Unknown time"

    return timestamp.strftime("%I:%M %p").lstrip("0")


if "mallow_data_source" not in st.session_state:
    st.session_state["mallow_data_source"] = "demo"

if "apple_health_data" not in st.session_state:
    st.session_state["apple_health_data"] = None

if "apple_health_info" not in st.session_state:
    st.session_state["apple_health_info"] = None


stored_apple_data = st.session_state.get(
    "apple_health_data"
)

using_apple_health = (
    st.session_state.get(
        "mallow_data_source"
    ) == "apple"
    and isinstance(
        stored_apple_data,
        pd.DataFrame,
    )
    and not stored_apple_data.empty
)


if using_apple_health:
    health_data = (
        stored_apple_data
        .copy()
        .sort_values(
            "date"
        )
        .reset_index(
            drop=True
        )
    )
else:
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


if using_apple_health:
    intraday_data = pd.DataFrame(
        columns=[
            "timestamp",
            "heart_rate",
            "hrv",
            "glucose",
            "oxygen_saturation",
            "respiratory_rate",
            "wrist_temperature",
            "systolic_bp",
            "diastolic_bp",
        ]
    )

    intraday_latest = None
    latest_bp = None
    latest_bp_time = None

else:
    intraday_data = generate_intraday_data(
        health_data.iloc[-1],
        interval_minutes=15,
        seed=84,
    )

    intraday_latest = intraday_data.iloc[
        -1
    ]

    bp_readings = intraday_data.dropna(
        subset=[
            "systolic_bp",
            "diastolic_bp",
        ]
    ).copy()

    if not bp_readings.empty:
        latest_bp = bp_readings.iloc[
            -1
        ]

        latest_bp_time = format_clock_time(
            latest_bp[
                "timestamp"
            ]
        )

    else:
        latest_bp = None
        latest_bp_time = None


try:
    anomaly_result = detect_current_anomaly(
        health_data
    )

    mallow_insight = build_anomaly_insight(
        anomaly_result
    )

except ValueError:
    anomaly_result = None

    mallow_insight = (
        "There is not enough overlapping recent data to evaluate "
        "today's overall combination yet. Mallow will keep the "
        "individual measurements available without inventing missing values."
    )


with st.sidebar:
    st.markdown("## Mallow 🌿")
    st.caption(
        "your gentle personal health companion"
    )

    dark_mode = st.toggle(
        "🌙 Dark mode",
        value=False,
    )

    st.write("")

    if using_apple_health:
        st.success(
            "Data source: Apple Health import"
        )

        view_options = [
            7,
            30,
            90,
        ]

        view_index = 1

    else:
        st.caption(
            "Data source: synthetic demo"
        )

        view_options = [
            1,
            7,
            30,
            90,
        ]

        view_index = 2

    view_days = st.selectbox(
        "View window",
        options=view_options,
        index=view_index,
        format_func=lambda days: (
            "Today"
            if days == 1
            else f"{days} days"
        ),
    )

    if using_apple_health:
        st.caption(
            "Apple Health import mode currently uses daily summaries. "
            "Intraday Today charts remain available in demo mode."
        )

        if st.button(
            "Use demo data",
            use_container_width=True,
        ):
            st.session_state[
                "mallow_data_source"
            ] = "demo"

            st.rerun()

    else:
        st.caption(
            "Today shows measurements throughout the day. "
            "Longer views show daily trends."
        )

    st.caption(
        "Personal baseline: previous 30 days"
    )

    st.divider()

    if using_apple_health:
        st.caption(
            "Real imported health data. Missing measurements remain missing."
        )
    else:
        st.caption(
            "Prototype using synthetic health data."
        )


def status_for(metric):
    return get_baseline_status(
        health_data,
        metric,
        days=30,
    )


def status_style(metric):
    level = status_for(
        metric
    )["level"]

    if level == "typical":
        return "good"

    if level == "watch":
        return "watch"

    if level == "unusual":
        return "unusual"

    return "neutral"


def combined_bp_status():
    systolic = status_for(
        "systolic_bp"
    )

    diastolic = status_for(
        "diastolic_bp"
    )

    if (
        systolic[
            "level"
        ] == "neutral"
        or diastolic[
            "level"
        ] == "neutral"
        or pd.isna(
            systolic[
                "z_score"
            ]
        )
        or pd.isna(
            diastolic[
                "z_score"
            ]
        )
    ):
        return {
            "label": "No data",
            "level": "neutral",
        }

    max_z = max(
        abs(
            systolic[
                "z_score"
            ]
        ),
        abs(
            diastolic[
                "z_score"
            ]
        ),
    )

    if max_z < 1:
        return {
            "label": "Near your usual range",
            "level": "typical",
        }

    if max_z < 2:
        return {
            "label": (
                "Somewhat different from baseline"
            ),
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


def format_measurement(
    value,
    decimals=1,
    unit="",
    signed=False,
):
    if (
        value is None
        or pd.isna(
            value
        )
    ):
        return "No data"

    if signed:
        number = (
            f"{float(value):+.{decimals}f}"
        )
    else:
        number = (
            f"{float(value):.{decimals}f}"
        )

    if unit:
        return (
            f"{number} {unit}"
        )

    return number


def format_bp(
    systolic,
    diastolic,
):
    if (
        systolic is None
        or diastolic is None
        or pd.isna(
            systolic
        )
        or pd.isna(
            diastolic
        )
    ):
        return "No data"

    return (
        f"{float(systolic):.0f} / "
        f"{float(diastolic):.0f}"
    )


def baseline_detail(
    metric,
    decimals=1,
    unit="",
    signed=False,
):
    value = baseline.get(
        metric,
        np.nan,
    )

    if pd.isna(
        value
    ):
        return (
            "No recent baseline data"
        )

    return (
        "30-day baseline: "
        + format_measurement(
            value,
            decimals=decimals,
            unit=unit,
            signed=signed,
        )
    )




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
        "chart_grid": "#46564A",
        "chart_line": "#A5C4AA",
        "chart_average": "#D4B9C8",
        "chart_label": "#F4F8F5",
        "chart_axis": "#667A6B",
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
        "chart_grid": "#D9D5D0",
        "chart_line": "#6F8F78",
        "chart_average": "#A77F94",
        "chart_label": "#27352B",
        "chart_axis": "#A7AEA9",
        "input": "#566B5D",
        "input_text": "#FFFFFF",
        "input_placeholder": "#D5DFD8",
        "input_focus": "#789583",
    }


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

    .relationship-card {{
        background-color: {colors["card"]};
        color: {colors["text"]};
        border: 1px solid {colors["border"]};
        border-radius: 20px;
        padding: 1.15rem 1.2rem;
        min-height: 175px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.03);
    }}

    .relationship-title {{
        color: {colors["heading"]};
        font-weight: 700;
        font-size: 0.95rem;
        margin-bottom: 0.7rem;
    }}

    .relationship-r {{
        color: {colors["text"]};
        font-size: 1.55rem;
        font-weight: 700;
        margin-bottom: 0.35rem;
    }}

    .relationship-detail {{
        color: {colors["muted"]};
        font-size: 0.82rem;
        line-height: 1.55;
    }}

    .comparison-card {{
        background-color: {colors["card"]};
        color: {colors["text"]};
        border: 1px solid {colors["border"]};
        border-radius: 20px;
        padding: 1.1rem 1.2rem;
        min-height: 170px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.03);
    }}

    .comparison-title {{
        color: {colors["muted"]};
        font-size: 0.84rem;
        font-weight: 600;
        margin-bottom: 0.55rem;
    }}

    .comparison-change {{
        color: {colors["text"]};
        font-size: 1.55rem;
        font-weight: 700;
        margin-bottom: 0.4rem;
    }}

    .comparison-detail {{
        color: {colors["muted"]};
        font-size: 0.80rem;
        line-height: 1.55;
    }}

    [data-testid="stTextInput"] div[data-baseweb="input"] {{
        background-color: {colors["input"]} !important;
        border: 1px solid {colors["input"]} !important;
        border-radius: 16px !important;
        box-shadow: none !important;
        overflow: hidden !important;
    }}

    [data-testid="stTextInput"] div[data-baseweb="input"]:focus-within {{
        border-color: {colors["input_focus"]} !important;
        box-shadow: none !important;
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
        outline: none !important;
        box-shadow: none !important;
        padding: 0.8rem 0.9rem !important;
        opacity: 1 !important;
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


def render_html(content):
    clean_html = " ".join(
        line.strip()
        for line in dedent(
            content
        ).strip().splitlines()
    )

    st.markdown(
        clean_html,
        unsafe_allow_html=True,
    )


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


def relationship_card(
    title,
    correlation,
    strength,
    direction,
    sample_count,
    data_support,
):
    direction_label = (
        "little clear direction"
        if direction == "little clear direction"
        else f"{direction} association"
    )

    return (
        f'<div class="relationship-card">'
        f'<div class="relationship-title">🌱 {title}</div>'
        f'<div class="relationship-r">r = {correlation:.2f}</div>'
        f'<div class="relationship-detail">'
        f'{strength.capitalize()} • {direction_label}<br>'
        f'{sample_count} paired daily observations<br>'
        f'{data_support.capitalize()} data support'
        f'</div>'
        f'</div>'
    )


def period_comparison_card(
    icon,
    comparison,
):
    """
    Render a neutral comparison card for two adjacent periods.
    """

    if comparison is None:
        return (
            f'<div class="comparison-card">'
            f'<div class="comparison-title">{icon} Comparison</div>'
            f'<div class="comparison-change">—</div>'
            f'<div class="comparison-detail">'
            f'Not enough history for an equal prior period.'
            f'</div>'
            f'</div>'
        )

    days = comparison[
        "days"
    ]

    current_text = format_average(
        comparison,
        "current_average",
    )

    previous_text = format_average(
        comparison,
        "previous_average",
    )

    difference_text = format_difference(
        comparison
    )

    if abs(
        comparison["difference"]
    ) < 1e-12:
        percent_text = " • essentially unchanged"
    elif comparison[
        "percent_change"
    ] is None:
        percent_text = ""
    else:
        percent_text = (
            f" • {abs(comparison['percent_change']):.1f}% "
            f"{comparison['direction']}"
        )

    return (
        f'<div class="comparison-card">'
        f'<div class="comparison-title">'
        f'{icon} {comparison["name"]}</div>'
        f'<div class="comparison-change">'
        f'{comparison["arrow"]} {difference_text}</div>'
        f'<div class="comparison-detail">'
        f'Recent {days} days: {current_text}<br>'
        f'Previous {days} days: {previous_text}<br>'
        f'Compared with prior period'
        f'{percent_text}'
        f'</div>'
        f'</div>'
    )


def chart_xaxis(title=""):
    return {
        "title": {
            "text": title,
            "font": {
                "color": colors["chart_label"],
                "size": 14,
            },
        },
        "tickfont": {
            "color": colors["chart_label"],
            "size": 12,
        },
        "linecolor": colors["chart_axis"],
        "tickcolor": colors["chart_axis"],
        "gridcolor": colors["chart_grid"],
        "zerolinecolor": colors["chart_axis"],
        "showline": True,
        "zeroline": False,
    }


def chart_yaxis(title=""):
    return {
        "title": {
            "text": title,
            "font": {
                "color": colors["chart_label"],
                "size": 14,
            },
        },
        "tickfont": {
            "color": colors["chart_label"],
            "size": 12,
        },
        "linecolor": colors["chart_axis"],
        "tickcolor": colors["chart_axis"],
        "gridcolor": colors["chart_grid"],
        "zerolinecolor": colors["chart_axis"],
        "showline": True,
        "zeroline": False,
    }


def apply_chart_style(
    figure,
    height=400,
    showlegend=False,
):
    figure.update_layout(
        height=height,
        paper_bgcolor=colors["chart_bg"],
        plot_bgcolor=colors["chart_bg"],
        font=dict(
            color=colors["chart_label"],
            size=13,
        ),
        legend=dict(
            font=dict(
                color=colors["chart_label"],
                size=13,
            ),
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        hoverlabel=dict(
            bgcolor=colors["card"],
            bordercolor=colors["chart_axis"],
            font=dict(
                color=colors["chart_label"],
                size=13,
            ),
        ),
        margin=dict(
            l=55,
            r=30,
            t=55,
            b=55,
        ),
        showlegend=showlegend,
    )


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


if using_apple_health:
    welcome_text = (
        f"Showing your imported Apple Health history across the "
        f"most recent {view_days} days, compared with your "
        f"30-day personal baseline where enough data exists."
    )

elif view_days == 1:
    welcome_text = (
        "Here is your synthetic health snapshot so far today. "
        "Measurements update across the intraday timeline."
    )

else:
    welcome_text = (
        f"Showing your recent {view_days}-day health trends "
        "against your 30-day personal baseline."
    )


render_html(
    f"""
    <div class="welcome-card">
        <b>Good morning ☀️</b>
        <br><br>
        {welcome_text}
        <br><br>
        <span style="color:{colors["muted"]};">
            Mallow separates the selected viewing period
            from your longer-term personal baseline.
        </span>
    </div>
    """
)


(
    overview_tab,
    heart_tab,
    metabolic_tab,
    sleep_tab,
    relationships_tab,
    apple_health_tab,
) = st.tabs(
    [
        "🌿 Overview",
        "❤️ Heart & circulation",
        "🩸 Blood & metabolic",
        "🌙 Sleep & respiratory",
        "📊 Relationships",
        "⌚ Apple Health",
    ]
)


with overview_tab:

    st.subheader(
        "Today's vitals"
    )

    row1 = st.columns(4)

    if view_days == 1:
        current_hr = intraday_latest[
            "heart_rate"
        ]
        today_hr_average = intraday_data[
            "heart_rate"
        ].mean()
        current_glucose = intraday_latest[
            "glucose"
        ]
        current_oxygen = intraday_latest[
            "oxygen_saturation"
        ]
        current_hrv = intraday_latest[
            "hrv"
        ]
        current_resp = intraday_latest[
            "respiratory_rate"
        ]
        current_temp = intraday_latest[
            "wrist_temperature"
        ]

        if latest_bp is not None:
            current_systolic = latest_bp[
                "systolic_bp"
            ]
            current_diastolic = latest_bp[
                "diastolic_bp"
            ]
            bp_detail = (
                f"Latest cuff reading • "
                f"{latest_bp_time}"
            )
        else:
            current_systolic = latest[
                "systolic_bp"
            ]
            current_diastolic = latest[
                "diastolic_bp"
            ]
            bp_detail = (
                "No cuff reading yet today"
            )

        live_status = (
            "Today's synthetic reading"
        )
        live_style = "neutral"

    else:
        current_hr = latest[
            "resting_hr"
        ]
        current_glucose = latest[
            "glucose"
        ]
        current_oxygen = latest[
            "oxygen_saturation"
        ]
        current_hrv = latest[
            "hrv"
        ]
        current_resp = latest[
            "respiratory_rate"
        ]
        current_temp = latest[
            "wrist_temperature"
        ]
        current_systolic = latest[
            "systolic_bp"
        ]
        current_diastolic = latest[
            "diastolic_bp"
        ]

    with row1[0]:
        if view_days == 1:
            title = "Heart rate"
            detail = (
                f"Today's average: "
                f"{today_hr_average:.0f} bpm"
            )
            status = live_status
            style = live_style
        else:
            title = "Resting heart rate"
            detail = baseline_detail(
                "resting_hr",
                0,
                "bpm",
            )
            status = status_for(
                "resting_hr"
            )["label"]
            style = status_style(
                "resting_hr"
            )

        render_html(
            metric_card(
                "❤️",
                title,
                format_measurement(current_hr, 0, "bpm"),
                detail,
                status,
                "⌚ Apple Watch",
                style,
            )
        )

    with row1[1]:
        render_html(
            metric_card(
                "🩸",
                "Blood pressure",
                format_bp(current_systolic, current_diastolic),
                (
                    bp_detail
                    if view_days == 1
                    else (
                        "30-day baseline: "
                        + format_bp(
                            baseline.get(
                                "systolic_bp",
                                np.nan,
                            ),
                            baseline.get(
                                "diastolic_bp",
                                np.nan,
                            ),
                        )
                    )
                ),
                (
                    live_status
                    if view_days == 1
                    else bp_status["label"]
                ),
                "🩺 Connected cuff",
                (
                    "neutral"
                    if view_days == 1
                    else bp_style
                ),
            )
        )

    with row1[2]:
        render_html(
            metric_card(
                "🍬",
                "Blood glucose",
                format_measurement(current_glucose, 0, "mg/dL"),
                (
                    f"Today's average: "
                    f"{intraday_data['glucose'].mean():.0f} mg/dL"
                    if view_days == 1
                    else baseline_detail(
                        "glucose",
                        0,
                        "mg/dL",
                    )
                ),
                (
                    live_status
                    if view_days == 1
                    else status_for(
                        "glucose"
                    )["label"]
                ),
                "🩸 CGM / HealthKit",
                (
                    "neutral"
                    if view_days == 1
                    else status_style(
                        "glucose"
                    )
                ),
            )
        )

    with row1[3]:
        render_html(
            metric_card(
                "🫁",
                "Oxygen saturation",
                format_measurement(current_oxygen, 1, "%"),
                (
                    f"Today's average: "
                    f"{intraday_data['oxygen_saturation'].mean():.1f}%"
                    if view_days == 1
                    else baseline_detail(
                        "oxygen_saturation",
                        1,
                        "%",
                    )
                ),
                (
                    live_status
                    if view_days == 1
                    else status_for(
                        "oxygen_saturation"
                    )["label"]
                ),
                "⌚ Apple Watch",
                (
                    "neutral"
                    if view_days == 1
                    else status_style(
                        "oxygen_saturation"
                    )
                ),
            )
        )

    st.write("")

    row2 = st.columns(4)

    with row2[0]:
        render_html(
            metric_card(
                "💓",
                "HRV",
                format_measurement(current_hrv, 0, "ms"),
                (
                    f"Today's average: "
                    f"{intraday_data['hrv'].mean():.0f} ms"
                    if view_days == 1
                    else baseline_detail(
                        "hrv",
                        0,
                        "ms",
                    )
                ),
                (
                    live_status
                    if view_days == 1
                    else status_for(
                        "hrv"
                    )["label"]
                ),
                "⌚ Apple Watch",
                (
                    "neutral"
                    if view_days == 1
                    else status_style(
                        "hrv"
                    )
                ),
            )
        )

    with row2[1]:
        render_html(
            metric_card(
                "🌡️",
                "Wrist temperature",
                format_measurement(current_temp, 2, "°F", signed=True),
                (
                    "Synthetic deviation"
                    if view_days == 1
                    else (
                        "Deviation from personal reference"
                    )
                ),
                (
                    live_status
                    if view_days == 1
                    else status_for(
                        "wrist_temperature"
                    )["label"]
                ),
                "⌚ Apple Watch",
                (
                    "neutral"
                    if view_days == 1
                    else status_style(
                        "wrist_temperature"
                    )
                ),
            )
        )

    with row2[2]:
        render_html(
            metric_card(
                "🌬️",
                "Respiratory rate",
                format_measurement(current_resp, 1, "/ min"),
                (
                    f"Today's average: "
                    f"{intraday_data['respiratory_rate'].mean():.1f}"
                    if view_days == 1
                    else baseline_detail(
                        "respiratory_rate",
                        1,
                        "/ min",
                    )
                ),
                (
                    live_status
                    if view_days == 1
                    else status_for(
                        "respiratory_rate"
                    )["label"]
                ),
                "⌚ Apple Watch",
                (
                    "neutral"
                    if view_days == 1
                    else status_style(
                        "respiratory_rate"
                    )
                ),
            )
        )

    with row2[3]:
        render_html(
            metric_card(
                "😴",
                "Sleep",
                format_measurement(latest.get("sleep_hours", np.nan), 1, "h"),
                (
                    "Previous synthetic night"
                    if view_days == 1
                    else baseline_detail(
                        "sleep_hours",
                        1,
                        "h",
                    )
                ),
                (
                    "Last night's summary"
                    if view_days == 1
                    else status_for(
                        "sleep_hours"
                    )["label"]
                ),
                "⌚ Apple Watch",
                (
                    "neutral"
                    if view_days == 1
                    else status_style(
                        "sleep_hours"
                    )
                ),
            )
        )

    st.write("")

    if view_days == 1:
        st.subheader(
            "Throughout today ⏱️"
        )

        intraday_metrics = {
            "Heart rate": {
                "column": "heart_rate",
                "unit": "bpm",
            },
            "HRV": {
                "column": "hrv",
                "unit": "ms",
            },
            "Blood glucose": {
                "column": "glucose",
                "unit": "mg/dL",
            },
            "Oxygen saturation": {
                "column": "oxygen_saturation",
                "unit": "%",
            },
            "Respiratory rate": {
                "column": "respiratory_rate",
                "unit": "breaths/min",
            },
            "Wrist temperature deviation": {
                "column": "wrist_temperature",
                "unit": "°F",
            },
        }

        chosen_metric = st.selectbox(
            "Measurement",
            list(
                intraday_metrics.keys()
            ),
        )

        chosen_column = intraday_metrics[
            chosen_metric
        ]["column"]

        chosen_unit = intraday_metrics[
            chosen_metric
        ]["unit"]

        values = intraday_data[
            chosen_column
        ]

        summary_columns = st.columns(
            4
        )

        summary_columns[0].metric(
            "Current",
            (
                f"{values.iloc[-1]:.1f} "
                f"{chosen_unit}"
            ),
        )

        summary_columns[1].metric(
            "Today average",
            (
                f"{values.mean():.1f} "
                f"{chosen_unit}"
            ),
        )

        summary_columns[2].metric(
            "Today low",
            (
                f"{values.min():.1f} "
                f"{chosen_unit}"
            ),
        )

        summary_columns[3].metric(
            "Today high",
            (
                f"{values.max():.1f} "
                f"{chosen_unit}"
            ),
        )

        intraday_fig = go.Figure()

        intraday_fig.add_trace(
            go.Scatter(
                x=intraday_data[
                    "timestamp"
                ],
                y=values,
                mode="lines+markers",
                line=dict(
                    color=colors[
                        "chart_line"
                    ],
                    width=3,
                ),
                marker=dict(
                    color=colors[
                        "chart_line"
                    ],
                    size=5,
                ),
                hovertemplate=(
                    "%{x|%I:%M %p}<br>"
                    + f"%{{y:.1f}} {chosen_unit}"
                    + "<extra></extra>"
                ),
            )
        )

        intraday_fig.add_hline(
            y=values.mean(),
            line_dash="dot",
            line_color=colors[
                "chart_average"
            ],
            annotation_text=(
                "Today average"
            ),
            annotation_font_color=colors[
                "chart_label"
            ],
        )

        intraday_fig.update_xaxes(
            **chart_xaxis(
                "Time"
            )
        )

        intraday_fig.update_yaxes(
            **chart_yaxis(
                chosen_unit
            )
        )

        apply_chart_style(
            intraday_fig,
            height=400,
            showlegend=False,
        )

        st.plotly_chart(
            intraday_fig,
            use_container_width=True,
            config={
                "displayModeBar": False,
            },
        )

        st.caption(
            "Synthetic intraday samples are shown at regular "
            "intervals for this prototype. Real device sampling "
            "frequency varies by measurement and device."
        )

    else:
        st.subheader(
            f"{view_days}-day resting heart-rate trend"
        )

        heart_df = health_data.tail(
            view_days
        ).copy()

        heart_df["date"] = pd.to_datetime(
            heart_df["date"]
        )

        heart_fig = go.Figure()

        heart_fig.add_trace(
            go.Scatter(
                x=heart_df[
                    "date"
                ],
                y=heart_df[
                    "resting_hr"
                ],
                mode="lines+markers",
                line=dict(
                    color=colors[
                        "chart_line"
                    ],
                    width=3,
                ),
                marker=dict(
                    color=colors[
                        "chart_line"
                    ],
                    size=6,
                ),
                hovertemplate=(
                    "%{x|%b %d}<br>"
                    "%{y:.1f} bpm"
                    "<extra></extra>"
                ),
            )
        )

        heart_fig.add_hline(
            y=baseline[
                "resting_hr"
            ],
            line_dash="dot",
            line_color=colors[
                "chart_average"
            ],
            annotation_text=(
                "30-day baseline"
            ),
            annotation_font_color=colors[
                "chart_label"
            ],
        )

        heart_fig.update_xaxes(
            **chart_xaxis("")
        )

        heart_fig.update_yaxes(
            **chart_yaxis(
                "bpm"
            )
        )

        apply_chart_style(
            heart_fig,
            height=350,
            showlegend=False,
        )

        st.plotly_chart(
            heart_fig,
            use_container_width=True,
            config={
                "displayModeBar": False,
            },
        )

        st.write("")
        st.subheader(
            "Recent trends 🌱"
        )

        st.caption(
            "These summarize the overall direction of each "
            "measurement across the selected window. They do "
            "not indicate whether a change is medically good "
            "or bad."
        )

        trend_metrics = [
            (
                "❤️",
                "resting_hr",
            ),
            (
                "💓",
                "hrv",
            ),
            (
                "😴",
                "sleep_hours",
            ),
            (
                "🍬",
                "glucose",
            ),
        ]

        trend_columns = st.columns(
            4
        )

        for (
            trend_column,
            (
                trend_icon,
                trend_metric,
            ),
        ) in zip(
            trend_columns,
            trend_metrics,
        ):
            trend = analyze_trend(
                health_data,
                trend_metric,
                days=view_days,
            )

            with trend_column:
                if trend is None:
                    render_html(
                        metric_card(
                            trend_icon,
                            trend_metric.replace(
                                "_",
                                " ",
                            ).title(),
                            "—",
                            "Not enough recent data",
                            "Awaiting data",
                            "🌿 Calculated by Mallow",
                            "neutral",
                        )
                    )
                else:
                    if trend[
                        "direction"
                    ] == "up":
                        trend_value = (
                            "↑ "
                            + trend[
                                "label"
                            ].replace(
                                "Clearly ",
                                "",
                            ).replace(
                                "Gradually ",
                                "",
                            ).capitalize()
                        )
                    elif trend[
                        "direction"
                    ] == "down":
                        trend_value = (
                            "↓ "
                            + trend[
                                "label"
                            ].replace(
                                "Clearly ",
                                "",
                            ).replace(
                                "Gradually ",
                                "",
                            ).capitalize()
                        )
                    else:
                        trend_value = (
                            "→ No clear trend"
                        )

                    render_html(
                        metric_card(
                            trend_icon,
                            trend["name"],
                            trend_value,
                            (
                                "Estimated change: "
                                + format_trend_change(
                                    trend
                                )
                            ),
                            (
                                f"{trend['data_support'].capitalize()} "
                                "data support"
                            ),
                            "🌿 Calculated by Mallow",
                            "neutral",
                        )
                    )

        st.caption(
            "Trend direction is estimated from a simple fitted "
            "line through the selected days. Data support reflects "
            "how much usable history backs the estimate; it is not "
            "a clinical confidence score."
        )

        if view_days in [
            7,
            30,
        ]:
            st.write("")
            st.subheader(
                "Compared with the previous period ↔️"
            )

            st.caption(
                f"The most recent {view_days} days are compared "
                f"with the {view_days} days immediately before them. "
                "Higher or lower does not automatically mean "
                "healthier or less healthy."
            )

            comparison_metrics = [
                "resting_hr",
                "hrv",
                "sleep_hours",
                "glucose",
            ]

            comparison_icons = {
                "resting_hr": "❤️",
                "hrv": "💓",
                "sleep_hours": "😴",
                "glucose": "🍬",
            }

            period_results = compare_metrics(
                health_data,
                comparison_metrics,
                days=view_days,
            )

            period_lookup = {
                item["metric"]: item
                for item in period_results
            }

            comparison_columns = st.columns(
                4
            )

            for (
                comparison_column,
                comparison_metric,
            ) in zip(
                comparison_columns,
                comparison_metrics,
            ):
                with comparison_column:
                    render_html(
                        period_comparison_card(
                            comparison_icons[
                                comparison_metric
                            ],
                            period_lookup.get(
                                comparison_metric
                            ),
                        )
                    )

            st.caption(
                "Period comparisons use simple averages and are "
                "descriptive only. They do not account for illness, "
                "medications, exercise, menstrual cycle, device "
                "changes, or other context."
            )

        elif view_days == 90:
            st.write("")
            st.caption(
                "A previous 90-day comparison is not shown because "
                "the current synthetic demo contains 90 days of "
                "history. Mallow only compares equal-length periods "
                "when both are fully available."
            )

    st.write("")
    st.subheader(
        "Data quality 🔎"
    )

    if view_days == 1:
        quality = intraday_quality(
            intraday_data
        )

        quality_columns = st.columns(
            3
        )

        quality_columns[0].metric(
            "Samples so far today",
            quality[
                "sample_count"
            ],
        )

        quality_columns[1].metric(
            "Core signal coverage",
            (
                f"{quality['coverage_percent']:.0f}%"
            ),
        )

        quality_columns[2].metric(
            "Data support",
            quality[
                "support"
            ].capitalize(),
        )

        st.caption(
            "Today coverage summarizes the synthetic intraday "
            "signals currently available. Discrete measurements "
            "such as cuff blood pressure are evaluated separately."
        )

    else:
        quality = window_quality(
            health_data,
            days=view_days,
        )

        quality_columns = st.columns(
            3
        )

        quality_columns[0].metric(
            "Daily window",
            (
                f"{quality['requested_days']} days"
            ),
        )

        quality_columns[1].metric(
            "Core metric coverage",
            (
                f"{quality['coverage_percent']:.0f}%"
            ),
        )

        quality_columns[2].metric(
            "Data support",
            quality[
                "support"
            ].capitalize(),
        )

        st.caption(
            "Data support describes how much usable history is "
            "available for analysis. It is not statistical or "
            "clinical certainty. This synthetic demo currently "
            "has intentionally complete daily data."
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

    if view_days == 1:
        assistant_window_text = (
            "Today view uses a 30-day window for longer-term "
            "trend and relationship questions unless you name "
            "another period."
        )
        assistant_days = 30
    else:
        assistant_window_text = (
            f"Questions use the selected {view_days}-day window "
            f"unless you name another period."
        )
        assistant_days = view_days

    st.caption(
        assistant_window_text
    )

    question = st.text_input(
        "Ask something about your health data",
        placeholder=(
            "How is my HRV trending over the last 30 days?"
        ),
        label_visibility="collapsed",
    )

    st.caption(
        "Try: “What is related to my sleep?” • "
        "“Is my resting heart rate trending down?” • "
        "“What was my average glucose over the last 7 days?”"
    )

    if question:
        try:
            answer = ask_mallow(
                question,
                health_data,
                analysis_days=assistant_days,
            )

        except ValueError:
            answer = (
                "I don't have enough overlapping recent measurements "
                "for that analysis yet. I can still summarize any "
                "individual Apple Health measurements that are available."
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


with heart_tab:

    st.subheader(
        "Heart & circulation ❤️"
    )

    heart_columns = st.columns(
        3
    )

    with heart_columns[0]:
        render_html(
            metric_card(
                "❤️",
                (
                    "Current heart rate"
                    if view_days == 1
                    else "Resting heart rate"
                ),
                (
                    f"{intraday_latest['heart_rate']:.0f} bpm"
                    if view_days == 1
                    else (
                        format_measurement(latest.get("resting_hr", np.nan), 0, "bpm")
                    )
                ),
                (
                    f"Today average: "
                    f"{intraday_data['heart_rate'].mean():.0f} bpm"
                    if view_days == 1
                    else baseline_detail(
                        "resting_hr",
                        0,
                        "bpm",
                    )
                ),
                (
                    "Today's synthetic reading"
                    if view_days == 1
                    else status_for(
                        "resting_hr"
                    )["label"]
                ),
                "⌚ Apple Watch",
                (
                    "neutral"
                    if view_days == 1
                    else status_style(
                        "resting_hr"
                    )
                ),
            )
        )

    with heart_columns[1]:
        render_html(
            metric_card(
                "💓",
                "HRV",
                (
                    f"{intraday_latest['hrv']:.0f} ms"
                    if view_days == 1
                    else (
                        format_measurement(latest.get("hrv", np.nan), 0, "ms")
                    )
                ),
                (
                    f"Today average: "
                    f"{intraday_data['hrv'].mean():.0f} ms"
                    if view_days == 1
                    else baseline_detail(
                        "hrv",
                        0,
                        "ms",
                    )
                ),
                (
                    "Today's synthetic reading"
                    if view_days == 1
                    else status_for(
                        "hrv"
                    )["label"]
                ),
                "⌚ Apple Watch",
                (
                    "neutral"
                    if view_days == 1
                    else status_style(
                        "hrv"
                    )
                ),
            )
        )

    with heart_columns[2]:
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

    heart_columns_2 = st.columns(
        3
    )

    with heart_columns_2[0]:
        if (
            view_days == 1
            and latest_bp is not None
        ):
            bp_value = (
                f"{latest_bp['systolic_bp']:.0f} / "
                f"{latest_bp['diastolic_bp']:.0f}"
            )
            bp_detail_text = (
                f"Latest cuff reading • "
                f"{latest_bp_time}"
            )
            bp_label = (
                "Discrete measurement"
            )
            bp_card_style = (
                "neutral"
            )

        elif view_days == 1:
            bp_value = "—"
            bp_detail_text = (
                "No cuff reading yet today"
            )
            bp_label = (
                "Awaiting measurement"
            )
            bp_card_style = (
                "neutral"
            )

        else:
            bp_value = format_bp(
                latest.get(
                    "systolic_bp",
                    np.nan,
                ),
                latest.get(
                    "diastolic_bp",
                    np.nan,
                ),
            )
            bp_detail_text = (
                "Pulse pressure: "
                + format_measurement(
                    latest.get(
                        "pulse_pressure",
                        np.nan,
                    ),
                    0,
                    "mmHg",
                )
            )
            bp_label = (
                bp_status["label"]
            )
            bp_card_style = (
                bp_style
            )

        render_html(
            metric_card(
                "🩸",
                "Blood pressure",
                bp_value,
                bp_detail_text,
                bp_label,
                "🩺 Connected cuff",
                bp_card_style,
            )
        )

    with heart_columns_2[1]:
        render_html(
            metric_card(
                "📊",
                "Mean arterial pressure",
                (
                    format_measurement(latest.get("map", np.nan), 0, "mmHg")
                ),
                "Estimated from cuff measurement",
                bp_status["label"],
                "🌿 Calculated by Mallow",
                bp_style,
            )
        )

    with heart_columns_2[2]:
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

    if view_days == 1:
        st.write("")

        st.subheader(
            "Today's blood-pressure readings 🩺"
        )

        if bp_readings.empty:
            st.info(
                "No synthetic cuff readings are available yet today."
            )
        else:
            bp_summary_columns = (
                st.columns(3)
            )

            bp_summary_columns[0].metric(
                "Readings today",
                len(
                    bp_readings
                ),
            )

            bp_summary_columns[1].metric(
                "Latest systolic",
                (
                    f"{latest_bp['systolic_bp']:.0f} mmHg"
                ),
            )

            bp_summary_columns[2].metric(
                "Latest diastolic",
                (
                    f"{latest_bp['diastolic_bp']:.0f} mmHg"
                ),
            )

            bp_fig = go.Figure()

            bp_fig.add_trace(
                go.Scatter(
                    x=bp_readings[
                        "timestamp"
                    ],
                    y=bp_readings[
                        "systolic_bp"
                    ],
                    mode="markers",
                    name="Systolic",
                    marker=dict(
                        size=13,
                        color=colors[
                            "chart_line"
                        ],
                    ),
                    hovertemplate=(
                        "%{x|%I:%M %p}<br>"
                        "Systolic: %{y:.0f} mmHg"
                        "<extra></extra>"
                    ),
                )
            )

            bp_fig.add_trace(
                go.Scatter(
                    x=bp_readings[
                        "timestamp"
                    ],
                    y=bp_readings[
                        "diastolic_bp"
                    ],
                    mode="markers",
                    name="Diastolic",
                    marker=dict(
                        size=13,
                        color=colors[
                            "chart_average"
                        ],
                    ),
                    hovertemplate=(
                        "%{x|%I:%M %p}<br>"
                        "Diastolic: %{y:.0f} mmHg"
                        "<extra></extra>"
                    ),
                )
            )

            bp_fig.update_xaxes(
                **chart_xaxis(
                    "Time"
                )
            )

            bp_fig.update_yaxes(
                **chart_yaxis(
                    "mmHg"
                )
            )

            apply_chart_style(
                bp_fig,
                height=380,
                showlegend=True,
            )

            st.plotly_chart(
                bp_fig,
                use_container_width=True,
                config={
                    "displayModeBar": False,
                },
            )

            st.caption(
                "Blood pressure is shown as discrete cuff readings, "
                "not a continuous signal. The synthetic prototype "
                "adds readings around 8 AM, 2 PM, and 8 PM when "
                "those times have occurred."
            )

    st.write("")

    st.subheader(
        "Rhythm & monitoring"
    )

    rhythm_columns = st.columns(
        3
    )

    with rhythm_columns[0]:
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

    with rhythm_columns[1]:
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

    with rhythm_columns[2]:
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


with metabolic_tab:

    st.subheader(
        "Blood & metabolic 🩸"
    )

    metabolic_columns = st.columns(
        3
    )

    with metabolic_columns[0]:
        render_html(
            metric_card(
                "🍬",
                "Current glucose",
                (
                    f"{intraday_latest['glucose']:.0f} mg/dL"
                    if view_days == 1
                    else (
                        format_measurement(latest.get("glucose", np.nan), 0, "mg/dL")
                    )
                ),
                (
                    f"Today average: "
                    f"{intraday_data['glucose'].mean():.0f} mg/dL"
                    if view_days == 1
                    else baseline_detail(
                        "glucose",
                        0,
                        "mg/dL",
                    )
                ),
                (
                    "Today's synthetic reading"
                    if view_days == 1
                    else status_for(
                        "glucose"
                    )["label"]
                ),
                "🩸 CGM / HealthKit",
                (
                    "neutral"
                    if view_days == 1
                    else status_style(
                        "glucose"
                    )
                ),
            )
        )

    with metabolic_columns[1]:
        if view_days == 1:
            today_glucose = (
                intraday_data[
                    "glucose"
                ]
            )

            glucose_cv = (
                today_glucose.std()
                / today_glucose.mean()
                * 100
            )

            glucose_cv_detail = (
                "Today's coefficient of variation"
            )
        else:
            glucose_window = (
                health_data
                .tail(30)[
                    "glucose"
                ]
            )

            glucose_cv = (
                glucose_window.std()
                / glucose_window.mean()
                * 100
            )

            glucose_cv_detail = (
                "30-day coefficient of variation"
            )

        render_html(
            metric_card(
                "📈",
                "Glucose variability",
                f"{glucose_cv:.1f}%",
                glucose_cv_detail,
                "Calculated from recent data",
                "🌿 Calculated by Mallow",
                "neutral",
            )
        )

    with metabolic_columns[2]:
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

    st.info(
        "Blood glucose and blood-pressure measurements "
        "will come from compatible devices, HealthKit, "
        "or manual entries. Mallow does not directly "
        "measure them."
    )


with sleep_tab:

    st.subheader(
        "Sleep & respiratory 🌙"
    )

    deep_percent = (
        latest[
            "deep_sleep_hours"
        ]
        / latest[
            "sleep_hours"
        ]
        * 100
    )

    rem_percent = (
        latest[
            "rem_sleep_hours"
        ]
        / latest[
            "sleep_hours"
        ]
        * 100
    )

    core_sleep = max(
        latest[
            "sleep_hours"
        ]
        - latest[
            "deep_sleep_hours"
        ]
        - latest[
            "rem_sleep_hours"
        ],
        0,
    )

    core_percent = (
        core_sleep
        / latest[
            "sleep_hours"
        ]
        * 100
    )

    sleep_columns = st.columns(
        4
    )

    with sleep_columns[0]:
        render_html(
            metric_card(
                "😴",
                "Total sleep",
                (
                    format_measurement(latest.get("sleep_hours", np.nan), 1, "h")
                ),
                baseline_detail(
                    "sleep_hours",
                    1,
                    "h",
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

    with sleep_columns[1]:
        render_html(
            metric_card(
                "🌙",
                "Deep sleep",
                (
                    format_measurement(latest.get("deep_sleep_hours", np.nan), 1, "h")
                ),
                (
                    f"{deep_percent:.0f}% of total sleep"
                ),
                "Last synthetic night",
                "⌚ Apple Watch",
                "neutral",
            )
        )

    with sleep_columns[2]:
        render_html(
            metric_card(
                "💭",
                "REM sleep",
                (
                    format_measurement(latest.get("rem_sleep_hours", np.nan), 1, "h")
                ),
                (
                    f"{rem_percent:.0f}% of total sleep"
                ),
                "Last synthetic night",
                "⌚ Apple Watch",
                "neutral",
            )
        )

    with sleep_columns[3]:
        render_html(
            metric_card(
                "🛏️",
                "Core sleep",
                f"{core_sleep:.1f} h",
                (
                    f"{core_percent:.0f}% of total sleep"
                ),
                "Calculated remainder",
                "🌿 Calculated by Mallow",
                "neutral",
            )
        )

    st.write("")

    respiratory_columns = st.columns(
        3
    )

    with respiratory_columns[0]:
        render_html(
            metric_card(
                "🌬️",
                "Respiratory rate",
                (
                    f"{intraday_latest['respiratory_rate']:.1f} / min"
                    if view_days == 1
                    else (
                        format_measurement(latest.get("respiratory_rate", np.nan), 1, "/ min")
                    )
                ),
                (
                    f"Today average: "
                    f"{intraday_data['respiratory_rate'].mean():.1f}"
                    if view_days == 1
                    else baseline_detail(
                        "respiratory_rate",
                        1,
                        "/ min",
                    )
                ),
                (
                    "Today's synthetic reading"
                    if view_days == 1
                    else status_for(
                        "respiratory_rate"
                    )["label"]
                ),
                "⌚ Apple Watch",
                (
                    "neutral"
                    if view_days == 1
                    else status_style(
                        "respiratory_rate"
                    )
                ),
            )
        )

    with respiratory_columns[1]:
        render_html(
            metric_card(
                "🫁",
                "Oxygen saturation",
                (
                    f"{intraday_latest['oxygen_saturation']:.1f}%"
                    if view_days == 1
                    else (
                        format_measurement(latest.get("oxygen_saturation", np.nan), 1, "%")
                    )
                ),
                (
                    f"Today average: "
                    f"{intraday_data['oxygen_saturation'].mean():.1f}%"
                    if view_days == 1
                    else baseline_detail(
                        "oxygen_saturation",
                        1,
                        "%",
                    )
                ),
                (
                    "Today's synthetic reading"
                    if view_days == 1
                    else status_for(
                        "oxygen_saturation"
                    )["label"]
                ),
                "⌚ Apple Watch",
                (
                    "neutral"
                    if view_days == 1
                    else status_style(
                        "oxygen_saturation"
                    )
                ),
            )
        )

    with respiratory_columns[2]:
        render_html(
            metric_card(
                "🌡️",
                "Wrist temperature",
                (
                    f"{intraday_latest['wrist_temperature']:+.2f} °F"
                    if view_days == 1
                    else (
                        format_measurement(latest.get("wrist_temperature", np.nan), 2, "°F", signed=True)
                    )
                ),
                (
                    "Synthetic deviation today"
                    if view_days == 1
                    else (
                        "Deviation from personal reference"
                    )
                ),
                (
                    "Today's synthetic reading"
                    if view_days == 1
                    else status_for(
                        "wrist_temperature"
                    )["label"]
                ),
                "⌚ Apple Watch",
                (
                    "neutral"
                    if view_days == 1
                    else status_style(
                        "wrist_temperature"
                    )
                ),
            )
        )


with relationships_tab:

    st.subheader(
        "Relationships 📊"
    )

    if view_days == 1:
        st.info(
            "Relationship analysis is intended for patterns "
            "across multiple days. Choose 7, 30, or 90 days "
            "to compare measurements."
        )

        st.caption(
            "For Today, use the intraday timeline on the "
            "Overview tab instead."
        )

    else:
        st.caption(
            "Mallow looks for measurements that have tended "
            "to move together in your selected window. "
            "Correlation describes association, not causation."
        )

        discovered_relationships = all_relationships(
            health_data,
            days=view_days,
            minimum_strength=0.35,
        )

        st.markdown(
            "### Mallow noticed 🌱"
        )

        if discovered_relationships:
            discovery_columns = st.columns(
                3
            )

            for column, result in zip(
                discovery_columns,
                discovered_relationships[:3],
            ):
                with column:
                    title = (
                        f"{result['metric_a_name'].title()} "
                        f"↔ {result['metric_b_name'].title()}"
                    )

                    render_html(
                        relationship_card(
                            title=title,
                            correlation=result[
                                "correlation"
                            ],
                            strength=result[
                                "strength"
                            ],
                            direction=result[
                                "direction"
                            ],
                            sample_count=result[
                                "sample_count"
                            ],
                            data_support=result[
                                "data_support"
                            ],
                        )
                    )
        else:
            st.info(
                "I don't see a clear relationship stronger "
                "than |r| = 0.35 in this window."
            )

        if view_days == 7:
            st.caption(
                "Seven days is a very small sample, so these "
                "relationships can change quickly. Longer windows "
                "are generally more stable."
            )
        else:
            st.caption(
                "These are exploratory statistical patterns in "
                "your recent data, not medical conclusions."
            )

        st.write("")
        st.markdown(
            "### Compare two measurements"
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

        selectors = st.columns(
            2
        )

        with selectors[0]:
            metric_a_name = st.selectbox(
                "First measurement",
                list(
                    available_metrics.keys()
                ),
                index=0,
                key="relationship_metric_a",
            )

        with selectors[1]:
            metric_b_name = st.selectbox(
                "Second measurement",
                list(
                    available_metrics.keys()
                ),
                index=1,
                key="relationship_metric_b",
            )

        metric_a = available_metrics[
            metric_a_name
        ]

        metric_b = available_metrics[
            metric_b_name
        ]

        if metric_a == metric_b:
            st.info(
                "Choose two different measurements."
            )

        else:
            relationship_data = get_relationship_data(
                health_data,
                metric_a,
                metric_b,
                days=view_days,
            )

            correlation = calculate_correlation(
                health_data,
                metric_a,
                metric_b,
                days=view_days,
            )

            if (
                correlation is None
                or len(
                    relationship_data
                ) < 5
            ):
                st.info(
                    "There isn't enough usable variation in "
                    "this window to compare those measurements "
                    "reliably yet."
                )

            else:
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
                    slope
                    * x_line
                    + intercept
                )

                relationship_fig = (
                    go.Figure()
                )

                relationship_fig.add_trace(
                    go.Scatter(
                        x=x,
                        y=y,
                        mode="markers",
                        name="Daily measurements",
                        marker=dict(
                            size=10,
                            color=colors[
                                "chart_line"
                            ],
                            opacity=0.88,
                        ),
                        hovertemplate=(
                            f"{metric_a_name}: "
                            "%{x:.2f}<br>"
                            f"{metric_b_name}: "
                            "%{y:.2f}"
                            "<extra></extra>"
                        ),
                    )
                )

                relationship_fig.add_trace(
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

                relationship_fig.update_xaxes(
                    **chart_xaxis(
                        metric_a_name
                    )
                )

                relationship_fig.update_yaxes(
                    **chart_yaxis(
                        metric_b_name
                    )
                )

                apply_chart_style(
                    relationship_fig,
                    height=450,
                    showlegend=True,
                )

                st.plotly_chart(
                    relationship_fig,
                    use_container_width=True,
                    config={
                        "displayModeBar": False,
                    },
                )

                relationship_summary = (
                    describe_relationship(
                        health_data,
                        metric_a,
                        metric_b,
                        days=view_days,
                    )
                )

                render_html(
                    f"""
                    <div class="insight-card">
                        🌿 <b>Mallow's observation</b>
                        <br><br>
                        {relationship_summary}
                        <br><br>
                        <span style="color:{colors["muted"]};">
                            Paired observations used:
                            {len(relationship_data)}.
                            Correlation does not establish
                            cause and effect.
                        </span>
                    </div>
                    """
                )



with apple_health_tab:

    st.subheader(
        "Apple Health import"
    )

    st.write(
        "Import your Apple Health export to see which measurements "
        "Mallow can read. Missing measurements stay missing — "
        "Mallow never fills gaps in real health data with synthetic values."
    )

    st.info(
        "On iPhone: Health app → your profile picture → "
        "Export All Health Data. You can upload the resulting ZIP file "
        "directly here, or upload export.xml from inside the archive."
    )

    st.warning(
        "For private personal health data, use Mallow locally on your own "
        "computer. The public Streamlit demo should remain a synthetic-data "
        "portfolio demo rather than a place to upload sensitive exports."
    )

    uploaded_health_file = st.file_uploader(
        "Upload Apple Health export",
        type=[
            "zip",
            "xml",
        ],
        help=(
            "Apple Health exports may be large. "
            "Mallow processes the file only for this Streamlit session."
        ),
        key="apple_health_export",
    )

    if uploaded_health_file is None:
        st.caption(
            "No Apple Health export loaded yet."
        )

    else:
        try:
            uploaded_bytes = (
                uploaded_health_file.getvalue()
            )

            (
                apple_daily_data,
                apple_import_info,
            ) = load_apple_health_export(
                uploaded_bytes
            )

        except Exception as exc:
            st.error(
                "Mallow could not read this Apple Health export."
            )

            st.caption(
                str(
                    exc
                )
            )

        else:
            st.session_state[
                "apple_health_data"
            ] = apple_daily_data.copy()

            st.session_state[
                "apple_health_info"
            ] = apple_import_info.copy()

            st.success(
                "Apple Health export loaded successfully."
            )

            action_columns = st.columns(
                2
            )

            with action_columns[
                0
            ]:
                if st.button(
                    "Use this data in Mallow",
                    type="primary",
                    use_container_width=True,
                ):
                    st.session_state[
                        "mallow_data_source"
                    ] = "apple"

                    st.rerun()

            with action_columns[
                1
            ]:
                if st.button(
                    "Clear imported data",
                    use_container_width=True,
                ):
                    st.session_state[
                        "apple_health_data"
                    ] = None

                    st.session_state[
                        "apple_health_info"
                    ] = None

                    st.session_state[
                        "mallow_data_source"
                    ] = "demo"

                    st.rerun()

            summary_columns = st.columns(
                4
            )

            summary_columns[
                0
            ].metric(
                "Calendar days",
                apple_import_info[
                    "calendar_days"
                ],
            )

            summary_columns[
                1
            ].metric(
                "Relevant records",
                apple_import_info[
                    "relevant_records"
                ],
            )

            summary_columns[
                2
            ].metric(
                "Available metrics",
                len(
                    apple_import_info[
                        "available_metrics"
                    ]
                ),
            )

            summary_columns[
                3
            ].metric(
                "Detected sources",
                len(
                    apple_import_info[
                        "source_names"
                    ]
                ),
            )

            st.write(
                ""
            )

            st.markdown(
                "#### Measurements Mallow found"
            )

            if apple_import_info[
                "available_metric_names"
            ]:
                st.write(
                    " • ".join(
                        apple_import_info[
                            "available_metric_names"
                        ]
                    )
                )
            else:
                st.caption(
                    "No supported measurements were found."
                )

            if apple_import_info[
                "unavailable_metric_names"
            ]:
                with st.expander(
                    "Measurements not present in this export"
                ):
                    st.write(
                        " • ".join(
                            apple_import_info[
                                "unavailable_metric_names"
                            ]
                        )
                    )

                    st.caption(
                        "This is normal. Apple Watch models and connected "
                        "devices do not all record the same measurements."
                    )

            if apple_import_info[
                "source_names"
            ]:
                with st.expander(
                    "Detected Health data sources"
                ):
                    for source_name in apple_import_info[
                        "source_names"
                    ]:
                        st.write(
                            f"• {source_name}"
                        )

            st.markdown(
                "#### Imported daily data"
            )

            display_apple_data = (
                apple_daily_data
                .sort_values(
                    "date",
                    ascending=False,
                )
                .reset_index(
                    drop=True
                )
            )

            st.dataframe(
                display_apple_data,
                use_container_width=True,
                hide_index=True,
            )

            csv_data = (
                display_apple_data
                .to_csv(
                    index=False
                )
                .encode(
                    "utf-8"
                )
            )

            st.download_button(
                "Download processed Mallow CSV",
                data=csv_data,
                file_name="mallow_apple_health_daily.csv",
                mime="text/csv",
            )

            if using_apple_health:
                st.success(
                    "The main Mallow dashboard is currently using your "
                    "imported Apple Health dataset."
                )
            else:
                st.caption(
                    "Choose “Use this data in Mallow” above to switch the "
                    "main dashboard from synthetic demo data to this import."
                )


st.write("")
st.divider()

footer_source_text = (
    "The active dashboard is using an imported Apple Health dataset."
    if using_apple_health
    else "The active dashboard is using synthetic demonstration data."
)

st.caption(
    "Mallow is a personal health-monitoring project and is not intended "
    "for diagnosis, treatment, or clinical use. Baseline labels describe "
    "statistical differences from personal history, not whether a "
    "measurement is medically normal. "
    + footer_source_text
)
