import duckdb

from jira_data_etl.load import DuckDBLoader, make_loader


def test_duckdb_loader_creates_table_from_union_of_keys(tmp_path):
    db = tmp_path / 't.duckdb'
    loader = DuckDBLoader(str(db))
    loader.load([{'a': 1, 'b': None}, {'a': 2, 'c': 'x'}], 'demo')
    loader.close()

    con = duckdb.connect(str(db), read_only=True)
    columns = [r[1] for r in con.execute('PRAGMA table_info("demo")').fetchall()]
    assert columns == ['a', 'b', 'c']
    assert con.execute('SELECT a, b, c FROM demo ORDER BY a').fetchall() == [('1', None, None), ('2', None, 'x')]


def test_duckdb_loader_replaces_rows_and_adds_new_columns(tmp_path):
    db = tmp_path / 't.duckdb'
    loader = DuckDBLoader(str(db))
    loader.load([{'a': 1}], 'demo')
    loader.load([{'a': 9, 'd': True}], 'demo')
    loader.close()

    con = duckdb.connect(str(db), read_only=True)
    assert con.execute('SELECT a, d FROM demo').fetchall() == [('9', 'True')]


def test_empty_rows_leave_table_untouched(tmp_path, capsys):
    loader = DuckDBLoader(str(tmp_path / 't.duckdb'))
    loader.load([{'a': 1}], 'demo')
    loader.load([], 'demo')
    assert loader.con.execute('SELECT COUNT(*) FROM demo').fetchone()[0] == 1
    assert 'no rows' in capsys.readouterr().out
    loader.close()


def test_make_loader_rejects_unknown_target():
    try:
        make_loader('sqlite', 'x')
    except ValueError as e:
        assert 'sqlite' in str(e)
    else:
        raise AssertionError('expected ValueError')
