# METEO_API_PROJECT

Basic API fetching structure for weather-style endpoints.

## Example

```python
from src.meteo_api import MeteoAPIClient

client = MeteoAPIClient("https://api.example.com")
data = client.fetch("/weather", params={"city": "Vilnius"})
```