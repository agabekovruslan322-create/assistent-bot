import requests

print(requests.get("https://api.telegram.org").status_code)

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8680262922:AAHNveyzRB_Gl4ZbFxq1JlceRXf8xQIeK3Q"

from program import get_todays_goal, add_todays_goal
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "I am your assistant 🚀\n\n"
        "Commands:\n"
        "/today - show todays goals\n"
        "/add - add todays goal\n"
    )
    await update.message.reply_text("I am your assistant 🚀")

async def today(update, context):
    result = get_todays_goal()
    await update.message.reply_text(result)

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("today", today))

app.run_polling()