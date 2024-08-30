from core import transform_dict, map_field, load, process_issues
from util import get_value, field_type, now

jql = 'issuekey = HOUSE-15'

def standard_fields(issues):
    load([
        {
            'issue_id': issue['id'],
            'issue_key': issue['key'],
            'mysql_updated': now(),
            **{field['field_id']: get_value(map_field(issues, field_type, 'standard'), field['field_id'])
               for field in map_field(issues, field_type, 'standard')}
        } for issue in issues if issue
    ], 'issue')

def custom_fields(issues):
    load(map_field(issues, field_type, 'custom'), 'custom_field_value')

def histories(data):
    load([
        transform_dict({
            'history_id': history['id'],
            'issue_id': issue['id'],
            'author': history['author'],
            'created': history['created'],
            'field': item['field'],
            'fromstring': item['fromString'],
            'tostring': item['toString'],
            'mysql_updated': now()
        })
        for issue in data
        for history in issue['changelog']['histories']
        for item in history['items']
    ], 'history')

process_issues(jql, [standard_fields, custom_fields, histories])