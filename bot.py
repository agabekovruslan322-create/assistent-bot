import requests

print(requests.get("https://api.telegram.org").status_code)

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from program import get_todays_goal, add_todays_goal

TOKEN = "8680262922:AAHNveyzRB_Gl4ZbFxq1JlceRXf8xQIeK3Q"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "здравствуйте! Я ваш ассистент. 🚀\n\n"
        "Команды:\n"
        "🔵 /today - Показать цели на сегодня\n"
        "🔵 /add - Добавить цель на завтра\n"
        "🔵 /list - Полный список целей\n"
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
    
async def showfile(update, context):
    user_id = update.message.from_user.id  
    filename = f"goals_{user_id}.txt"

    try:
        with open(filename, "r") as file:
            content = file.read()
            await update.message.reply_text(content or "Empty")
    except:
        await update.message.reply_text("Список целей пуст!")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("list", showfile))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("today", today))
    app.add_handler(CommandHandler("add", add))

    app.run_polling()

if __name__ == "__main__":
    main()