import re

from jira_data_etl import transform

TIMESTAMP = re.compile(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}$')


def test_one_issue_row_per_issue_with_its_own_values(search_page):
    issues = search_page['issues']
    rows = transform.standard_fields(issues)
    assert [r['issue_key'] for r in rows] == [i['key'] for i in issues]
    assert [r['summary'] for r in rows] == [i['fields']['summary'] for i in issues]
    assert all(TIMESTAMP.match(r['created']) for r in rows)
    assert all(not k.startswith('customfield_') for r in rows for k in r)


def test_custom_field_rows_are_long_and_non_null(search_page):
    rows = transform.custom_fields(search_page['issues'])
    expected = sum(1 for i in search_page['issues'] for k, v in i['fields'].items()
                   if k.startswith('customfield_') and v is not None)
    assert len(rows) == expected
    assert all(r['value'] is not None for r in rows)


def test_one_history_row_per_changelog_item(search_page):
    issues = search_page['issues']
    rows = transform.histories(issues)
    expected = sum(len(h['items']) for i in issues for h in i['changelog']['histories'])
    assert len(rows) == expected
    status_rows = [r for r in rows if r['field'] == 'status']
    assert status_rows, 'fixture should contain at least one status change'
    assert all(r['fromstring'] != r['tostring'] for r in status_rows)


def test_comments_paginate_per_issue(search_page, comments_page, monkeypatch):
    first = search_page['issues'][0]
    calls = []

    def fake(url, headers=None):
        calls.append(url)
        return comments_page if url.startswith(first['self']) else {'comments': [], 'total': 0, 'maxResults': 100}

    monkeypatch.setattr(transform, 'make_api_request', fake)
    rows = transform.comments(search_page['issues'], headers={}, max_results=100)
    assert len(rows) == comments_page['total']
    assert {r['issue_id'] for r in rows} == {first['id']}
    assert all(TIMESTAMP.match(r['created']) for r in rows)
    assert len(calls) == len(search_page['issues'])
    assert calls[0] == f"{first['self']}/comment?startAt=0&maxResults=100"
