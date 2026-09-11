import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import requests as req


class MeteoCLient:

    def __init__(self, station_code, place_code, api_url):
        self.station_code = station_code
        self.place_code = place_code
        self.api_url = api_url

    # Fetch observations for one day
    def _get_day(self, date):

        date_string = date.strftime("%Y-%m-%d")

        url = (
            f"{self.api_url}/stations/"
            f"{self.station_code}/observations/"
            f"{date_string}"
        )

        for attempt in range(5):

            try:
                response = req.get(
                    url,
                    timeout=30,
                )

                # Handle rate limiting
                if response.status_code == 429:

                    wait_time = 10 * (attempt + 1)

                    print(
                        f"Rate limited. "
                        f"Waiting {wait_time}s..."
                    )

                    time.sleep(wait_time)
                    continue

                # No data available for this date
                if response.status_code == 404:
                    return []

                response.raise_for_status()

                return response.json()["observations"]

            except req.RequestException as e:

                if attempt == 4:

                    print(
                        f"Failed {date_string}: {e}"
                    )

                    return []

                wait_time = 2 ** attempt

                print(
                    f"Request failed for {date_string}. "
                    f"Retrying in {wait_time}s..."
                )

                time.sleep(wait_time)

        return []

    # Fetch historical observations concurrently
    def get_historical(self, start_date, end_date):

        all_observations = []
        completed = 0

        dates = pd.date_range(
            start=start_date,
            end=end_date,
            freq="D",
        )

        with ThreadPoolExecutor(max_workers=3) as executor:

            futures = [
                executor.submit(
                    self._get_day,
                    date,
                )
                for date in dates
            ]

            for future in as_completed(futures):

                observations = future.result()
                all_observations.extend(
                    observations
                )

                completed += 1

                print(
                    f"Completed {completed} "
                    f"out of {len(dates)} days"
                )

        df = pd.DataFrame(
            all_observations
        )

        if df.empty:
            return df

        # Convert timestamps to local time
        df["observationTimeUtc"] = pd.to_datetime(
            df["observationTimeUtc"],
            utc=True,
        )

        df["observationTimeUtc"] = (
            df["observationTimeUtc"]
            .dt.tz_convert("Europe/Vilnius")
        )

        df = df.set_index(
            "observationTimeUtc"
        )

        return df.sort_index()

    # Fetch long-term forecast
    def get_forecast(self):

        url = (
            f"{self.api_url}/places/"
            f"{self.place_code}/forecasts/long-term"
        )

        response = req.get(url)
        response.raise_for_status()

        data = response.json()

        forecast = pd.DataFrame(
            data["forecastTimestamps"]
        )

        forecast["forecastTimeUtc"] = pd.to_datetime(
            forecast["forecastTimeUtc"],
            utc=True,
        )

        forecast["forecastTimeUtc"] = (
            forecast["forecastTimeUtc"]
            .dt.tz_convert("Europe/Vilnius")
        )

        forecast = forecast.set_index(
            "forecastTimeUtc"
        )

        return forecast.sort_index()