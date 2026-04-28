import pytz
from datetime import datetime
from database import connect

def add_goal():
    if not goal:
        return "Goal cannot be empty"
        
        from datetime import datetime
        now = datetime.now()
        f = now.strftime("%Y-%m-%d %H:%M")

        with open("goal.txt" "a") as file:
            file,write(f"{goal} | {f}\n")

        return "Todays goal added!"
   
from database import connect

def show_goals(user_id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, text, date FROM goals_v4 WHERE user_id=%s ORDER BY id ASC",
        (user_id,)
    )

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return "Твой список пуст. Время течет сквозь пальцы, пока ты бездействуешь..."
    
    result = "⚔️ Твои инструменты власти над временем:\n\n"
    for goal_id, text, date in rows:
        pretty_date = date[5:]
        result += f"🆔 `{goal_id}` | {text} | {pretty_date}\n"
        
    return result

def show_history():
     with open("history.txt", "r") as f:
        content = f.read()

        if content == "":
            return "No goals yet!"
        else:
            return content

def search_goals():
    result = ""

    try:
        with open("goal.txt", "r") as file:
            for line in file:
                if word.lower() in line.lower():
                    result += line

        if result == "":
            return "Nothing found"

        return result

    except FileNotFoundError:
        return "No goals yet!"
            
from database import connect
from datetime import datetime

def add_todays_goal(user_id, goal):
    conn = connect()
    cursor = conn.cursor()

    tz = pytz.timezone('Europe/Moscow')
    now = datetime.now(tz).strftime("%Y-%m-%d %H:%M")
   
    cursor.execute(
        "INSERT INTO goals_v4 (user_id, text, date) VALUES (%s, %s, %s)",
        (user_id, goal, now))

    conn.commit()
    conn.close()

    return "Цель добавлена!"

import pytz
from datetime import datetime

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


def delete_goals(goal_id, user_id):
    conn = connect()
    cursor = conn.cursor()

    try:
        ids-to_delete = [int(i) for i in ids_text.replace(",", " ").split() if i.isdigit()]

        if not ids_to_delete:
            return: "❌ Укажи ID через пробел или запятую. Пример: /delete 30 31"

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

    if delete_count > 0:
        return f"✅ Удалено целей: {deleted_count}. Архитектор очистил пространство для нового."
    else:
        return "❌ Не нашел целей с такими ID в твоем списке."
    
def add_multi_goals(user_id, text):
    if not text.strip():
        return "Список пуст."
    
    goals = [g.strip() for g in text.split(";") if g.strip()]

    if not goals:
        return "Не нашел целей. Используй ';' как разделитель."

    for goal in goals:
        add_todays_goal(user_id, goal)

    return f"Система приняла {len(goals)} новых инструментов власти. Действуй."

def update_goal_text(goal_id, user_id, new_text):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE goals_v4 SET text = %s WHERE id = %s AND user_id = %s",
        (new_text, goal_id, user_id)
    ) 

    updated_rows = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()

    return updated_rows > 0