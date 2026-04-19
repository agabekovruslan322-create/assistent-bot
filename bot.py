import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from program import get_todays_goal, add_todays_goal

TOKEN = os.getenv("8680262922:AAHNveyzRB_Gl4ZbFxq1JlceRXf8xQIeK3Q")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("I am your assistant 🚀")

async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = get_todays_goal()
    await update.message.reply_text(result)

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Example: /add Go to gym")
        return

    goal = " ".join(context.args)
    result = add_todays_goal(goal)

    await update.message.reply_text(result)

async def showfile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with open("todays_goal.txt", "r") as f:
            content = f.read()
            await update.message.reply_text(content or "Empty")
    except:
        await update.message.reply_text("File not found")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("today", today))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("file", showfile)) 

    app.run_polling()

if __name__ == "__main__":
    main()