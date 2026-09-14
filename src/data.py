import numpy as np
import pandas as pd

from datetime import datetime, timedelta


def generate_health_data(days=90, seed=42):
    """
    Generate synthetic daily health measurements for Mallow.

    These values are fictional and are used only for testing
    analytics, visualization, and ML features.
    """

    rng = np.random.default_rng(seed)

    dates = [
        datetime.today().date() - timedelta(days=i)
        for i in range(days - 1, -1, -1)
    ]

    sleep_hours = rng.normal(
        loc=7.1,
        scale=0.7,
        size=days,
    )

    sleep_hours = np.clip(
        sleep_hours,
        4.0,
        10.0,
    )

    sleep_deviation = (
        sleep_hours - 7.1
    )

    resting_hr = (
        62
        - 2.5 * sleep_deviation
        + rng.normal(
            loc=0,
            scale=1.8,
            size=days,
        )
    )

    hrv = (
        48
        + 5.0 * sleep_deviation
        + rng.normal(
            loc=0,
            scale=3.5,
            size=days,
        )
    )

    systolic_bp = (
        118
        - 1.5 * sleep_deviation
        + rng.normal(
            loc=0,
            scale=5.5,
            size=days,
        )
    )

    diastolic_bp = (
        74
        - 0.8 * sleep_deviation
        + rng.normal(
            loc=0,
            scale=3.5,
            size=days,
        )
    )

    glucose = (
        98
        - 2.5 * sleep_deviation
        + rng.normal(
            loc=0,
            scale=6.0,
            size=days,
        )
    )

    oxygen_saturation = rng.normal(
        loc=97.5,
        scale=0.7,
        size=days,
    )

    respiratory_rate = rng.normal(
        loc=14.5,
        scale=1.0,
        size=days,
    )

    wrist_temperature = rng.normal(
        loc=0,
        scale=0.25,
        size=days,
    )

    deep_sleep_fraction = rng.normal(
        loc=0.17,
        scale=0.02,
        size=days,
    )

    rem_sleep_fraction = rng.normal(
        loc=0.22,
        scale=0.025,
        size=days,
    )

    deep_sleep_hours = (
        sleep_hours
        * deep_sleep_fraction
    )

    rem_sleep_hours = (
        sleep_hours
        * rem_sleep_fraction
    )

    resting_hr = np.clip(
        resting_hr,
        45,
        100,
    )

    hrv = np.clip(
        hrv,
        15,
        100,
    )

    systolic_bp = np.clip(
        systolic_bp,
        90,
        160,
    )

    diastolic_bp = np.clip(
        diastolic_bp,
        55,
        110,
    )

    glucose = np.clip(
        glucose,
        65,
        180,
    )

    oxygen_saturation = np.clip(
        oxygen_saturation,
        90,
        100,
    )

    respiratory_rate = np.clip(
        respiratory_rate,
        8,
        25,
    )

    wrist_temperature = np.clip(
        wrist_temperature,
        -2.0,
        2.0,
    )

    deep_sleep_hours = np.clip(
        deep_sleep_hours,
        0,
        sleep_hours,
    )

    rem_sleep_hours = np.clip(
        rem_sleep_hours,
        0,
        sleep_hours,
    )

    data = pd.DataFrame(
        {
            "date": dates,
            "resting_hr": resting_hr,
            "hrv": hrv,
            "systolic_bp": systolic_bp,
            "diastolic_bp": diastolic_bp,
            "glucose": glucose,
            "oxygen_saturation": oxygen_saturation,
            "respiratory_rate": respiratory_rate,
            "wrist_temperature": wrist_temperature,
            "sleep_hours": sleep_hours,
            "deep_sleep_hours": deep_sleep_hours,
            "rem_sleep_hours": rem_sleep_hours,
        }
    )

    data["pulse_pressure"] = (
        data["systolic_bp"]
        - data["diastolic_bp"]
    )

    data["map"] = (
        data["diastolic_bp"]
        + data["pulse_pressure"] / 3
    )

    return data


