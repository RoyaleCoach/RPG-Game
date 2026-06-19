import json
import os
import sys
from .items import weapons, potions

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )

SAVE_DIR = os.path.join(BASE_DIR, "save")

class Player:
    def __init__(
        self,
        name="Adventurer",
        hp=100,
        attack=10,
        quest=None,
        defense=5,
        gold=50,
        inventory=None,
        exp=0,
        level=1,
        floor=1,
        weapon="Fists",
        story_progress=0
    ):
        self.name = name
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.gold = gold
        self.inventory = inventory if inventory is not None else {"Fists": 1}
        self.exp = exp
        self.level = level
        self.floor = floor
        self.weapon = weapon
        self.story_progress = story_progress
        self.quest = quest or []

    def show_status(self):
        print(f"\n=== {self.name} (Lv {self.level}) ===")
        print(f"HP: {self.hp}")
        print(f"ATK: {self.attack} | DEF: {self.defense}")
        print(f"Weapon: {self.weapon}")
        print(f"EXP: {self.exp}/100 | Floor: {self.floor}")
        print(f"Gold: {self.gold}")

    def gain_exp(self, amount):
        self.exp += amount
        print(f"✨ Kamu mendapat {amount} EXP!")

        if self.exp >= 100:
            self.exp -= 100
            self.level += 1
            self.attack += 2
            self.hp += 20

            print(
                f"🎉 Level UP! "
                f"Sekarang Lv {self.level} (+ATK, +HP)"
            )

    def equip_weapon(self, weapon_name):
        if weapon_name not in self.inventory:
            print("⚠️ Senjata tidak ada di inventory.")
            return True

        if weapon_name not in weapons:
            print("⚠️ Senjata tidak dikenal.")
            return True

        if self.weapon == weapon_name:
            print("⚠️ Senjata ini sudah digunakan.")
            return True

        new_damage = weapons[weapon_name]
        old_damage = weapons.get(self.weapon, 0)

        self.attack -= old_damage
        self.attack += new_damage

        self.weapon = weapon_name

        print(f"🗡️ Kamu melengkapi {weapon_name}!")
        return False

    def equip_potion(self, potion_name):
        if potion_name not in self.inventory:
            print("⚠️ Potion tidak ada di inventory.")
            return

        if potion_name not in potions:
            print("⚠️ Potion tidak dikenal.")
            return

        heal_amount = potions[potion_name]
        self.hp += heal_amount
        self.inventory[potion_name] -= 1

        if self.inventory[potion_name] <= 0:
            self.inventory.pop(potion_name)

        print(
            f"🧪 Kamu menggunakan {potion_name}! "
            f"HP bertambah {heal_amount}."
        )

    def damage(self, amount):
        amount -= self.defense

        if amount <= 0:
            print("Damage tertangkis")
            return 0

        self.hp -= amount

        if self.hp <= 0:
            print("Game Over!")
            sys.exit()

        return amount

    def save(self, filename="save.json"):
        os.makedirs(SAVE_DIR, exist_ok=True)

        path = os.path.join(
            SAVE_DIR,
            filename
        )

        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                self.__dict__,
                f,
                indent=4,
                ensure_ascii=False
            )

    @staticmethod
    def load(filename="save.json"):
        path = os.path.join(
            SAVE_DIR,
            filename
        )

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            return Player(**data)

        except FileNotFoundError as e:
            print("LOAD ERROR:", e)
            return Player()