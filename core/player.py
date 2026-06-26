from __future__ import annotations


class Player:
    """Represents the player character and all associated state."""

    # Experience required to level up (constant for now, easy to change later)
    EXP_PER_LEVEL = 100
    HP_PER_LEVEL = 100
    MANA_PER_LEVEL = 10
    ATTACK_BONUS_PER_LEVEL = 2

    def __init__(
        self,
        name: str = "Adventurer",
        hp: int = 100,
        attack: int = 10,
        defense: int = 5,
        gold: int = 50,
        mana: int | None = None,
        level: int = 1,
        exp: int = 0,
        floor: int = 1,
        weapon: str = "Fists",
        armor: str | None = None,
        inventory: dict | None = None,
        learned_spells: list | None = None,
        skill_points: int = 0,
        unlocked_skills: list | None = None,
        quest: list | None = None,
        completed_quests: list | None = None,
        story_progress: int = 0,
        enemies_killed: int = 0,
        puzzles_solved: int = 0,
        boss_progress: int = 0,
        dungeon_runs: int = 0,
        luck: int = 0,
        reputation: int = 0,
        last_event: str | None = None,
        skip_next_battle: bool = False,
        skip_next_trap: bool = False,
        skip_next_boss_preparation: bool = False,
        items: dict | None = None,
    ):
        # ── Item catalog (injected from game data) ───────────────────────────
        self.initialize_items(items or {})

        # ── Core stats ───────────────────────────────────────────────────────
        self.name = name
        self._base_attack = attack
        self._base_defense = defense
        self._max_mana_bonus = 0
        self.level = level
        self._hp = min(hp, self.max_hp)
        self._mana = mana if mana is not None else self.max_mana

        # ── Resources ────────────────────────────────────────────────────────
        self.gold = gold
        self.exp = exp

        # ── Location ─────────────────────────────────────────────────────────
        self.floor = floor

        # ── Equipment & inventory ────────────────────────────────────────────
        self.weapon = weapon
        self.armor = armor
        self.inventory = inventory if inventory is not None else {"Fists": 1}

        # ── Spells & skills ──────────────────────────────────────────────────
        self.learned_spells = learned_spells or []
        self.skill_points = skill_points
        self.unlocked_skills = unlocked_skills or []

        # ── Quests & story ───────────────────────────────────────────────────
        self.quest = quest or []
        self.completed_quests = completed_quests or []
        self.story_progress = story_progress

        # ── Statistics ───────────────────────────────────────────────────────
        self.enemies_killed = enemies_killed
        self.puzzles_solved = puzzles_solved
        self.boss_progress = boss_progress
        self.dungeon_runs = dungeon_runs

        # ── Misc ─────────────────────────────────────────────────────────────
        self.luck = luck
        self.reputation = reputation
        self.last_event = last_event
        self.skip_next_battle = skip_next_battle
        self.skip_next_trap = skip_next_trap
        self.skip_next_boss_preparation = skip_next_boss_preparation

    # ── Item catalog ─────────────────────────────────────────────────────────

    def initialize_items(self, items: dict) -> None:
        """
        Attach the shared item catalog to the player.

        Called after creating a new player or loading a save.
        Keeping this logic inside Player prevents external classes
        from depending on Player's internal attributes.
        """
        self.items = items
        self.weapons = items.get("weapons", {})
        self.potions = items.get("potions", {})
        self.defends = items.get("defends", {})

    # ── Properties ───────────────────────────────────────────────────────────

    @property
    def max_hp(self) -> int:
        return self.level * self.HP_PER_LEVEL

    @property
    def max_mana(self) -> int:
        return self.level * self.MANA_PER_LEVEL + self._max_mana_bonus

    @property
    def hp(self) -> int:
        return self._hp

    @hp.setter
    def hp(self, value: int) -> None:
        self._hp = max(0, min(value, self.max_hp))

    @property
    def mana(self) -> int:
        return self._mana

    @mana.setter
    def mana(self, value: int) -> None:
        self._mana = max(0, min(value, self.max_mana))

    @property
    def attack(self) -> int:
        bonus = self.weapons.get(self.weapon, {}).get("attack", 0)
        return self._base_attack + bonus

    @attack.setter
    def attack(self, value: int) -> None:
        self._base_attack = value

    @property
    def defense(self) -> int:
        bonus = self.defends.get(self.armor, {}).get(
            "defense", 0) if self.armor else 0
        return self._base_defense + bonus

    @defense.setter
    def defense(self, value: int) -> None:
        self._base_defense = value

    @property
    def is_alive(self) -> bool:
        return self._hp > 0

    @property
    def exp_to_next_level(self) -> int:
        return max(0, self.EXP_PER_LEVEL - self.exp)

    # ── Display ───────────────────────────────────────────────────────────────

    def show_status(self) -> None:
        lines = [
            f"\n=== {self.name} (Lv {self.level}) ===",
            f"HP    : {self.hp}/{self.max_hp}",
            f"Mana  : {self.mana}/{self.max_mana}",
            f"ATK   : {self.attack}",
            f"DEF   : {self.defense}",
            f"Weapon: {self.weapon}",
            f"Armor : {self.armor or 'None'}",
            f"EXP   : {self.exp}/{self.EXP_PER_LEVEL} (Need {self.exp_to_next_level})",
            f"Floor : {self.floor}",
            f"Gold  : {self.gold}",
            f"Luck  : {self.luck}",
            f"Rep   : {self.reputation}",
            f"SP    : {self.skill_points}",
        ]
        print("\n".join(lines))

    # ── Experience & levelling ────────────────────────────────────────────────

    def gain_exp(self, amount: int) -> None:
        self.exp += amount
        print(f"✨ You gained {amount} EXP!")

        while self.exp >= self.EXP_PER_LEVEL:
            self.exp -= self.EXP_PER_LEVEL
            self.level += 1
            self._base_attack += self.ATTACK_BONUS_PER_LEVEL
            self.skill_points += 1
            self.hp = self.max_hp      # triggers setter → clamps to new max
            self.mana = self.max_mana
            print(f"🎉 Level UP! Now Lv {self.level}")
            print(f"🎯 +1 Skill Point (Total: {self.skill_points})")

    # ── Equipment ─────────────────────────────────────────────────────────────

    def _resolve_item(self, name: str, catalog: dict) -> str | None:
        """Case-insensitive lookup; returns the canonical key or None."""
        name_lower = name.lower()
        return next((k for k in catalog if k.lower() == name_lower), None)

    def equip_weapon(self, weapon_name: str) -> bool:
        """Equip a weapon. Returns True if something went wrong."""
        key = self._resolve_item(weapon_name, self.weapons)
        if key is None:
            print("⚠️ Unknown weapon.")
            return True
        if key not in self.inventory:
            print("⚠️ Weapon not in inventory.")
            return True
        if self.weapon == key:
            print("⚠️ Already equipped.")
            return True
        self.weapon = key
        print(f"🗡️ You equipped {key}!")
        return False

    def equip_defense(self, armor_name: str) -> bool:
        """Equip armor. Returns True if something went wrong."""
        key = self._resolve_item(armor_name, self.defends)
        if key is None:
            print("⚠️ Unknown armor.")
            return True
        if key not in self.inventory:
            print("⚠️ Armor not in inventory.")
            return True
        if self.armor == key:
            print("⚠️ Already equipped.")
            return True
        self.armor = key
        print(f"🛡️ You equipped {key}!")
        return False

    # ── Potions ───────────────────────────────────────────────────────────────

    def equip_potion(self, potion_name: str) -> None:
        """Use a consumable potion from inventory."""
        key = self._resolve_item(potion_name, self.potions)
        if key is None:
            print("⚠️ Unknown potion.")
            return
        if key not in self.inventory:
            print("⚠️ Potion not in inventory.")
            return

        heal = self.potions[key]["effect"]
        self.hp += heal

        self.inventory[key] -= 1
        if self.inventory[key] <= 0:
            del self.inventory[key]

        print(f"🧪 You used {key}! HP +{heal}.")

    # ── Combat ────────────────────────────────────────────────────────────────

    def damage(self, amount: int, guard: int) -> int:
        """Apply incoming damage after guard reduction. Returns damage dealt."""
        final = max(1, amount - guard)
        self.hp -= final
        if not self.is_alive:
            print("💀 Game Over!")
        return final

    # ── Persistence ───────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
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
            "learned_spells": self.learned_spells,
            "skill_points": self.skill_points,
            "unlocked_skills": self.unlocked_skills,
            "luck": self.luck,
            "reputation": self.reputation,
            "last_event": self.last_event,
            "skip_next_battle": self.skip_next_battle,
            "skip_next_trap": self.skip_next_trap,
            "skip_next_boss_preparation": self.skip_next_boss_preparation,
        }
