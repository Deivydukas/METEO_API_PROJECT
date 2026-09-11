import pandas as pd


def interpolate_temperature(series: pd.Series,) -> pd.Series:

    # Ensure the series uses datetime index
    if not isinstance(
        series.index,
        pd.DatetimeIndex,
    ):
        raise TypeError(
            "Series index must be a DatetimeIndex."
        )

    series = series.sort_index()

    # Resample and interpolate missing values
    interpolated = (
        series
        .resample("5min")
        .interpolate(method="time")
    )

    return interpolated