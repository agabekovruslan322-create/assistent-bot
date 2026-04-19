import requests

print(requests.get("https://api.telegram.org").status_code)

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from program import get_todays_goal, add_todays_goal

TOKEN = "8680262922:AAHNveyzRB_Gl4ZbFxq1JlceRXf8xQIeK3Q"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "I am your assistant 🚀\n\n"
        "Commands:\n"
        "/today - show todays goals\n"
        "/add - add todays goal\n"
    )
    await update.message.reply_text(text)

async def today(update, context: ContextTypes.DEFAULT_TYPE):
    result = get_todays_goal()
    await update.message.reply_text(result)

async def add(update, context):
    if not context.args:
        await update.message.reply_text(
            "Напиши цель после команды.\nПример: /add Go to gym"
        )
        return

    goal = " ".join(context.args)

    result = add_todays_goal(goal)
    await update.message.reply_text(result)
    
    async def showfile(update, context):
        try:
            with open("todays_goal.txt", "r") as f:
                content = f.read()
                await update.message.reply_text(content or "Empty")
        except:
            await update.message.reply_text("File not found")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("file", showfile))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("today", today))
    app.add_handler(CommandHandler("add", add))

    app.run_polling()

if __name__ == "__main__":
    main()