import sqlite3

def connect():
    return sqlite3.connect("database.db")

def create_table():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS goals_v2 (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        text TEXT,
        DELE text 
    )
    """)

    conn.commit()
    conn.close()

def upgrade_db():
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE goals ADD COLUMN date TEXT")
        conn.commit()
        print("Колонка успешно добавлена!")
    except:
        print("Колонка уже существует или же чтото пошло не так")
    conn.close()