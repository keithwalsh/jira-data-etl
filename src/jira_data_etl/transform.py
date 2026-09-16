"""Turn the API's issue JSON into flat rows for the four target tables."""

from jira_data_etl.extract import make_api_request
from jira_data_etl.field import clean, field_type, get, map_field
from jira_data_etl.time import now


def standard_fields(issues: list) -> list:
    """One row per issue: id, key, every standard field the API returned, cleaned."""
    return [
        {
            'issue_id': issue['id'],
            'issue_key': issue['key'],
            **{key: clean(value) for key, value in issue['fields'].items() if field_type(key, 'standard')},
            'mysql_updated': now(),
        }
        for issue in issues if issue and 'fields' in issue
    ]


def custom_fields(issues: list) -> list:
    """One row per issue per populated custom field, in long format."""
    return map_field(issues, field_type, 'custom')


def histories(issues: list) -> list:
    """One row per changelog item. Needs the search to have been run with expand=changelog."""
    return [
        {
            'history_id': history['id'],
            'issue_id': issue['id'],
            'author': clean(history.get('author')),
            'created': clean(history.get('created')),
            'field': item.get('field'),
            'fromstring': clean(item.get('fromString')),
            'tostring': clean(item.get('toString')),
            'mysql_updated': now(),
        }
        for issue in issues if issue
        for history in issue.get('changelog', {}).get('histories', [])
        for item in history.get('items', [])
    ]


def comments(issues: list, headers: dict, max_results: int = 100) -> list:
    """One row per comment, fetched per issue and paginated."""
    rows = []
    for issue in issues:
        start_at, total = 0, None
        while total is None or start_at < total:
            response = make_api_request(f"{issue['self']}/comment?startAt={start_at}&maxResults={max_results}", headers)
            page = [item for item in get(response, 'comments') or [] if isinstance(item, dict)]
            rows.extend(
                {
                    'comment_id': get(item, 'id'),
                    'issue_id': issue['id'],
                    'author': clean(get(item, 'author')),
                    'body': clean(get(item, 'body')),
                    'updateauthor': clean(get(item, 'updateAuthor')),
                    'created': clean(get(item, 'created')),
                    'updated': clean(get(item, 'updated')),
                    'jsdpublic': get(item, 'jsdPublic'),
                    'mysql_updated': now(),
                }
                for item in page
            )
            start_at += len(page) or response.get('maxResults', max_results)
            total = response.get('total', 0)
    return rows
