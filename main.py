import re
from core import extract, load
from util import format_jira_datetime, convert_millis_to_minutes
from urllib.parse import quote as encode_uri
from datetime import datetime

def process_value(value):
    if isinstance(value, dict):
        # Handling specific nested dictionary keys with special logic
        if 'displayName' in value:
            return value['displayName']
        elif 'requestType' in value and 'name' in value['requestType']:
            return value['requestType']['name']
        elif 'value' in value:
            return value['value']
        elif 'name' in value:
            return value['name']
        elif 'completedCycles' in value and value['completedCycles']:
            return str([{
                key: format_jira_datetime(cycle[key]['jira']) if key in ['startTime', 'stopTime', 'breachTime']
                else convert_millis_to_minutes(cycle[key]['millis']) if key in ['goalDurationMins', 'elapsedTimeMins', 'remainingTimeMins']
                else cycle[key] for key in cycle
            } for cycle in value['completedCycles']])
        elif 'ongoingCycle' in value:
            cycle = value['ongoingCycle']
            return str({
                key: format_jira_datetime(cycle[key]['jira']) if key in ['startTime', 'breachTime']
                else convert_millis_to_minutes(cycle[key]['millis']) if key in ['goalDurationMins', 'elapsedTimeMins', 'remainingTimeMins']
                else cycle[key] for key in cycle
            })
    elif isinstance(value, list):
        return ','.join(v['name'] for v in value if isinstance(v, dict) and 'name' in v)
    elif isinstance(value, str):
        if re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}\+\d{4}', value):
            return format_jira_datetime(value)
        return value if value.strip() else None
    return str(value)

def process_data(issues):
    data = [
        {
            'issue_id': issue['id'], 
            'field_id': key, 
            'value': process_value(value),
            'mysql_updated': datetime.now()
        }
        for issue in issues for key, value in issue['fields'].items() if key.startswith('customfield_') and value is not None
    ]
    load(data, 'custom_field_value')

jql = encode_uri('issuekey = JIR-12345')
response = extract(f'rest/api/2/search?jql={jql}&startAt=0')
process_data(response['issues'])
