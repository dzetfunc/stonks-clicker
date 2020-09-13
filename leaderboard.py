import telebot
from user import UserStats
from typing import Dict
from collections import Counter


class Leaderboard:
    def __init__(self, users_db, bot):
        # This dict contains
        self.users: Dict[int, UserStats] = users_db
        self.bot = bot

    def dump(self) -> str:
        best_10 = Counter({user.name_surname: user.total_stonks for user in self.users.values()}).most_common(10)
        final_string = ""
        for i, (name, nstonks) in enumerate(best_10):
            final_string += f"{i + 1}. {name}: {nstonks}\n"
        return final_string
