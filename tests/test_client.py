import unittest
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError, URLError

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
    def test_fetch_raises_when_json_is_not_object(self, mock_urlopen):
        response = MagicMock()
        response.read.return_value = b"[1, 2, 3]"
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

    @patch("src.meteo_api.client.urlopen")
    def test_fetch_raises_on_http_error(self, mock_urlopen):
        mock_urlopen.side_effect = HTTPError(
            url="https://example.com/weather",
            code=500,
            msg="Server error",
            hdrs=None,
            fp=None,
        )
        client = MeteoAPIClient("https://example.com")

        with self.assertRaises(ApiFetchError):
            client.fetch("/weather")

    @patch("src.meteo_api.client.urlopen")
    def test_fetch_raises_on_non_success_status(self, mock_urlopen):
        response = MagicMock()
        response.read.return_value = b'{"message": "error"}'
        response.getcode.return_value = 500
        mock_urlopen.return_value.__enter__.return_value = response

        client = MeteoAPIClient("https://example.com")

        with self.assertRaises(ApiFetchError):
            client.fetch("/weather")


if __name__ == "__main__":
    unittest.main()
