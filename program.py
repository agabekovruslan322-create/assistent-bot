import pytz
from datetime import datetime
from database import connect

# --- БЛОК ДОБАВЛЕНИЯ И ПРОСМОТРА ---

def add_todays_goal(user_id, goal):
    conn = connect()
    cursor = conn.cursor()
    tz = pytz.timezone('Europe/Moscow')
    now = datetime.now(tz).strftime("%Y-%m-%d %H:%M")
    
    cursor.execute(
        "INSERT INTO goals_v4 (user_id, text, date) VALUES (%s, %s, %s)",
        (user_id, goal, now)
    )
    conn.commit()
    conn.close()
    return "Цель добавлена!"

def get_todays_goal(user_id):
    conn = connect()
    cursor = conn.cursor()
    tz = pytz.timezone('Europe/Moscow')
    today_str = datetime.now(tz).strftime("%Y-%m-%d")

    cursor.execute(
        "SELECT text FROM goals_v4 WHERE user_id=%s AND date LIKE %s",
        (user_id, f"{today_str}%")
    )
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return "На сегодня целей нет. Ты свободен или просто забыл про мечты?"

    result = f"📅 Твой план на сегодня ({today_str}):\n\n"
    for i, (text,) in enumerate(rows, start=1):
        result += f"{i}. {text}\n"
    return result

def show_goals(user_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, text, date, is_completed FROM goals_v4 WHERE user_id=%s ORDER BY id ASC",
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return "Твой список пуст. Время течет сквозь пальцы..."
    
    result = "⚔️ Твои инструменты власти над временем:\n\n"
    for goal_id, text, date, is_completed in rows:
        status = "✅" if is_completed else "⏳"
        pretty_date = date[5:16] if date else "??-??" # Вывел еще и время (ЧЧ:ММ)
        result += f"{status} 🆔 `{goal_id}` | {text} | {pretty_date}\n"
    return result

# --- БЛОК РЕДАКТИРОВАНИЯ И УДАЛЕНИЯ ---

def delete_goals(ids_text, user_id):
    conn = connect()
    cursor = conn.cursor()
    try:
        ids_to_delete = [int(i) for i in ids_text.replace(",", " ").split() if i.isdigit()]
        if not ids_to_delete:
            return "❌ Укажи ID через пробел или запятую."

        cursor.execute(
            "DELETE FROM goals_v4 WHERE user_id = %s AND id IN %s",
            (user_id, tuple(ids_to_delete))
        )
        delete_count = cursor.rowcount
        conn.commit()
    except Exception as e:
        conn.close()
        return f"☢️ Ошибка базы: {e}"
    
    conn.close()
    return f"✅ Удалено целей: {delete_count}." if delete_count > 0 else "❌ Задачи не найдены."

def complete_goal(goal_id, user_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE goals_v4 SET is_completed = TRUE WHERE id = %s AND user_id = %s RETURNING text",
        (goal_id, user_id)
    )
    row = cursor.fetchone()
    conn.commit()
    conn.close()
    return row[0] if row else None

def update_goal_text(goal_id, user_id, new_text):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE goals_v4 SET text = %s WHERE id = %s AND user_id = %s",
        (new_text, goal_id, user_id)
    ) 
    updated_rows = cursor.rowcount
    conn.commit()
    conn.close()
    return updated_rows > 0

# --- СТАТИСТИКА ---

def get_user_stats(user_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            COUNT(*), 
            SUM(CASE WHEN is_completed THEN 1 ELSE 0 END) 
        FROM goals_v4 
        WHERE user_id = %s
    """, (user_id,))
    
    total, completed = cursor.fetchone()
    conn.close()

    if not total:
        return "Твой путь еще не начат. Добавь первую цель!"

    completed = completed or 0
    percent = int((completed / total) * 100)
    bar = "🟢" * (percent // 10) + "⚪" * (10 - (percent // 10))

    return (
        f"🏛 **Твоя Стоя:**\n\n"
        f"📊 Прогресс: {percent}%\n"
        f"[{bar}]\n\n"
        f"✅ Завершено: {completed}\n"
        f"⏳ Всего: {total}\n\n"
        f"_«Не важно, как медленно ты идешь, главное — не останавливаться»._"
    )

def add_multi_goals(user_id, text):
    goals = [g.strip() for g in text.split(";") if g.strip()]
    for goal in goals:
        add_todays_goal(user_id, goal)
    return f"⚡️ Добавлено целей: {len(goals)}"
    