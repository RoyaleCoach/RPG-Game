from core.player import Player
from core.saveload import SaveSystem
from core.combat import Combat
from core.data_loader import DataLoader
from core.inventory import Inventory
from core.enemy import Enemy
from core.skill import Skill
from core.skill_tree import SkillTree
from core.skill_tree_menu import SkillTreeMenu

from world.map import Explore
from world.merchant import Merchant
from world.dungeon import Dungeon
from world.quest import QuestSystem

from utils.press_any_key import press_any
from utils.text_effect import typewriter

from story.intro_story import intro_story
from story.main_story import main_story


class Game:

    MENU_OPTIONS = {
        "1": "Main Story",
        "2": "Explore Dungeon",
        "3": "Merchant",
        "4": "Inventory",
        "5": "Skill Tree",
        "6": "Save Game",
        "0": "Exit",
    }

    def __init__(self):
        self.player = None
        self._init_data()
        self._init_systems()
        self.first_loop = True

    # ── Data ────────────────────────────────────────────────────────────────

    def _init_data(self):
        loader = DataLoader()

        self.items = loader.load_items()
        self.spells = loader.load_spells()
        self.quests = loader.load_quests()
        self.bosses = loader.load_bosses()
        self.skill_tree_data = loader.load_skill_tree()

        version = loader.load_version()
        self.version = version.get("version", "Unknown")
        self.game_name = version.get("game_name", "Unknown Game")
        self.author = version.get("author", "Unknown")

    # ── Systems ─────────────────────────────────────────────────────────────

    def _init_systems(self):
        Enemy.load_bosses(self.bosses)

        self.skill_system = Skill(self.spells)
        self.skill_tree = SkillTree(self.skill_tree_data)
        self.skill_tree_menu = SkillTreeMenu(self.skill_tree)

        self.save_system = SaveSystem(self)
        self.quest_system = QuestSystem(self.quests)
        self.combat = Combat(self.quest_system, self.items, self.skill_system)
        self.dungeon_system = Dungeon()
        self.inventory_system = Inventory(self.items)
        self.merchant = Merchant(self.items)
        self.explore_system = Explore(
            combat=self.combat,
            dungeon_system=self.dungeon_system,
            quest_system=self.quest_system,
        )

    # ── Player setup ────────────────────────────────────────────────────────

    def _setup_player_data(self):
        """Attach item references to the player after load or creation."""
        self.player.items = self.items
        self.player.weapons = self.items.get("weapons", {})
        self.player.potions = self.items.get("potions", {})
        self.player.defends = self.items.get("defends", {})

    def _new_player(self, name: str | None = None) -> Player:
        if name is None:
            name = input("Enter player name: ").strip()
        player = Player(name=name, items=self.items, skill_points=1)
        self._setup_player_data()
        self.skill_system.learn_spell(player, "icicle")
        intro_story(player)
        return player

    # ── Boot ────────────────────────────────────────────────────────────────

    def start(self):
        print(f"=== {self.game_name.upper()} ===")
        print(f"Version : {self.version}")
        print(f"Author  : {self.author}\n")

        choice = self._prompt_until_valid(
            "Start new (n) or load (l)? ", {"n", "l"}
        )

        if choice == "l":
            self.player = self.save_system.load()
            if self.player is None:
                print("⚠️  Save not found — starting a new game.")
                self.player = self._new_player()
            else:
                self._setup_player_data()
        else:
            self.player = self._new_player()

        self._game_loop()

    # ── Game loop ────────────────────────────────────────────────────────────

    def _game_loop(self):
        actions = {
            "1": self._do_main_story,
            "2": self._do_explore,
            "3": lambda: self.merchant.trade(self.player),
            "4": lambda: self.inventory_system.open(self.player),
            "5": lambda: self.skill_tree_menu.show_skill_tree(self.player),
            "6": self.save_system.save,
            "0": self._do_exit,
        }

        while True:
            if not self.first_loop:
                press_any()
            self.first_loop = False

            self.player.show_status()
            action = self._show_main_menu()

            handler = actions.get(action)
            if handler is None:
                print("❌ Invalid choice.")
                continue

            handler()

            if action == "0" or self.player.hp <= 0:
                break

        if self.player.hp <= 0:
            print("\n💀 Game Over.")

    # ── Menu actions ─────────────────────────────────────────────────────────

    def _do_main_story(self):
        main_story(self.player, self.player.story_progress, self.combat)

    def _do_explore(self):
        self.explore_system.explore(self.player)

    def _do_exit(self):
        if self._prompt_until_valid("Save before quitting? (y/n) ", {"y", "n"}) == "y":
            self.save_system.save()
        typewriter("Exiting the game", dramatic=True)

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _show_main_menu(self) -> str:
        print("\n=== MENU ===")
        for key, label in self.MENU_OPTIONS.items():
            prefix = "[0]" if key == "0" else f"[{key}]"
            print(f"{prefix} {label}")
        return input("> ").strip()

    @staticmethod
    def _prompt_until_valid(prompt: str, valid: set[str]) -> str:
        while True:
            answer = input(prompt).lower().strip()
            if answer in valid:
                return answer
