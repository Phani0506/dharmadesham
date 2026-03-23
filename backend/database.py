import sqlite3
import uuid

DB_FILE = "chats.db"

def get_connection():
    return sqlite3.connect(DB_FILE)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS chats (
            id TEXT PRIMARY KEY,
            title TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT,
            role TEXT,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (chat_id) REFERENCES chats (id)
        )
    ''')
    conn.commit()
    conn.close()

def create_chat(title="New Chat"):
    conn = get_connection()
    c = conn.cursor()
    chat_id = str(uuid.uuid4())
    c.execute("INSERT INTO chats (id, title) VALUES (?, ?)", (chat_id, title))
    conn.commit()
    conn.close()
    return chat_id

def get_chats():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT id, title, created_at, updated_at FROM chats ORDER BY updated_at DESC")
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_messages(chat_id: str):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT role, content, created_at FROM messages WHERE chat_id = ? ORDER BY created_at ASC", (chat_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def add_message(chat_id: str, role: str, content: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO messages (chat_id, role, content) VALUES (?, ?, ?)", (chat_id, role, content))
    c.execute("UPDATE chats SET updated_at = CURRENT_TIMESTAMP WHERE id = ?", (chat_id,))
    
    if role == 'user':
        c.execute("SELECT title, (SELECT count(*) FROM messages WHERE chat_id = ?) as msg_count FROM chats WHERE id = ?", (chat_id, chat_id))
        row = c.fetchone()
        if row and row[0] == "New Chat" and row[1] <= 2:
            new_title = (content[:30] + '...') if len(content) > 30 else content
            c.execute("UPDATE chats SET title = ? WHERE id = ?", (new_title, chat_id))
            
    conn.commit()
    conn.close()
