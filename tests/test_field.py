from jira_data_etl.field import clean, field_type, map_field


def test_timestamps_are_reformatted():
    assert clean('2026-09-16T06:43:03.000+0000') == '2026-09-16 06:43'
    assert clean('2026-09-16T06:43:03.000-0500') == '2026-09-16 06:43'


def test_objects_reduce_to_one_string():
    assert clean({'displayName': 'Keith Walsh', 'name': 'kwalsh'}) == 'Keith Walsh'
    assert clean({'name': 'In Progress', 'id': '3'}) == 'In Progress'
    assert clean({'value': 'Option A'}) == 'Option A'
    assert clean({'watchCount': 3}) is None


def test_lists_join_with_commas_and_skip_empties():
    assert clean([{'name': 'core'}, {'name': 'streams'}, {'watchCount': 1}]) == 'core, streams'
    assert clean([]) is None


def test_sub_resource_links_become_issue_ids_on_any_host():
    assert clean('https://issues.apache.org/jira/rest/api/2/issue/13666761/comment/18000000') == '13666761'
    assert clean('https://yourco.atlassian.net/rest/api/3/issue/10001/comment/2') == '10001'
    assert clean('https://issues.apache.org/jira/rest/api/2/issue/13666761') == \
        'https://issues.apache.org/jira/rest/api/2/issue/13666761'


def test_atlassian_document_format_is_flattened():
    adf = {'type': 'doc', 'content': [
        {'type': 'paragraph', 'content': [
            {'type': 'text', 'text': 'Fix '},
            {'type': 'text', 'text': 'now', 'marks': [{'type': 'strong'}]},
        ]},
        {'type': 'bulletList', 'content': [
            {'type': 'listItem', 'content': [{'type': 'paragraph', 'content': [{'type': 'text', 'text': 'one'}]}]},
        ]},
    ]}
    assert clean(adf) == 'Fix **now**\n* one'


def test_strings_are_stripped_and_empties_become_none():
    assert clean('  KAFKA  ') == 'KAFKA'
    assert clean('   ') is None
    assert clean(None) is None
    assert clean(7) == 7


def test_field_type_splits_on_prefix():
    assert field_type('summary', 'standard') is True
    assert field_type('customfield_12310220', 'standard') is False
    assert field_type('customfield_12310220', 'custom') is True


def test_map_field_gives_long_rows_for_populated_custom_fields_only():
    issues = [{'id': '1', 'fields': {'summary': 'x', 'customfield_1': {'value': 'A'}, 'customfield_2': None}}]
    rows = map_field(issues, field_type, 'custom')
    assert [(r['issue_id'], r['field_id'], r['value']) for r in rows] == [('1', 'customfield_1', 'A')]
