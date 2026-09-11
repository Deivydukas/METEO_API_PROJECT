import pandas as pd


# Save historical weather data
def save_historical(data,filename="historical_weather.csv",):
    data.to_csv(filename)


# Load historical weather data
def load_historical(filename="historical_weather.csv",):
    data = pd.read_csv(
        filename,
        index_col=0,
    )

    data.index = pd.to_datetime(
        data.index,
        utc=True,
    ).tz_convert("Europe/Vilnius")

    return data


# Check whether stored data contains today's data
def is_historical_data_current(data,today,):
    latest_date = data.index.max().date()

    return latest_date >= today