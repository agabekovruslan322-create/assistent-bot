import sqlite3

def connect():
    return sqlite3.connect("goals.db")

def create_table():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        text TEXT,
        date TEXT
    )
    """)

    conn.commit()
    conn.close()