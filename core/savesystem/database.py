# database.py

import sqlite3
import os 
import sys 
from contextlib import contextmanager
from typing import Generator, Any, Dict, List, Tuple, Union # Added Tuple and Union for type hints

DB_PATH = "game.db" # This will be resolved to an absolute path by the caller if needed.

@contextmanager
def get_db_connection(db_path: str = DB_PATH) -> Generator[sqlite3.Connection, None, None]:
    """
    Provides a database connection.
    Activates foreign key enforcement and uses Row for dictionary-like access.
    Handles commit/rollback and connection closing.
    """
    conn = None
    try:
        abs_db_path = os.path.abspath(db_path) # Ensure absolute path is used by sqlite3.connect
        
        conn = sqlite3.connect(abs_db_path)
        conn.row_factory = sqlite3.Row  # Enable dictionary-like row access
        conn.execute("PRAGMA foreign_keys = ON")
        yield conn
        conn.commit()
    except sqlite3.Error as e: # Catch SQLite errors specifically during connection/commit/rollback
        print(f"SQLite Error during DB operation: {e} in {abs_db_path}", file=sys.stderr)
        if conn:
            conn.rollback()
        raise  # Re-raise the exception after rollback
    except Exception as e: # Catch other potential errors
        print(f"Non-SQLite error during DB operation: {e} in {abs_db_path}", file=sys.stderr)
        if conn:
            conn.rollback()
        raise

def execute_query(db_path: str, query: str, params: Tuple = ()) -> List[sqlite3.Row]:
    """Executes a query and returns all rows."""
    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.execute(query, params)
            results = cursor.fetchall()
            return results
    except sqlite3.Error as e:
        print(f"SQL Error during query execution: {e}", file=sys.stderr)
        print(f"  Query: {query}", file=sys.stderr)
        print(f"  Params: {params}", file=sys.stderr)
        raise e

def execute_non_query(db_path: str, query: str, params: Union[Tuple, List[Tuple]] = ()) -> None:
    """
    Executes a query that does not return rows (INSERT, UPDATE, DELETE, REPLACE).
    This function now strictly distinguishes between single-tuple parameters for conn.execute
    and list-of-tuples parameters for conn.executemany.
    """
    try:
        with get_db_connection(db_path) as conn:
            # --- Strict parameter handling ---
            if isinstance(params, list): # It's potentially a list for executemany
                if not params: # If list is empty, do nothing
                    pass
                elif isinstance(params[0], tuple): # Ensure it's structured as a list of tuples
                    try:
                        conn.executemany(query, params)
                    except sqlite3.ProgrammingError as pe:
                        print(f"ERROR during executemany (ProgrammingError): {pe}", file=sys.stderr)
                        print(f"  Query attempted: {query}", file=sys.stderr)
                        print(f"  Number of param sets: {len(params)}", file=sys.stderr)
                        raise pe
                    except sqlite3.Error as se: # Catch other SQLite errors during executemany
                        print(f"ERROR during executemany (SQLiteError): {se}", file=sys.stderr)
                        print(f"  Query attempted: {query}", file=sys.stderr)
                        print(f"  Number of param sets: {len(params)}", file=sys.stderr)
                        raise se
                else: # It's a list, but its elements are not tuples (e.g., list of ints) - unexpected
                    print(f"ERROR: execute_non_query received a list with non-tuple elements. Query: {query[:50]}...", file=sys.stderr)
                    raise TypeError("Expected list of tuples for executemany, but item types are incorrect.")

            elif isinstance(params, tuple): # It's a single parameter tuple for conn.execute
                conn.execute(query, params) 
            
            elif not params: # params is empty (equivalent to None or empty tuple/list)
                conn.execute(query) # Execute query with no parameters
            else:
                # Fallback for unexpected types of 'params'
                print(f"ERROR: Unexpected type for params in execute_non_query: {type(params)}. Query: {query[:50]}...", file=sys.stderr)
                raise TypeError(f"Unexpected type for params: {type(params)}")

    except sqlite3.Error as e:
        print(f"SQL Error during non-query execution: {e}", file=sys.stderr)
        print(f"  Query: {query}", file=sys.stderr)
        print(f"  Params: {params}", file=sys.stderr) 
        raise e

def execute_script(db_path: str, script: str) -> None:
    """Executes a script containing multiple SQL statements."""
    try:
        with get_db_connection(db_path) as conn:
            conn.executescript(script)
    except sqlite3.Error as e:
        print(f"SQL Error during script execution: {e}", file=sys.stderr)
        print(f"  Script begins: {script[:100]}...", file=sys.stderr)
        raise e
