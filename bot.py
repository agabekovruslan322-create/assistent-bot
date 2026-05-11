import re
import os
import requests
import pytz
import logging
import traceback
from datetime import datetime, timedelta

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, 
    CommandHandler, 
    ContextTypes, 
    CallbackQueryHandler, 
    ConversationHandler, 
    MessageHandler, 
    filters
)

# Импорты из файлов
from database import create_table, connect, get_or_create_settings, update_user_time
from program import (
    get_todays_goal, add_todays_goal, show_goals, delete_goals, 
    add_multi_goals, update_goal_text, complete_goal, 
    get_user_stats, get_history, check_vow, add_vow, get_users_for_judgement
)

# Константы для диалогов
WAITING_FOR_GOAL = 1

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

TOKEN = os.getenv("BOT")

if not TOKEN:
    print("Ошибка: Переменная BOT_TOKEN не найдена")
    exit(1)

#  ОБРАБОТКА ОШИБОК
async def error_handler(update, context):
    logging.error(f"Произошла ошибка: {update}:")
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)
    logging.error(tb_string)

# --- ГЛАВНЫЕ КОМАНДЫ ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not check_vow(user_id):
        manifest_text = (
            f"Приветствую тебя, {update.effective_user.first_name}. ⚔️\n\n"
            "Ты нашел **Synora**. Это система твоей личной дисциплины.\n"
            "Входя сюда, ты заключаешь договор с самим собой.\n\n"
            "**ТЫ ОБЕЩАЕШЬ:**\n"
            "• Не сворачивать с выбранного пути.\n"
            "• Быть честным перед собой.\n\n"
            "Готов ли ты взять власть над своей жизнью?"
        )
        keyboard = [[InlineKeyboardButton("Я ПРИНИМАЮ ВЫЗОВ", callback_data="accept_vow")]]
        await update.message.reply_text(manifest_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return
    
    main_menu_keyboard = [
        ['⚔️ Мои цели', '📊 Статистика'],
        ['📜 История', '📝 Новая задача'],
        ['⚙️ Настройки'] 
    ]
    await update.message.reply_text(
        "Synora активна. 🚀\nВыбирай действие:",
        reply_markup=ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True)
    )

# --- ЛОГИКА ЦЕЛЕЙ ---
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
        await update.message.reply_text("На сегодня целей нет. Отдыхаешь или забыл про мечты?")
        return

    keyboard = [[InlineKeyboardButton(f"✅ {text}", callback_data=f"done_{goal_id}")] for goal_id, text in rows]
    await update.message.reply_text("Твои задачи на сегодня:", reply_markup=InlineKeyboardMarkup(keyboard))

async def new_task_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Слушаю тебя. Напиши цель (можно со временем, например: 'Йога 07:00')")
    return WAITING_FOR_GOAL

async def new_task_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    goal_text = update.message.text
    result = add_todays_goal(user_id, goal_text)
    await update.message.reply_text(f"✅ {result}")
    return ConversationHandler.END

# --- НАСТРОЙКИ ---
async def settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    settings = get_or_create_settings(user_id)
    current_time = settings[0] if settings else "22:00"

    text = (
        "⚙️ **НАСТРОЙКИ**\n\n"
        f"Текущее время Судного Вечера: `{current_time}`\n\n"
        "Чтобы изменить время, напиши команду: \n`/set_time ЧЧ:ММ`"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def set_time_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not context.args:
        await update.message.reply_text("Пример: `/set_time 21:30`", parse_mode="Markdown")
        return

    new_time = context.args[0]
    if not re.match(r"^\d{2}:\d{2}$", new_time):
        await update.message.reply_text("❌ Неверный формат. Нужно ЧЧ:ММ")
        return

    update_user_time(user_id, new_time)
    await update.message.reply_text(f"✅ Время отчета изменено на {new_time}")

# --- ОБРАБОТКА КНОПОК ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    callback_data = query.data

    if callback_data == "accept_vow":
        add_vow(user_id)
        await query.answer("Обещание принято.")
        await query.edit_message_text("**Обещание зафиксировано.**\nИспользуй меню для работы.", parse_mode="Markdown")

    main_menu_keyboard = [['⚔️ Мои цели', '📊 Статистика'], ['📜 История', '📝 Новая задача'], ['⚙️ Настройки']]
    await context.bot.send_message(
        chat_id=user_id,
        text="Synora активна. Время действовать! 🚀",
        reply_markup=ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True)
    )
    elif callback_data.startswith("done_"):
        goal_id = int(callback_data.split("_")[1])
        task_text = complete_goal(goal_id, user_id)
        if task_text:
            await query.answer(f"Выполнено!")
            await query.edit_message_text(f"🔥 Задача «{task_text}» выполнена. Красава!")
        else:
            await query.answer("Ошибка: Задача не найдена.")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    result = get_user_stats(user_id)
    await update.message.reply_text(result)

async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    result = get_history(user_id)
    await update.message.reply_text(result)

async def delete(update, context):
    user_id = update.effective_user.id
    user_input = " ".join(context.args)
    result = delete_goals(user_input, user_id)
    await update.message.reply_text(result)

# Логика напоминаний (Маяки)
async def send_reminder_with_text(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    await context.bot.send_message(
        chat_id=job.chat_id,
        text=f"⏰ ВРЕМЯ ВЫШЛО!\nТвоя цель: {job.data}\n\nКак успехи? Сделал?"
    )

async def remind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Пример: /remind 10m или /remind 21:00")
        return

# --- СИСТЕМНЫЕ ФУНКЦИИ ---
async def check_for_judgement(context: ContextTypes.DEFAULT_TYPE):
    tz = pytz.timezone('Europe/Moscow')
    current_time = datetime.now(tz).strftime("%H:%M")
    user_ids = get_users_for_judgement(current_time)

    for uid in user_ids:
        try:
            await context.bot.send_message(chat_id=uid, text="🚨 Судный Вечер! Проверь цели через /today.")
        except Exception as e:
            logging.error(f"Ошибка уведомления {uid}: {e}")
async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Возвращаемся в меню.", reply_markup=ReplyKeyboardMarkup([
        ['⚔️ Мои цели', '📊 Статистика'], ['📜 История', '📝 Новая задача'], ['⚙️ Настройки']
    ], resize_keyboard=True))
    return ConversationHandler.END
    
# --- ОСНОВНОЙ ЗАПУСК ---
def main():
    create_table()
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.job_queue.run_repeating(check_for_judgement, interval=60, first=10)
    
    # Режим диалога
    new_task_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^📝 Новая задача$"), new_task_start)],
        states={
            WAITING_FOR_GOAL: [
                MessageHandler(filters.Regex("^(⚔️ Мои цели|📊 Статистика|📜 История|⚙️ Настройки)$"), cancel_handler),
                MessageHandler(filters.TEXT & ~filters.COMMAND, new_task_save)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_handler)],
        allow_reentry=True
    )
    
    app.add_handler(new_task_handler)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("set_time", set_time_handler))
    
    # Кнопки меню
    app.add_handler(MessageHandler(filters.Text("⚔️ Мои цели"), today))
    app.add_handler(MessageHandler(filters.Text("📊 Статистика"), stats))
    app.add_handler(MessageHandler(filters.Text("📜 История"), history))
    app.add_handler(MessageHandler(filters.Text("⚙️ Настройки"), settings_menu)) 

    # Команды
    app.add_handler(CommandHandler("today", today))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("history", history))
    app.add_handler(CommandHandler("delete", delete))

    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_error_handler(error_handler)

    print("Synora запущен. 🚀")
    app.run_polling()

if __name__ == "__main__":
    main()