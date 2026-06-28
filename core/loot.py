"""
core/loot.py
------------
Loot table system and rare drop system.

LootTable   — rolls normal drops from a data-driven table.
RareDrops   — rolls independent rare/unique drops.
LootEngine  — combines both and grants items to the player.

All data is loaded from data/loot_tables.json. Combat code only needs
to call ``LootEngine.roll_for_enemy(enemy, player)`` after victory.
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING, Any

from core.rarity import get_rarity_label, get_sell_multiplier

if TYPE_CHECKING:
    from core.player import Player
    from core.enemy import Enemy


# ─────────────────────────────────────────────────────────────────────────────
# LOOT TABLE
# ─────────────────────────────────────────────────────────────────────────────

class LootTable:
    """
    Rolls normal drops for a single enemy.

    Expected data format (from loot_tables.json):
    {
        "guaranteed": [{"item": "Gold", "min": 10, "max": 30}],
        "random": [
            {"item": "Wooden Sword", "chance": 30, "min": 1, "max": 1},
            {"item": "Health Potion", "chance": 50, "min": 1, "max": 2}
        ]
    }
    """

    def __init__(self, data: dict[str, Any]) -> None:
        self.guaranteed: list[dict] = data.get("guaranteed", [])
        self.random: list[dict] = data.get("random", [])

    def roll(self) -> list[dict[str, Any]]:
        """
        Roll all drops. Returns a list of {"item": str, "quantity": int}.
        """
        drops: list[dict[str, Any]] = []

        # Guaranteed drops always happen
        for entry in self.guaranteed:
            item_name = entry["item"]
            qty = random.randint(entry.get("min", 1), entry.get("max", 1))
            if qty > 0:
                drops.append({"item": item_name, "quantity": qty})

        # Random drops roll independently
        for entry in self.random:
            chance = entry.get("chance", 0)
            if random.randint(1, 100) <= chance:
                item_name = entry["item"]
                qty = random.randint(entry.get("min", 1), entry.get("max", 1))
                if qty > 0:
                    drops.append({"item": item_name, "quantity": qty})

        return drops


# ─────────────────────────────────────────────────────────────────────────────
# RARE DROPS
# ─────────────────────────────────────────────────────────────────────────────

class RareDrops:
    """
    Rolls independent rare drops.

    Expected data format:
    [
        {"item": "Dragon Scale", "chance": 2, "type": "material"},
        {"item": "Shadow Blade", "chance": 1, "type": "equipment"},
        {"item": "Ancient Coin", "chance": 3, "type": "collectible"}
    ]
    """

    def __init__(self, data: list[dict[str, Any]]) -> None:
        self.entries: list[dict[str, Any]] = data

    def roll(self) -> list[dict[str, Any]]:
        """
        Roll rare drops. Returns a list of {"item": str, "quantity": int, "type": str}.
        """
        drops: list[dict[str, Any]] = []

        for entry in self.entries:
            chance = entry.get("chance", 0)
            if random.randint(1, 1000) <= chance:  # per-mille for very rare
                item_name = entry["item"]
                qty = random.randint(entry.get("min", 1), entry.get("max", 1))
                if qty > 0:
                    drops.append({
                        "item": item_name,
                        "quantity": qty,
                        "type": entry.get("type", "unknown"),
                    })

        return drops


# ─────────────────────────────────────────────────────────────────────────────
# LOOT ENGINE
# ─────────────────────────────────────────────────────────────────────────────

class LootEngine:
    """
    Combines loot tables and rare drops, grants items to the player.

    Usage:
        LootEngine.roll_for_enemy(enemy, player, items_catalog)
    """

    def __init__(self, loot_data: dict[str, Any], items_catalog: dict) -> None:
        """
        Args:
            loot_data: full contents of loot_tables.json
            items_catalog: the game's items.json data (for rarity lookups)
        """
        self.loot_data = loot_data
        self.items_catalog = items_catalog
        self._build_tables()

    def _build_tables(self) -> None:
        """Pre-build LootTable and RareDrops from loaded data."""
        self._tables: dict[str, LootTable] = {}
        self._rare_tables: dict[str, RareDrops] = {}

        for enemy_key, table_data in self.loot_data.get("enemies", {}).items():
            self._tables[enemy_key] = LootTable(table_data.get("loot", {}))
            rare_data = table_data.get("rare_drops", [])
            if rare_data:
                self._rare_tables[enemy_key] = RareDrops(rare_data)

    def _get_enemy_key(self, enemy: "Enemy") -> str | None:
        """Find the loot table key for an enemy by name."""
        enemy_name = enemy.name
        # Direct match first
        if enemy_name in self._tables:
            return enemy_name
        # Case-insensitive fallback
        for key in self._tables:
            if key.lower() == enemy_name.lower():
                return key
        return None

    def _get_item_rarity(self, item_name: str) -> str:
        """Look up an item's rarity from the catalog."""
        for category in ("weapons", "potions", "defends"):
            cat = self.items_catalog.get(category, {})
            if item_name in cat:
                return cat[item_name].get("rarity", "Common")
        return "Common"

    def _get_item_type(self, item_name: str) -> str:
        """Determine item type from the catalog."""
        if item_name in self.items_catalog.get("weapons", {}):
            return "weapon"
        if item_name in self.items_catalog.get("potions", {}):
            return "consumable"
        if item_name in self.items_catalog.get("defends", {}):
            return "armor"
        return "material"

    def roll_for_enemy(self, enemy: "Enemy", player: "Player") -> list[dict[str, Any]]:
        """
        Roll all drops for defeating an enemy. Grants items to player.

        Returns a list of all drops for display/logging purposes.
        Each drop: {"item": str, "quantity": int, "rarity": str, "rare": bool}
        """
        all_drops: list[dict[str, Any]] = []
        enemy_key = self._get_enemy_key(enemy)

        if enemy_key is None:
            return all_drops

        # Normal loot
        table = self._tables[enemy_key]
        for drop in table.roll():
            item_name = drop["item"]
            qty = drop["quantity"]

            if item_name == "Gold":
                player.gold += qty
                all_drops.append({
                    "item": f"{qty} Gold",
                    "quantity": qty,
                    "rarity": "Common",
                    "rare": False,
                })
            else:
                player.inventory[item_name] = (
                    player.inventory.get(item_name, 0) + qty
                )
                rarity = self._get_item_rarity(item_name)
                all_drops.append({
                    "item": item_name,
                    "quantity": qty,
                    "rarity": rarity,
                    "rare": False,
                })

        # Rare drops
        rare_table = self._rare_tables.get(enemy_key)
        if rare_table:
            for drop in rare_table.roll():
                item_name = drop["item"]
                qty = drop["quantity"]

                player.inventory[item_name] = (
                    player.inventory.get(item_name, 0) + qty
                )
                all_drops.append({
                    "item": item_name,
                    "quantity": qty,
                    "rarity": "Legendary",
                    "rare": True,
                })

        return all_drops

    @staticmethod
    def display_drops(drops: list[dict[str, Any]]) -> None:
        """Print drops to the console with rarity formatting."""
        if not drops:
            return

        print("\n[Loot]")
        for drop in drops:
            name = drop["item"]
            qty = drop["quantity"]
            rarity = drop.get("rarity", "Common")
            is_rare = drop.get("rare", False)

            if is_rare:
                label = get_rarity_label(rarity)
                print(f"  *** RARE DROP! {name} x{qty} {label} ***")
            elif name.endswith("Gold"):
                print(f"  [Gold] {name}")
            else:
                label = get_rarity_label(rarity)
                print(f"  - {name} x{qty} {label}")
