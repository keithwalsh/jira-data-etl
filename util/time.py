from datetime import datetime

def format_jira_datetime(date_str):
    if date_str is not None:
        input_format = "%Y-%m-%dT%H:%M:%S.%f%z"
        output_format = "%Y-%m-%d %H:%M"
        date_datetime = datetime.strptime(date_str, input_format)
        formatted_date_str = date_datetime.strftime(output_format)   
        return formatted_date_str
    else:
        return date_str

def now():
    return datetime.now()

def convert_millis_to_minutes(milliseconds):
    # Convert milliseconds to minutes and round to the nearest minute
    return round(milliseconds / 60000)