import requests

print(requests.get("https://api.telegram.org").status_code)

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from program import get_todays_goal, add_todays_goal, show_goals, delete_goals

TOKEN = "8680262922:AAHNveyzRB_Gl4ZbFxq1JlceRXf8xQIeK3Q"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Здравствуйте! Я ваш ассистент. 🚀\n\n"
        "Команды:\n"
        "🔵 /today - Показать цели на сегодня.\n"
        "🔵 /add - Добавить цель на завтра.\n"
        "🔵 /list - Полный список целей.\n"
        "🔵 /delete - Удалить цель.\n"
    )
    await update.message.reply_text(text)

async def today(update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id 
    
    result = get_todays_goal(user_id)
    await update.message.reply_text(result)

async def add(update, context):
    user_id = update.message.from_user.id 

    if not context.args:
        await update.message.reply_text(
            "Напиши цель после команды.\nПример: /add Go to gym"
        )
        return

    goal = " ".join(context.args)

    result = add_todays_goal(user_id, goal)

    await update.message.reply_text(result)
    
async def list_goals(update, context):
    user_id = update.message.from_user.id  
    filename = f"goals_{user_id}.txt"
    result = show_goals(user_id)

    try:
        with open(filename, "r") as file:
            content = file.read()
            await update.message.reply_text(content or "Empty")
    except:
        await update.message.reply_text("Список целей пуст!")

async def delete(update, context):
    userid = update.message.from_user.id 

    if not context.args:
        await update.message.reply_text("Пример /delete 1")
        return

    try:
        index = int(context.args[0])
    except:
        await update.message.reply_text("Введите номер цели!")
        return
    result = delete_goal(user_id, index)

    await update.message.reply_text(result)

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("list", list_goals))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("today", today))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("delete", delete))

    app.run_polling()

if __name__ == "__main__":
    main()