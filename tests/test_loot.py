"""
tests/test_loot.py
-----------------
Unit tests for the loot table and rare drop system.
"""

import pytest
from unittest.mock import patch
from core.loot import LootTable, RareDrops, LootEngine


class TestLootTable:
    """LootTable rolls correctly."""

    def test_guaranteed_drops_always_returned(self):
        table = LootTable({
            "guaranteed": [{"item": "Gold", "min": 10, "max": 10}],
            "random": [],
        })
        for _ in range(20):
            drops = table.roll()
            assert len(drops) == 1
            assert drops[0]["item"] == "Gold"
            assert drops[0]["quantity"] == 10

    def test_random_drop_with_100_chance(self):
        table = LootTable({
            "guaranteed": [],
            "random": [{"item": "Sword", "chance": 100, "min": 1, "max": 1}],
        })
        for _ in range(20):
            drops = table.roll()
            assert len(drops) == 1
            assert drops[0]["item"] == "Sword"

    def test_random_drop_with_0_chance(self):
        table = LootTable({
            "guaranteed": [],
            "random": [{"item": "Sword", "chance": 0, "min": 1, "max": 1}],
        })
        for _ in range(20):
            drops = table.roll()
            assert len(drops) == 0

    def test_quantity_range(self):
        table = LootTable({
            "guaranteed": [{"item": "Gold", "min": 5, "max": 50}],
            "random": [],
        })
        quantities = set()
        for _ in range(100):
            drops = table.roll()
            quantities.add(drops[0]["quantity"])
        assert len(quantities) > 1  # should vary
        assert all(5 <= q <= 50 for q in quantities)

    def test_empty_table(self):
        table = LootTable({"guaranteed": [], "random": []})
        assert table.roll() == []

    def test_multiple_guaranteed_drops(self):
        table = LootTable({
            "guaranteed": [
                {"item": "Gold", "min": 10, "max": 10},
                {"item": "Potion", "min": 1, "max": 1},
            ],
            "random": [],
        })
        drops = table.roll()
        assert len(drops) == 2

    def test_zero_quantity_skipped(self):
        table = LootTable({
            "guaranteed": [{"item": "Gold", "min": 0, "max": 0}],
            "random": [],
        })
        drops = table.roll()
        assert len(drops) == 0


class TestRareDrops:
    """RareDrops rolls correctly."""

    def test_rare_drop_with_1000_chance_always(self):
        rare = RareDrops([{"item": "Dragon Heart", "chance": 1000, "type": "material"}])
        for _ in range(20):
            drops = rare.roll()
            assert len(drops) == 1
            assert drops[0]["item"] == "Dragon Heart"

    def test_rare_drop_with_0_chance_never(self):
        rare = RareDrops([{"item": "Dragon Heart", "chance": 0, "type": "material"}])
        for _ in range(20):
            drops = rare.roll()
            assert len(drops) == 0

    def test_rare_drop_has_type(self):
        rare = RareDrops([{"item": "Dragon Scale", "chance": 1000, "type": "material"}])
        drops = rare.roll()
        assert drops[0]["type"] == "material"

    def test_empty_rare_drops(self):
        rare = RareDrops([])
        assert rare.roll() == []


class TestLootEngine:
    """LootEngine integration."""

    @pytest.fixture
    def engine(self):
        loot_data = {
            "enemies": {
                "Goblin": {
                    "loot": {
                        "guaranteed": [{"item": "Gold", "min": 5, "max": 15}],
                        "random": [{"item": "Dagger", "chance": 100, "min": 1, "max": 1}],
                    },
                    "rare_drops": [
                        {"item": "Goblin Tooth", "chance": 1000, "type": "collectible"}
                    ],
                },
                "EmptyEnemy": {
                    "loot": {"guaranteed": [], "random": []},
                    "rare_drops": [],
                },
            }
        }
        items = {
            "weapons": {"Dagger": {"attack": 4, "rarity": "Common"}},
            "potions": {},
            "defends": {},
        }
        return LootEngine(loot_data, items)

    @pytest.fixture
    def mock_player(self):
        class MockPlayer:
            gold = 0
            inventory = {}
        return MockPlayer()

    @pytest.fixture
    def goblin(self):
        class MockEnemy:
            name = "Goblin"
        return MockEnemy()

    def test_roll_grants_gold(self, engine, goblin, mock_player):
        engine.roll_for_enemy(goblin, mock_player)
        assert mock_player.gold >= 5

    def test_roll_grants_items(self, engine, goblin, mock_player):
        engine.roll_for_enemy(goblin, mock_player)
        assert "Dagger" in mock_player.inventory

    def test_roll_grants_rare_drops(self, engine, goblin, mock_player):
        engine.roll_for_enemy(goblin, mock_player)
        assert "Goblin Tooth" in mock_player.inventory

    def test_roll_returns_drop_list(self, engine, goblin, mock_player):
        drops = engine.roll_for_enemy(goblin, mock_player)
        assert len(drops) > 0
        assert any(d["item"] == "Dagger" for d in drops)

    def test_rare_drop_flagged(self, engine, goblin, mock_player):
        drops = engine.roll_for_enemy(goblin, mock_player)
        rare_drops = [d for d in drops if d.get("rare")]
        assert len(rare_drops) > 0

    def test_unknown_enemy_returns_empty(self, engine, mock_player):
        class UnknownEnemy:
            name = "UnknownCreature"
        drops = engine.roll_for_enemy(UnknownEnemy(), mock_player)
        assert drops == []

    def test_case_insensitive_match(self, engine, mock_player):
        class CaseEnemy:
            name = "goblin"  # lowercase
        drops = engine.roll_for_enemy(CaseEnemy(), mock_player)
        assert len(drops) > 0

    def test_rarity_in_drops(self, engine, goblin, mock_player):
        drops = engine.roll_for_enemy(goblin, mock_player)
        for drop in drops:
            assert "rarity" in drop

    def test_display_drops_does_not_raise(self, engine, goblin, mock_player):
        drops = engine.roll_for_enemy(goblin, mock_player)
        LootEngine.display_drops(drops)

    def test_display_empty_drops(self, capsys):
        LootEngine.display_drops([])
        captured = capsys.readouterr()
        assert captured.out == ""
