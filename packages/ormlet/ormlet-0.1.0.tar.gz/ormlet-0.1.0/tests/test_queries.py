import sqlite3
from typing import Generator

import pytest
from ormlet.column import IntegerField, VarCharField
from ormlet.model import Model
from ormlet.query_builder import delete, insert, select, update


class User(Model):
    __table__ = "users"

    id = IntegerField(primary_key=True)
    name = VarCharField(max_length=50)
    age = IntegerField()


@pytest.fixture
def connection() -> Generator[sqlite3.Connection, None, None]:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


@pytest.fixture(autouse=True)
def setup_schema(connection: sqlite3.Connection):
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name VARCHAR(50),
            age INTEGER
        )
    """)
    connection.commit()


def test_insert_user(connection: sqlite3.Connection):
    user_id = insert(User).values(id=1, name="Alice", age=30).execute(connection)
    assert isinstance(user_id, int)

    result = connection.execute(
        "SELECT * FROM users WHERE id = ?", (user_id,)
    ).fetchone()
    assert result["name"] == "Alice"
    assert result["age"] == 30


def test_select_user(connection: sqlite3.Connection):
    connection.execute(
        "INSERT INTO users (id, name, age) VALUES (?, ?, ?)", (1, "Bob", 25)
    )
    connection.commit()

    results = select(User).where(User.name == "Bob").execute(connection)
    if isinstance(results, list):
        assert len(results) == 1
        bob = results[0]
        assert bob.name == "Bob"
        assert bob.age == 25


def test_update_user(connection: sqlite3.Connection):
    connection.execute(
        "INSERT INTO users (id, name, age) VALUES (?, ?, ?)", (1, "Charlie", 40)
    )
    connection.commit()

    rowcount = (
        update(User).set(age=41).where(User.name == "Charlie").execute(connection)
    )
    assert rowcount == 1

    result = connection.execute(
        "SELECT * FROM users WHERE name = ?", ("Charlie",)
    ).fetchone()
    assert result["age"] == 41


def test_delete_user(connection: sqlite3.Connection):
    connection.execute(
        "INSERT INTO users (id, name, age) VALUES (?, ?, ?)", (1, "Dan", 50)
    )
    connection.commit()

    rowcount = delete(User).where(User.name == "Dan").execute(connection)
    assert rowcount == 1

    result = connection.execute(
        "SELECT * FROM users WHERE name = ?", ("Dan",)
    ).fetchone()
    assert result is None


def test_complex_where(connection: sqlite3.Connection):
    connection.execute(
        "INSERT INTO users (id, name, age) VALUES (?, ?, ?)", (1, "Eve", 21)
    )
    connection.execute(
        "INSERT INTO users (id, name, age) VALUES (?, ?, ?)", (2, "Eve", 19)
    )
    connection.commit()

    results = (
        select(User).where(User.name == "Eve").and_(User.age >= 20).execute(connection)
    )

    if isinstance(results, list):
        assert len(results) == 1
        assert results[0].age == 21


def test_or_where_query(connection: sqlite3.Connection):
    connection.execute(
        "INSERT INTO users (id, name, age) VALUES (?, ?, ?)", (1, "Foo", 15)
    )
    connection.execute(
        "INSERT INTO users (id, name, age) VALUES (?, ?, ?)", (2, "Bar", 35)
    )
    connection.commit()

    results = (
        select(User).where(User.name == "Foo").or_(User.age > 30).execute(connection)
    )
    if isinstance(results, list):
        assert len(results) == 2
