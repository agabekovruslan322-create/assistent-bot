import re
import os
import requests
import pytz
import logging
import traceback

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("apscheduler").setLevel(logging.WARNING)

from datetime import datetime, timedelta

print(requests.get("https://api.telegram.org").status_code)

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
from database import create_table
from telegram.ext import ConversationHandler, MessageHandler, filters
from database import connect

CHOOSING, TYPING_REPLY = range(2)

from program import get_todays_goal, add_todays_goal, show_goals, delete_goals, add_multi_goals, update_goal_text, complete_goal, get_user_stats, get_history, check_vow, add_vow, get_users_for_judgement, get_todays_goal

TOKEN = os.getenv("BOT")

if not TOKEN:
    print("Ошибка: Переменная BOT_TOKEN не найдена")
    exit(1)

async def error_handler(update, context):
    logging.error(f"Произошла ошибка: {update}:")

    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    logging.error(tb_string)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not check_vow(user_id):
        manifest_text = (
            f"Приветствую тебя, {update.effective_user.first_name}. ⚔️\n\n"
            "Ты нашел **Synora**. Это не просто бот. Это система твоей личной дисциплины.\n"
            "Входя сюда, ты заключаешь договор с самим собой.\n\n"
            "**ТЫ ОБЕЩАЕШЬ:**\n"
            "• Не сворачивать с выбранного пути.\n"
            "• Делать хотя бы минимум, даже в самые трудные дни.\n"
            "• Быть честным перед собой.\n\n"
            "Готов ли ты взять власть над своей жизнью?\n\n"
            "**while alive: create()** - Пока жив твори."
        )

        keyboard = [[InlineKeyboardButton("Я ПРИНИМАЮ ВЫЗОВ", callback_data="accept_vow")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(manifest_text, reply_markup=reply_markup, parse_mode="Markdown")
        return

    menu_text = (
        "Рад видеть тебя в строю!🚀\n\n"
        "Твой пульт управления:\n"
        "🔵 /start - Меню.\n"
        "🔵 /today - Показать цели на сегодня.\n"
        "🔵 /add - Добавить цель на завтра.\n"
        "🔵 /list - Полный список целей.\n"
        "🔵 /delete - Удалить цель.\n"
        "🔵 /remind - напоминание целей.\n"
        "🔵 /multi - Массовое добавление.\n"
        "🔵 /edit - Отредактировать цель.\n"
        "🔵 /done - Выбрать выполненные цели.\n"
        "🔵 /stats - Список выполненных целей."
    )
    await update.message.reply_text(menu_text)

async def today(update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conn = connect()
    cursor = conn.cursor()
    
    tz = pytz.timezone('Europe/Moscow')
    today_str = datetime.now(tz).strftime("%Y-%m-%d")

    cursor.execute(
        "SELECT id, text FROM goals_v4 WHERE user_id=%s AND date LIKE %s AND is_completed=FALSE",
        (user_id, f"{today_str}%")
    )
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        await update.message.reply_text("На сегодня целей нет. Ты свободен или просто забыл про мечты?")
        return

    keyboard = []
    for goal_id, text in rows:
        keyboard.append([InlineKeyboardButton(f"✅ {text}", callback_data=f"done_{goal_id}")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Твои задачи на сегодня. Нажми на выполненную:", reply_markup=reply_markup)


async def add(update, context):
    user_id = update.message.from_user.id 
    raw_text = " ".join(context.args)

    if not raw_text.strip():
        await update.message.reply_text(
            "Напиши цель после команды.\nПример: /add Пойти в магазин 19:00"
        )
        return
    
    time_pattern = r"(\d{1,2}:\d{2})$"

    match = re.search(time_pattern, raw_text.strip())
    goal_text = raw_text
    found_time = None

    if match:
        found_time = match.group(1)
        goal_text = raw_text.replace(found_time, "").strip()
    
    if found_time:
        try:
            tz = pytz.timezone('Europe/Moscow')
            now = datetime.now(tz)

            t = datetime.strptime(found_time, "%H:%M")
            target_time = tz.localize(datetime(
                now.year, now.month, now.day, t.hour, t.minute
            ))

            if target_time < now:
                target_time += timedelta(days=1)
            diff = (target_time - now).total_seconds()

            logging.info(f">>> Маяк сработает через {diff} секунд")

            context.job_queue.run_once(
                send_reminder_with_text,
                when=diff,
                chat_id=update.message.chat_id,
                name=f"{user_id}_{found_time}",
                data=goal_text
            )
        except Exception as e:
            logging.error(f"Ошибка при установке маяка {e}")

    from program import add_todays_goal
    result = add_todays_goal(user_id, goal_text)

    if found_time:
        result += f"\n⏰ Маяк установлен на {found_time}"
    await update.message.reply_text(result)

async def list_goals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    result = show_goals(user_id)
    
    await update.message.reply_text(result, parse_mode="Markdown")

async def delete(update, context):
    user_id = update.effective_user.id
    user_input = " ".join(context.args)

    result = delete_goals(user_input, user_id)
    await update.message.reply_text(result)

async def send_reminder_with_text(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    await context.bot.send_message(
        chat_id=job.chat_id,
        text=f"⏰ ВРЕМЯ ВЫШЛО!\nТвоя цель: {job.data}\n\nКак успехи? Сделал?"
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
        send_reminder_with_text,
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
            await update.message.reply_text(f"🔥 **Триумф!** 🔥\nЗадача «{task_text}» выполнена. Стоик непоколебим.")
        else:
            await update.message.reply_text("Задача не найдена. Возможно, она уже в прошлом или не твоя.")
     
    except ValueError:
        await update.message.reply_text("ID должен быть числом мой друг.")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    result = get_user_stats(user_id)
    await update.message.reply_text(result)

async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    result = get_history(user_id)
    await update.message.reply_text(result)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    date = query.data

    if date == "accept_vow":
        add_vow(user_id)
        await query.answer("Обещание принято.")
        await query.edit_message_text(
            text="**Обещание зафиксировано.**\n\nТеперь тебе доступны все инструменты системы. Начни с команды /add или посмотри /start.",
            parse_mode="Markdown"
        )
    
    elif date.startswitch("done_"):
        goal_id = int(data.split("_")[1])
        task_text = complete_goal(goal_id, user_id)

    if task_text:
        await query.answer(f"Выполнено: {task_text}")
        await query.edit_message_text(f"🔥 Задача «{task_text}» выполнена. Я рад за тебя, ты продвинулся ближе к своей мечте.")
    else:
        await query.answer("Ошибка: Задача не найдена.")

async def  check_for_judgement(context: ContextTypes.DEFAULT_TYPE):
    tz = pytz.timezone('Europe/Moscow')
    current_time = datetime.now(tz).strftime("%H:%M")
    user_ids = get_users_for_judgement(current_time)

    for uid in user_ids:
        try:
            await context.bot.send_message(
                chat_id=uid,
                text="🚨 Время вышло. Судный Вечер настал. Проверь свои цели через /today."
            )
        except Exception as e:
            logging.error(f"Ошибка при уведомлении {uid}: {e}")

def main():
    create_table()

    app = ApplicationBuilder().token(TOKEN).build()
    
    app.job_queue.run_repeating(check_for_judgement, interval=60, first=10)
    
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
    app.add_handler(CommandHandler("status", stats))
    app.add_handler(CommandHandler("history", history))

    app.add_handler(CallbackQueryHandler(button_handler))

    app.add_error_handler(error_handler)
    print("Synora запущен. Полет нормальный. 🚀")
    app.run_polling()

if __name__ == "__main__":
    main()