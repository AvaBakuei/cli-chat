import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DB_PATH = BASE_DIR / "data/chat.db"


# Initialize Database
def init_db():
    create_table = """CREATE TABLE IF NOT EXISTS conversations(
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            conversation_id TEXT,
            title TEXT,
            role TEXT, 
            content TEXT, 
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP 
        );"""

    try:
        with sqlite3.connect(str(DB_PATH)) as conn:
            cursor = conn.cursor()
            cursor.execute(create_table)

    except sqlite3.OperationalError as e:
        print(e)


def save_conversations(conversation_id, title, role, content, timestamp):
    with sqlite3.connect(str(DB_PATH)) as conn:
        sql_query = """ INSERT INTO conversations(conversation_id, title, role, content, timestamp)
        VALUES(?, ?, ?, ?, ?) """
        cursor = conn.cursor()
        cursor.execute(sql_query, (conversation_id,
                       title, role, content, timestamp))


def get_all_conversations():
    with sqlite3.connect(str(DB_PATH)) as conn:
        sql_query = """
            SELECT MAX(timestamp), title, conversation_id
            FROM conversations
            GROUP BY conversation_id
            ORDER BY timestamp DESC
        """

        cursor = conn.cursor()
        cursor.execute(sql_query)
        return cursor.fetchall()


def show_conversation(conversation_id):
    with sqlite3.connect(str(DB_PATH)) as conn:
        sql_query = """ SELECT * FROM conversations WHERE conversation_id = ? """
        cursor = conn.cursor()
        cursor.execute(sql_query, (conversation_id, ))
        return cursor.fetchall()


def get_latest_conversations(limit=10):
    with sqlite3.connect(str(DB_PATH)) as conn:
        sql_query = """ SELECT conversation_id FROM conversations GROUP BY conversation_id ORDER BY MAX(id) DESC LIMIT ? """
        cursor = conn.cursor()
        cursor.execute(sql_query, (limit, ))
        return cursor.fetchall()


def delete_all_conversations():
    with sqlite3.connect(str(DB_PATH)) as conn:
        sql_query = """ DELETE FROM conversations """
        cursor = conn.cursor()
        cursor.execute(sql_query)
        conn.isolation_level = None
        conn.execute("VACUUM")
