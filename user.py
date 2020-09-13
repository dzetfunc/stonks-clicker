import time
import json


class UserStats:
    def __init__(self, user_id):
        self.user_id = user_id
        self.noobs = []
        self.noob_level = 1
        self.advanced = []
        self.tiers = {i: 0 for i in range(3, 9)}
        self.tier_level = {i: 1 for i in range(3, 9)}
        self.tier_available = {i: False for i in range(3, 9)}
        self.advanced_level = 1
        self.total_stonks = 1
        self.shop_level = 2
        self.calc_sps()
        self.last_time_asked = time.time()
        self.displaying = False
        with open("./milestones.json") as f:
            self.milestones = dict((int(key), value) for key, value in json.load(f).items())
        self.milestones_shown = set()
        self.name_surname = ""
        with open("./tier_names.json") as f:
            self.tier_shop_names = dict((int(key), value) for key, value in json.load(f).items())

    def calc_sps(self):
        self.sps = 1 + len(self.noobs) * 1 * self.noob_level * 0.75 \
                   + len(self.advanced) * 4 * self.advanced_level

    def set_name_surname(self, name: str):
        self.name_surname = name

    def update_tier_available(self):
        for nstonks, name in self.milestones.items():
            ll = name.split("tier")
            if len(ll) <= 1:
                continue
            tier = int(ll[1][0])
            if not self.tier_available[tier] and self.total_stonks >= nstonks:
                self.tier_available[tier] = True

    def update_shop(self) -> str:
        shop = """
Нанять Новичка (ава - stonk man с нуглерской шапочкой).
Петя из соседнего подъезда, который тоже захотел поднять денег побыстрее -- 20 стонксов

Нанять Читателя Тинькофф Журнала -- 1000 стониксов
Слишком много читает тинькофф журнал, программист, о котором говорила психолог Вероника Степанова
Кодовое имя -- Вася
\n"""
        for tier in range(3, 9):
            if self.tier_available[tier]:
                shop += self.tier_shop_names[tier] + "\n"
        return shop
