import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, unquote, urlencode, urljoin, urlparse, urlsplit
from urllib.request import Request, urlopen


class ApiFetchError(Exception):
    pass


class InvalidResponseError(ApiFetchError):
    pass


class MeteoAPIClient:
    def __init__(self, base_url: str, timeout: int = 10):
        parsed = urlparse(base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("base_url must be an absolute HTTP(S) URL")
        if timeout <= 0:
            raise ValueError("timeout must be greater than 0")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def fetch(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        if endpoint.startswith(("http://", "https://", "//")):
            raise ApiFetchError("Endpoint must be a relative path")
        split_endpoint = urlsplit(endpoint)
        path_segments = unquote(split_endpoint.path).split("/")
        if ".." in path_segments:
            raise ApiFetchError("Endpoint must not contain path traversal segments")
        endpoint_path = split_endpoint.path.lstrip("/")
        merged_query: dict[str, list[Any]] = parse_qs(split_endpoint.query, keep_blank_values=True)
        for key, value in (params or {}).items():
            merged_query.setdefault(key, [])
            if isinstance(value, (list, tuple)):
                merged_query[key].extend(value)
            else:
                merged_query[key].append(value)
        query = urlencode(merged_query, doseq=True)
        base_url = f"{self.base_url}/"
        url = urljoin(base_url, endpoint_path)
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
