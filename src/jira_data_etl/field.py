import re

from jira_data_etl.text import extract_text_from_content
from jira_data_etl.time import format_jira_datetime, now

JIRA_DATETIME = re.compile(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}[+-]\d{4}')
ISSUE_SUBRESOURCE = re.compile(r'https?://.+/rest/api/\d+/issue/(\d+)/\w+/\d+')


def field_type(key, mode='standard'):
    fields = {'standard': not key.startswith('customfield_'), 'custom': key.startswith('customfield_')}
    return fields.get(mode)


def get(data, field_id):
    if isinstance(data, dict):
        return data.get(field_id)
    if isinstance(data, list) and all(isinstance(item, dict) for item in data):
        return next((item['value'] for item in data if item['field_id'] == field_id), None)
    raise ValueError('data must be either a dictionary or a list of dictionaries')


def clean(value):
    """Reduce any Jira field value to one string (or None), whatever shape the API returned."""
    if value is None:
        return None
    if isinstance(value, list):
        return ', '.join(filter(None, (clean(item) for item in value))) or None
    if isinstance(value, dict):
        return extract_text_from_content(value) if 'content' in value else \
            next((clean(value[key]) for key in ('displayName', 'jira', 'key', 'name', 'value', 'votes') if key in value), None)
    if isinstance(value, str):
        if JIRA_DATETIME.fullmatch(value):
            return format_jira_datetime(value)
        match = ISSUE_SUBRESOURCE.fullmatch(value)
        if match:
            return match.group(1)
        return value.strip() or None
    return value


def map_field(issues, is_field_type, mode):
    return [
        {
            'issue_id': issue['id'],
            'field_id': key,
            'value': clean(value),
            'mysql_updated': now(),
        }
        for issue in issues if issue and 'fields' in issue
        for key, value in issue['fields'].items() if is_field_type(key, mode) and value is not None
    ]
