# jira-data-etl

A lightweight Python loader from the Jira Cloud REST API into a SQL database. One JQL query in;
four tables out: issues with their standard fields, custom fields in long format, the full
changelog, and comments, with Jira's nested JSON flattened into plain columns.

**Status, 16 September 2026: a working prototype from September 2024, being reshaped into a
tool other people can run.** What it does today is described below exactly as the code does it,
including the defects. The roadmap at the end is the order they get fixed.

## What it does

`main.py` runs one JQL query with `expand=changelog` and hands each page of issues to four
loaders:

| Table | Grain | Columns |
| --- | --- | --- |
| `issue` | One row per issue | `issue_id`, `issue_key`, one column per standard field returned by the API, `mysql_updated` |
| `custom_field_value` | One row per issue per populated custom field | `issue_id`, `field_id`, `value`, `mysql_updated` |
| `history` | One row per changelog item (one status change, one assignee change, and so on) | `history_id`, `issue_id`, `author`, `created`, `field`, `fromstring`, `tostring`, `mysql_updated` |
| `comment` | One row per comment | `comment_id`, `issue_id`, `author`, `body`, `updateauthor`, `created`, `updated`, `jsdpublic`, `mysql_updated` |

Every value passes through one `clean()` function before it is stored:

- Rich text in Atlassian Document Format (descriptions, comment bodies) is flattened to text:
  paragraphs and headings kept, bold marked `**like this**`, links as `[text](url)`, bullet
  lists as `* item`.
- Objects such as users, statuses, priorities and select-list options are reduced to one
  string, the first of `displayName`, `key`, `name`, `value` that is present.
- Lists (labels, components, multi-selects) are joined with commas.
- Jira timestamps become `YYYY-MM-DD HH:MM`. Issue self-links become the issue id.
- Empty strings become `NULL`.

Custom fields go into a long table on purpose: adding a field in Jira then adds rows, not
columns, and the schema never changes underneath a downstream model. The changelog is stored
row for row because it is the only source of truth for how long an issue spent in each status;
the issue's current status is a snapshot.

Each run is a full refresh: every loader truncates its table and inserts the current result.
There is no incremental mode.

## Running it

Requires Python 3.12 or later and a MySQL database in which the four tables above already
exist. No DDL ships with the repo yet; the `issue` table's columns depend on which standard
fields your instance returns.

```bash
pip install -r requirements.txt
cp .env.example .env      # then fill it in
python main.py
```

The JQL lives in `main.py` (`jql = ...`). Change it there.

| Variable | Meaning |
| --- | --- |
| `JIRA_EMAIL` | Atlassian account email. With `JIRA_API_TOKEN` it forms the Basic auth header. |
| `JIRA_API_TOKEN` | API token from id.atlassian.com. Sent on its own if no email is set. |
| `JIRA_DOMAIN` | Your site, `yourcompany.atlassian.net`. **Read by nothing yet; see Known issues.** |
| `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE` | Target database. |

## Layout

```
main.py            the JQL and the four loaders
core/extract.py    one authenticated GET
core/workflow.py   pages through the search results and calls the loaders
core/load.py       truncate and bulk insert
util/auth.py       Basic auth header
util/field.py      standard/custom split, clean()
util/text.py       Atlassian Document Format to text
util/time.py       timestamp formatting
```

## Known issues

Verified against the code on 16 September 2026.

1. **Pagination does not advance.** `core/workflow.py` counts `startAt` up but always requests
   `startAt=0`, so a query larger than one page re-reads the first page until the counter passes
   `total`. Comments have the same shape: `startAt` is never sent.
2. **Each page truncates the table.** Combined with the above, a multi-page run keeps only the
   rows from the last page processed. The tool is correct only for queries that fit in one page.
3. **The site is hardcoded.** The search URL names one Atlassian site (which no longer answers)
   and ignores `JIRA_DOMAIN`.
4. **No schema shipped.** The four tables must be created by hand.
5. **A failed request ends the run with a traceback.** `make_api_request` prints the error and
   returns `None`; the caller then indexes it.
6. Jira Cloud only (REST API v3, Atlassian Document Format bodies). MySQL only. No tests.

## Roadmap

In this order.

- [ ] Pagination and `JIRA_DOMAIN`: fix items 1 to 3 above, and load each table once per run
- [ ] A command line: `jira-data-etl --base-url ... --jql ... --to mysql|duckdb`
- [ ] DuckDB target, with tables created on first run, so a clone runs with no database setup
- [ ] Jira Data Center support (REST API v2, wiki-markup bodies), demonstrated against Apache's
      public Jira at `issues.apache.org/jira`, which allows anonymous reads
- [ ] Tests against recorded API responses; GitHub Actions on every push
- [ ] Publish to PyPI

## Related

- [jira-dbt](https://github.com/keithwalsh/jira-dbt): a dbt project over the tables this loads,
  with cycle time, time-in-status, throughput and reopen rate as tested marts.
- [dbt-catalog-mcp](https://github.com/keithwalsh/dbt-catalog-mcp): an MCP server that lets an
  LLM find the right model or column in that project.

## Licence

MIT
