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
        "SELECT text, date FROM goals_v4 WHERE user_id=%s",
        (user_id,)
    )

    rows = cursor.fetchall()

    conn.close()

    if not rows:
        return "Твой список пуст. Время течет сквозь пальцы, пока ты бездействуешь..."
    
    result = "⚔️ Твои инструменты власти над временем:\n\n"
    for i,(text, date) in enumerate(rows, start=1):
        pretty_date = date[5:]
        result += f"{i}. {text} | {pretty_date}\n"
        
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


def delete_goals(user_id, index):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM goals_v4 WHERE user_id=%s ORDER BY id ASC",
        (user_id,)
    )
    rows = cursor.fetchall()

    if not rows or index < 1 or index > len(rows):
        conn.close()
        return "Неверный номер цели. Смотри внимательнее в /list."

    target_id = rows[index - 1][0]

    cursor.execute("DELETE FROM goals_v4 WHERE id=%s", (target_id,))

    conn.commit()
    conn.close()

    return f"Цель №{index} стерта из времени. Освободившееся время — это ресурс. Как ты распорядишься им теперь?"

def exit_program():
    print("Goodbye!")
    exit()

