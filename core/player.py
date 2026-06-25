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
        items=None,
        mana=None,
        learned_spells=None
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

        self._mana = (
            mana
            if mana is not None
            else self.max_mana
        )

        self.learned_spells = (
            learned_spells or []
        )

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

    @property
    def max_mana(self):
        return self.level * 10

    @property
    def mana(self):
        return self._mana

    @mana.setter
    def mana(self, value):
        self._mana = min(
            max(0, value),
            self.max_mana
        )

    # ==========================
    # Display
    # ==========================

    def show_status(self):
        print(f"\n=== {self.name} (Lv {self.level}) ===")
        print(f"HP: {self.hp}/{self.max_hp}")
        print(f"Mana: {self.mana}/{self.max_mana}")
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
            f"✨ You gained "
            f"{amount} EXP!"
        )

        while self.exp >= 100:

            self.exp -= 100
            self.level += 1

            self._base_attack += 2

            self.hp = self.max_hp
            self.mana = self.max_mana

            print(
                f"🎉 Level UP! "
                f"Now Lv {self.level}"
            )

    # ==========================
    # Equipment
    # ==========================

    def equip_weapon(self, weapon_name):
        weapon_name = weapon_name.lower()
        matched_weapon = None
        
        for weapon in self.weapons:
            if weapon.lower() == weapon_name:
                matched_weapon = weapon
                break

        if matched_weapon is None:
            print("⚠️ Unknown weapon.")
            return True

        if matched_weapon not in self.inventory:
            print("⚠️ Weapon not in inventory.")
            return True

        if self.weapon == matched_weapon:
            print("⚠️ This weapon is already equipped.")
            return True

        self.weapon = matched_weapon

        print(
            f"🗡️ You equipped "
            f"{matched_weapon}!"
        )

        return False

    def equip_defense(self, armor_name):

        armor_name = armor_name.lower()

        matched_armor = None

        for armor in self.defends:
            if armor.lower() == armor_name:
                matched_armor = armor
                break

        if matched_armor is None:
            print("⚠️ Unknown armor.")
            return True

        if matched_armor not in self.inventory:
            print("⚠️ Armor not in inventory.")
            return True

        if self.armor == matched_armor:
            print("⚠️ This armor is already equipped.")
            return True

        self.armor = matched_armor

        print(
            f"🛡️ You equipped "
            f"{matched_armor}!"
        )

        return False

    # ==========================
    # Potions
    # ==========================

    def equip_potion(self, potion_name):

        potion_name = potion_name.lower()

        matched_potion = None

        for potion in self.potions:
            if potion.lower() == potion_name:
                matched_potion = potion
                break

        if matched_potion is None:
            print("⚠️ Unknown potion.")
            return

        if matched_potion not in self.inventory:
            print("⚠️ Potion not in inventory.")
            return

        heal_amount = (
            self.potions[matched_potion]["effect"]
        )

        self.hp += heal_amount

        self.inventory[matched_potion] -= 1

        if self.inventory[matched_potion] <= 0:
            self.inventory.pop(matched_potion)

        print(
            f"🧪 You used "
            f"{matched_potion}! "
            f"HP increased by "
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
            "dungeon_runs": self.dungeon_runs,
            "mana": self.mana,
            "learned_spells": self.learned_spells
        }