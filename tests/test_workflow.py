from jira_data_etl import workflow


def test_fetch_issues_follows_start_at_until_total(monkeypatch):
    calls = []

    def fake(url, headers=None):
        calls.append(url)
        start = int(url.split('startAt=')[1].split('&')[0])
        page = [{'id': str(i)} for i in range(start, min(start + 50, 120))]
        return {'issues': page, 'maxResults': 50, 'total': 120}

    monkeypatch.setattr(workflow, 'make_api_request', fake)
    issues = workflow.fetch_issues('https://example.atlassian.net/', '3', 'project = X', {}, max_results=50)

    assert len(issues) == 120
    assert [c.split('startAt=')[1].split('&')[0] for c in calls] == ['0', '50', '100']
    assert calls[0].startswith('https://example.atlassian.net/rest/api/3/search?jql=project%20%3D%20X')
    assert 'expand=changelog' in calls[0]


def test_fetch_issues_uses_the_api_version_and_stops_on_empty_result(monkeypatch):
    calls = []

    def fake(url, headers=None):
        calls.append(url)
        return {'issues': [], 'maxResults': 50, 'total': 0}

    monkeypatch.setattr(workflow, 'make_api_request', fake)
    assert workflow.fetch_issues('https://issues.apache.org/jira', '2', 'key = X-1') == []
    assert len(calls) == 1 and '/rest/api/2/search' in calls[0]
