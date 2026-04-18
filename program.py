print("Hello i am your assistant.")

def add_goal():
    while True:
        goal = input("Enter your goal: ")

        if goal == "":
            print("Goal cannot be empty!")
        else:
            from datetime import datetime
            now = datetime.now()
            f = now.strftime("%Y-%m-%d %H:%M")
            with open("goal.txt", "a") as file:
                file.write(f"{goal} | {f}\n")
                
            with open("history.txt", "a") as history:
                history.write(f"{goal} | {f}\n")
                print("Goal added!")

            while True:
                answer = input("Do you want to add another goal? (yes/no): ").lower().strip()
            
                if answer == "yes":
                    break
                elif answer == "no":
                    return
                else:
                    print("Please enter yes or no.")

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
        from datetime import datetime
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

while True:
    print("\n--- MENU ---")
    print("1 - Add goal")
    print("2 - Show goals")
    print("3 - Show history")
    print("4 - Search goals")
    print("5 - Add today's goals")
    print("6 - Get today's goals")
    print("7 - Delete goals")
    print("8 - Exit")

    choice = input("Choose: ")

    if choice == "1":
       add_goal()
            

    elif choice == "2":
        show_goals()

    elif choice == "3":
        show_history()

    elif choice == "4":
       search_goals()

    elif choice == "5":
        add_todays_goals()

    elif choice == "6":
        result = get_todays_goal()
        print(result)

    elif choice == "7":
       delete_goals()

        
    elif choice == "8":
       exit_program()