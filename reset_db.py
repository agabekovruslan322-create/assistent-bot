from database import connect

def full_reset():
    conn = connect()
    cursor = conn.cursor()
    
    print("⚠️ Начинаю полную очистку базы данных Synora...")
    
    try:
        cursor.execute("TRUNCATE TABLE goals_v4 RESTART IDENTITY CASCADE;")
        cursor.execute("TRUNCATE TABLE vows RESTART IDENTITY CASCADE;")
        cursor.execute("TRUNCATE TABLE user_settings RESTART IDENTITY CASCADE;")
        
        conn.commit()
        print("✅ База данных успешно очищена. Все ID сброшены на 1.")
        
    except Exception as e:
        print(f"❌ Ошибка при очистке: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    confirm = input("Ты уверен, что хочешь УДАЛИТЬ ВСЕ данные? (y/n): ")
    if confirm.lower() == 'y':
        full_reset()
    else:
        print("Отмена очистки.")