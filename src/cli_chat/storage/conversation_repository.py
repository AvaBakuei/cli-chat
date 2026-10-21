import sqlite3
import time

from cli_chat.models import ConversationSummary, Message
from cli_chat.storage.database import execute, fetch_all, vacuum


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
        execute(create_table)
    except sqlite3.OperationalError as e:
        print(e)


def save_message(conversation_id: str, title: str, role: str, content: str) -> None:
    query = """
        INSERT INTO conversations (conversation_id, title, role, content, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """
    params = (conversation_id, title, role, content, int(time.time()))
    execute(query, params)


def list_conversations() -> list[ConversationSummary]:
    rows = fetch_all(
        """
        SELECT conversation_id, title, MAX(timestamp) AS last_activity
        FROM conversations
        GROUP BY conversation_id
        ORDER BY last_activity DESC
        """
    )
    return [
        ConversationSummary(
            conversation_id=row["conversation_id"],
            title=row["title"],
            last_activity=row["last_activity"],
        )
        for row in rows
    ]


def get_messages(conversation_id: str) -> list[Message]:
    rows = fetch_all(
        """
        SELECT conversation_id, role, content, timestamp
        FROM conversations
        WHERE conversation_id = ?
        ORDER BY timestamp ASC, id ASC
        """,
        (conversation_id,),
    )
    return [
        Message(
            conversation_id=row["conversation_id"],
            role=row["role"],
            content=row["content"],
            timestamp=row["timestamp"],
        )
        for row in rows
    ]


def delete_all_conversations():
    execute(""" DELETE FROM conversations """)
    vacuum()
