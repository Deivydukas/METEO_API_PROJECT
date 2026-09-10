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
        response.headers.get_content_charset.return_value = "utf-8"
        mock_urlopen.return_value.__enter__.return_value = response

        client = MeteoAPIClient("https://example.com")
        result = client.fetch("/weather", params={"city": "Vilnius"})

        self.assertEqual(result, {"temperature": 22})
        called_request = mock_urlopen.call_args.args[0]
        self.assertIn("city=Vilnius", called_request.full_url)

    @patch("src.meteo_api.client.urlopen")
    def test_fetch_preserves_base_path_prefix(self, mock_urlopen):
        response = MagicMock()
        response.read.return_value = b'{"temperature": 22}'
        response.getcode.return_value = 200
        response.headers.get_content_charset.return_value = "utf-8"
        mock_urlopen.return_value.__enter__.return_value = response

        client = MeteoAPIClient("https://example.com/v1")
        client.fetch("/weather")

        called_request = mock_urlopen.call_args.args[0]
        self.assertEqual(called_request.full_url, "https://example.com/v1/weather")

    @patch("src.meteo_api.client.urlopen")
    def test_fetch_raises_on_invalid_json(self, mock_urlopen):
        response = MagicMock()
        response.read.return_value = b"not-json"
        response.getcode.return_value = 200
        response.headers.get_content_charset.return_value = "utf-8"
        mock_urlopen.return_value.__enter__.return_value = response

        client = MeteoAPIClient("https://example.com")

        with self.assertRaises(InvalidResponseError):
            client.fetch("/weather")

    @patch("src.meteo_api.client.urlopen")
    def test_fetch_raises_when_json_is_not_object(self, mock_urlopen):
        response = MagicMock()
        response.read.return_value = b"[1, 2, 3]"
        response.getcode.return_value = 200
        response.headers.get_content_charset.return_value = "utf-8"
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

    def test_fetch_raises_on_absolute_endpoint(self):
        client = MeteoAPIClient("https://example.com")

        with self.assertRaises(ApiFetchError):
            client.fetch("https://malicious.example/weather")

    def test_fetch_raises_on_path_traversal_endpoint(self):
        client = MeteoAPIClient("https://example.com/v1")

        with self.assertRaises(ApiFetchError):
            client.fetch("../admin")

    def test_fetch_raises_on_encoded_path_traversal_endpoint(self):
        client = MeteoAPIClient("https://example.com/v1")

        with self.assertRaises(ApiFetchError):
            client.fetch("%2e%2e/admin")

    def test_init_raises_on_invalid_base_url(self):
        with self.assertRaises(ValueError):
            MeteoAPIClient("example.com")

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
        response.headers.get_content_charset.return_value = "utf-8"
        mock_urlopen.return_value.__enter__.return_value = response

        client = MeteoAPIClient("https://example.com")

        with self.assertRaises(ApiFetchError):
            client.fetch("/weather")


if __name__ == "__main__":
    unittest.main()
