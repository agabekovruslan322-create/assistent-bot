import logging
import pytz
import re
from datetime import datetime
from database import connect


def add_todays_goal(user_id, goal):

    goal_text, reminder_time = extract_time(goal)
    print(goal_text)
    print(reminder_time)

    with connect() as conn:
        cursor = conn.cursor()
        tz = pytz.timezone('Europe/Moscow')
        now = datetime.now(tz)
    
        cursor.execute(
            """INSERT INTO goals_v4 (
            user_id, 
            text, 
            created_at, 
            reminder_time
            ) 
            VALUES (%s, %s, %s, %s)
            """,
            (user_id, goal_text, now, reminder_time)
        )
        conn.commit()
        return "Цель добавлена!"

def get_today_goals(user_id):

    with connect() as conn:
        cursor = conn.cursor()

        tz = pytz.timezone('Europe/Moscow')
        today_str = datetime.now(tz).strftime("%Y-%m-%d")

        cursor.execute(
            "SELECT id, text FROM goals_v4 WHERE user_id=%s AND date LIKE %s AND is_completed=FALSE",
            (user_id, f"{today_str}%")
        )

        rows = cursor.fetchall()

        return rows

def show_goals(user_id, only_active=True):
    with connect() as conn:
        cursor = conn.cursor()
    
        if only_active:
            query = "SELECT id, text, date FROM goals_v4 WHERE user_id=%s AND is_completed=FALSE ORDER BY id ASC"
        else:
            query = "SELECT id, text, date FROM goals_v4 WHERE user_id=%s AND is_completed=TRUE ORDER BY date DESC"

        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()

    if not rows:
        return "Твой список пуст. Время течет сквозь пальцы..."

    title = "⚔️ Актуальные цели:" if only_active else "📜 Архив твоих побед:"
    result = f"{title}\n\n"

    for goal_id, text, date  in rows:
        icon = "⏳" if only_active else "🏛"
        result += f"{icon} 🆔 `{goal_id}` | {text} | {date[5:10]}\n"

    return result

def get_history(user_id):
    return show_goals(user_id, only_active=False)

def delete_goals(ids_text, user_id):
    with connect() as conn:
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
            return f"☢️ Ошибка базы: {e}"
    
        return f"✅ Удалено целей: {delete_count}." if delete_count > 0 else "❌ Задачи не найдены."

def complete_goal(goal_id, user_id):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE goals_v4 SET is_completed = TRUE WHERE id = %s AND user_id = %s RETURNING text",
            (goal_id, user_id)
        )
        row = cursor.fetchone()
        conn.commit()
        return row[0] if row else None

def update_goal_text(goal_id, user_id, new_text):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE goals_v4 SET text = %s WHERE id = %s AND user_id = %s",
            (new_text, goal_id, user_id)
       ) 
        updated_rows = cursor.rowcount
        conn.commit()
        return updated_rows > 0

def get_user_stats(user_id):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                COUNT(*), 
                SUM(CASE WHEN is_completed THEN 1 ELSE 0 END) 
            FROM goals_v4 
            WHERE user_id = %s
        """, (user_id,))
    
        total, completed = cursor.fetchone()

    if not total:
        return "Твой путь еще не начат. Добавь первую цель!"

    completed = completed or 0
    percent = int((completed / total) * 100)
    bar = "🟢" * (percent // 10) + "⚪" * (10 - (percent // 10))

    return (
        f"🏛 **Твои результаты!:**🔥\n\n"
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

def check_vow(user_id):
    with connect() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT 1 FROM vows WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            return result is not None
        except Exception as e:
            logging.error(f"Ошибка при проверке клятвы: {e}")
            return False

def add_vow(user_id):
    with connect() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO vows (user_id) VALUES (%s) ON CONFLICT (user_id) DO NOTHING", 
                (user_id,)
            )
            conn.commit()
            logging.info(f"Клятва для {user_id} успешно записана!")
        except Exception as e:
            logging.error(f"ОШИБКА ПРИ ЗАПИСИ КЛЯТВЫ: {e}")

def get_users_for_judgement(current_time):
    with connect() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT user_id FROM user_settings WHERE day_end_time = %s", (current_time,))
        result = cursor.fetchall()
        return [u[0] for u in result]
    
def extract_time(goal_text):
    match = re.search(r"\b\d{2}:\d{2}\b", goal_text)

    if not match:
        return goal_text, None
    
    reminder_time = match.group()
    clean_text = goal_text.replace(reminder_time, "").strip()

    return clean_text, reminder_time