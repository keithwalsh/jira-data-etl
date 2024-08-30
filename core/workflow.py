from core import extract
from urllib.parse import quote as encode_uri

def process_issues(jql, processing_functions):
    start_at = 0
    max_results = 50
    total = None
    
    while total is None or start_at < total:
        api_url = f'https://keithwalsh.atlassian.net/rest/api/3/search?jql={encode_uri(jql)}&startAt={start_at}&maxResults={max_results}&expand=changelog'
        response = extract(api_url)
        data = response['issues']
        
        # Call each processing function on the data
        for process_function in processing_functions:
            process_function(data)
        
        start_at += max_results
        total = response.get('total', 0)