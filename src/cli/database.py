import sqlite3
from cli.config import get_settings


def create_schema(create_table):
    try:
        with sqlite3.connect(get_settings().db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(create_table)

    except sqlite3.OperationalError as e:
        print(e)


def execute_write(query, params):
    with sqlite3.connect(get_settings().db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)


def fetch_all(query):
    with sqlite3.connect(get_settings().db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        return cursor.fetchall()


def fetch_all_with_param(query, params):
    with sqlite3.connect(get_settings().db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (params, ))
        return cursor.fetchall()


def delete_and_vacuum(query):
    with sqlite3.connect(get_settings().db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        conn.isolation_level = None
        conn.execute("VACUUM")
