import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
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
        endpoint = endpoint.lstrip("/")
        query = urlencode(params or {})
        url = f"{self.base_url}/{endpoint}"
        if query:
            url = f"{url}?{query}"

        request = Request(url, method="GET")
        try:
            with urlopen(request, timeout=self.timeout) as response:
                payload = response.read().decode("utf-8")
                status_code = response.getcode() or 200
        except (HTTPError, URLError, TimeoutError) as exc:
            raise ApiFetchError(f"API request failed: {exc}") from exc

        if status_code >= 400:
            raise ApiFetchError(f"API returned status code {status_code}")

        try:
            return json.loads(payload)
        except json.JSONDecodeError as exc:
            raise InvalidResponseError("API response is not valid JSON") from exc
