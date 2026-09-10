import unittest
from unittest.mock import MagicMock, patch
from urllib.error import URLError

from src.meteo_api.client import ApiFetchError, InvalidResponseError, MeteoAPIClient


class TestMeteoAPIClient(unittest.TestCase):
    @patch("src.meteo_api.client.urlopen")
    def test_fetch_returns_json_payload(self, mock_urlopen):
        response = MagicMock()
        response.read.return_value = b'{"temperature": 22}'
        response.getcode.return_value = 200
        mock_urlopen.return_value.__enter__.return_value = response

        client = MeteoAPIClient("https://example.com")
        result = client.fetch("/weather", params={"city": "Vilnius"})

        self.assertEqual(result, {"temperature": 22})

    @patch("src.meteo_api.client.urlopen")
    def test_fetch_raises_on_invalid_json(self, mock_urlopen):
        response = MagicMock()
        response.read.return_value = b"not-json"
        response.getcode.return_value = 200
        mock_urlopen.return_value.__enter__.return_value = response

        client = MeteoAPIClient("https://example.com")

        with self.assertRaises(InvalidResponseError):
            client.fetch("/weather")

    @patch("src.meteo_api.client.urlopen")
    def test_fetch_raises_on_network_error(self, mock_urlopen):
        mock_urlopen.side_effect = URLError("network unavailable")
        client = MeteoAPIClient("https://example.com")

        with self.assertRaises(ApiFetchError):
            client.fetch("/weather")


if __name__ == "__main__":
    unittest.main()
