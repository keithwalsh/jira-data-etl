from urllib.parse import quote as encode_uri

from jira_data_etl.extract import make_api_request


def fetch_issues(base_url: str, api_version: str, jql: str, headers: dict | None = None,
                 max_results: int = 100) -> list:
    """Return every issue matching the JQL, with changelogs, following Jira's startAt pagination."""
    issues, start_at, total = [], 0, None
    while total is None or start_at < total:
        url = (f"{base_url.rstrip('/')}/rest/api/{api_version}/search"
               f"?jql={encode_uri(jql)}&startAt={start_at}&maxResults={max_results}&expand=changelog")
        response = make_api_request(url, headers)
        page = response.get('issues', [])
        issues.extend(page)
        start_at += len(page) or response.get('maxResults', max_results)
        total = response.get('total', 0)
    return issues
