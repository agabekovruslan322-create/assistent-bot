import sqlite3

def connect():
    return sqlite3.connect("database.db")

def create_table():
    conn = connect()
    cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    text TEXTS,
    DELE text 
    )
    """)

conn.commit()
conn.close()