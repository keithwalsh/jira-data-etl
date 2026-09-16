# jira-data-etl

[![CI](https://github.com/keithwalsh/jira-data-etl/actions/workflows/ci.yml/badge.svg)](https://github.com/keithwalsh/jira-data-etl/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/jira-data-etl)](https://pypi.org/project/jira-data-etl/)

A lightweight Python loader from the Jira REST API into a SQL database. One JQL query in; four
tables out: issues with their standard fields, custom fields in long format, the full changelog,
and comments, with Jira's nested JSON flattened into plain columns. Works against Jira Cloud
(REST API v3) and Jira Data Center (v2), writes to DuckDB with no setup or to MySQL.

**Status, 16 September 2026: runs end to end against Apache's public Jira.** A working
prototype from September 2024, reshaped into a tool other people can run. What it does is
described below exactly as the code does it. The roadmap at the end is the order the rest lands.

## Try it in one minute

Apache's Jira allows anonymous reads, so this needs no account:

```bash
pip install jira-data-etl
jira-data-etl --base-url https://issues.apache.org/jira --api-version 2 \
  --jql "project = KAFKA AND created >= -5d" --to duckdb --db kafka.duckdb
```

Checked on 16 September 2026: 35 issues fetched, and Jira's own count for that JQL was 35.
Then, in Python or the DuckDB CLI:

```sql
SELECT issue_key, status, assignee, created FROM issue ORDER BY created DESC;
SELECT fromstring, tostring, created FROM history WHERE field = 'status';
```

## What it does

`fetch_issues()` runs one JQL query with `expand=changelog`, following `startAt` until every
page is in. Four transforms then produce the rows, and a loader writes each table once:

| Table | Grain | Columns |
| --- | --- | --- |
| `issue` | One row per issue | `issue_id`, `issue_key`, one column per standard field returned by the API, `mysql_updated` |
| `custom_field_value` | One row per issue per populated custom field | `issue_id`, `field_id`, `value`, `mysql_updated` |
| `history` | One row per changelog item (one status change, one assignee change, and so on) | `history_id`, `issue_id`, `author`, `created`, `field`, `fromstring`, `tostring`, `mysql_updated` |
| `comment` | One row per comment | `comment_id`, `issue_id`, `author`, `body`, `updateauthor`, `created`, `updated`, `jsdpublic`, `mysql_updated` |

Every value passes through one `clean()` function before it is stored:

- Rich text in Atlassian Document Format (Cloud descriptions and comment bodies) is flattened to
  text: paragraphs and headings kept, bold marked `**like this**`, links as `[text](url)`,
  bullet lists as `* item`. Data Center returns wiki markup as plain strings, stored as is.
- Objects such as users, statuses, priorities and select-list options are reduced to one
  string, the first of `displayName`, `key`, `name`, `value` that is present.
- Lists (labels, components, multi-selects) are joined with commas.
- Jira timestamps become `YYYY-MM-DD HH:MM`. Issue sub-resource links become the issue id.
- Empty strings become `NULL`.

Custom fields go into a long table on purpose: adding a field in Jira then adds rows, not
columns, and the schema never changes underneath a downstream model. The changelog is stored
row for row because it is the only source of truth for how long an issue spent in each status;
the issue's current status is a snapshot.

Each run is a full refresh: every table is emptied and reloaded with the current result. There
is no incremental mode.

## Running it

Requires Python 3.12 or later.

```bash
pip install jira-data-etl            # DuckDB target
pip install "jira-data-etl[mysql]"   # adds the MySQL driver
jira-data-etl --help
```

From a clone, `pip install -e ".[test]"` and `pytest`. Releases are built and published to PyPI
by GitHub Actions when a `v*` tag is pushed.

| Option | Meaning |
| --- | --- |
| `--jql` | The query. Required. |
| `--base-url` | `https://yourco.atlassian.net` or `https://issues.apache.org/jira`. Defaults to `https://$JIRA_DOMAIN`. |
| `--api-version` | `3` for Jira Cloud (default), `2` for Jira Data Center. |
| `--to` | `duckdb` (default) or `mysql`. |
| `--db` | DuckDB file, default `jira.duckdb`. Tables are created on first sight, every column `VARCHAR`; type them downstream. |
| `--max-results` | Page size, default 100. |
| `--skip-comments` | Skip comments, which cost one request per issue. |

Credentials come from the environment or a `.env` file (see `.env.example`): `JIRA_EMAIL` and
`JIRA_API_TOKEN` for Jira Cloud, `MYSQL_*` for the MySQL target. With no token set, requests go
out anonymously, which is what a public instance wants.

## Layout

```
src/jira_data_etl/
  cli.py         arguments, wiring, exit codes
  workflow.py    fetch_issues(): paginated search with changelogs
  extract.py     one GET, raises with the URL on failure
  transform.py   the four row builders, including paginated comments
  load.py        DuckDBLoader (creates tables), MySQLLoader (tables must exist)
  auth.py        Basic auth header, or None for anonymous
  field.py       standard/custom split, clean()
  text.py        Atlassian Document Format to text
  time.py        timestamp formatting
```

## Known issues

Verified against the code on 16 September 2026.

1. **MySQL tables are not created.** The DuckDB target creates its own; the MySQL target
   truncates and inserts into tables you create by hand, and the `issue` table's columns depend
   on which standard fields your instance returns.
2. **A failed request stops the run.** Nothing is retried, and because each table is emptied
   before insert, a run that fails part-way leaves the tables already loaded refreshed and the
   rest untouched.
3. **Tests cover the transforms, pagination and the DuckDB loader, not the MySQL loader.** The
   fixtures under `tests/fixtures/` are two real KAFKA issues and one comment page recorded from
   Apache's Jira on 16 September 2026, so `pytest` needs no network. Run with
   `pip install -e ".[test]" && pytest`.

Fixed 16 September 2026: issue and comment pagination never advanced past the first page, each
page truncated its table so only the last page survived, the search URL was hardcoded to one
Atlassian site, and the `issue` table gave every row the first issue's field values.

## Roadmap

In this order.

- [x] Pagination and `JIRA_DOMAIN`; load each table once per run
- [x] Command line entry point; DuckDB target with tables created on first run
- [x] Jira Data Center (REST API v2) and anonymous access, checked against Apache's Jira
- [x] Tests against recorded API responses; GitHub Actions on every push (Python 3.12 and 3.13)
- [x] Publish to PyPI (0.2.0, 16 September 2026)
- [ ] Create MySQL tables when missing
- [ ] Retry transient HTTP failures; incremental mode (`updated >= last run`)

## Related

- [jira-dbt](https://github.com/keithwalsh/jira-dbt): a dbt project over the tables this loads,
  with cycle time, time-in-status, throughput and reopen rate as tested marts.
- [dbt-catalog-mcp](https://github.com/keithwalsh/dbt-catalog-mcp): an MCP server that lets an
  LLM find the right model or column in that project.

## Licence

MIT
