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
        "SELECT text, date FROM goals_v3 WHERE user_id=?",
        (user_id,)
    )

    rows = cursor.fetchall()

    conn.close()

    if not rows:
        return "Список пуст"
    
    result = ""
    for i,(text, date) in enumerate(rows, start=1):
        result += f"{i}. {text} | {date}\n"
        
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
        "INSERT INTO goals_v3 (user_id, text, date) VALUES (?, ?, ?)",
        (user_id, goal, now))

    conn.commit()
    conn.close()

    return "Цель добавлена!"

def get_todays_goal(user_id):
    filename = f"goals_{user_id}.txt"
    today = datetime.now().strftime("%Y-%m-%d")

    try:
        with open(filename, "r") as file:
            lines = file.readlines()

        result = ""

        for line in lines:
            if "|" not in line:
                continue

            goal, date = line.strip().split("|")
            date = date.strip().split()[0]

            if date == today:
                result += f"• {goal.strip()}\n"

        return result if result else "На сегодня целей нет!"

    except FileNotFoundError:
        return "Целей пока нет!"

def delete_goals(user_id, index):
    filename = f"goals_{user_id}.txt"

    try:
        with open(filename, "r") as file:
            lines = file.readlines()

        if not lines:
            return "Список пуст!"

        if index < 1 or index > len(lines):
            return "Неверный номер!"

        deleted = lines.pop(index - 1)

        with open(filename, "w") as file:
            file.writelines(lines)

            return f"Удалено: {deleted.strip()}"
    except FileNotFoundError:
        return "Список пуст!"

def exit_program():
    print("Goodbye!")
    exit()

