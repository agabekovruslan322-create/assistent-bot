import os
import requests
import pytz
from datetime import datetime, timedelta

print(requests.get("https://api.telegram.org").status_code)

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from database import create_table
from telegram.ext import ConversationHandler, MessageHandler, filters

from program import get_todays_goal, add_todays_goal, show_goals, delete_goals, add_multi_goals, update_goal_text, complete_goal

TOKEN = os.getenv("BOT")

if not TOKEN:
    print("Ошибка: Переменная BOT_TOKEN не найдена")
    exit(1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Здравствуйте! Я ваш ассистент. 🚀\n\n"
        "Команды:\n"
        "🔵 /start - Меню.\n"
        "🔵 /today - Показать цели на сегодня.\n"
        "🔵 /add - Добавить цель на завтра.\n"
        "🔵 /list - Полный список целей.\n"
        "🔵 /delete - Удалить цель.\n"
        "🔵 /remind - напоминание целей.\n"
        "🔵 /multi - Добавление нескольких целей подряд.\n"
        "🔵 /edit - Отредактировать цель\n"
    )
    await update.message.reply_text(text)

async def today(update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id 
    
    result = get_todays_goal(user_id)
    print(f"DEBUG: Result for user {user_id} is: {result}")

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
    user_id = update.effective_user.id

    user_input = " ".join(context.args)
    
    result = delete_goals(user_input, user_id)
    await update.message.reply_text(result)

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
    minutes = 0

    try:
        if arg.endswith('m'):
            minutes = int(arg[:-1])
        elif arg.endswith('h'):
            minutes = int(arg[:-1]) * 60
        elif arg.endswith('d'):
            minutes = int(arg[:-1]) * 1440

        elif ":" in arg:
            tz = pytz.timezone('Europe/Moscow')
            now = datetime.now(tz)

            t = datetime.strptime(arg, "%H:%M")

            target_time = tz.localize(datetime(
                now.year, now.month, now.day, t.hour, t.minute
            ))

            if target_time < now:
                target_time += timedelta(days=1)

            diff = target_time - now
            minutes = int(diff.total_seconds() / 60)

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

async def multi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    all_text = " ".join(context.args)

    if not all_text:
        await update.message.reply_text("💡 Пример: /multi Цель 1; Цель 2; Цель 3")
        return

    result = add_multi_goals(user_id, all_text)

    await update.message.reply_text(result)

async def edit_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not context.args or len(context.args) < 2:
        await update.message.reply_text("⚠️ Формат: `/edit [ID] [новый текст]`")
        return

    try:
        goal_id = int(context.args[0])
        new_text = " ".join(context.args[1:])

        success = update_goal_text(goal_id, user_id, new_text)

        if success:
            await update.message.reply_text(f"✅ Задача №{goal_id} обновлена.")
        else:
            await update.message.reply_text("❌ Задача не найдена.")

    except ValueError:
        await update.message.reply_text("❌ ID должен быть числом.")

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not context.args:
        await update.message.reply_text("Укажи ID задачи. Пример: /done 7")
        return
    try:
        goal_id = int(context.args[0])
        task_text = complete_goal(goal_id, user_id)

        if task_text:
            await update.message.reply_text(f"🔥 **Триумф!**\nЗадача «{task_text}» выполнена. Стоик непоколебим.")
        else:
            await update.message.reply_text("Задача не найдена. Возможно, она уже в прошлом или не твоя.")
     
    except ValueError:
        await update.message.reply_text("ID должен быть числом мой друг.")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    result = get_user_stats(user_id)
    await update.message.reply_text(result)

def main():
    create_table()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("list", list_goals))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("today", today))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("delete", delete))
    app.add_handler(CommandHandler("remind", remind))
    app.add_handler(CommandHandler("multi", multi))
    app.add_handler(CommandHandler("edit", edit_goal))
    app.add_handler(CommandHandler("done", done))
    app.add_handler(CommandHandler("stats", stats))
    
    app.run_polling()

if __name__ == "__main__":
    main()