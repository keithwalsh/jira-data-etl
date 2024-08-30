from core import extract, transform, load
from urllib.parse import quote as encode_uri
from datetime import datetime
from util import get_value_by_field_id

def process_standard_field_value(issues):

    field_values = [{
        'field_id': key,
        'value': transform(value)
    } for issue in issues if issue and 'fields' in issue for key, value in issue['fields'].items() if not key.startswith('customfield_')]
    
    processed_data = [{
        'issue_id': issue['id'],
        'issue_key': issue['key'],
        'mysql_updated': datetime.now(),
        **{field['field_id']: get_value_by_field_id(field_values, field['field_id']) for field in field_values}
    } for issue in issues if issue]
    
    load(processed_data,'issue')


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
        for transformed_value in [transform(value)] if transformed_value is not None
    ]
    load(data, 'custom_field_value')


def fetch_and_process_all_issues(jql):

    start_at = 0
    max_results = 50
    total = None
    
    while total is None or start_at < total:
        api_url = f'rest/api/3/search?jql={jql}&startAt={start_at}&maxResults={max_results}'
        response = extract(api_url)
        
        if 'issues' in response:
            process_standard_field_value(response['issues'])
            process_custom_field_value(response['issues'])
        
        start_at += max_results
        total = response.get('total', 0)

# Encode your JQL query
jql = encode_uri('issuekey = HOUSE-15')
# Fetch and process all issues
fetch_and_process_all_issues(jql)
