import os
import pandas as pd

from datetime import timedelta
from src.meteo_api import MeteoCLient
from src.weather_analysis import WeatherAnalysis
from src.data_manager import (
    load_historical,
    save_historical,
    is_historical_data_current,
)
from src.plotting import plot_temperature
from src.interpolation import interpolate_temperature


def main():

    # Historical data file
    filename = "historical_weather.csv"

    # API client
    client = MeteoCLient(
        station_code="vilniaus-ams",
        place_code="vilnius",
        api_url="https://api.meteo.lt/v1",
    )

    # Calculate historical date range
    end_date = pd.Timestamp.now(tz="Europe/Vilnius")
    start_date = end_date - timedelta(days=365)

    # Load existing data or fetch fresh data
    if os.path.exists(filename):

        print("Loading historical data...")

        historical_data = load_historical(
            filename=filename
        )

        if is_historical_data_current(
            historical_data,
            today=end_date.date(),
        ):
            print("Historical data is current.")

        else:
            print(
                "Historical data is outdated. "
                "Fetching new data..."
            )

            historical_data = client.get_historical(
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d"),
            )

            save_historical(
                historical_data,
                filename=filename,
            )

    else:

        print(
            "Historical data not found. "
            "Fetching from API..."
        )

        historical_data = client.get_historical(
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
        )

        save_historical(
            historical_data,
            filename=filename,
        )

        print(
            "Historical data saved to",
            filename,
        )

    # Analyze historical data
    analyzer = WeatherAnalysis(historical_data)

    average_temperature = analyzer.average_temperature()

    average_humidity = analyzer.average_humidity()
    
    average_day_temperature = analyzer.average_day_temperature()

    average_night_temperature = analyzer.average_night_temperature()

    rainy_count = analyzer.rainy_weekends()
    

    # Print analysis results
    print(
        f"Average Temperature: "
        f"{average_temperature:.2f} C"
    )

    print(
        f"Average Humidity: "
        f"{average_humidity:.2f} %"
    )

    print(
        f"Average Day Temperature: "
        f"{average_day_temperature:.2f} C"
    )

    print(
        f"Average Night Temperature: "
        f"{average_night_temperature:.2f} C"
    )

    print(
        f"Rainy Weekends: {rainy_count}"
    )

    # Get forecast and combine with historical data
    forecast_data = client.get_forecast()

    temperature_data = (
        analyzer.combine_with_forecast(
            forecast_data
        )
    )

    plot_temperature(temperature_data)

    # Interpolate historical temperature data
    temperature_series = historical_data[
        "airTemperature"
    ]

    interpolated_temperature_series = (
        interpolate_temperature(
            temperature_series
        )
    )

    print(
        interpolated_temperature_series.head(20)
    )


if __name__ == "__main__":
    main()