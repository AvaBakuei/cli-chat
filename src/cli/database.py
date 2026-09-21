import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent

DB_PATH = BASE_DIR / "data/chat.db"


def initToDb(create_table):
    try:
        with sqlite3.connect(str(DB_PATH)) as conn:
            cursor = conn.cursor()
            cursor.execute(create_table)

    except sqlite3.OperationalError as e:
        print(e)


def insertToDb(query, params):
    with sqlite3.connect(str(DB_PATH)) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)


def fetchFromDb(query):
    with sqlite3.connect(str(DB_PATH)) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        return cursor.fetchall()


def fetchByID(query, params):
    with sqlite3.connect(str(DB_PATH)) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (params, ))
        return cursor.fetchall()


def deleteFromDb(query):
    with sqlite3.connect(str(DB_PATH)) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        conn.isolation_level = None
        conn.execute("VACUUM")
