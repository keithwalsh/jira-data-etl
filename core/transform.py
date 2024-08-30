import re
from util import format_jira_datetime, convert_millis_to_minutes, extract_text_from_content

def transform(value):
    if isinstance(value, dict):
        if 'displayName' in value:
            return value['displayName']
        elif 'requestType' in value and 'name' in value['requestType']:
            return value['requestType']['name']
        elif 'value' in value:
            return value['value']
        elif 'name' in value:
            return value['name']
        elif isinstance(value, dict) and 'content' in value:
            return extract_text_from_content(value)
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
        elif 'hasEpicLinkFieldDependency' in value:
            return None
        elif isinstance(value, dict) and 'votes' in value:
            return value['votes']
        elif isinstance(value, dict) and 'watchCount' in value:
            return value['watchCount']
    elif isinstance(value, list):
        if not value:
            return None
        result = ','.join(v['name'] for v in value if isinstance(v, dict) and 'name' in v)
        return result if result else None
    elif isinstance(value, str):
        if re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}\+\d{4}', value):
            return format_jira_datetime(value)
        return value if value.strip() else None
    return str(value) if str(value).strip() else None
