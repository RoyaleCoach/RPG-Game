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

#Welcome to NIGTMARE mate
#if it works it works

class Game:

    def __init__(self):

        self.player = None

        # -------------------------
        # DATA
        # -------------------------
        self.data_loader = DataLoader()

        self.quests = self.data_loader.load_quests()
        self.bosses = self.data_loader.load_bosses()
        self.items = self.data_loader.load_items()
        self.spells = self.data_loader.load_spells()
        self.skill_tree_data = self.data_loader.load_skill_tree()

        version_data = self.data_loader.load_version()

        self.version = version_data.get(
            "version",
            "Unknown"
        )

        self.game_name = version_data.get(
            "game_name",
            "Unknown Game"
        )

        self.author = version_data.get(
            "author",
            "Unknown"
        )

        self.skill_system = Skill(self.spells)
        self.skill_tree = SkillTree(self.skill_tree_data)
        self.skill_tree_menu = SkillTreeMenu(self.skill_tree)

        # -------------------------
        # LOAD BOSS DATA
        # -------------------------
        Enemy.load_bosses(
            self.bosses
        )

        # -------------------------
        # CORE SYSTEMS
        # -------------------------
        self.save_system = SaveSystem(self)

        self.quest_system = QuestSystem(
            self.quests
        )

        self.combat = Combat(
            self.quest_system,
            self.items,
            self.skill_system
        )

        self.dungeon_system = Dungeon()

        self.inventory_system = Inventory(
            self.items
        )

        self.merchant = Merchant(
            self.items
        )

        # -------------------------
        # EXPLORE SYSTEM
        # -------------------------
        self.explore_system = Explore(
            combat=self.combat,
            dungeon_system=self.dungeon_system,
            quest_system=self.quest_system
        )

        self.first_loop = True

    # -------------------------
    # PLAYER SETUP
    # -------------------------
    def setup_player_data(self):

        self.player.items = self.items

        self.player.weapons = (
            self.items.get(
                "weapons",
                {}
            )
        )

        self.player.potions = (
            self.items.get(
                "potions",
                {}
            )
        )

        self.player.defends = (
            self.items.get(
                "defends",
                {}
            )
        )

    # -------------------------
    # BOOT GAME
    # -------------------------
    def start(self):

        print(
            f"=== {self.game_name.upper()} ==="
        )

        print(
            f"Version: {self.version}"
        )

        print(
            f"Author: {self.author}\n"
        )

        choice = None

        while choice not in ["n", "l"]:

            print(
                "Start new (n) or load (l)?"
            )

            choice = (
                input(
                    "> "
                )
                .lower()
                .strip()
            )

        # -------------------------
        # LOAD GAME
        # -------------------------
        if choice == "l":

            self.player = self.save_system.load()

            if self.player is None:

                print(
                    "⚠️ Save not found, creating new game..."
                )

                self.player = Player(
                    items=self.items,
                    skill_points=1
                )

                self.setup_player_data()
                self.skill_system.learn_spell(
                    self.player,
                    "icicle"
                )
                intro_story(
                    self.player
                )

            else:

                self.setup_player_data()

        # -------------------------
        # NEW GAME
        # -------------------------
        else:

            self.player = Player(
                name=input(
                    "Enter player name: "
                ),
                items=self.items,
                skill_points=1
            )

            self.setup_player_data()
            self.skill_system.learn_spell(
                self.player,
                "icicle"
            )
            intro_story(
                self.player
            )

        self.game_loop()

    # -------------------------
    # GAME LOOP
    # -------------------------
    def game_loop(self):

        while True:

            if not self.first_loop:
                press_any()

            self.first_loop = False

            self.player.show_status()

            action = self.show_main_menu()

            if action == "1":

                main_story(
                    self.player,
                    self.player.story_progress,
                    self.combat
                )

            elif action == "2":

                self.explore_system.explore(
                    self.player
                )

                if self.player.hp <= 0:

                    print(
                        "\n💀 Game Over."
                    )

                    break

            elif action == "3":

                self.merchant.trade(
                    self.player
                )

            elif action == "4":

                self.inventory_system.open(
                    self.player
                )

            elif action == "5":

                self.skill_tree_menu.show_skill_tree(
                    self.player
                )

            elif action == "6":

                self.save_system.save()

            elif action == "0":

                self.exit_game()

                break

            else:
                print(
                    "❌ Invalid choice."
                )

    # -------------------------
    # MENU
    def show_main_menu(self):

        print("\n=== MENU ===")
        print("[1] Main Story")
        print("[2] Explore Dungeon")
        print("[3] Merchant")
        print("[4] Inventory")
        print("[5] Skill Tree")
        print("[6] Save Game")
        print("[0] Exit")

        return input("> ").strip()

    # -------------------------
    # EXIT HANDLER
    def exit_game(self):

        print(
            "Save game? (y/n)"
        )

        save_choice = (
            input(
                "> "
            )
            .lower()
            .strip()
        )

        if save_choice in [
            "y",
            "yes"
        ]:

            self.save_system.save()

        typewriter(
            "Exiting the game",
            dramatic=True
        )
