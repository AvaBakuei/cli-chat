from cli.database import create_schema, execute_write, fetch_all, fetch_all_with_param, delete_and_vacuum


def init_db():
    create_table = """CREATE TABLE IF NOT EXISTS conversations(
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            conversation_id TEXT,
            title TEXT,
            role TEXT, 
            content TEXT, 
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP 
        );"""
    create_schema(create_table)


def save_message(conversation_id, title, role, content, timestamp):
    query = """ INSERT INTO conversations(conversation_id, title, role, content, timestamp)
                    VALUES(?, ?, ?, ?, ?) 
                    """
    params = (conversation_id,
              title, role, content, timestamp)
    execute_write(query, params)


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
    return fetch_all_with_param(query, params)


def delete_all_conversations():
    query = """ DELETE FROM conversations """
    delete_and_vacuum(query)
