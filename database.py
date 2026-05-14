import logging
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def connect():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL не найден в переменных окружения!")
    return psycopg2.connect(DATABASE_URL)

def create_table():
    with connect() as conn:
        cursor = conn.cursor()
    #Таблица клятв
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vows (
                user_id BIGINT PRIMARY KEY
                )
            ''')
    #ТАБЛИЦА ЦЕЛЕЙ
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS goals_v4 (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            text TEXT NOT NULL,
            created_at TIMESTAMP,
            due_date TIMESTAMP,
                       
            reminder_time TIME,
                       
            is_completed BOOLEAN DEFAULT FALSE,
            is_reminded BOOLEAN DEFAULT FALSE
        )
        """)
    #Таблица настроек
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_settings (
            user_id BIGINT PRIMARY KEY,
            day_end_time TEXT DEFAULT '22:00',
            timezone TEXT DEFAULT 'Europe/Moscow'
            )
        """)

        cursor.execute("""
            ALTER TABLE goals_v4
            ADD COLUMN IF NOT EXISTS created_at TIMESTAMP
        """)

        cursor.execute("""
            ALTER TABLE goals_v4
            ADD COLUMN IF NOT EXISTS due_date TIMESTAMP
        """)

        cursor.execute("""
            ALTER TABLE goals_v4
            ADD COLUMN IF NOT EXISTS reminder_time TIME
        """)

        cursor.execute("""
            ALTER TABLE goals_v4
            ADD COLUMN IF NOT EXISTS is_reminded BOOLEAN DEFAULT FALSE""")
        
        cursor.execute("""
            ALTER TABLE goals_v4
            DROP COLUMN IF EXISTS date""")

    conn.commit()
    cursor.close()
    logging.info("✅ Облачная база Synora v4 готова!")

def get_or_create_settings(user_id):
    with connect() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT day_end_time FROM user_settings WHERE user_id = %s", (user_id,))
        row = cursor.fetchone()
    
        if not row:
            cursor.execute("INSERT INTO user_settings (user_id, day_end_time) VALUES (%s, %s)", (user_id, "22:00"))
            conn.commit()
            row = ("22:00",)
    
        return row

def update_user_time(user_id, new_time):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO user_settings (user_id, day_end_time) VALUES (%s, %s)"
            "ON CONFLICT (user_id) DO UPDATE SET day_end_time = EXCLUDED.day_end_time",
            (user_id, new_time)
        )
        conn.commit()

def is_user_vowed(user_id):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM vows WHERE user_id = %s", (user_id,))
        exists = cursor.fetchone() is not None
        return exists