from dotenv import load_dotenv
from core import load, process_issues, make_api_request
from util import get, field_type, now, clean, map_field

load_dotenv()

jql = 'issuekey IN (EDU-1, HOUSE-15)'

def standard_fields(issues):
    load([
       {
            'issue_id': issue['id'],
            'issue_key': issue['key'],
            **{field['field_id']: get(map_field(issues, field_type, 'standard'), field['field_id'])
               for field in map_field(issues, field_type, 'standard')},
            'mysql_updated': now()
        } for issue in issues if issue
    ], 'issue')

def custom_fields(issues):
    load(map_field(issues, field_type, 'custom'), 'custom_field_value')

def histories(data):
    load([
        {
            'history_id': history['id'],
            'issue_id': issue['id'],
            'author': clean(history['author']),
            'created': clean(history['created']),
            'field': item['field'],
            'fromstring': clean(item['fromString']),
            'tostring': clean(item['toString']),
            'mysql_updated': now()
        }
        for issue in data
        for history in issue['changelog']['histories']
        for item in history['items']
    ], 'history')

def comments(issues):
    all_comments = []
    for issue in issues:
        start_at, total = 0, None
        while total is None or start_at < total:
            response = make_api_request(f'{issue['self']}/comment')
            for item in get(response,'comments'):
                if isinstance(item, dict):
                    comment = {
                        'comment_id': get(item,'id'),
                        'issue_id': clean(get(item,'self')),
                        'author': clean(get(item,'author')),
                        'body': clean(get(item,'body')),
                        'updateauthor': clean(get(item,'updateAuthor')),
                        'created': clean(get(item,'created')),
                        'updated': clean(get(item,'updated')),
                        'jsdpublic': get(item,'jsdPublic'),
                        'mysql_updated': now()
                    }
                    all_comments.append(comment)  # Add the comment to the list
            start_at += response.get('maxResults', 0)
            total = response.get('total', 0)
    load(all_comments,'comment')


process_issues(jql, [standard_fields, custom_fields, histories, comments])