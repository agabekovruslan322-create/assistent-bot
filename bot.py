import requests

print(requests.get("https://api.telegram.org").status_code)

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from database import create_table

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
        "🛠 Бета версия /remind - напоминание целей (🔧находится в разработке🔧).\n"
    )
    await update.message.reply_text(text)

async def today(update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id 
    
    result = get_todays_goal(user_id)
    await update.message.reply_text(result)

async def add(update, context):
    user_id = update.message.from_user.id 

    goal_text = " ".join(context.args)

    if not goal_text.strip():
        await update.message.reply_text(
            "Напиши цель после команды.\nПример: /add Go to gym"
        )
        return

    result = add_todays_goal(user_id, goal_text)

    await update.message.reply_text(result)
    
async def list_goals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    result = show_goals(user_id)
    await update.message.reply_text(result)

async def delete(update, context):
    print("ARGS:", context.args)
    user_id = update.message.from_user.id 

    if not context.args:
        await update.message.reply_text("Пример /delete 1")
        return

    try:
        index = int(context.args[0])
        result = delete_goals(user_id, index)
        await update.message.reply_text(result)
    except:
        await update.message.reply_text("Введите номер цели!")
        return

from datetime import timedelta

async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text="⏰ Напоминание! Проверь свои цели!"
    )

async def remind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Пример: /remind 10 (минут) или /remind 1h (час) или /remind 1d (день)")
        return

    arg = context.args[0].lower()

    try:
        if arg.endswith('m'):
            minutes = int(arg[:-1])
        elif arg.endswith('h'):
            minutes = int(arg[:-1]) * 60
        elif arg.endswith('d'):
            minutes = int(arg[:-1]) * 1440
        elif arg.isdigit():
            minutes = int(arg)
        else:
            raise ValueError
    except ValueError:
        await update.message.reply_text("Используй формат: 10m, 1h или 1d")
        return

    context.job_queue.run_once(
        send_reminder,
        when=timedelta(minutes=minutes),
        chat_id=update.message.chat_id,
        name=str(update.message.from_user.id)
    )

    time_text = f"{minutes} минут"
    if minutes >= 60:
        time_text = f"{minutes // 60} ч. {minutes % 60} мин."

    await update.message.reply_text(f"Принято! Напомню через {time_text} ⏰")

def main():
    create_table()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("list", list_goals))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("today", today))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("delete", delete))
    app.add_handler(CommandHandler("remind", remind))

    app.run_polling()

if __name__ == "__main__":
    main()