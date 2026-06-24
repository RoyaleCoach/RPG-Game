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
        armor=None,
        story_progress=0,
        completed_quests=None,
        enemies_killed=0,
        puzzles_solved=0,
        boss_progress=0,
        dungeon_runs=0,
        items=None
    ):
        self.name = name

        self.items = items or {}

        self.weapons = self.items.get(
            "weapons",
            {}
        )

        self.potions = self.items.get(
            "potions",
            {}
        )

        self.defends = self.items.get(
            "defends",
            {}
        )

        self._hp = hp
        self._base_attack = attack
        self._base_defense = defense

        self.gold = gold

        self.inventory = (
            inventory
            if inventory is not None
            else {"Fists": 1}
        )

        self.exp = exp
        self.level = level
        self.floor = floor

        self.weapon = weapon
        self.armor = armor

        self.story_progress = story_progress
        self.quest = quest or []

        self.enemies_killed = enemies_killed
        self.puzzles_solved = puzzles_solved

        self.completed_quests = (
            completed_quests or []
        )

        self.boss_progress = boss_progress
        self.dungeon_runs = dungeon_runs

    # ==========================
    # Properties
    # ==========================

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        self._hp = min(
            max(0, value),
            self.max_hp
        )

    @property
    def max_hp(self):
        return self.level * 100

    @property
    def attack(self):
        weapon_bonus = 0

        if self.weapon in self.weapons:
            weapon_bonus = (
                self.weapons[self.weapon]["attack"]
            )

        return self._base_attack + weapon_bonus

    @property
    def defense(self):
        armor_bonus = 0

        if self.armor in self.defends:
            armor_bonus = (
                self.defends[self.armor]["defense"]
            )

        return self._base_defense + armor_bonus

    @property
    def is_alive(self):
        return self.hp > 0

    @property
    def exp_to_next_level(self):
        return max(0, 100 - self.exp)

    # ==========================
    # Display
    # ==========================

    def show_status(self):
        print(f"\n=== {self.name} (Lv {self.level}) ===")
        print(f"HP: {self.hp}/{self.max_hp}")
        print(f"ATK: {self.attack}")
        print(f"DEF: {self.defense}")
        print(f"Weapon: {self.weapon}")
        print(f"Armor : {self.armor or 'None'}")
        print(
            f"EXP: {self.exp}/100 "
            f"(Need {self.exp_to_next_level})"
        )
        print(f"Floor: {self.floor}")
        print(f"Gold: {self.gold}")

    # ==========================
    # Experience
    # ==========================

    def gain_exp(self, amount):
        self.exp += amount

        print(
            f"✨ Kamu mendapat "
            f"{amount} EXP!"
        )

        while self.exp >= 100:

            self.exp -= 100
            self.level += 1

            self._base_attack += 2

            self.hp = self.max_hp

            print(
                f"🎉 Level UP! "
                f"Sekarang Lv {self.level}"
            )

    # ==========================
    # Equipment
    # ==========================

    def equip_weapon(self, weapon_name):

        if weapon_name not in self.inventory:
            print("⚠️ Senjata tidak ada di inventory.")
            return True

        if weapon_name not in self.weapons:
            print("⚠️ Senjata tidak dikenal.")
            return True

        if self.weapon == weapon_name:
            print("⚠️ Senjata ini sudah digunakan.")
            return True

        self.weapon = weapon_name

        print(
            f"🗡️ Kamu melengkapi "
            f"{weapon_name}!"
        )

        return False

    def equip_defense(self, armor_name):

        if armor_name not in self.inventory:
            print("⚠️ Armor tidak ada di inventory.")
            return True

        if armor_name not in self.defends:
            print("⚠️ Armor tidak dikenal.")
            return True

        if self.armor == armor_name:
            print("⚠️ Armor ini sudah digunakan.")
            return True

        self.armor = armor_name

        print(
            f"🛡️ Kamu melengkapi "
            f"{armor_name}!"
        )

        return False

    # ==========================
    # Potions
    # ==========================

    def equip_potion(self, potion_name):

        if potion_name not in self.inventory:
            print("⚠️ Potion tidak ada di inventory.")
            return

        if potion_name not in self.potions:
            print("⚠️ Potion tidak dikenal.")
            return

        heal_amount = (
            self.potions[potion_name]["effect"]
        )

        self.hp += heal_amount

        self.inventory[potion_name] -= 1

        if self.inventory[potion_name] <= 0:
            self.inventory.pop(potion_name)

        print(
            f"🧪 Kamu menggunakan "
            f"{potion_name}! "
            f"HP bertambah "
            f"{heal_amount}."
        )

    # ==========================
    # Combat
    # ==========================

    def damage(self, amount, guard):

        final_damage = max(
            1,
            amount - guard
        )

        self.hp -= final_damage

        if not self.is_alive:
            print("💀 Game Over!")

        return final_damage

    # ==========================
    # Save Data
    # ==========================

    def to_dict(self):
        return {
            "name": self.name,
            "hp": self.hp,
            "attack": self._base_attack,
            "defense": self._base_defense,
            "gold": self.gold,
            "inventory": self.inventory,
            "exp": self.exp,
            "level": self.level,
            "floor": self.floor,
            "weapon": self.weapon,
            "armor": self.armor,
            "story_progress": self.story_progress,
            "quest": self.quest,
            "enemies_killed": self.enemies_killed,
            "puzzles_solved": self.puzzles_solved,
            "completed_quests": self.completed_quests,
            "boss_progress": self.boss_progress,
            "dungeon_runs": self.dungeon_runs
        }