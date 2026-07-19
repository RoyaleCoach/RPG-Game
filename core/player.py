"""
core/player.py
--------------
Represents the player character and all associated runtime state.

Perubahan dari versi sebelumnya:
  [NEW] critical_chance     — % peluang critical hit (default 15)
  [NEW] critical_multiplier — pengali damage saat crit (default 2.0)
  [NEW] accuracy            — menaikkan minimum damage (default 5)
  [NEW] dodge               — % peluang menghindari seluruh damage (default 5)
  [NEW] status_effects      — list effect aktif (Burn, Poison, dll.)

Serialization contract
~~~~~~~~~~~~~~~~~~~~~~
``to_dict()``   → produces a *minimal* save payload grouped by responsibility.
``from_dict()`` → reconstructs a Player from that payload with safe defaults
                  for every missing field (backward-compatible with old saves).
"""

from __future__ import annotations

from typing import Any


class Player:
    """Represents the player character and all associated state."""

    # ── Level-up constants ────────────────────────────────────────────────────
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
        armor: str = "Health Potion",
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
        # ── NEW combat stats ─────────────────────────────────────────────────
        critical_chance: int = 15,
        critical_multiplier: float = 2.0,
        accuracy: int = 5,
        dodge: int = 5,
    ) -> None:
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

        # ── NEW: Combat stats ─────────────────────────────────────────────────
        # critical_chance: peluang crit dalam persen (0-100)
        self.critical_chance = critical_chance
        # critical_multiplier: pengali damage saat crit (mis. 2.0 = 2x damage)
        self.critical_multiplier = critical_multiplier
        # accuracy: menaikkan minimum damage; semakin tinggi → damage lebih konsisten
        self.accuracy = accuracy
        # dodge: peluang dalam persen untuk menghindari seluruh serangan
        self.dodge = dodge

        # ── NEW: Status effects ───────────────────────────────────────────────
        # Dikelola oleh status_effects.py; tidak di-save (transient per battle)
        self.status_effects: list = []

    # ── Item catalog ─────────────────────────────────────────────────────────

    def initialize_items(self, items: dict) -> None:
        """Attach the shared item catalog to the player."""
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
            f"CRIT  : {self.critical_chance}% x{self.critical_multiplier}",
            f"ACC   : {self.accuracy}",
            f"DODGE : {self.dodge}%",
            f"Weapon: {self.weapon}",
            f"Armor : {self.armor or 'None'}",
            f"EXP   : {self.exp}/{self.EXP_PER_LEVEL} (Need {self.exp_to_next_level})",
            f"Floor : {self.floor}",
            f"Gold  : {self.gold}",
            f"Luck  : {self.luck}",
            f"Rep   : {self.reputation}",
            f"SP    : {self.skill_points}",
        ]
        # Tampilkan status effect aktif (jika ada)
        if self.status_effects:
            fx = ", ".join(repr(e) for e in self.status_effects)
            lines.append(f"STATUS: {fx}")
        print("\n".join(lines))

    # ── Experience & levelling ────────────────────────────────────────────────

    def gain_exp(self, amount: int) -> None:
        self.exp += amount
        print(f"✨ +{amount} EXP")
        while self.exp >= self.EXP_PER_LEVEL:
            self.exp -= self.EXP_PER_LEVEL
            self._level_up()

    def _level_up(self) -> None:
        self.level += 1
        self._base_attack += self.ATTACK_BONUS_PER_LEVEL
        # Kecil bonus stats saat level up
        self.critical_chance = min(50, self.critical_chance + 1)
        self.accuracy = min(self.attack, self.accuracy + 1)
        self.dodge = min(40, self.dodge + 1)
        self._hp = self.max_hp   # full heal on level up
        self._mana = self.max_mana
        print(
            f"\n🎉 Level Up! {self.name} sekarang Level {self.level}!\n"
            f"   ATK: {self.attack} | HP: {self.max_hp} | "
            f"CRIT: {self.critical_chance}% | ACC: {self.accuracy} | DODGE: {self.dodge}%"
        )
        self.skill_points += 1

    # ── Equipment ─────────────────────────────────────────────────────────────

    def _resolve_item(self, name: str, catalog: dict) -> str | None:
        """Return the canonical key matching *name* (case-insensitive)."""
        if name in catalog:
            return name
        lower = name.lower()
        for key in catalog:
            if key.lower() == lower:
                return key
        return None

    def equip_weapon(self, weapon_name: str) -> None:
        key = self._resolve_item(weapon_name, self.weapons)
        if key is None:
            print("⚠️ Unknown weapon.")
            return
        if key not in self.inventory:
            print("⚠️ Weapon not in inventory.")
            return
        req = self.weapons[key].get("level_required", 1)
        if self.level < req:
            print(f"⚠️ Need level {req} to equip {key}.")
            return
        self.weapon = key
        atk = self.weapons[key]["attack"]
        print(f"⚔️ Equipped {key} (ATK +{atk}).")

    def equip_defense(self, armor_name: str) -> None:
        key = self._resolve_item(armor_name, self.defends)
        if key is None:
            print("⚠️ Unknown armor.")
            return
        if key not in self.inventory:
            print("⚠️ Armor not in inventory.")
            return
        req = self.defends[key].get("level_required", 1)
        if self.level < req:
            print(f"⚠️ Need level {req} to equip {key}.")
            return
        self.armor = key
        defense = self.defends[key]["defense"]
        print(f"🛡️ Equipped {key} (DEF +{defense}).")

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

    def damage(self, amount: int) -> int:
        """Apply incoming damage after guard reduction. Returns damage dealt."""
        final = max(1, amount - guard)
        self.hp -= final
        if not self.is_alive:
            print("💀 Game Over!")
        return final

    # ── Persistence ───────────────────────────────────────────────────────────

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize the player into a minimal, responsibility-grouped payload.
        Status effects TIDAK disimpan (transient, di-reset setiap battle baru).
        """
        return {
            "player": {
                "name": self.name,
                "level": self.level,
                "exp": self.exp,
                "hp": self.hp,
                "mana": self.mana,
                "base_attack": self._base_attack,
                "base_defense": self._base_defense,
                "gold": self.gold,
                "luck": self.luck,
                "reputation": self.reputation,
                "skill_points": self.skill_points,
                # NEW stats — disimpan agar progres level-up tersimpan
                "critical_chance": self.critical_chance,
                "critical_multiplier": self.critical_multiplier,
                "accuracy": self.accuracy,
                "dodge": self.dodge,
            },
            "world": {
                "floor": self.floor,
                "boss_progress": self.boss_progress,
                "dungeon_runs": self.dungeon_runs,
                "last_event": self.last_event,
            },
            "loadout": {
                "weapon": self.weapon,
                "armor": self.armor,
                "inventory": self.inventory,
                "learned_spells": self.learned_spells,
                "unlocked_skills": self.unlocked_skills,
            },
            "quests": {
                "story_progress": self.story_progress,
                "quest": self.quest,
                "completed_quests": self.completed_quests,
            },
            "statistics": {
                "enemies_killed": self.enemies_killed,
                "puzzles_solved": self.puzzles_solved,
            },
            "flags": {
                "skip_next_battle": self.skip_next_battle,
                "skip_next_trap": self.skip_next_trap,
                "skip_next_boss_preparation": self.skip_next_boss_preparation,
            },
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Player":
        """
        Reconstruct a Player from a ``to_dict()`` payload.
        Backward-compatible: new stats default ke nilai awal jika tidak ada.
        """
        is_sectioned = "player" in data and isinstance(data["player"], dict)
        if is_sectioned:
            return cls._from_sectioned_dict(data)
        else:
            return cls._from_legacy_dict(data)

    @classmethod
    def _from_sectioned_dict(cls, data: dict[str, Any]) -> "Player":
        p = data.get("player", {})
        w = data.get("world", {})
        lo = data.get("loadout", {})
        q = data.get("quests", {})
        s = data.get("statistics", {})
        f = data.get("flags", {})

        return cls(
            name=p.get("name", "Adventurer"),
            level=p.get("level", 1),
            exp=p.get("exp", 0),
            hp=p.get("hp", 100),
            mana=p.get("mana", None),
            attack=p.get("base_attack", 10),
            defense=p.get("base_defense", 5),
            gold=p.get("gold", 50),
            luck=p.get("luck", 0),
            reputation=p.get("reputation", 0),
            skill_points=p.get("skill_points", 0),
            critical_chance=p.get("critical_chance", 15),
            critical_multiplier=p.get("critical_multiplier", 2.0),
            accuracy=p.get("accuracy", 5),
            dodge=p.get("dodge", 5),
            floor=w.get("floor", 1),
            boss_progress=w.get("boss_progress", 0),
            dungeon_runs=w.get("dungeon_runs", 0),
            last_event=w.get("last_event", None),
            weapon=lo.get("weapon", "Fists"),
            armor=lo.get("armor", "Health Potion"),
            inventory=lo.get("inventory", {"Fists": 1}),
            learned_spells=lo.get("learned_spells", []),
            unlocked_skills=lo.get("unlocked_skills", []),
            story_progress=q.get("story_progress", 0),
            quest=q.get("quest", []),
            completed_quests=q.get("completed_quests", []),
            enemies_killed=s.get("enemies_killed", 0),
            puzzles_solved=s.get("puzzles_solved", 0),
            skip_next_battle=f.get("skip_next_battle", False),
            skip_next_trap=f.get("skip_next_trap", False),
            skip_next_boss_preparation=f.get("skip_next_boss_preparation", False),
        )

    @classmethod
    def _from_legacy_dict(cls, data: dict[str, Any]) -> "Player":
        """Backward compat untuk save format lama (flat dict)."""
        return cls(
            name=data.get("name", "Adventurer"),
            level=data.get("level", 1),
            exp=data.get("exp", 0),
            hp=data.get("hp", 100),
            mana=data.get("mana", None),
            attack=data.get("attack", 10),
            defense=data.get("defense", 5),
            gold=data.get("gold", 50),
            luck=data.get("luck", 0),
            reputation=data.get("reputation", 0),
            skill_points=data.get("skill_points", 0),
            critical_chance=data.get("critical_chance", 15),
            critical_multiplier=data.get("critical_multiplier", 2.0),
            accuracy=data.get("accuracy", 5),
            dodge=data.get("dodge", 5),
            floor=data.get("floor", 1),
            boss_progress=data.get("boss_progress", 0),
            dungeon_runs=data.get("dungeon_runs", 0),
            last_event=data.get("last_event", None),
            weapon=data.get("weapon", "Fists"),
            armor=data.get("armor", "Health Potion"),
            inventory=data.get("inventory", {"Fists": 1}),
            learned_spells=data.get("learned_spells", []),
            unlocked_skills=data.get("unlocked_skills", []),
            story_progress=data.get("story_progress", 0),
            quest=data.get("quest", []),
            completed_quests=data.get("completed_quests", []),
            enemies_killed=data.get("enemies_killed", 0),
            puzzles_solved=data.get("puzzles_solved", 0),
            skip_next_battle=data.get("skip_next_battle", False),
            skip_next_trap=data.get("skip_next_trap", False),
            skip_next_boss_preparation=data.get("skip_next_boss_preparation", False),
        )