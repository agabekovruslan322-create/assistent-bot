import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def connect():
    return 
psycopg2.connect(DATABASE_URL)

def create_table():
    conn = connect()
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
        text TEXT,
        date TEXT,
        is_completed BOOLEAN DEFAULT FALSE
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

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Облачная база Synora v4 готова!")

def get_or_create_settings(user_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT day_end_time FROM user_settings WHERE user_id = %s", (user_id,))
    row = cursor.fetchone()
    
    if not row:
        cursor.execute("INSERT INTO user_settings (user_id, day_end_time) VALUES (%s, %s)", (user_id, "22:00"))
        conn.commit()
        row = ("22:00",)
    
    conn.close()
    return row

def update_user_time(user_id, new_time):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO user_settings (user_id, day_end_time) VALUES (%s, %s)"
        "ON CONFLICT (user_id) DO UPDATE SET day_end_time = EXCLUDED.day_end_time",
        (user_id, new_time)
    )
    conn.commit()
    conn.close()



