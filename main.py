import re
from core import extract, transform_custom_field_value, load
from util import format_jira_datetime, convert_millis_to_minutes
from urllib.parse import quote as encode_uri
from datetime import datetime

def process_custom_field_value(issues):
    data = [
        {
            'issue_id': issue['id'],
            'field_id': key,
            'value': transformed_value,
            'mysql_updated': datetime.now()
        }
        for issue in issues if issue and 'fields' in issue
        for key, value in issue['fields'].items() if key.startswith('customfield_') and value is not None
        for transformed_value in [transform_custom_field_value(value)] if transformed_value is not None
    ]
    load(data, 'custom_field_value')

def fetch_and_process_all_issues(jql):
    start_at = 0
    max_results = 50
    total = None
    
    while total is None or start_at < total:
        api_url = f'rest/api/2/search?jql={jql}&startAt={start_at}&maxResults={max_results}'
        response = extract(api_url)

        if 'issues' in response:
            process_custom_field_value(response['issues'])

        start_at += max_results
        total = response.get('total', 0)

# Encode your JQL query
jql = encode_uri('created > 2024-08-29')
# Fetch and process all issues
fetch_and_process_all_issues(jql)
