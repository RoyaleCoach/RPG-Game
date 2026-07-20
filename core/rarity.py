"""
core/rarity.py
--------------
Rarity definitions and helper functions.

Each rarity defines:
  - display label (e.g. "[Rare]")
  - text indicator for environments without color support
  - stat multiplier (applied to base stats)
  - sell value multiplier (applied to merchant price)
"""

from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# RARITY DATA
# ─────────────────────────────────────────────────────────────────────────────

RARITIES: dict[str, dict] = {
    "Common": {
        "label": "[Common]",
        "stat_multiplier": 1.0,
        "sell_multiplier": 1.0,
        "order": 0,
    },
    "Uncommon": {
        "label": "[Uncommon]",
        "stat_multiplier": 1.1,
        "sell_multiplier": 1.25,
        "order": 1,
    },
    "Rare": {
        "label": "[Rare]",
        "stat_multiplier": 1.25,
        "sell_multiplier": 1.5,
        "order": 2,
    },
    "Epic": {
        "label": "[Epic]",
        "stat_multiplier": 1.5,
        "sell_multiplier": 2.0,
        "order": 3,
    },
    "Legendary": {
        "label": "[Legendary]",
        "stat_multiplier": 1.75,
        "sell_multiplier": 3.0,
        "order": 4,
    },
    "Mythic": {
        "label": "[Mythic]",
        "stat_multiplier": 2.0,
        "sell_multiplier": 4.0,
        "order": 5,
    },
}


def get_rarity(name: str) -> dict:
    """Return rarity data, defaulting to Common for unknown rarities."""
    return RARITIES.get(name, RARITIES["Common"])


def get_rarity_label(name: str) -> str:
    """Return the display label for a rarity (e.g. '[Rare]')."""
    return get_rarity(name)["label"]


def get_stat_multiplier(name: str) -> float:
    """Return the stat multiplier for a rarity."""
    return get_rarity(name)["stat_multiplier"]


def get_sell_multiplier(name: str) -> float:
    """Return the sell value multiplier for a rarity."""
    return get_rarity(name)["sell_multiplier"]


def all_rarities() -> list[str]:
    """Return all rarity names in ascending order."""
    return sorted(RARITIES.keys(), key=lambda r: RARITIES[r]["order"])
