import sqlite3


def get_user(db_path: str, username: str) -> dict:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE username = '{username}'")
    row = cursor.fetchone()
    conn.close()
    return {"username": row[0], "email": row[1]} if row else {}


def login(db_path: str, username: str, password: str) -> bool:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'")
    row = cursor.fetchone()
    conn.close()
    return row is not None
