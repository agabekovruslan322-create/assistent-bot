import psycopg2
import os

DATABASE_URL = "postgresql://postgres:zEtOhYFvUsDHxkMAFtdratYjfHuJaqvF@shuttle.proxy.rlwy.net:16580/railway"

def connect():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def create_table():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vows (
            user_id BIGINT PRIMARY KEY
            )
        ''')

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS goals_v4 (
        id SERIAL PRIMARY KEY,
        user_id BIGINT,
        text TEXT,
        date TEXT,
        is_completed BOOLEAN DEFAULT FALSE
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_settings (
        user_id BIGINT PRIMARY KEY,
        day_end_time TEXT DEFAULT '22:00',
        timezone TEXT DEFAULT 'Europe/Moscow'
        )
    """)

def get_or_create_settings(user_id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO user_settings (user_id)
        VALUES (%s)
        ON CONFLICT (user_id) DO NOTHING;
    """, (user_id))

    cursor.execute("SELECT day_end_time, FROM user_settings WHERE user_id = %s", (user_id,))
    settings = cursor.fetchone()
    conn.commit()
    conn.close()
    return settings

    conn.commit()
    conn.close()
    print("Облачная база Synora v4 готова!")