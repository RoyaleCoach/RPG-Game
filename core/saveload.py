import json
import time
import os
import sys

from core.player import Player


# -------------------------
# BASE DIRECTORY
# -------------------------
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )

SAVE_DIR = os.path.join(
    BASE_DIR,
    "save"
)


class SaveSystem:

    def __init__(self, game):
        self.game = game

    # -------------------------
    # HELPERS
    # -------------------------
    def get_save_path(
        self,
        filename="save.json"
    ):
        return os.path.join(
            SAVE_DIR,
            filename
        )

    # -------------------------
    # SAVE GAME
    # -------------------------
    def save(
        self,
        filename="save.json"
    ):

        os.makedirs(
            SAVE_DIR,
            exist_ok=True
        )

        path = self.get_save_path(
            filename
        )

        save_data = {
            "timestamp": time.time(),

            "player": self.game.player.to_dict(),

            "world": {
                "current_floor": (
                    self.game.player.floor
                ),

                "boss_progress": (
                    self.game.player.boss_progress
                ),

                "dungeon_runs": (
                    self.game.player.dungeon_runs
                )
            }
        }

        try:

            with open(
                path,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    save_data,
                    f,
                    indent=4,
                    ensure_ascii=False
                )

            print(
                f"💾 Game saved: {path}"
            )

            return True

        except (
            OSError,
            TypeError
        ) as e:

            print(
                f"SAVE ERROR: {e}"
            )

            return False

    # -------------------------
    # LOAD GAME
    # -------------------------
    def load(
        self,
        filename="save.json"
    ):

        path = self.get_save_path(
            filename
        )

        try:

            with open(
                path,
                "r",
                encoding="utf-8"
            ) as f:

                save_data = json.load(f)

            player_data = (
                save_data["player"]
            )

            world_data = (
                save_data["world"]
            )

            player = Player(
                **player_data
            )

            player.floor = (
                world_data.get(
                    "current_floor",
                    1
                )
            )

            player.boss_progress = (
                world_data.get(
                    "boss_progress",
                    0
                )
            )

            player.dungeon_runs = (
                world_data.get(
                    "dungeon_runs",
                    0
                )
            )

            print(
                f"📂 Save loaded: {path}"
            )

            return player

        except (
            FileNotFoundError,
            json.JSONDecodeError,
            KeyError,
            TypeError,
            ValueError
        ) as e:

            print(
                f"LOAD ERROR: {e}"
            )

            return None