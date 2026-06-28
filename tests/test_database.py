"""
tests/test_database.py
---------------------
Unit tests for the database layer.
"""

import os
import sqlite3
import pytest
from core.savesystem.database import (
    get_db_connection, execute_query, execute_non_query, execute_script,
)


@pytest.fixture
def tmp_db(tmp_path):
    """Create a temporary database with test tables."""
    db_path = str(tmp_path / "test.db")
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE test_table (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            value INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()
    return db_path


class TestExecuteQuery:
    """execute_query tests."""

    def test_select_empty_table(self, tmp_db):
        results = execute_query(tmp_db, "SELECT * FROM test_table")
        assert results == []

    def test_select_after_insert(self, tmp_db):
        execute_non_query(tmp_db, "INSERT INTO test_table (name, value) VALUES (?, ?)",
                          ("item1", 10))
        results = execute_query(tmp_db, "SELECT * FROM test_table")
        assert len(results) == 1
        assert results[0]["name"] == "item1"
        assert results[0]["value"] == 10

    def test_select_with_params(self, tmp_db):
        execute_non_query(tmp_db, "INSERT INTO test_table (name, value) VALUES (?, ?)",
                          ("item1", 10))
        execute_non_query(tmp_db, "INSERT INTO test_table (name, value) VALUES (?, ?)",
                          ("item2", 20))
        results = execute_query(tmp_db, "SELECT * FROM test_table WHERE name = ?",
                                ("item2",))
        assert len(results) == 1
        assert results[0]["value"] == 20


class TestExecuteNonQuery:
    """execute_non_query tests."""

    def test_single_tuple_insert(self, tmp_db):
        execute_non_query(tmp_db, "INSERT INTO test_table (name, value) VALUES (?, ?)",
                          ("test", 42))
        results = execute_query(tmp_db, "SELECT * FROM test_table")
        assert len(results) == 1

    def test_list_of_tuples_insert(self, tmp_db):
        params = [("item1", 10), ("item2", 20), ("item3", 30)]
        execute_non_query(tmp_db, "INSERT INTO test_table (name, value) VALUES (?, ?)",
                          params)
        results = execute_query(tmp_db, "SELECT * FROM test_table")
        assert len(results) == 3

    def test_empty_list_does_nothing(self, tmp_db):
        execute_non_query(tmp_db, "INSERT INTO test_table (name, value) VALUES (?, ?)",
                          [])
        results = execute_query(tmp_db, "SELECT * FROM test_table")
        assert len(results) == 0

    def test_no_params(self, tmp_db):
        execute_non_query(tmp_db,
                          "INSERT INTO test_table (id, name) VALUES (1, 'solo')")
        results = execute_query(tmp_db, "SELECT * FROM test_table")
        assert len(results) == 1

    def test_update(self, tmp_db):
        execute_non_query(tmp_db, "INSERT INTO test_table (name, value) VALUES (?, ?)",
                          ("test", 10))
        execute_non_query(tmp_db, "UPDATE test_table SET value = ? WHERE name = ?",
                          (99, "test"))
        results = execute_query(tmp_db, "SELECT * FROM test_table WHERE name = ?",
                                ("test",))
        assert results[0]["value"] == 99

    def test_delete(self, tmp_db):
        execute_non_query(tmp_db, "INSERT INTO test_table (name, value) VALUES (?, ?)",
                          ("test", 10))
        execute_non_query(tmp_db, "DELETE FROM test_table WHERE name = ?", ("test",))
        results = execute_query(tmp_db, "SELECT * FROM test_table")
        assert len(results) == 0

    def test_invalid_query_raises(self, tmp_db):
        with pytest.raises(sqlite3.Error):
            execute_non_query(tmp_db, "INVALID SQL SYNTAX")


class TestExecuteScript:
    """execute_script tests."""

    def test_create_table_via_script(self, tmp_db):
        execute_script(tmp_db, """
            CREATE TABLE script_table (
                id INTEGER PRIMARY KEY,
                data TEXT
            );
            INSERT INTO script_table (data) VALUES ('hello');
        """)
        results = execute_query(tmp_db, "SELECT * FROM script_table")
        assert len(results) == 1
        assert results[0]["data"] == "hello"


class TestConnectionString:
    """get_db_connection context manager."""

    def test_commit_on_success(self, tmp_db):
        with get_db_connection(tmp_db) as conn:
            conn.execute("INSERT INTO test_table (name, value) VALUES ('committed', 1)")
        results = execute_query(tmp_db, "SELECT * FROM test_table WHERE name = 'committed'")
        assert len(results) == 1

    def test_rollback_on_error(self, tmp_db):
        try:
            with get_db_connection(tmp_db) as conn:
                conn.execute("INSERT INTO test_table (name, value) VALUES ('rolled_back', 1)")
                raise RuntimeError("Force rollback")
        except RuntimeError:
            pass
        results = execute_query(tmp_db, "SELECT * FROM test_table WHERE name = 'rolled_back'")
        assert len(results) == 0
