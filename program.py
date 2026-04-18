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

def add_todays_goal(goal):
    if not goal:
        return "Goal cannot be empty!"

    now = datetime.now()
    f = now.strftime("%Y-%m-%d %H:%M")

    with open("todays_goal.txt", "a") as file:
        file.write(f"{goal} | {f}\n")

    return "Today's goal added!"
    

def get_todays_goal():
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        found = False

        with open("todays_goal.txt", "r") as file:
            goals = file.readlines()

            result = ""

            if not goals:
                return "No goals yet!"
            else:
                for line in goals:
                    text = line.strip()

                    if "|" not in text:
                        continue

                        goal, date = text.split("|")

                        goal = goal.strip()
                        date = date.strip()

                        date = date.split()[0]

                        if date == today:
                            result += "Today's goal: " + goal + "\n"
                            found = True

        if not found:
            return "No goals for today!"

        return result

    except FileNotFoundError:
         return "No goals yet!"

def delete_goals():
    try:
        with open("goal.txt", "r") as f:
            lines = f.readlines()

        if not lines:
            print("No goals yet!")
            return

        for index, line in enumerate(lines, start=1):
            print(f"{index}. {line.strip()}")

        try:
            num = int(input("Choose number: "))
        except ValueError:
            print("Enter a valid number!")
            return

        if num < 1 or num > len(lines):
            print("Invalid number!")
            return

        del lines[num - 1]

        with open("goal.txt", "w") as f:
            f.writelines(lines)

        print("Goal deleted!")

    except FileNotFoundError:
        print("No goals yet!")

def exit_program():
    print("Goodbye!")
    exit()

print("\n🔥---TODAY---🔥")
get_todays_goal()
