"""Low-level SQLite helpers. This module knows nothing about conversations."""
import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from cli_chat.config import get_settings


@contextmanager
def connect() -> Generator[sqlite3.Connection, None, None]:
    conn = sqlite3.connect(get_settings().db_path)
    conn.row_factory = sqlite3.Row
    try:
        with conn:
            yield conn
    finally:
        conn.close()

def execute(query: str, params: tuple = ()) -> None:
    with connect() as conn:
        conn.execute(query, params)


def fetch_all(query: str, params: tuple = ()) -> list[sqlite3.Row]:
    with connect() as conn:
        return conn.execute(query, params).fetchall()

def vacuum() -> None:
    conn = sqlite3.connect(get_settings().db_path, isolation_level=None)
    try:
        conn.execute("VACUUM")
    finally:
        conn.close()
