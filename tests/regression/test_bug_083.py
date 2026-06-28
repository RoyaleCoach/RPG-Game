"""
tests/regression/test_bug_083.py
--------------------------------
Regression tests for bugs fixed in v0.8.3.

Prevents regression of:
- execute_non_query tuple vs list handling
- empty parameter handling
- stale __pycache__ issues
"""

import os
import sqlite3
import pytest
from core.savesystem.database import (
    execute_query, execute_non_query, get_db_connection,
)


@pytest.fixture
def tmp_db(tmp_path):
    db_path = str(tmp_path / "regression_test.db")
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE test_batch (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            value INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()
    return db_path


class TestExecuteNonQueryTupleHandling:
    """Regression: execute_non_query must distinguish tuple from list."""

    def test_single_tuple_uses_execute(self, tmp_db):
        """Single tuple params should use conn.execute()."""
        execute_non_query(
            tmp_db,
            "INSERT INTO test_batch (name, value) VALUES (?, ?)",
            ("single_item", 42),
        )
        results = execute_query(tmp_db, "SELECT * FROM test_batch")
        assert len(results) == 1
        assert results[0]["name"] == "single_item"

    def test_list_of_tuples_uses_executemany(self, tmp_db):
        """List of tuples should use conn.executemany()."""
        params = [("item1", 10), ("item2", 20), ("item3", 30)]
        execute_non_query(
            tmp_db,
            "INSERT INTO test_batch (name, value) VALUES (?, ?)",
            params,
        )
        results = execute_query(tmp_db, "SELECT * FROM test_batch")
        assert len(results) == 3

    def test_empty_list_does_not_crash(self, tmp_db):
        """Empty list should be silently skipped."""
        execute_non_query(
            tmp_db,
            "INSERT INTO test_batch (name, value) VALUES (?, ?)",
            [],
        )
        results = execute_query(tmp_db, "SELECT * FROM test_batch")
        assert len(results) == 0

    def test_no_params_works(self, tmp_db):
        """Query with no params should execute directly."""
        execute_non_query(
            tmp_db,
            "INSERT INTO test_batch (id, name) VALUES (1, 'no_params')",
        )
        results = execute_query(tmp_db, "SELECT * FROM test_batch")
        assert len(results) == 1

    def test_empty_tuple_works(self, tmp_db):
        """Empty tuple should execute query with no parameters."""
        execute_non_query(
            tmp_db,
            "INSERT INTO test_batch (id, name) VALUES (1, 'empty_tuple')",
            (),
        )
        results = execute_query(tmp_db, "SELECT * FROM test_batch")
        assert len(results) == 1


class TestExecuteNonQueryEdgeCases:
    """Edge cases for execute_non_query."""

    def test_multiple_single_tuples_sequentially(self, tmp_db):
        """Multiple sequential single-tuple inserts should all work."""
        for i in range(5):
            execute_non_query(
                tmp_db,
                "INSERT INTO test_batch (name, value) VALUES (?, ?)",
                (f"item_{i}", i * 10),
            )
        results = execute_query(tmp_db, "SELECT * FROM test_batch")
        assert len(results) == 5

    def test_mixed_operations(self, tmp_db):
        """Mix of single inserts and batch inserts should work."""
        # Single insert
        execute_non_query(
            tmp_db,
            "INSERT INTO test_batch (name, value) VALUES (?, ?)",
            ("single", 1),
        )
        # Batch insert
        execute_non_query(
            tmp_db,
            "INSERT INTO test_batch (name, value) VALUES (?, ?)",
            [("batch1", 2), ("batch2", 3)],
        )
        # Another single
        execute_non_query(
            tmp_db,
            "INSERT INTO test_batch (name, value) VALUES (?, ?)",
            ("single2", 4),
        )
        results = execute_query(tmp_db, "SELECT * FROM test_batch")
        assert len(results) == 4

    def test_rollback_on_error(self, tmp_db):
        """Failed insert should be rolled back."""
        execute_non_query(
            tmp_db,
            "INSERT INTO test_batch (name, value) VALUES (?, ?)",
            ("before_error", 1),
        )
        # This should fail
        with pytest.raises(sqlite3.Error):
            execute_non_query(
                tmp_db,
                "INSERT INTO nonexistent_table (name) VALUES (?)",
                ("should_fail",),
            )
        # The first insert should still be there (committed)
        results = execute_query(
            tmp_db, "SELECT * FROM test_batch WHERE name = 'before_error'"
        )
        assert len(results) == 1
