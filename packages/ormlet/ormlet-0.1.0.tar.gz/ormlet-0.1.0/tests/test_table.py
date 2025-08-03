from ormlet import Model, column


class User(Model):
    __table__ = "users"

    id = column.IntegerField(primary_key=True)
    name = column.VarCharField(max_length=100, unique=True, nullable=False)
    age = column.IntegerField(default=18)


def test_table_schema():
    schema = User.get_table_schema()
    assert "CREATE TABLE IF NOT EXISTS" in schema
    assert "id INTEGER PRIMARY KEY" in schema
    assert "name VARCHAR(100) UNIQUE NOT NULL" in schema
    assert "age INTEGER DEFAULT 18" in schema


def test_table_name():
    assert User.get_table_name() == "users"


def test_get_columns():
    cols = User.get_columns()
    assert "id" in cols
    assert "name" in cols
    assert "age" in cols
    assert cols["id"].primary_key


def test_get_primary_field():
    pk = User.get_primary_field()
    if pk:
        assert pk.primary_key
        assert pk.field_name == "id"


def test_column_sql_and_operators():
    col = column.IntegerField(primary_key=True, unique=True, default=1, nullable=False)
    col.field_name = "test"
    sql = col.to_sql()

    assert "PRIMARY KEY" in sql
    assert "UNIQUE" in sql
    assert "NOT NULL" in sql
    assert "DEFAULT 1" in sql
    assert (col == 5) == "test = 5"
    assert (col != 2) == "test != 2"
    assert (col < 3) == "test < 3"
    assert (col > 1) == "test > 1"
    assert col.like("abc%") == "test LIKE 'abc%'"
    assert col.in_([1, 2]) == "test IN (1, 2)"
    assert col.is_null() == "test IS NULL"
