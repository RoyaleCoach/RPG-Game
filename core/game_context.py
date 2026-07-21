"""
game_context.py
---------------
Shared state and system container for the game.

GameData   – immutable bag of data loaded from disk at startup.
GameContext – single object that owns every live system and the player.

The Game class receives a GameContext and acts only as an orchestrator;
it never constructs systems directly.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Forward references so this module has no circular imports at runtime.
    from core.player import Player
    from core.save_system import SaveSystem
    from core.combat import Combat
    from core.inventory import Inventory
    from core.skill import Skill
    from core.skill_tree import SkillTree
    from core.skill_tree_menu import SkillTreeMenu
    from core.loot import LootEngine
    from core.encyclopedia import ItemEncyclopedia
    from world.map import Explore
    from world.merchant import Merchant
    from world.dungeon import Dungeon
    from world.quest import QuestSystem





# ── Game data ─────────────────────────────────────────────────────────────────

@dataclass
class GameData:
    """
    Immutable bag of data loaded from disk at startup.

    Accessed via ``context.data.items``, ``context.data.quests``, etc.
    Adding a new data source is a one-line change here — nothing else moves.
    """

    items: dict = field(default_factory=dict)
    spells: dict = field(default_factory=dict)
    quests: dict = field(default_factory=dict)
    bosses: dict = field(default_factory=dict)
    skill_tree: dict = field(default_factory=dict)
    loot_tables: dict = field(default_factory=dict)

    # Version / meta
    version: str = "Unknown"
    game_name: str = "Unknown Game"
    author: str = "Unknown"

    @classmethod
    def load(cls) -> "GameData":
        """
        Factory: create a fully populated GameData by calling DataLoader.

        Keeping the load logic here means GameContext.__init__ stays clean,
        and tests can monkey-patch or subclass without touching Game.
        """
        from core.data_loader import DataLoader

        loader = DataLoader()
        version_raw = loader.load_version()

        return cls(
            items=loader.load_items(),
            spells=loader.load_spells(),
            quests=loader.load_quests(),
            bosses=loader.load_bosses(),
            skill_tree=loader.load_skill_tree(),
            loot_tables=loader.load_loot_tables(),
            version=version_raw.get("version", "Unknown"),
            game_name=version_raw.get("game_name", "Unknown Game"),
            author=version_raw.get("author", "Unknown"),
        )


# ── Game context ──────────────────────────────────────────────────────────────

class GameContext:
    """
    Single source of truth for every live system and the current player.

    Construction is split into logical groups so adding a new system
    (e.g. CraftingSystem, CompanionSystem) is a localised change.

    Usage
    -----
    ctx = GameContext()
    ctx.player = Player(...)   # set after start/load
    ctx.combat.run(...)
    ctx.data.items
    """

    def __init__(self) -> None:
        # ── 1. Data (loaded first — everything else depends on it) ──────────
        self.data: GameData = GameData.load()

        # ── 2. Player (assigned later by Game.start) ─────────────────────────
        self.player: "Player | None" = None

        # ── 3. Core systems ───────────────────────────────────────────────────
        self._init_core_systems()

        # ── 4. Gameplay systems ───────────────────────────────────────────────
        self._init_gameplay_systems()

        # ── 5. UI / presentation systems ─────────────────────────────────────
        self._init_ui_systems()

    # ── Initialisation helpers ────────────────────────────────────────────────

    def _init_core_systems(self) -> None:
        """Systems that underpin everything: save, quests, combat."""
        from core.enemy import Enemy
        from core.save_system import SaveSystem  # <<< MODIFIED IMPORT
        from core.skill import Skill
        from world.quest import QuestSystem
        from core.combat import Combat

        # Enemy class-level boss registry lives here because it is global state.
        Enemy.load_bosses(self.data.bosses)

        self.skill_system: "Skill" = Skill(self.data.spells)
        self.save_system: "SaveSystem" = SaveSystem(self)
        self.quest_system: "QuestSystem" = QuestSystem(self.data.quests)
        self.combat: "Combat" = Combat(
            self.quest_system,
            self.data.items,
            self.skill_system,
        )

        # Loot & encyclopedia (attached to combat for rewards)
        from core.loot import LootEngine
        from core.encyclopedia import ItemEncyclopedia

        self.loot_engine: "LootEngine" = LootEngine(
            self.data.loot_tables,
            self.data.items,
        )
        self.encyclopedia: "ItemEncyclopedia" = ItemEncyclopedia(
            self.data.items,
        )

        # Wire loot + encyclopedia into combat
        self.combat.set_loot_engine(self.loot_engine)
        self.combat.set_encyclopedia(self.encyclopedia)

    def _init_gameplay_systems(self) -> None:
        """Systems the player interacts with during a session."""
        from core.inventory import Inventory
        from world.dungeon import Dungeon
        from world.merchant import Merchant
        from world.map import Explore

        self.inventory: "Inventory" = Inventory(self.data.items)
        self.dungeon: "Dungeon" = Dungeon()
        self.merchant: "Merchant" = Merchant(self.data.items)
        self.explore: "Explore" = Explore(
            combat=self.combat,
            dungeon_system=self.dungeon,
            quest_system=self.quest_system,
        )

    def sync_encyclopedia(self) -> None:
        """Sync encyclopedia with player's discovered items and inventory.

        Call this after player creation or load to restore discovery progress.
        """
        if self.player is None:
            return
        # Restore items discovered in previous sessions
        for item_name in getattr(self.player, '_discovered_items', []):
            self.encyclopedia.discover(item_name)
        # Also sync with current inventory
        self.encyclopedia.sync_with_player(self.player.inventory)
        # Push discovered set back into player for future saves
        self.player._discovered_items = set(self.encyclopedia.discovered)

    def _init_ui_systems(self) -> None:
        """Systems that present information or menus to the player."""
        from core.skill_tree import SkillTree
        from core.skill_tree_menu import SkillTreeMenu

        self.skill_tree: "SkillTree" = SkillTree(self.data.skill_tree)
        self.skill_tree_menu: "SkillTreeMenu" = SkillTreeMenu(self.skill_tree)
