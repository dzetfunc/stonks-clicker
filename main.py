import telebot
import os
from telebot.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
import requests
import time
import multiprocessing as mp
from user import UserStats
from showcases import *
from milestones import show_milestone
from leaderboard import Leaderboard

mess_db = {}
users_db = {}

try:
    token = os.environ["TELEBOT_TOKEN"]
except KeyError:
    raise RuntimeError("Environment variable TELEBOT_TOKEN must be specified")
bot = telebot.TeleBot(token, threaded=True, num_threads=12)

STATUS_TEMPLATE = """
Stonks: {0},
Нубы: {1},
Увровень нубов: {2},
Крутые брокеры: {3},
Уровень крутых брокеров: {4}
Доход в секунду: {5}

**Магазин**:
{6}

**Ачивки и сюжетка**:
100000 стонксов,
500000 стонксов,
1000000 стонксов,
2000000 стонксов,
5000000 стонксов
"""


with open("./content/welcome.txt") as f:
    WELCOME_MESSAGE = f.read()


with open("./content/help.txt") as f:
    HELP_MESSAGE = f.read()

def make_leaderboard():
    res = Leaderboard(users_db, bot).dump()
    return res  # "1. Ruslan Khaidurov: {}".format(list(users_db.values())[0].total_stonks)

def update_user_wealth(user, cost, mess, tier):
    if user.total_stonks < cost:
        bot.reply_to(mess, "Недостаточно Стонксов!")
    else:
        if tier == 2:
            if len(user.advanced) == 0:
                show_milestone(bot, mess, "vasya_noob")
            user.advanced.append(1)
        elif tier == 1:
            if len(user.noobs) == 0:
                show_milestone(bot, mess, "petya_noob")
            user.noobs.append(1)
        else:
            user.tiers[tier] += 1
        user.total_stonks -= cost
        bot.reply_to(mess, "Вы купили нового брокера ранга {}!".format(tier))

@bot.message_handler(commands=["help"])
def helpp(mess: Message):
    ss = '{"inline_keyboard":[[{"text":"supa", "callback_data": "fig"},{"text":"mario", "callback_data": "nafig"}]]}'
    bot.send_message(mess.chat.id, "What should I do?", reply_markup=ss)


@bot.message_handler(commands=["start"])
def welcome(mess: Message):
    bot.send_message(mess.chat.id, WELCOME_MESSAGE)

@bot.message_handler(content_types=["text"])
def handle_sticker(mess: Message):
    # INIT USER
    if mess.chat.id not in users_db:
        users_db[mess.chat.id] = UserStats(mess.chat.id)
        users_db[mess.chat.id].set_name_surname(mess.from_user.first_name + " " + mess.from_user.last_name)
    user = users_db[mess.chat.id]

    # STOP LIVE UPDATES
    if mess.text.lower() == "stop displaying":
        okay_sure_msg = bot.reply_to(mess, "Okay, Sure!")
        mess_db[mess.chat.id] = okay_sure_msg.message_id
        if user.displaying:
            user.last_time_asked = time.time()
            user.displaying = False

    # STATUS
    elif mess.text.lower() == "status" or mess.text.lower() == "статус":
        okay_sure_msg = bot.reply_to(mess, "Showing you the status")
        mess_db[mess.chat.id] = okay_sure_msg.message_id
        if not user.displaying:
            user.total_stonks += (time.time() - user.last_time_asked) * user.sps
            user.displaying = True
        cur_msg = okay_sure_msg.message_id
        before = time.time()
        while True:
            if mess_db[mess.chat.id] != cur_msg:
                break
            try:
                bot.edit_message_text(
                    STATUS_TEMPLATE.format(
                        user.total_stonks,
                        len(user.noobs),
                        user.noob_level,
                        len(user.advanced),
                        user.advanced_level,
                        user.sps,
                        user.update_shop()
                    ),
                    mess.chat.id,
                    cur_msg,
                )
            except telebot.apihelper.ApiTelegramException:
                bot.send_message(mess.chat.id, "МЫ ЗАКОЛЕБАЛИСЬ ДАВАТЬ ВАМ БАНКОВСКИЕ ВЫПИСКИ! ПОЖАЛУЙСТА СПРОСИТЕ ПОПОЗЖЕ!")
                user.displaying = False
                break
            time.sleep(10)
            user.total_stonks += user.sps * (time.time() - before)
            before = time.time()
            while user.total_stonks > min(user.milestones.keys()):
                content = user.milestones[min(user.milestones.keys())]
                if content not in user.milestones_shown:
                    show_milestone(bot, mess, content)
                    user.milestones_shown.add(content)
                user.update_tier_available()
                del user.milestones[min(user.milestones.keys())]

    # NEW WORKERS
    # Tier 1
    elif mess.text.lower() == "купить петю":
        update_user_wealth(user, 20, mess, 1)

    # Tier 2
    elif mess.text.lower() == "купить васю":
        update_user_wealth(user, 1000, mess, 2)

    # Tier 3
    elif mess.text.lower() == "купить брокера":
        if user.tier_available[3]:
            update_user_wealth(user, 200000, mess, 3)
        else:
            bot.reply_to(mess, "Этот тип работяги ещё не разблокирован!")

    # UPGRADES
    # Tier 1
    elif mess.text.lower() == "апгрейд нуба":
        if user.total_stonks < 10000:
            bot.reply_to(mess, "Недостаточно Стонксов!")
        else:
            bot.reply_to(mess, "Вы апгрейднули нуба!")
            user.total_stonks -= 10000
            user.noob_level += 1
    # Tier 2
    elif mess.text.lower() == "апгрейд крутого брокера":
        if user.total_stonks < 100000:
            bot.reply_to(mess, "Недостаточно Стонксов!")
        else:
            bot.reply_to(mess, "Вы апгрейднули нуба!")
            user.total_stonks -= 100000
            user.advanced_level += 1

    # Лидерборд
    elif mess.text.lower() == "лидерборд" or mess.text.lower() == "leaderboard":
        bot.reply_to(mess, make_leaderboard())

    else:
        return
    user.calc_sps()


if __name__ == "__main__":
    bot.polling()
