"""
tests/integration/test_save_load.py
---------------------------------
Integration test for save/load workflow.
"""

import pytest
from core.save_system import SaveSystem
from core.player import Player
from core.encyclopedia import ItemEncyclopedia


class MockGame:
    player = None


@pytest.fixture
def savesystem():
    game = MockGame()
    return SaveSystem(game)


@pytest.fixture
def player_with_progress(items_data):
    p = Player(name="SaveHero", level=5, exp=50, hp=400,
               attack=15, defense=10, gold=300, items=items_data)
    p.initialize_items(items_data)
    p.inventory = {"Fists": 1, "Iron Sword": 1, "Health Potion": 5}
    p.learned_spells = ["icicle", "fireball"]
    p.unlocked_skills = ["magic_apprentice"]
    p.enemies_killed = 15
    p.floor = 4
    p.puzzles_solved = 2
    p.story_progress = 3
    return p


class TestSaveLoadWorkflow:
    """Complete save/load workflow."""

    def test_full_save_load_cycle(self, savesystem, player_with_progress):
        savesystem.game.player = player_with_progress
        savesystem.save("integration_test")

        loaded = savesystem.load("integration_test")
        assert loaded is not None
        assert loaded.name == "SaveHero"
        assert loaded.level == 5

    def test_inventory_preserved(self, savesystem, player_with_progress):
        savesystem.game.player = player_with_progress
        savesystem.save("inv_test")

        loaded = savesystem.load("inv_test")
        assert "Iron Sword" in loaded.inventory
        assert loaded.inventory["Health Potion"] == 5

    def test_spells_preserved(self, savesystem, player_with_progress):
        savesystem.game.player = player_with_progress
        savesystem.save("spell_test")

        loaded = savesystem.load("spell_test")
        assert "icicle" in loaded.learned_spells
        assert "fireball" in loaded.learned_spells

    def test_world_state_preserved(self, savesystem, player_with_progress):
        savesystem.game.player = player_with_progress
        savesystem.save("world_test")

        loaded = savesystem.load("world_test")
        assert loaded.floor == 4
        assert loaded.enemies_killed == 15

    def test_combat_stats_preserved(self, savesystem, player_with_progress):
        savesystem.game.player = player_with_progress
        player_with_progress.critical_chance = 25
        player_with_progress.accuracy = 10
        player_with_progress.dodge = 12
        savesystem.save("combat_test")

        loaded = savesystem.load("combat_test")
        assert loaded.critical_chance == 25
        assert loaded.accuracy == 10
        assert loaded.dodge == 12

    def test_multiple_saves_independent(self, savesystem, player_with_progress):
        savesystem.game.player = player_with_progress
        savesystem.save("slot_a")

        player_with_progress.gold = 999
        savesystem.save("slot_b")

        loaded_a = savesystem.load("slot_a")
        loaded_b = savesystem.load("slot_b")
        assert loaded_a.gold != loaded_b.gold
