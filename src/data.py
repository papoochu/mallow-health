import numpy as np
import pandas as pd

from datetime import datetime, timedelta


def generate_health_data(days=90, seed=42):
    """
    Generate synthetic daily health measurements for the Mallow prototype.

    Some measurements intentionally contain mild relationships so that
    Mallow's analytics, correlation tools, and ML features can be tested.

    These values are completely fictional and are not clinical data.
    """

    rng = np.random.default_rng(seed)

    dates = [
        datetime.today().date() - timedelta(days=i)
        for i in range(days - 1, -1, -1)
    ]

    # Sleep
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

    # Difference from the synthetic person's typical sleep duration
    sleep_deviation = (
        sleep_hours - 7.1
    )

    # Cardiovascular
    # Less sleep tends to occur alongside a higher resting heart rate.
    resting_hr = (
        62
        - 2.5 * sleep_deviation
        + rng.normal(
            loc=0,
            scale=1.8,
            size=days,
        )
    )

    # More sleep tends to occur alongside higher HRV.
    hrv = (
        48
        + 5.0 * sleep_deviation
        + rng.normal(
            loc=0,
            scale=3.5,
            size=days,
        )
    )

    # Blood pressure has a smaller relationship with sleep.
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

    # Metabolic
    # Shorter sleep is given a modest association with higher glucose.
    glucose = (
        98
        - 2.5 * sleep_deviation
        + rng.normal(
            loc=0,
            scale=6.0,
            size=days,
        )
    )

    # Respiratory
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

    # Temperature
    # Stored as deviation from personal wrist-temperature baseline.
    wrist_temperature = rng.normal(
        loc=0,
        scale=0.25,
        size=days,
    )

    # Sleep stages
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

    # Keep synthetic values within plausible demo ranges
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

    # Build health dataset
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