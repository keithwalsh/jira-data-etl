import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / 'fixtures'


@pytest.fixture(scope='session')
def search_page() -> dict:
    """One Jira Data Center (v2) search page with changelogs, recorded from issues.apache.org."""
    return json.loads((FIXTURES / 'search_v2_page.json').read_text(encoding='utf-8'))


@pytest.fixture(scope='session')
def comments_page() -> dict:
    """One comment page for the first issue in search_page."""
    return json.loads((FIXTURES / 'comments_v2_page.json').read_text(encoding='utf-8'))
