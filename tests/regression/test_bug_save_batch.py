"""
tests/regression/test_bug_save_batch.py
--------------------------------------
Regression tests for save system batch operations.

Prevents regression where:
- executemany receives incorrect parameters
- active quests fail to save
- completed quests fail to save
- inventory batch inserts fail
"""

import pytest
from core.save_system import SaveSystem
from core.player import Player


class MockGame:
    player = None


@pytest.fixture
def savesystem():
    return SaveSystem(MockGame())


@pytest.fixture
def player(items_data):
    p = Player(name="BatchTest", level=3, exp=50, hp=300,
               attack=12, defense=8, gold=150, items=items_data)
    p.initialize_items(items_data)
    p.inventory = {"Fists": 1, "Iron Sword": 1, "Health Potion": 5,
                   "Leather Armour": 1, "Mana Potion": 2}
    p.learned_spells = ["icicle", "fireball"]
    p.unlocked_skills = ["magic_apprentice"]
    p.quest = [
        {"name": "Kill Goblins", "progress": 3, "target": 10},
        {"name": "Find Artifact", "progress": 0, "target": 1},
    ]
    p.completed_quests = ["Tutorial"]
    p.enemies_killed = 7
    p.floor = 2
    return p


class TestInventoryBatchSave:
    """Inventory batch operations."""

    def test_inventory_saves_all_items(self, savesystem, player):
        """All inventory items should be saved."""
        savesystem.game.player = player
        savesystem.save("batch_test")
        loaded = savesystem.load("batch_test")
        assert loaded is not None
        for item_name in player.inventory:
            assert item_name in loaded.inventory, \
                f"{item_name} not saved"

    def test_inventory_quantities_preserved(self, savesystem, player):
        """Item quantities should be preserved."""
        savesystem.game.player = player
        savesystem.save("qty_test")
        loaded = savesystem.load("qty_test")
        assert loaded.inventory["Health Potion"] == 5
        assert loaded.inventory["Mana Potion"] == 2

    def test_empty_inventory_saves(self, savesystem, player):
        """Empty inventory (except Fists) should save without error."""
        player.inventory = {"Fists": 1}
        savesystem.game.player = player
        result = savesystem.save("empty_inv")
        assert result is True


class TestQuestBatchSave:
    """Quest batch operations."""

    def test_active_quests_saved(self, savesystem, player):
        """Active quests should be saved."""
        savesystem.game.player = player
        savesystem.save("quest_test")
        loaded = savesystem.load("quest_test")
        assert loaded is not None
        assert len(loaded.quest) == len(player.quest)

    def test_completed_quests_saved(self, savesystem, player):
        """Completed quests should be saved."""
        savesystem.game.player = player
        savesystem.save("completed_test")
        loaded = savesystem.load("completed_test")
        assert "Tutorial" in loaded.completed_quests

    def test_empty_quests_saved(self, savesystem, player):
        """Empty quest lists should save without error."""
        player.quest = []
        player.completed_quests = []
        savesystem.game.player = player
        result = savesystem.save("empty_quests")
        assert result is True


class TestLoadBatchIntegrity:
    """Load operations should restore all data correctly."""

    def test_full_round_trip(self, savesystem, player):
        """Complete save/load round-trip preserves all data."""
        savesystem.game.player = player
        savesystem.save("full_test")
        loaded = savesystem.load("full_test")

        assert loaded.name == player.name
        assert loaded.level == player.level
        assert loaded.gold == player.gold
        assert loaded.floor == player.floor
        assert loaded.enemies_killed == player.enemies_killed
        assert len(loaded.inventory) == len(player.inventory)
        assert len(loaded.learned_spells) == len(player.learned_spells)
        assert len(loaded.quest) == len(player.quest)
        assert len(loaded.completed_quests) == len(player.completed_quests)

    def test_multiple_save_load_cycles(self, savesystem, player):
        """Multiple save/load cycles should not corrupt data."""
        savesystem.game.player = player

        for i in range(3):
            savesystem.save(f"cycle_{i}")
            loaded = savesystem.load(f"cycle_{i}")
            assert loaded is not None
            assert loaded.name == player.name
