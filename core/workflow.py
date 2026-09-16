import os
from urllib.parse import quote as encode_uri

from core import make_api_request


def fetch_issues(jql: str) -> list:
    """Return every issue matching the JQL, following Jira's startAt pagination."""
    issues, start_at, total = [], 0, None
    while total is None or start_at < total:
        url = (f"https://{os.environ['JIRA_DOMAIN']}/rest/api/3/search"
               f"?jql={encode_uri(jql)}&startAt={start_at}&expand=changelog")
        response = make_api_request(url)
        if response is None:
            raise RuntimeError(f"Jira request failed at startAt={start_at}")
        page = response.get('issues', [])
        issues.extend(page)
        start_at += len(page) or response.get('maxResults', 50)
        total = response.get('total', 0)
    return issues


def process_issues(jql: str, process_functions: list):
    """Fetch all pages first, then run each loader exactly once over the full result."""
    issues = fetch_issues(jql)
    for process_function in process_functions:
        process_function(issues)
