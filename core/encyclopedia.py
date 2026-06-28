"""
core/encyclopedia.py
--------------------
Item Encyclopedia system.

Automatically records every discovered item. Unknown items remain hidden
until obtained. Supports filtering by rarity, type, and displays
completion percentage.

Persistence is handled via the save system (discovered items stored in
the database). For now, discovered items live in memory and are tracked
through the player session.
"""

from __future__ import annotations

from typing import Any

from core.rarity import all_rarities, get_rarity_label


# ─────────────────────────────────────────────────────────────────────────────
# ITEM ENCYCLOPEDIA
# ─────────────────────────────────────────────────────────────────────────────

class ItemEncyclopedia:
    """
    Tracks all items in the game and which ones the player has discovered.

    Usage:
        enc = ItemEncyclopedia(items_catalog)
        enc.discover("Iron Sword")
        enc.show()
    """

    # Category display names
    CATEGORY_NAMES = {
        "weapons": "Weapons",
        "potions": "Potions",
        "defends": "Armor",
    }

    def __init__(self, items_catalog: dict[str, Any]) -> None:
        """
        Args:
            items_catalog: the game's items.json data (weapons, potions, defends)
        """
        self.catalog = items_catalog
        self.discovered: set[str] = set()
        self._build_master_list()

    def _build_master_list(self) -> None:
        """Build the complete list of all discoverable items."""
        self._all_items: dict[str, dict[str, Any]] = {}

        for category, items in self.catalog.items():
            for item_name, item_data in items.items():
                self._all_items[item_name] = {
                    "name": item_name,
                    "category": category,
                    "rarity": item_data.get("rarity", "Common"),
                    "type": self._resolve_type(category, item_data),
                    "description": self._build_description(category, item_data),
                }

    @staticmethod
    def _resolve_type(category: str, item_data: dict) -> str:
        """Determine the item's functional type."""
        if category in ("weapons", "defends"):
            return "equipment"
        if category == "potions":
            return "consumable"
        return "material"

    @staticmethod
    def _build_description(category: str, item_data: dict) -> str:
        """Build a human-readable description from item data."""
        parts: list[str] = []

        if category == "weapons":
            atk = item_data.get("attack", 0)
            parts.append(f"ATK +{atk}")
        elif category == "defends":
            defense = item_data.get("defense", 0)
            parts.append(f"DEF +{defense}")
        elif category == "potions":
            effect = item_data.get("effect", 0)
            parts.append(f"Restores {effect} HP")

        req = item_data.get("level_required", 1)
        if req > 1:
            parts.append(f"Requires Lv {req}")

        return " | ".join(parts) if parts else "Unknown item"

    # ── Discovery ──────────────────────────────────────────────────────────

    def discover(self, item_name: str) -> bool:
        """
        Mark an item as discovered.

        Returns True if the item was newly discovered, False if already known.
        """
        if item_name not in self._all_items:
            return False
        if item_name in self.discovered:
            return False
        self.discovered.add(item_name)
        return True

    def is_discovered(self, item_name: str) -> bool:
        return item_name in self.discovered

    def sync_with_player(self, player_inventory: dict[str, int]) -> None:
        """Discover all items currently in the player's inventory."""
        for item_name in player_inventory:
            if item_name in self._all_items:
                self.discovered.add(item_name)

    # ── Display ────────────────────────────────────────────────────────────

    def show(self) -> None:
        """Display the full encyclopedia with filtering and completion."""
        print("\n========================================")
        print("ITEM ENCYCLOPEDIA")
        print("========================================")

        # Group by category
        categories = self._group_by_category()

        total_items = len(self._all_items)
        total_discovered = len(self.discovered)

        for category, items in categories.items():
            display_name = self.CATEGORY_NAMES.get(category, category.title())
            discovered_in_cat = sum(1 for i in items if i["name"] in self.discovered)
            total_in_cat = len(items)

            print(f"\n  {display_name} {discovered_in_cat}/{total_in_cat}")

            for item in items:
                name = item["name"]
                if name in self.discovered:
                    rarity_label = get_rarity_label(item["rarity"])
                    print(f"    + {name} {rarity_label}")
                    if item["description"]:
                        print(f"      {item['description']}")
                else:
                    print(f"    ? ???")

        # Completion
        pct = (total_discovered / total_items * 100) if total_items > 0 else 0
        print(f"\n  Completion: {pct:.0f}%")
        print("=" * 40)

    def show_by_rarity(self, rarity: str) -> None:
        """Display only items of a specific rarity."""
        print(f"\n  {get_rarity_label(rarity)} Items:")

        matching = [
            item for item in self._all_items.values()
            if item["rarity"] == rarity
        ]

        if not matching:
            print("    No items of this rarity.")
            return

        for item in matching:
            name = item["name"]
            if name in self.discovered:
                print(f"    + {name} ({item['type']})")
            else:
                print(f"    ? ???")

    def show_by_type(self, item_type: str) -> None:
        """Display only items of a specific type (equipment, consumable, material)."""
        print(f"\n  {item_type.title()}s:")

        matching = [
            item for item in self._all_items.values()
            if item["type"] == item_type
        ]

        if not matching:
            print(f"    No {item_type}s found.")
            return

        for item in matching:
            name = item["name"]
            if name in self.discovered:
                rarity_label = get_rarity_label(item["rarity"])
                print(f"    + {name} {rarity_label}")
            else:
                print(f"    ? ???")

    def show_menu(self) -> None:
        """Interactive encyclopedia menu with filtering."""
        while True:
            self.show()

            print("\n  Filters:")
            print("  [1] By Rarity")
            print("  [2] By Type")
            print("  [0] Back")

            choice = input("> ").strip()

            if choice == "0":
                break
            elif choice == "1":
                self._rarity_filter_menu()
            elif choice == "2":
                self._type_filter_menu()

    def _rarity_filter_menu(self) -> None:
        """Sub-menu for filtering by rarity."""
        rarities = all_rarities()
        print("\n  Select rarity:")
        for i, r in enumerate(rarities, 1):
            print(f"  [{i}] {get_rarity_label(r)}")
        print("  [0] Back")

        choice = input("> ").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(rarities):
                self.show_by_rarity(rarities[idx])
        except (ValueError, IndexError):
            pass

    def _type_filter_menu(self) -> None:
        """Sub-menu for filtering by type."""
        types = ["equipment", "consumable", "material"]
        print("\n  Select type:")
        for i, t in enumerate(types, 1):
            print(f"  [{i}] {t.title()}")
        print("  [0] Back")

        choice = input("> ").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(types):
                self.show_by_type(types[idx])
        except (ValueError, IndexError):
            pass

    # ── Helpers ────────────────────────────────────────────────────────────

    def _group_by_category(self) -> dict[str, list[dict]]:
        """Group all items by their category."""
        groups: dict[str, list[dict]] = {}
        for item in self._all_items.values():
            cat = item["category"]
            if cat not in groups:
                groups[cat] = []
            groups[cat].append(item)
        return groups

    # ── Persistence hooks (for future save integration) ────────────────────

    def to_dict(self) -> dict[str, Any]:
        """Serialize discovered items for saving."""
        return {
            "discovered": sorted(self.discovered),
        }

    def from_dict(self, data: dict[str, Any]) -> None:
        """Load discovered items from save data."""
        self.discovered = set(data.get("discovered", []))
