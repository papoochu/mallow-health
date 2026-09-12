import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from datetime import datetime, timedelta
from textwrap import dedent


st.set_page_config(
    page_title="Mallow",
    page_icon="🌿",
    layout="wide",
)


# Sidebar
with st.sidebar:
    st.markdown("## Mallow 🌿")
    st.caption("your gentle personal health companion")

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
        "neutral_bg": "#393329",
        "neutral_text": "#D7C7A4",
        "chart_bg": "#202720",
        "chart_grid": "#354139",
        "chart_line": "#A5C4AA",
        "chart_average": "#C6A8B8",
        "input": "#202720",
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
        "neutral_bg": "#F5F0E6",
        "neutral_text": "#81765F",
        "chart_bg": "#FFFFFF",
        "chart_grid": "#EEE9E3",
        "chart_line": "#7F9D87",
        "chart_average": "#C9B3BE",
        "input": "#FFFFFF",
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

    .status-good {{
        display: inline-block;
        background-color: {colors["good_bg"]};
        color: {colors["good_text"]};
        border-radius: 999px;
        padding: 0.25rem 0.55rem;
        font-size: 0.74rem;
        margin-top: 0.15rem;
    }}

    .status-neutral {{
        display: inline-block;
        background-color: {colors["neutral_bg"]};
        color: {colors["neutral_text"]};
        border-radius: 999px;
        padding: 0.25rem 0.55rem;
        font-size: 0.74rem;
        margin-top: 0.15rem;
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
    }}

    /* Ask Mallow input */

    [data-testid="stTextInput"] {{
        margin-top: 0.25rem;
    }}

    [data-testid="stTextInput"] div[data-baseweb="input"] {{
        background-color: {colors["input"]} !important;
        border: 1px solid {colors["border"]} !important;
        border-radius: 16px !important;
        box-shadow: none !important;
        overflow: hidden !important;
    }}

    [data-testid="stTextInput"] div[data-baseweb="input"]:hover {{
        border-color: {colors["muted"]} !important;
    }}

    [data-testid="stTextInput"] div[data-baseweb="input"]:focus-within {{
        border: 1px solid {colors["heading"]} !important;
        box-shadow: none !important;
        outline: none !important;
    }}

    [data-testid="stTextInput"] input {{
        background-color: transparent !important;
        color: {colors["text"]} !important;
        border: none !important;
        border-radius: 0 !important;
        outline: none !important;
        box-shadow: none !important;
        padding: 0.8rem 0.9rem !important;
    }}

    [data-testid="stTextInput"] input::placeholder {{
        color: {colors["muted"]} !important;
        opacity: 1 !important;
    }}

    [data-testid="stTextInput"] div[data-baseweb="base-input"] {{
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
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
    clean_html = dedent(content).strip()

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
    status_class = (
        "status-good"
        if status_type == "good"
        else "status-neutral"
    )

    return (
        f'<div class="metric-card">'
        f'<div class="metric-title">{icon} {title}</div>'
        f'<div class="metric-value">{value}</div>'
        f'<div class="metric-detail">{detail}</div>'
        f'<div class="{status_class}">{status}</div>'
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


# Welcome card
render_html(
    f"""
    <div class="welcome-card">
        <b>Good morning ☀️</b>
        <br><br>
        Most of your sample measurements are close to your usual range today.
        <br><br>
        <span style="color:{colors["muted"]}">
            Mallow is currently displaying synthetic demo data.
        </span>
    </div>
    """
)


# Tabs
overview_tab, heart_tab, metabolic_tab, sleep_tab = st.tabs(
    [
        "🌿 Overview",
        "❤️ Heart & circulation",
        "🩸 Blood & metabolic",
        "🌙 Sleep & respiratory",
    ]
)


# Overview
with overview_tab:

    st.subheader("Today's vitals")

    row1 = st.columns(4)

    with row1[0]:
        render_html(
            metric_card(
                "❤️",
                "Heart rate",
                "68 bpm",
                "Resting: 61 bpm",
                "Within your usual range",
                "⌚ Apple Watch",
            )
        )

    with row1[1]:
        render_html(
            metric_card(
                "🩸",
                "Blood pressure",
                "116 / 72",
                "MAP: 87 mmHg",
                "Near your baseline",
                "🩺 Connected cuff",
            )
        )

    with row1[2]:
        render_html(
            metric_card(
                "🍬",
                "Blood glucose",
                "94 mg/dL",
                "Today's average: 101 mg/dL",
                "Stable",
                "🩸 CGM / HealthKit",
            )
        )

    with row1[3]:
        render_html(
            metric_card(
                "🫁",
                "Oxygen saturation",
                "98%",
                "Overnight average: 97%",
                "Typical",
                "⌚ Apple Watch",
            )
        )

    st.write("")

    row2 = st.columns(4)

    with row2[0]:
        render_html(
            metric_card(
                "💓",
                "HRV",
                "52 ms",
                "30-day average: 48 ms",
                "Slightly above baseline",
                "⌚ Apple Watch",
            )
        )

    with row2[1]:
        render_html(
            metric_card(
                "🌡️",
                "Wrist temperature",
                "+0.1 °F",
                "Compared with personal baseline",
                "Typical",
                "⌚ Apple Watch",
            )
        )

    with row2[2]:
        render_html(
            metric_card(
                "🌬️",
                "Respiratory rate",
                "14.2 / min",
                "30-day average: 14.6",
                "Typical",
                "⌚ Apple Watch",
            )
        )

    with row2[3]:
        render_html(
            metric_card(
                "😴",
                "Sleep",
                "7 h 34 m",
                "Deep sleep: 1 h 16 m",
                "28 min above average",
                "⌚ Apple Watch",
            )
        )

    st.write("")

    st.subheader("30-day heart trend")

    np.random.seed(42)

    dates = [
        datetime.today() - timedelta(days=i)
        for i in range(29, -1, -1)
    ]

    heart_rate = np.random.normal(
        loc=62,
        scale=2.5,
        size=30,
    )

    heart_df = pd.DataFrame(
        {
            "Date": dates,
            "Resting Heart Rate": heart_rate,
        }
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=heart_df["Date"],
            y=heart_df["Resting Heart Rate"],
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
                "%{y:.0f} bpm"
                "<extra></extra>"
            ),
        )
    )

    fig.add_hline(
        y=62,
        line_dash="dot",
        line_color=colors["chart_average"],
        annotation_text="30-day average",
        annotation_font_color=colors["muted"],
    )

    fig.update_layout(
        height=350,
        margin=dict(
            l=25,
            r=25,
            t=25,
            b=25,
        ),
        paper_bgcolor=colors["chart_bg"],
        plot_bgcolor=colors["chart_bg"],
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
            gridcolor=colors["chart_grid"],
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

    st.subheader("Mallow noticed 🌱")

    render_html(
        """
        <div class="insight-card">
            <b>
                Your cardiovascular measurements look fairly steady today.
            </b>
            <br><br>
            Your sample HRV is slightly higher than its 30-day average,
            while your resting heart rate remains close to baseline.
            <br><br>
            No major deviation appears in the current demo data.
        </div>
        """
    )

    st.subheader("Ask Mallow 💬")

    question = st.text_input(
        "Ask something about your health data",
        placeholder="Why has my resting heart rate changed this week?",
        label_visibility="collapsed",
    )

    if question:
        render_html(
            """
            <div class="insight-card">
                🌿 <b>Mallow isn't connected to its AI brain yet.</b>
                <br><br>
                Eventually, this response will use your measurements,
                personal baselines, trends, and detected patterns to
                explain what may have changed.
            </div>
            """
        )


# Heart & circulation
with heart_tab:

    st.subheader("Heart & circulation ❤️")

    row1 = st.columns(3)

    with row1[0]:
        render_html(
            metric_card(
                "❤️",
                "Resting heart rate",
                "61 bpm",
                "30-day average: 62 bpm",
                "Typical",
                "⌚ Apple Watch",
            )
        )

    with row1[1]:
        render_html(
            metric_card(
                "💓",
                "HRV",
                "52 ms",
                "30-day average: 48 ms",
                "Above baseline",
                "⌚ Apple Watch",
            )
        )

    with row1[2]:
        render_html(
            metric_card(
                "🫀",
                "Last ECG",
                "Sinus rhythm",
                "72 bpm during recording",
                "No demo alert",
                "⌚ Apple Watch",
            )
        )

    st.write("")

    row2 = st.columns(3)

    with row2[0]:
        render_html(
            metric_card(
                "🩸",
                "Blood pressure",
                "116 / 72",
                "Pulse pressure: 44 mmHg",
                "Near baseline",
                "🩺 Connected cuff",
            )
        )

    with row2[1]:
        render_html(
            metric_card(
                "📊",
                "Mean arterial pressure",
                "87 mmHg",
                "Estimated from cuff measurement",
                "Stable",
                "🌿 Calculated by Mallow",
            )
        )

    with row2[2]:
        render_html(
            metric_card(
                "🏃",
                "Heart-rate recovery",
                "27 bpm",
                "1-minute recovery",
                "Typical",
                "⌚ Apple Watch",
            )
        )

    st.write("")

    st.subheader("Rhythm & monitoring")

    row3 = st.columns(3)

    with row3[0]:
        render_html(
            metric_card(
                "💗",
                "Irregular rhythm alerts",
                "None",
                "Demo history",
                "No recent alerts",
                "⌚ Apple Watch",
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
                status_type="neutral",
            )
        )

    with row3[2]:
        render_html(
            metric_card(
                "🚶",
                "Walking heart rate",
                "91 bpm",
                "30-day average: 93 bpm",
                "Typical",
                "⌚ Apple Watch",
            )
        )


# Blood & metabolic
with metabolic_tab:

    st.subheader("Blood & metabolic 🩸")

    row1 = st.columns(3)

    with row1[0]:
        render_html(
            metric_card(
                "🍬",
                "Current glucose",
                "94 mg/dL",
                "Daily average: 101 mg/dL",
                "Stable",
                "🩸 CGM",
            )
        )

    with row1[1]:
        render_html(
            metric_card(
                "📈",
                "Glucose variability",
                "12%",
                "Synthetic demo value",
                "Stable",
                "🌿 Calculated by Mallow",
            )
        )

    with row1[2]:
        render_html(
            metric_card(
                "⏱️",
                "Time in selected range",
                "94%",
                "Synthetic demo value",
                "Stable",
                "🩸 CGM",
            )
        )

    st.write("")

    row2 = st.columns(3)

    with row2[0]:
        render_html(
            metric_card(
                "🩸",
                "Blood pressure",
                "116 / 72",
                "Latest cuff reading",
                "Near baseline",
                "🩺 Connected cuff",
            )
        )

    with row2[1]:
        render_html(
            metric_card(
                "⚖️",
                "Weight",
                "—",
                "No demo measurement",
                "Awaiting data",
                "HealthKit / smart scale",
                status_type="neutral",
            )
        )

    with row2[2]:
        render_html(
            metric_card(
                "💉",
                "Insulin delivery",
                "—",
                "No demo measurement",
                "Awaiting data",
                "HealthKit",
                status_type="neutral",
            )
        )

    st.write("")

    st.info(
        "Blood glucose and blood-pressure measurements will come "
        "from compatible devices, HealthKit, or manual entries. "
        "Mallow does not directly measure them."
    )


# Sleep & respiratory
with sleep_tab:

    st.subheader("Sleep & respiratory 🌙")

    row1 = st.columns(4)

    with row1[0]:
        render_html(
            metric_card(
                "😴",
                "Total sleep",
                "7 h 34 m",
                "30-day average: 7 h 06 m",
                "Above average",
                "⌚ Apple Watch",
            )
        )

    with row1[1]:
        render_html(
            metric_card(
                "🌙",
                "Deep sleep",
                "1 h 16 m",
                "17% of total sleep",
                "Typical",
                "⌚ Apple Watch",
            )
        )

    with row1[2]:
        render_html(
            metric_card(
                "💭",
                "REM sleep",
                "1 h 41 m",
                "22% of total sleep",
                "Typical",
                "⌚ Apple Watch",
            )
        )

    with row1[3]:
        render_html(
            metric_card(
                "🛏️",
                "Core sleep",
                "4 h 11 m",
                "55% of total sleep",
                "Typical",
                "⌚ Apple Watch",
            )
        )

    st.write("")

    row2 = st.columns(4)

    with row2[0]:
        render_html(
            metric_card(
                "🌬️",
                "Respiratory rate",
                "14.2 / min",
                "Overnight average",
                "Typical",
                "⌚ Apple Watch",
            )
        )

    with row2[1]:
        render_html(
            metric_card(
                "🫁",
                "Oxygen saturation",
                "98%",
                "Overnight average: 97%",
                "Typical",
                "⌚ Apple Watch",
            )
        )

    with row2[2]:
        render_html(
            metric_card(
                "🌡️",
                "Wrist temperature",
                "+0.1 °F",
                "Compared with baseline",
                "Typical",
                "⌚ Apple Watch",
            )
        )

    with row2[3]:
        render_html(
            metric_card(
                "🌘",
                "Night awakenings",
                "2",
                "Synthetic demo value",
                "Typical",
                "⌚ Apple Watch",
            )
        )


# Footer
st.write("")
st.divider()

st.caption(
    "Mallow is a personal health-monitoring project and is not intended "
    "for diagnosis, treatment, or clinical use. "
    "All measurements shown in this prototype are synthetic."
)