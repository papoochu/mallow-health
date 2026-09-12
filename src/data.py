import numpy as np
import pandas as pd

from datetime import datetime, timedelta


def generate_health_data(days=90, seed=42):
    """
    Generate synthetic daily health measurements for the Mallow prototype.

    These values are completely fictional and are only used to develop
    and test the dashboard.
    """

    rng = np.random.default_rng(seed)

    dates = [
        datetime.today().date() - timedelta(days=i)
        for i in range(days - 1, -1, -1)
    ]

    # Cardiovascular
    resting_hr = rng.normal(
        loc=62,
        scale=3,
        size=days,
    )

    hrv = rng.normal(
        loc=48,
        scale=7,
        size=days,
    )

    systolic_bp = rng.normal(
        loc=118,
        scale=6,
        size=days,
    )

    diastolic_bp = rng.normal(
        loc=74,
        scale=4,
        size=days,
    )

    # Metabolic
    glucose = rng.normal(
        loc=98,
        scale=8,
        size=days,
    )

    # Respiratory
    oxygen_saturation = rng.normal(
        loc=97.5,
        scale=0.7,
        size=days,
    )

    respiratory_rate = rng.normal(
        loc=14.5,
        scale=1,
        size=days,
    )

    # Temperature is stored as deviation from personal baseline
    wrist_temperature = rng.normal(
        loc=0,
        scale=0.25,
        size=days,
    )

    # Sleep
    sleep_hours = rng.normal(
        loc=7.1,
        scale=0.7,
        size=days,
    )

    deep_sleep_hours = sleep_hours * rng.normal(
        loc=0.17,
        scale=0.02,
        size=days,
    )

    rem_sleep_hours = sleep_hours * rng.normal(
        loc=0.22,
        scale=0.025,
        size=days,
    )

    # Prevent impossible demo values
    resting_hr = np.clip(resting_hr, 45, 100)
    hrv = np.clip(hrv, 15, 100)

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

    sleep_hours = np.clip(
        sleep_hours,
        4,
        10,
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

    # Derived cardiovascular measurements
    data["pulse_pressure"] = (
        data["systolic_bp"]
        - data["diastolic_bp"]
    )

    data["map"] = (
        data["diastolic_bp"]
        + data["pulse_pressure"] / 3
    )

    return data