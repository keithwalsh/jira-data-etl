import re
from util import format_jira_datetime, extract_text_from_content, now

def field_type(key, mode='standard'):
    fields = { 'standard': not key.startswith('customfield_'), 'custom': key.startswith('customfield_') }
    return fields.get(mode)

def get(data, field_id):
    if isinstance(data, dict):
        return data.get(field_id)
    if isinstance(data, list) and all(isinstance(item, dict) for item in data):
        return next((item['value'] for item in data if item['field_id'] == field_id), None)
    raise ValueError("data must be either a dictionary or a list of dictionaries")

def clean(value):
    if value is None:
        return None
    if isinstance(value, list):
        return ", ".join(filter(None, (clean(item) for item in value))) or None
    elif isinstance(value, dict):
        return extract_text_from_content(value['content']) if 'content' in value else \
               next((clean(value[key]) for key in ("displayName", "jira", "key", "name", "value", "votes") if key in value), None)
    elif isinstance(value, str):
        if re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}\+\d{4}', value):
            return format_jira_datetime(value)
        if re.fullmatch(r'https://\w*.atlassian.net/rest/api/\d*/issue/\d*/\w*/\d*', value):
            issue_id = re.search(r'issue/(\d+)',value).group(1)
            return issue_id
        return value.strip() or None
    return value

def map_field(issues, is_field_type, mode):
    return [
        {
            'issue_id': issue['id'],
            'field_id': key,
            'value': clean(value),
            'mysql_updated': now()
        }
        for issue in issues if issue and 'fields' in issue
        for key, value in issue['fields'].items() if is_field_type(key, mode) and value is not None
    ]