def generate_intraday_data(
    latest_daily,
    interval_minutes=15,
    seed=84,
):
    """
    Generate synthetic measurements throughout the current day.

    Real health devices sample different measurements at different
    frequencies. This regular timeline is a simplified prototype
    used to test Mallow's intraday interface.
    """

    rng = np.random.default_rng(seed)

    now = pd.Timestamp.now().floor(
        f"{interval_minutes}min"
    )

    start = now.normalize()

    timestamps = pd.date_range(
        start=start,
        end=now,
        freq=f"{interval_minutes}min",
    )

    count = len(timestamps)

    hours = (
        timestamps.hour.to_numpy()
        + timestamps.minute.to_numpy() / 60
    )

    # General daytime rhythm
    circadian = np.sin(
        2 * np.pi * (hours - 8) / 24
    )

    # Activity bumps during common daytime periods
    morning_activity = 8 * np.exp(
        -0.5
        * ((hours - 9.0) / 0.7) ** 2
    )

    afternoon_activity = 10 * np.exp(
        -0.5
        * ((hours - 15.5) / 0.9) ** 2
    )

    evening_activity = 6 * np.exp(
        -0.5
        * ((hours - 19.0) / 0.8) ** 2
    )

    activity = (
        morning_activity
        + afternoon_activity
        + evening_activity
    )

    heart_rate = (
        float(latest_daily["resting_hr"])
        + 8
        + 3.5 * circadian
        + activity
        + rng.normal(
            loc=0,
            scale=2.2,
            size=count,
        )
    )

    heart_rate = np.clip(
        heart_rate,
        48,
        130,
    )

    hrv = (
        float(latest_daily["hrv"])
        - 0.55
        * (
            heart_rate
            - heart_rate.mean()
        )
        + rng.normal(
            loc=0,
            scale=3.0,
            size=count,
        )
    )

    hrv = np.clip(
        hrv,
        15,
        120,
    )

    # Simplified meal-related glucose changes
    breakfast = 14 * np.exp(
        -0.5
        * ((hours - 8.5) / 0.8) ** 2
    )

    lunch = 18 * np.exp(
        -0.5
        * ((hours - 13.0) / 0.9) ** 2
    )

    dinner = 16 * np.exp(
        -0.5
        * ((hours - 19.0) / 1.0) ** 2
    )

    glucose = (
        float(latest_daily["glucose"])
        - 5
        + breakfast
        + lunch
        + dinner
        + rng.normal(
            loc=0,
            scale=2.2,
            size=count,
        )
    )

    glucose = np.clip(
        glucose,
        65,
        180,
    )

    oxygen_saturation = (
        float(
            latest_daily[
                "oxygen_saturation"
            ]
        )
        + rng.normal(
            loc=0,
            scale=0.35,
            size=count,
        )
    )

    oxygen_saturation = np.clip(
        oxygen_saturation,
        92,
        100,
    )

    respiratory_rate = (
        float(
            latest_daily[
                "respiratory_rate"
            ]
        )
        + 0.04
        * (
            heart_rate
            - heart_rate.mean()
        )
        + rng.normal(
            loc=0,
            scale=0.45,
            size=count,
        )
    )

    respiratory_rate = np.clip(
        respiratory_rate,
        8,
        25,
    )

    wrist_temperature = (
        float(
            latest_daily[
                "wrist_temperature"
            ]
        )
        + 0.10 * circadian
        + rng.normal(
            loc=0,
            scale=0.05,
            size=count,
        )
    )

    wrist_temperature = np.clip(
        wrist_temperature,
        -2.0,
        2.0,
    )

    intraday = pd.DataFrame(
        {
            "timestamp": timestamps,
            "heart_rate": heart_rate,
            "hrv": hrv,
            "glucose": glucose,
            "oxygen_saturation": oxygen_saturation,
            "respiratory_rate": respiratory_rate,
            "wrist_temperature": wrist_temperature,
        }
    )

    # Blood pressure is sampled only a few times rather than
    # pretending a cuff produces continuous readings.
    intraday["systolic_bp"] = np.nan
    intraday["diastolic_bp"] = np.nan

    bp_times = [
        8,
        14,
        20,
    ]

    for hour in bp_times:
        candidates = intraday[
            intraday["timestamp"].dt.hour == hour
        ]

        if candidates.empty:
            continue

        index = candidates.index[0]

        intraday.loc[
            index,
            "systolic_bp",
        ] = (
            float(
                latest_daily[
                    "systolic_bp"
                ]
            )
            + rng.normal(
                loc=0,
                scale=3.0,
            )
        )

        intraday.loc[
            index,
            "diastolic_bp",
        ] = (
            float(
                latest_daily[
                    "diastolic_bp"
                ]
            )
            + rng.normal(
                loc=0,
                scale=2.0,
            )
        )

    return intraday