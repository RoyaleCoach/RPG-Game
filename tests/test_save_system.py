"""
tests/test_save_system.py
------------------------
Unit tests for the Save System.
"""

import os
import pytest
from core.save_system import SaveSystem
from core.player import Player


class MockGame:
    """Minimal mock game object for SaveSystem."""
    player = None


@pytest.fixture
def tmp_save_dir(tmp_path):
    """Create a temporary directory for saves."""
    return str(tmp_path)


@pytest.fixture
def savesystem(tmp_save_dir):
    """Create a SaveSystem with a temporary database."""
    game = MockGame()
    # Override db_path to use temp directory
    ss = SaveSystem(game)
    return ss


@pytest.fixture
def player(items_data):
    """Create a player for save/load tests."""
    p = Player(name="SaveTest", level=5, exp=50, hp=400,
               attack=15, defense=10, gold=200, items=items_data)
    p.initialize_items(items_data)
    p.inventory = {"Fists": 1, "Iron Sword": 1, "Health Potion": 3}
    p.learned_spells = ["icicle"]
    p.unlocked_skills = ["magic_apprentice"]
    p.enemies_killed = 10
    p.floor = 3
    return p


class TestSaveSystemInit:
    """SaveSystem initialization."""

    def test_db_initialized(self, savesystem):
        """Database should be initialized on creation."""
        assert os.path.exists(savesystem.db_path)

    def test_repos_created(self, savesystem):
        assert savesystem.player_repo is not None
        assert savesystem.inventory_repo is not None
        assert savesystem.quest_repo is not None


class TestSaveLoad:
    """Save and load workflow."""

    def test_save_creates_slot(self, savesystem, player):
        savesystem.game.player = player
        result = savesystem.save("test_slot")
        assert result is True

    def test_save_exists_after_save(self, savesystem, player):
        savesystem.game.player = player
        savesystem.save("test_slot")
        assert savesystem.save_exists("test_slot") is True

    def test_save_not_exists_before_save(self, savesystem):
        assert savesystem.save_exists("nonexistent") is False

    def test_load_returns_player(self, savesystem, player):
        savesystem.game.player = player
        savesystem.save("test_slot")
        loaded = savesystem.load("test_slot")
        assert loaded is not None
        assert isinstance(loaded, Player)

    def test_load_preserves_name(self, savesystem, player):
        savesystem.game.player = player
        savesystem.save("test_slot")
        loaded = savesystem.load("test_slot")
        assert loaded.name == "SaveTest"

    def test_load_preserves_level(self, savesystem, player):
        savesystem.game.player = player
        savesystem.save("test_slot")
        loaded = savesystem.load("test_slot")
        assert loaded.level == 5

    def test_load_preserves_gold(self, savesystem, player):
        savesystem.game.player = player
        savesystem.save("test_slot")
        loaded = savesystem.load("test_slot")
        assert loaded.gold == 200

    def test_load_preserves_inventory(self, savesystem, player):
        savesystem.game.player = player
        savesystem.save("test_slot")
        loaded = savesystem.load("test_slot")
        assert "Iron Sword" in loaded.inventory
        assert loaded.inventory["Health Potion"] == 3

    def test_load_preserves_spells(self, savesystem, player):
        savesystem.game.player = player
        savesystem.save("test_slot")
        loaded = savesystem.load("test_slot")
        assert "icicle" in loaded.learned_spells

    def test_load_preserves_floor(self, savesystem, player):
        savesystem.game.player = player
        savesystem.save("test_slot")
        loaded = savesystem.load("test_slot")
        assert loaded.floor == 3

    def test_load_preserves_statistics(self, savesystem, player):
        savesystem.game.player = player
        savesystem.save("test_slot")
        loaded = savesystem.load("test_slot")
        assert loaded.enemies_killed == 10

    def test_load_nonexistent_returns_none(self, savesystem):
        result = savesystem.load("nonexistent_slot")
        assert result is None

    def test_save_overwrite(self, savesystem, player):
        savesystem.game.player = player
        savesystem.save("slot1")
        player.gold = 999
        savesystem.save("slot1")
        loaded = savesystem.load("slot1")
        assert loaded.gold == 999


class TestDeleteSave:
    """Save deletion."""

    def test_delete_existing_save(self, savesystem, player):
        savesystem.game.player = player
        savesystem.save("to_delete")
        result = savesystem.delete_save("to_delete")
        assert result is True
        assert savesystem.save_exists("to_delete") is False

    def test_delete_nonexistent_save(self, savesystem):
        result = savesystem.delete_save("nonexistent")
        assert result is False


class TestBackwardCompatibility:
    """Backward compatibility with older save formats."""

    def test_load_with_defaults(self, savesystem):
        """Loading a save with missing fields should use defaults."""
        # This tests that the from_dict handles missing fields
        from core.player import Player
        legacy_data = {
            "player": {"name": "Legacy", "level": 1},
            "world": {},
            "loadout": {},
            "quests": {},
            "statistics": {},
            "flags": {},
        }
        p = Player.from_dict(legacy_data)
        assert p.name == "Legacy"
        assert p.critical_chance == 15  # default
        assert p.accuracy == 5  # default
