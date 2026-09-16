from datetime import datetime

def format_jira_datetime(date_str: str, input_format: str = "%Y-%m-%dT%H:%M:%S.%f%z", output_format: str = "%Y-%m-%d %H:%M") -> str:
    return datetime.strptime(date_str, input_format).strftime(output_format) if date_str else None

now = lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S')

convert_millis_to_minutes = lambda milliseconds: round(milliseconds / 60000)
