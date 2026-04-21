print("Hello i am your assistant.")

def add_goal():
    if not goal:
        return "Goal cannot be empty"
        
        from datetime import datetime
        now = datetime.now()
        f = now.strftime("%Y-%m-%d %H:%M")

        with open("goal.txt" "a") as file:
            file,write(f"{goal} | {f}\n")

        return "Todays goal added!"
   

def show_goals():
    try:
        
            with open("goal.txt", "r") as f:
                goals = f.readlines()

            if not goals:
                return "No goals yet!"
            
            result = ""
        
            for line in goals:
                text = line.strip()

                if "|" not in text:
                    continue

                goal, date = text.split("|")

                goal = goal.strip()
                date = date.strip()

                result += goal + " (" + date + ")\n"
            
            return result

    except FileNotFoundError:
        return "No goals yet!"

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
            

from datetime import datetime

def add_todays_goal(user_id, goal):
    filename = f"goals_{user_id}.txt"

    if not goal:
        return "Goal cannot be empty!"

    now = datetime.now()
    f = now.strftime("%Y-%m-%d %H:%M")

    with open(filename, "a") as file:
        file.write(f"{goal} | {f}\n")

    return "Цель на завтра добавлена!!"

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
            goal = goal.strip()
            date = date.strip()

            if date == today:
                result += f"• {goal}\n"

        return result if result else "На сегодня целей нет!"

    except FileNotFoundError:
        return "Целей пока нет!"

def delete_goals(user_id, index):
    filename = f"goals_{user_id}.txt"

    try:
        with open(filename, "r") as file:
            lines = file.readlines()

        if not lines:
            print("No goals yet!")
            return

        if index < 1 or index > len(lines):
            return "Неверный номер!"

        deleted = lines.pop(index - 1)

        with open(filename, "w") as file:
            file.writelines(lines)

            return f"Удалено: {deleted.strip()}"

    except FileNotFoundError:
        print("Список целей пуст!")

def exit_program():
    print("Goodbye!")
    exit()

