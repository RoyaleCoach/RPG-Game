"""
game.py
-------
Top-level orchestrator. Game's only job is to wire context + menu together
and run the main loop. It knows *what* to do, not *how* systems work.

All shared state lives in GameContext.
All menu configuration lives in MenuRegistry.
"""

from __future__ import annotations

from core.player import Player
from utils.press_any_key import press_any
from utils.text_effect import typewriter
from story.intro_story import intro_story
from story.main_story import main_story

from core.game_context import GameContext
from core.game_menu import MenuEntry, MenuRegistry


class Game:
    """
    Bootstraps the game and runs the main loop.

    Keeps no game state itself — everything lives in ``self.ctx``.
    To add a new feature, add a system to GameContext and a MenuEntry here.
    """

    def __init__(self) -> None:
        self.ctx = GameContext()
        self.first_loop = True

    # ── Boot ─────────────────────────────────────────────────────────────────

    def start(self) -> None:
        self._print_title()

        choice = self._prompt_until_valid(
            "Start new (n) or load (l)? ", {"n", "l"})

        if choice == "l":
            self.ctx.player = self.ctx.save_system.load()
            if self.ctx.player is None:
                print("⚠️  Save not found — starting a new game.")
                self.ctx.player = self._create_new_player()
            else:
                self.ctx.player.initialize_items(self.ctx.data.items)
        else:
            self.ctx.player = self._create_new_player()

        self._game_loop()

    # ── Player creation ───────────────────────────────────────────────────────

    def _create_new_player(self, name: str | None = None) -> Player:
        """
        Prompt for a name (if not supplied), build a Player, run the intro.

        The player is fully initialised here so _game_loop receives a ready
        object and never has to check for partial state.
        """
        if name is None:
            name = input("Enter player name: ").strip()

        player = Player(name=name, items=self.ctx.data.items, skill_points=1)
        player.initialize_items(self.ctx.data.items)
        self.ctx.skill_system.learn_spell(player, "icicle")
        intro_story(player)
        return player

    # ── Game loop ─────────────────────────────────────────────────────────────

    def _game_loop(self) -> None:
        menu = self._build_menu()

        while True:
            if not self.first_loop:
                press_any()
            self.first_loop = False

            self.ctx.player.show_status()
            key = menu.show()

            if not menu.dispatch(key):
                print("❌ Invalid choice.")
                continue

            if menu.is_exit(key) or self.ctx.player.hp <= 0:
                break

        if self.ctx.player.hp <= 0:
            print("\n💀 Game Over.")

    # ── Menu construction ─────────────────────────────────────────────────────

    def _build_menu(self) -> MenuRegistry:
        """
        Declare all menu entries in one place.

        To add a new feature (e.g. Crafting), add one MenuEntry line here
        and implement the corresponding _do_* method. Nothing else changes.
        """
        ctx = self.ctx  # local alias for brevity inside lambdas

        return MenuRegistry([
            MenuEntry("1", "Main Story", self._do_main_story),
            MenuEntry("2", "Explore Dungeon", self._do_explore),
            MenuEntry("3", "Merchant", lambda: ctx.merchant.trade(ctx.player)),
            MenuEntry("4", "Inventory",
                      lambda: ctx.inventory.open(ctx.player)),
            MenuEntry("5", "Skill Tree",
                      lambda: ctx.skill_tree_menu.show_skill_tree(ctx.player)),
            MenuEntry("6", "Save Game", ctx.save_system.save),
            MenuEntry("0", "Exit", self._do_exit),
        ])

    # ── Menu actions ──────────────────────────────────────────────────────────

    def _do_main_story(self) -> None:
        main_story(
            self.ctx.player,
            self.ctx.player.story_progress,
            self.ctx.combat,
        )

    def _do_explore(self) -> None:
        self.ctx.explore.explore(self.ctx.player)

    def _do_exit(self) -> None:
        if self._prompt_until_valid("Save before quitting? (y/n) ", {"y", "n"}) == "y":
            self.ctx.save_system.save()
        typewriter("Exiting the game", dramatic=True)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _print_title(self) -> None:
        d = self.ctx.data
        print(f"=== {d.game_name.upper()} ===")
        print(f"Version : {d.version}")
        print(f"Author  : {d.author}\n")

    @staticmethod
    def _prompt_until_valid(prompt: str, valid: set[str]) -> str:
        while True:
            answer = input(prompt).lower().strip()
            if answer in valid:
                return answer
