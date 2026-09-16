"""Command line entry point: one JQL query in, four tables out."""

import argparse
import os
import sys

from dotenv import load_dotenv

from jira_data_etl import __version__
from jira_data_etl.auth import get_auth_header
from jira_data_etl.load import make_loader
from jira_data_etl.transform import comments, custom_fields, histories, standard_fields
from jira_data_etl.workflow import fetch_issues


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='jira-data-etl',
        description='Load Jira issues, custom fields, changelogs and comments into DuckDB or MySQL.',
    )
    parser.add_argument('--jql', required=True, help='JQL query selecting the issues to load')
    parser.add_argument('--base-url', default=None,
                        help='Jira base URL, e.g. https://issues.apache.org/jira or https://yourco.atlassian.net. '
                             'Defaults to https://$JIRA_DOMAIN')
    parser.add_argument('--api-version', default='3', choices=['2', '3'],
                        help='REST API version: 3 for Jira Cloud, 2 for Jira Data Center (default: 3)')
    parser.add_argument('--to', default='duckdb', choices=['duckdb', 'mysql'], help='target database (default: duckdb)')
    parser.add_argument('--db', default='jira.duckdb', help='DuckDB file path (default: jira.duckdb)')
    parser.add_argument('--max-results', type=int, default=100, help='page size to request (default: 100)')
    parser.add_argument('--skip-comments', action='store_true', help='do not fetch comments (one request per issue)')
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    return parser


def main(argv=None) -> int:
    load_dotenv()
    args = build_parser().parse_args(argv)

    base_url = args.base_url or (f"https://{os.environ['JIRA_DOMAIN']}" if os.getenv('JIRA_DOMAIN') else None)
    if not base_url:
        print('error: pass --base-url or set JIRA_DOMAIN', file=sys.stderr)
        return 2

    headers = {}
    auth = get_auth_header(os.getenv('JIRA_EMAIL'), os.getenv('JIRA_API_TOKEN'))
    if auth:
        headers['Authorization'] = auth
    else:
        print('No JIRA_API_TOKEN set: requesting anonymously.')

    try:
        issues = fetch_issues(base_url, args.api_version, args.jql, headers, args.max_results)
        print(f'Fetched {len(issues)} issues.')
        loader = make_loader(args.to, args.db)
        loader.load(standard_fields(issues), 'issue')
        loader.load(custom_fields(issues), 'custom_field_value')
        loader.load(histories(issues), 'history')
        if not args.skip_comments:
            loader.load(comments(issues, headers, args.max_results), 'comment')
        loader.close()
    except Exception as e:  # surface one line, not a traceback, for the common failures
        print(f'error: {e}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
