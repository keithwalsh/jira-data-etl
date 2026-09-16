"""Target databases. Each loader replaces a table's contents with the rows it is given."""

import os


def _columns(rows: list) -> list:
    """Union of keys across all rows, in first-seen order, so ragged rows share one column list."""
    return list(dict.fromkeys(key for row in rows for key in row))


def _as_text(value):
    return None if value is None else str(value)


class DuckDBLoader:
    """Creates each table on first sight (every column VARCHAR; type them downstream in dbt)."""

    def __init__(self, path: str):
        import duckdb
        self.con = duckdb.connect(path)

    def load(self, rows: list, table: str):
        if not rows:
            return print(f'{table}: no rows, table left as it was.')
        columns = _columns(rows)
        self.con.execute(f'CREATE TABLE IF NOT EXISTS "{table}" ({", ".join(f'"{c}" VARCHAR' for c in columns)})')
        existing = {r[1] for r in self.con.execute(f'PRAGMA table_info("{table}")').fetchall()}
        for column in columns:
            if column not in existing:
                self.con.execute(f'ALTER TABLE "{table}" ADD COLUMN "{column}" VARCHAR')
        self.con.execute(f'DELETE FROM "{table}"')
        self.con.executemany(
            f'INSERT INTO "{table}" ({", ".join(f'"{c}"' for c in columns)}) VALUES ({", ".join("?" * len(columns))})',
            [tuple(_as_text(row.get(c)) for c in columns) for row in rows],
        )
        print(f'{table}: {len(rows)} rows loaded.')

    def close(self):
        self.con.close()


class MySQLLoader:
    """Truncates and inserts into tables that must already exist, with the columns the rows carry."""

    def __init__(self):
        import mysql.connector
        self.con = mysql.connector.connect(
            **{param: os.getenv(f'MYSQL_{param.upper()}') for param in ['host', 'port', 'user', 'password', 'database']}
        )

    def load(self, rows: list, table: str):
        if not rows:
            return print(f'{table}: no rows, table left as it was.')
        columns = _columns(rows)
        with self.con.cursor() as cursor:
            cursor.execute(f'TRUNCATE TABLE `{table}`')
            cursor.executemany(
                f'INSERT INTO `{table}` ({", ".join(f"`{c}`" for c in columns)}) VALUES ({", ".join(["%s"] * len(columns))})',
                [tuple(row.get(c) for c in columns) for row in rows],
            )
            self.con.commit()
        print(f'{table}: {len(rows)} rows loaded.')

    def close(self):
        if self.con.is_connected():
            self.con.close()


def make_loader(target: str, db_path: str):
    if target == 'duckdb':
        return DuckDBLoader(db_path)
    if target == 'mysql':
        return MySQLLoader()
    raise ValueError(f'unknown target {target!r}')
