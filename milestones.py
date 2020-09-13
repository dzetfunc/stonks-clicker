from telebot import TeleBot
from telebot.types import Message
import os


def show_milestone(bot: TeleBot, mess: Message, content: str):
    if os.path.exists(os.path.join("content", content + ".png")):
        photo_path = os.path.join("content", content + ".png")
    else:
        photo_path = os.path.join("content", content + ".jpg")

    with open(os.path.join("content", content + ".txt")) as f:
        caption = f.read()

    with open(photo_path, 'rb') as f:
        bot.send_photo(mess.chat.id, photo=f, caption=caption)
