"""
core/player.py
--------------
Represents the player character and all associated runtime state.

Serialization contract
~~~~~~~~~~~~~~~~~~~~~~
``to_dict()``   → produces a *minimal* save payload grouped by responsibility.
``from_dict()`` → reconstructs a Player from that payload with safe defaults
                  for every missing field (backward-compatible with old saves).

Rules for what goes into ``to_dict()``:
  • Save only *persistent* state — data that cannot be reconstructed at runtime.
  • Do NOT save computed values (``attack``, ``defense``) — only the base
    scalars that feed them (``_base_attack``, ``_base_defense``).
  • Do NOT save the item / spell / quest *databases* — those are injected from
    game data after loading.
  • Group fields by responsibility so future sections can be added or removed
    independently (player core, world progress, quests, statistics, flags).
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

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize the player into a minimal, responsibility-grouped payload.

        Design decisions
        ~~~~~~~~~~~~~~~~
        * Only *persistent* state is stored — nothing that can be reconstructed
          at runtime (e.g. ``attack`` and ``defense`` are computed properties;
          only ``_base_attack`` / ``_base_defense`` are saved).
        * Fields are grouped by *responsibility* so sections can evolve
          independently without touching unrelated data.
        * ``floor``, ``boss_progress``, and ``dungeon_runs`` live here (single
          source of truth) — the old ``world`` section in SaveSystem is gone.
        * Transient skip-flags ARE saved so a session interrupted mid-dungeon
          restores correctly.
        """
        return {
            # Who the player is and their core RPG state
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
            },
            # Where the player is and what world state they've accumulated
            "world": {
                "floor": self.floor,
                "boss_progress": self.boss_progress,
                "dungeon_runs": self.dungeon_runs,
                "last_event": self.last_event,
            },
            # What the player owns and has learned
            "loadout": {
                "weapon": self.weapon,
                "armor": self.armor,
                "inventory": self.inventory,
                "learned_spells": self.learned_spells,
                "unlocked_skills": self.unlocked_skills,
            },
            # Active and completed quests and story chapter
            "quests": {
                "story_progress": self.story_progress,
                "quest": self.quest,
                "completed_quests": self.completed_quests,
            },
            # Lifetime counters (achievements / leaderboards)
            "statistics": {
                "enemies_killed": self.enemies_killed,
                "puzzles_solved": self.puzzles_solved,
            },
            # One-time flags that survive a session save mid-dungeon
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

        Backward compatibility
        ~~~~~~~~~~~~~~~~~~~~~~
        Every field has a safe default so old flat saves (pre-refactor) and
        new sectioned saves both load without crashing.  The method checks for
        the new sectioned format first; if sections are absent it falls back to
        reading the top-level keys that the old ``to_dict()`` wrote.

        The item catalog is NOT part of the save — callers must call
        ``player.initialize_items(game_data.items)`` after loading.
        """
        # ── Detect save format ────────────────────────────────────────────────
        is_sectioned = "player" in data and isinstance(data["player"], dict)

        if is_sectioned:
            return cls._from_sectioned_dict(data)
        else:
            return cls._from_legacy_dict(data)

    @classmethod
    def _from_sectioned_dict(cls, data: dict[str, Any]) -> "Player":
        """Reconstruct from the new multi-section save format."""
        p = data.get("player", {})
        w = data.get("world", {})
        lo = data.get("loadout", {})
        q = data.get("quests", {})
        s = data.get("statistics", {})
        f = data.get("flags", {})

        return cls(
            # player section
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
            # world section
            floor=w.get("floor", 1),
            boss_progress=w.get("boss_progress", 0),
            dungeon_runs=w.get("dungeon_runs", 0),
            last_event=w.get("last_event", None),
            # loadout section
            weapon=lo.get("weapon", "Fists"),
            armor=lo.get("armor", None),
            inventory=lo.get("inventory", {"Fists": 1}),
            learned_spells=lo.get("learned_spells", []),
            unlocked_skills=lo.get("unlocked_skills", []),
            # quests section
            story_progress=q.get("story_progress", 0),
            quest=q.get("quest", []),
            completed_quests=q.get("completed_quests", []),
            # statistics section
            enemies_killed=s.get("enemies_killed", 0),
            puzzles_solved=s.get("puzzles_solved", 0),
            # flags section
            skip_next_battle=f.get("skip_next_battle", False),
            skip_next_trap=f.get("skip_next_trap", False),
            skip_next_boss_preparation=f.get("skip_next_boss_preparation", False),
        )

    @classmethod
    def _from_legacy_dict(cls, data: dict[str, Any]) -> "Player":
        """
        Reconstruct from the old flat ``to_dict()`` format.

        Kept for backward compatibility with saves written before this refactor.
        The old format stored ``attack`` / ``defense`` as base values (not
        computed), so we read them directly.
        """
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
            floor=data.get("floor", 1),
            boss_progress=data.get("boss_progress", 0),
            dungeon_runs=data.get("dungeon_runs", 0),
            last_event=data.get("last_event", None),
            weapon=data.get("weapon", "Fists"),
            armor=data.get("armor", None),
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