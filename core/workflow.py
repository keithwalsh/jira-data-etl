from core import make_api_request
from urllib.parse import quote as encode_uri


def process_issues(jql: str, process_functions: list):
    start_at, total = 0, None
    while total is None or start_at < total:
        api_url = f'https://keithwalsh.atlassian.net/rest/api/3/search?jql={encode_uri(jql)}&startAt=0&expand=changelog'
        response = make_api_request(api_url)
        for process_function in process_functions:
            process_function(response['issues'])    
        start_at += response.get('maxResults', 0)
        total = response.get('total', 0)