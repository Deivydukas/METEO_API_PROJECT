import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen


class ApiFetchError(Exception):
    pass


class InvalidResponseError(ApiFetchError):
    pass


class MeteoAPIClient:
    def __init__(self, base_url: str, timeout: int = 10):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def fetch(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        if endpoint.startswith(("http://", "https://", "//")):
            raise ApiFetchError("Endpoint must be a relative path")
        endpoint = endpoint.lstrip("/")

        query = urlencode(params or {})
        base_url = f"{self.base_url}/"
        url = urljoin(base_url, endpoint)
        if query:
            url = f"{url}?{query}"

        request = Request(url, method="GET")
        try:
            with urlopen(request, timeout=self.timeout) as response:
                charset = response.headers.get_content_charset() or "utf-8"
                payload = response.read().decode(charset)
                status_code = response.getcode() or 200
        except (HTTPError, URLError, TimeoutError) as exc:
            raise ApiFetchError(f"API request failed: {exc}") from exc
        except (LookupError, UnicodeDecodeError) as exc:
            raise InvalidResponseError("API response could not be decoded") from exc

        if status_code >= 400:
            raise ApiFetchError(f"API returned status code {status_code}")

        try:
            data = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise InvalidResponseError("API response is not valid JSON") from exc

        if not isinstance(data, dict):
            raise InvalidResponseError("API response JSON must be an object")

        return data
