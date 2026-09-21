from cli.database import initToDb, insertToDb, fetchFromDb, fetchByID, deleteFromDb


def init_db():
    create_table = """CREATE TABLE IF NOT EXISTS conversations(
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            conversation_id TEXT,
            title TEXT,
            role TEXT, 
            content TEXT, 
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP 
        );"""
    initToDb(create_table)


def save_conversations(conversation_id, title, role, content, timestamp):
    query = """ INSERT INTO conversations(conversation_id, title, role, content, timestamp)
                    VALUES(?, ?, ?, ?, ?) 
                    """
    params = (conversation_id,
              title, role, content, timestamp)
    insertToDb(query, params)


def get_all_conversations():
    query = """
            SELECT MAX(timestamp), title, conversation_id
            FROM conversations
            GROUP BY conversation_id
            ORDER BY timestamp DESC 
            """
    return fetchFromDb(query)


def show_conversation(conversation_id):
    query = """ SELECT * FROM conversations 
            WHERE conversation_id = ? 
            ORDER BY timestamp ASC
            """
    params = conversation_id
    return fetchByID(query, params)


def delete_all_conversations():
    query = """ DELETE FROM conversations """
    deleteFromDb(query)
