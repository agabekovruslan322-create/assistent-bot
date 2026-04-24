import psycopg2
import os

DATABASE_URL = "postgresql://postgres:zEtOhYFvUsDHxkMAFtdratYjfHuJaqvF@shuttle.proxy.rlwy.net:16580/railway"

def connect():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def create_table():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS goals_v4 (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        text TEXT,
        date text 
    )
    """)

    conn.commit()
    conn.close()
    print("Облачная база Synora v4 готова!")