from backend.db.database import get_connection


def create_conversation(title: str) -> int:
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO conversations (title) VALUES (?)",
        (title,),
    )
    conn.commit()
    conversation_id = cursor.lastrowid
    conn.close()
    return conversation_id


def save_message(conversation_id: int, role: str, content: str):
    conn = get_connection()
    conn.execute(
        "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
        (conversation_id, role, content),
    )
    conn.commit()
    conn.close()


def get_messages(conversation_id: int) -> list:
    conn = get_connection()
    rows = conn.execute(
        "SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY id",
        (conversation_id,),
    ).fetchall()
    conn.close()
    return [{"role": row["role"], "content": row["content"]} for row in rows]
def list_conversations() -> list:
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, title, created_at FROM conversations ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def conversation_exists(conversation_id: int) -> bool:
    conn = get_connection()
    row = conn.execute(
        "SELECT 1 FROM conversations WHERE id = ?",
        (conversation_id,),
    ).fetchone()
    conn.close()
    return row is not None