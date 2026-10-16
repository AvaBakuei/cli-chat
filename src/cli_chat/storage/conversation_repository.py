import sqlite3
from cli_chat.storage.database import execute, fetch_all, vacuum


def init_db():
    create_table = """CREATE TABLE IF NOT EXISTS conversations(
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            conversation_id TEXT,
            title TEXT,s
            role TEXT, 
            content TEXT, 
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP 
        );"""
    try:
        execute(create_table)
    except sqlite3.OperationalError as e:
        print(e)



def save_message(conversation_id, title, role, content, timestamp):
    query = """ INSERT INTO conversations(conversation_id, title, role, content, timestamp)
                    VALUES(?, ?, ?, ?, ?) 
                    """
    params = (conversation_id,
              title, role, content, timestamp)
    execute(query, params)


def list_conversations():
    query = """
            SELECT MAX(timestamp), title, conversation_id
            FROM conversations
            GROUP BY conversation_id
            ORDER BY timestamp DESC 
            """
    return fetch_all(query)


def get_messages(conversation_id):
    query = """ SELECT * FROM conversations 
            WHERE conversation_id = ? 
            ORDER BY timestamp ASC
            """
    params = conversation_id
    return fetch_all(query, (conversation_id,))


def delete_all_conversations():
    execute(""" DELETE FROM conversations """)
    vacuum()
