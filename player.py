import json
import sys
from items import weapons, potions

class Player:
    def __init__(self,
                 name="Adventurer",
                 hp=100, attack=10,
                 quest=None,
                 defense=5,
                 gold=50,
                 inventory={"Fists": 1},
                 exp=0, level=1,
                 floor=1,
                 weapon="Fists",
                 story_progress=0):
        self.name = name
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.gold = gold
        self.inventory = inventory or {}
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
            print(f"🎉 Level UP! Sekarang Lv {self.level} (+ATK, +HP)")

    def equip_weapon(self, weapon_name):
        if weapon_name not in self.inventory:
            print("⚠️ Senjata tidak ada di inventory.")
            return True

        if weapon_name not in weapons:
            print("⚠️ Senjata tidak dikenal.")
            return True

        if getattr(self, "weapon", None) == weapon_name:
            print("⚠️ Senjata ini sudah digunakan. Gagal equip.")
            return True

        new_weapon_damage = weapons[weapon_name]
        old_weapon_damage = weapons.get(getattr(self, "weapon", ""), 0)

        # Update attack: kurangi damage senjata lama dulu
        self.attack -= old_weapon_damage
        self.attack += new_weapon_damage

        # Update weapon
        self.weapon = weapon_name

        if new_weapon_damage > old_weapon_damage:
            print(f"🗡️ Kamu melengkapi {weapon_name}! ATK meningkat {new_weapon_damage - old_weapon_damage}.")
            return False
        elif new_weapon_damage < old_weapon_damage:
            print(f"🗡️ Kamu melengkapi {weapon_name}. ATK turun {old_weapon_damage - new_weapon_damage}.")
            return False
        else:
            print(f"🗡️ Kamu melengkapi {weapon_name}. ATK tetap sama.")
            return False

    def equip_potion(self, potion_name):
        if potion_name not in self.inventory:
            print("⚠️ Potion tidak ada di inventory.")
            return

        if potion_name not in potions:
            print("⚠️ Potion tidak dikenal.")
            return

        if getattr(self, "potion", None) == potion_name:
            print("⚠️ Potion ini sudah dipilih. Gagal equip.")
            return

        if potion_name == "Health Potion":
            # Gunakan potion: tambah HP
            heal_amount = potions[potion_name]
            self.hp += heal_amount

            # Update potion aktif (opsional, jika ingin tracking)
            self.potion = potion_name

            # Kurangi jumlah potion di inventory
            if isinstance(self.inventory, dict):
                self.inventory[potion_name] -= 1
                if self.inventory[potion_name] <= 0:
                    self.inventory.pop(potion_name)
            elif isinstance(self.inventory, list):
                self.inventory.remove(potion_name)

            print(f"🧪 Kamu menggunakan {potion_name}! HP bertambah {heal_amount}. Saat ini HP: {self.hp}")

    def damage(self, amount):
        amount = amount - self.defense
        if amount >= 1:
            self.hp -= amount
            if self.hp <= 0:
                print("Game Over!")
                sys.exit()
            return amount
        elif amount <= 0:
            print("Damage tertangkis")
            amount = 0
            return amount

    def save(self, filename="save.json"):
        data = self.__dict__
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def load(filename="save.json"):
        try:
            with open(filename, "r") as f:
                data = json.load(f)
                return Player(**data)
        except FileNotFoundError:
            return Player()
