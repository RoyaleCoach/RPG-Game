"""
tests/test_data_loader.py
------------------------
Unit tests for DataLoader and JSON asset validation.
"""

import json
import pytest
from pathlib import Path
from core.data_loader import DataLoader


@pytest.fixture
def loader():
    return DataLoader()


class TestDataLoader:
    """DataLoader loads JSON files correctly."""

    def test_load_items(self, loader):
        items = loader.load_items()
        assert "weapons" in items
        assert "potions" in items
        assert "defends" in items

    def test_load_quests(self, loader):
        quests = loader.load_quests()
        assert len(quests) > 0

    def test_load_bosses(self, loader):
        bosses = loader.load_bosses()
        assert len(bosses) > 0

    def test_load_spells(self, loader):
        spells = loader.load_spells()
        assert len(spells) > 0

    def test_load_skill_tree(self, loader):
        tree = loader.load_skill_tree()
        assert "skill_nodes" in tree

    def test_load_version(self, loader):
        version = loader.load_version()
        assert "version" in version

    def test_load_nonexistent_returns_empty(self, loader):
        result = loader.load_json("nonexistent.json")
        assert result == {}

    def test_reload_items(self, loader):
        result = loader.reload("items")
        assert "weapons" in result

    def test_reload_unknown_returns_empty(self, loader):
        result = loader.reload("unknown")
        assert result == {}


class TestItemsValidation:
    """Validate items.json structure."""

    def test_weapons_have_required_fields(self, items_data):
        for name, data in items_data.get("weapons", {}).items():
            assert "attack" in data, f"Weapon {name} missing attack"
            assert "rarity" in data, f"Weapon {name} missing rarity"
            assert isinstance(data["attack"], int), f"Weapon {name} attack not int"

    def test_potions_have_required_fields(self, items_data):
        for name, data in items_data.get("potions", {}).items():
            assert "effect" in data, f"Potion {name} missing effect"
            assert "rarity" in data, f"Potion {name} missing rarity"

    def test_defends_have_required_fields(self, items_data):
        for name, data in items_data.get("defends", {}).items():
            assert "defense" in data, f"Armor {name} missing defense"
            assert "rarity" in data, f"Armor {name} missing rarity"

    def test_valid_rarities(self, items_data):
        valid = {"Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic"}
        for category in items_data.values():
            for name, data in category.items():
                assert data.get("rarity", "Common") in valid, \
                    f"{name} has invalid rarity: {data.get('rarity')}"

    def test_prices_non_negative(self, items_data):
        for category in items_data.values():
            for name, data in category.items():
                price = data.get("price")
                if price is not None:
                    assert price >= 0, f"{name} has negative price"

    def test_level_required_positive(self, items_data):
        for category in items_data.values():
            for name, data in category.items():
                req = data.get("level_required", 1)
                assert req >= 1, f"{name} has invalid level_required"

    def test_no_duplicate_names_within_category(self, items_data):
        for category_name, category in items_data.items():
            names = list(category.keys())
            assert len(names) == len(set(names)), \
                f"Duplicate names in {category_name}"


class TestLootTablesValidation:
    """Validate loot_tables.json structure."""

    def test_enemies_section_exists(self, loot_tables_data):
        assert "enemies" in loot_tables_data

    def test_each_enemy_has_loot(self, loot_tables_data):
        for enemy_name, data in loot_tables_data["enemies"].items():
            assert "loot" in data, f"Enemy {enemy_name} missing loot section"

    def test_guaranteed_drops_valid(self, loot_tables_data):
        for enemy_name, data in loot_tables_data["enemies"].items():
            for drop in data.get("loot", {}).get("guaranteed", []):
                assert "item" in drop, f"{enemy_name} guaranteed drop missing item"
                assert "min" in drop, f"{enemy_name} guaranteed drop missing min"
                assert "max" in drop, f"{enemy_name} guaranteed drop missing max"
                assert drop["min"] <= drop["max"], \
                    f"{enemy_name} guaranteed drop min > max"

    def test_random_drops_valid(self, loot_tables_data):
        for enemy_name, data in loot_tables_data["enemies"].items():
            for drop in data.get("loot", {}).get("random", []):
                assert "item" in drop
                assert "chance" in drop
                assert 0 <= drop["chance"] <= 100

    def test_rare_drops_valid(self, loot_tables_data):
        for enemy_name, data in loot_tables_data["enemies"].items():
            for drop in data.get("rare_drops", []):
                assert "item" in drop
                assert "chance" in drop
                assert "type" in drop
                assert 0 <= drop["chance"] <= 1000


class TestBossesValidation:
    """Validate bosses.json structure."""

    def test_bosses_have_hp(self, bosses_data):
        for key, data in bosses_data.items():
            assert data["hp"] > 0, f"Boss {key} has non-positive HP"

    def test_bosses_have_attack(self, bosses_data):
        for key, data in bosses_data.items():
            assert data["attack"] > 0, f"Boss {key} has non-positive attack"

    def test_bosses_have_rewards(self, bosses_data):
        for key, data in bosses_data.items():
            assert data["exp_reward"] >= 0
            assert data["gold_reward"] >= 0


class TestQuestsValidation:
    """Validate quests.json structure."""

    def test_quests_have_type(self, quests_data):
        for name, data in quests_data.items():
            assert "type" in data, f"Quest {name} missing type"
            assert data["type"] in ("kills", "floor", "level", "puzzle")

    def test_quests_have_target(self, quests_data):
        for name, data in quests_data.items():
            assert "target" in data, f"Quest {name} missing target"
            assert data["target"] > 0

    def test_quests_have_reward(self, quests_data):
        for name, data in quests_data.items():
            assert "reward" in data, f"Quest {name} missing reward"
            assert "reward_gold" in data
