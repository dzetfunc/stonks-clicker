from telebot import TeleBot
from telebot.types import Message
import os


def show_milestone(bot: TeleBot, mess: Message, content: str):
    photo_exist = false
    if os.path.exists(os.path.join("content", content + ".png")):
        photo_path = os.path.join("content", content + ".png")
        photo_exist = true
    if os.path.exists(os.path.join("content", content + ".jpg")):
        photo_path = os.path.join("content", content + ".jpg")
        photo_exist = true

    with open(os.path.join("content", content + ".txt")) as f:
        caption = f.read()

    if photo_exist:
        with open(photo_path, 'rb') as f:
            bot.send_photo(mess.chat.id, photo=f, caption=caption)
