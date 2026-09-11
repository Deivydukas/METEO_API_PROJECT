import pandas as pd


class WeatherAnalysis:

    def __init__(self, weather_data):
        self.weather_data = weather_data

    # Calculate overall average temperature
    def average_temperature(self):
        return self.weather_data["airTemperature"].mean()

    # Calculate average humidity
    def average_humidity(self):
        return self.weather_data["relativeHumidity"].mean()

    # Calculate average daytime temperature
    def average_day_temperature(self):

        daytime = self.weather_data.between_time("08:00","20:00",)

        return daytime["airTemperature"].mean()

    # Calculate average nighttime temperature
    def average_night_temperature(self):

        nighttime = self.weather_data.between_time("20:01","07:59",)

        return nighttime["airTemperature"].mean()

    # Find weekends with rain
    def rainy_weekends(self):

        data = self.weather_data.copy()

        weekend = data[data.index.dayofweek >= 5]

        rain_conditions = {
            "light-rain",
            "rain",
            "heavy-rain",
            "isolated-thunderstorms",
            "thunderstorms",
            "heavy-rain-with-thunderstorms",
            "freezing-rain",
            "rain-showers",
            "light-rain-at-times",
            "rain-at-times",
        }

        rainy = weekend[weekend["conditionCode"].isin(rain_conditions)]

        if rainy.empty:
            return 0

        weekend_start = (
            rainy.index
            - pd.to_timedelta(
                (rainy.index.dayofweek - 5) % 7,
                unit="D",
            )
        ).normalize()

        rainy_weekend_dates = sorted(weekend_start.unique())

        return (len(rainy_weekend_dates))

    # Combine recent measurements with forecast
    def combine_with_forecast(self,forecast_data,):

        historical = self.weather_data[["airTemperature"]].copy()

        last_week = (self.weather_data.index.max()- pd.Timedelta(days=7))

        historical = historical[historical.index >= last_week]

        historical["type"] = "Measured"

        forecast = forecast_data[["airTemperature"]].copy()

        forecast = forecast[forecast.index> self.weather_data.index.max()]

        forecast["type"] = "Forecast"

        combined = pd.concat([historical, forecast])

        return combined.sort_index()