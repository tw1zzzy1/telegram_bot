import os
import datetime

import requests
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler

from processing import processing

token = token = os.getenv("BOT_TOKEN")

activeusers=[]
raspisanie=""

def cleardir():
    folder = "content"
    if not os.path.exists(folder):
        os.makedirs(folder)
    for files in os.listdir(folder):
        file_path = os.path.join(folder, files)
        if os.path.isfile(file_path):
            os.remove(file_path)

def append_active_user(id):
    global activeusers
    activeusers.append(id)
    with open('activeusers.txt', 'a') as f:
        f.write(str(id)+'\n')

def update_raspisanie():
    global raspisanie
    filename = requests.get('https://polytech-rzn.ru/doc/schedule/soln/name.txt').text
    if not os.path.exists(f'content/{filename}'):
        cleardir()
        getfile = requests.get(f'https://polytech-rzn.ru/doc/schedule/soln/file/{filename}')
        with open(f"content/{filename}", 'wb') as f:
            f.write(getfile.content)
        raspisanie = processing(f'content/{filename}')
        return True
    return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in activeusers:
        append_active_user(user_id)
    keyboard = [
        [KeyboardButton("Расписание"), KeyboardButton("Звонки")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(f"Привет, это бот который отправляет расписание группы '516В'",reply_markup=reply_markup)

async def get_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if (update.message.text == "Расписание"):
        if user_id not in activeusers:
            append_active_user(user_id)
        await update.message.reply_text(raspisanie)
    if (update.message.text == "Звонки"):
        if user_id not in activeusers:
            append_active_user(user_id)
        with open("zvonki.jpg", "rb") as photo:
            await update.message.reply_photo(photo)

async def checkfile(context: ContextTypes.DEFAULT_TYPE):
    hour = int(datetime.datetime.now().hour)+1
    if (10<hour<21) or (raspisanie == ""):
        if update_raspisanie() == True:
            await notify(context)

async def notify(context):
    for user in activeusers:
        try:
            await context.bot.send_message(chat_id=user, text="Доступно новое расписание!")
        except:
            pass

def main():
    global app    
    cleardir()
    if not os.path.exists('activeusers.txt'):
        open('activeusers.txt', 'x').close()
    with open('activeusers.txt', 'r') as f:
        for line in f:
            line = line.strip()
            if line.isdigit():
                activeusers.append(int(line))

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), get_schedule))
    app.job_queue.run_repeating(checkfile, interval=2700, first=10)

    app.run_polling()
main()
