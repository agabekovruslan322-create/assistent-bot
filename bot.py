import re
import os
import pytz
import logging
import traceback
from datetime import datetime

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
from database import create_table, get_or_create_settings, update_user_time
from program import (
    add_todays_goal, delete_goals, 
    complete_goal, get_user_stats, get_history, 
    check_vow, add_vow, get_users_for_judgement, get_today_goals, 
    get_goals_for_reminder,
    mark_goal_as_reminded, get_overdue_goals
)

# Константы для диалогов
WAITING_FOR_GOAL = 1

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logging.getLogger('apscheduler').setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger('apscheduler.executors.default').setLevel(logging.WARNING)

TOKEN = os.getenv("BOT_TOKEN")

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

    if not await require_vow(update):
        return

    user_id = update.effective_user.id

    rows = get_today_goals(user_id)

    if not rows:
        await update.message.reply_text("На сегодня целей нет. Отдыхаешь или забыл про мечты?")
        return

    keyboard = [[InlineKeyboardButton(f"✅ {text}", callback_data=f"done_{goal_id}")] for goal_id, text in rows]
    await update.message.reply_text("Твои задачи на сегодня:", reply_markup=InlineKeyboardMarkup(keyboard))

async def new_task_start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await require_vow(update):
        return

    await update.message.reply_text("Слушаю тебя. Напиши цель (можно со временем, например: 'Йога 07:00')")
    return WAITING_FOR_GOAL

async def new_task_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    result = add_todays_goal(user_id, text)
    await update.message.reply_text(f"✅ {result}")
    return ConversationHandler.END

# --- НАСТРОЙКИ ---
async def settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await require_vow(update):
        return


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
        get_or_create_settings(user_id)
        await query.answer("Обещание принято.")
        await query.edit_message_text("**Обещание зафиксировано.**\nИспользуй меню для работы.", parse_mode="Markdown")

        main_menu_keyboard = [
            ['⚔️ Мои цели', '📊 Статистика'], 
            ['📜 История', '📝 Новая задача'], 
            ['⏳ Просрочено', '⚙️ Настройки']
            ]
        await context.bot.send_message(
            chat_id=user_id,
            text="Synora активна. Время действовать! 🚀",
            reply_markup=ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True)
        )

    elif callback_data.startswith("done_"):
        goal_id = int(callback_data.split("_")[1])
        task_text = complete_goal(goal_id, user_id)
        if task_text:
            await query.answer("Выполнено!")
            await query.edit_message_text(f"🔥 Задача «{task_text}» выполнена. Красава!")
        else:
            await query.answer("Ошибка: Задача не найдена.")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_vow(update):
        return 

    user_id = update.effective_user.id
    result = get_user_stats(user_id)
    await update.message.reply_text(result)

async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await require_vow(update):
        return

    user_id = update.effective_user.id
    result = get_history(user_id)
    await update.message.reply_text(result)

async def delete(update, context):

    if not await require_vow(update):
        return

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
    text = update.message.text

    await update.message.reply_text("Возвращаемся в меню...")

    if text == "⚙️ Настройки":
        return await settings_menu(update, context)
    elif text == "⚔️ Мои цели":
        return await today(update, context)
    elif text == "📊 Статистика":
        return await stats(update, context)
    elif text == "📜 История":
        return await history(update, context)
    elif text == "⏳ Просрочено":
        return await overdue(update, context)

    return ConversationHandler.END

async def require_vow(update):
    user_id = update.effective_user.id

    if not check_vow(user_id):
        await update.message.reply_text(
            "⚔️ Сначала прими вызов через /start"
        )
        return False

    return True

async def check_reminders(context: ContextTypes.DEFAULT_TYPE):
    tz = pytz.timezone('Europe/Moscow')
    current_time = datetime.now(tz).strftime("%H:%M")

    goals = get_goals_for_reminder(current_time)

    for goal_id, user_id, text in goals:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"⏰ Напоминание!\n\nТвоя цель: {text}"
        )
        mark_goal_as_reminded(goal_id)

async def overdue(update, context: ContextTypes.DEFAULT_TYPE):

    if not await require_vow(update):
        return
    
    user_id = update.effective.user_id
    rows = get_overdue_goals(user_id)

    if not rows:
        await update.message.reply_text(
            "Просроченных целей нет. Хороший знак. ⚔️"
        )
        return
    text = "⏳ Просроченные цели:\n\n"

    for goal_id, goal_text in rows:
        text += f"• {goal_text}\n"

    await update.message.reply_text(text)

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
                MessageHandler(filters.Regex("^(⚔️ Мои цели|📊 Статистика|📜 История|⚙️ Настройки|⏳ Просрочено)$"), cancel_handler),
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
    app.add_handler(MessageHandler(filters.Text("⏳ Просрочено"), overdue))

    # Команды
    app.add_handler(CommandHandler("today", today))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("history", history))
    app.add_handler(CommandHandler("delete", delete))

    app.job_queue.run_repeating(check_reminders, interval=60, first=10)

    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_error_handler(error_handler)

    logging.info("Synora запущен. 🚀")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()