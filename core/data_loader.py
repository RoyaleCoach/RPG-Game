import json
from pathlib import Path


class DataLoader:

    def __init__(self):

        self.base_path = (
            Path(__file__)
            .resolve()
            .parent.parent
            / "data"
        )

    def load_json(self, filename):

        path = self.base_path / filename

        try:

            with open(
                path,
                "r",
                encoding="utf-8"
            ) as f:

                return json.load(f)

        except FileNotFoundError:

            print(
                f"❌ File tidak ditemukan: {path}"
            )

            return {}

        except json.JSONDecodeError as e:

            print(
                f"❌ JSON error di {path}: {e}"
            )

            return {}

    def load_quests(self):
        return self.load_json("quests.json")

    def load_bosses(self):
        return self.load_json("bosses.json")

    def load_items(self):
        return self.load_json("items.json")

    def load_spells(self):
        return self.load_json("spells.json")

    def load_version(self):
        return self.load_json("version.json")

    # -------------------------
    # RELOAD SYSTEM (HOT RELOAD OPTIONAL)
    # -------------------------
    def reload(self, target):

        if target == "quests":
            return self.load_quests()

        elif target == "bosses":
            return self.load_bosses()

        elif target == "items":
            return self.load_items()

        elif target == "version":
            return self.load_version()

        else:
            print("❌ Unknown data type:", target)
            return {}