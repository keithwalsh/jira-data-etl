import requests


def make_api_request(url: str, headers: dict | None = None, timeout: int = 60) -> dict:
    """GET one JSON document. Raises with the URL in the message on any HTTP or network failure."""
    try:
        response = requests.get(url, headers=headers or {}, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise RuntimeError(f'request failed: {url}: {e}') from e
