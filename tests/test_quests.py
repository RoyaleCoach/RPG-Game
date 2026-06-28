"""
tests/test_quests.py
-------------------
Unit tests for the Quest system.
"""

import pytest
from world.quest import QuestSystem
from core.player import Player


@pytest.fixture
def quests_data():
    return {
        "Test Kill Quest": {
            "description": "Defeat 5 enemies.",
            "type": "kills",
            "target": 5,
            "reward": "Iron Sword",
            "reward_gold": 100,
        },
        "Test Floor Quest": {
            "description": "Reach Floor 10.",
            "type": "floor",
            "target": 10,
            "reward": "Dragon Slayer",
            "reward_gold": 500,
        },
    }


@pytest.fixture
def quest_system(quests_data):
    return QuestSystem(quests_data)


@pytest.fixture
def player(items_data):
    p = Player(name="QuestTester", items=items_data)
    p.initialize_items(items_data)
    return p


class TestQuestProgress:
    """Quest progress tracking."""

    def test_kills_progress(self, quest_system, player):
        player.enemies_killed = 3
        progress = quest_system.get_progress(player, "kills")
        assert progress == 3

    def test_floor_progress(self, quest_system, player):
        player.floor = 7
        progress = quest_system.get_progress(player, "floor")
        assert progress == 7

    def test_level_progress(self, quest_system, player):
        player.level = 5
        progress = quest_system.get_progress(player, "level")
        assert progress == 5

    def test_puzzle_progress(self, quest_system, player):
        player.puzzles_solved = 3
        progress = quest_system.get_progress(player, "puzzle")
        assert progress == 3

    def test_unknown_type_returns_zero(self, quest_system, player):
        assert quest_system.get_progress(player, "unknown") == 0


class TestQuestCompletion:
    """Quest completion and rewards."""

    def test_quest_not_completed_initially(self, quest_system, player):
        assert "Test Kill Quest" not in player.completed_quests

    def test_quest_completes_on_target(self, quest_system, player):
        player.enemies_killed = 5
        quest_system.check(player)
        assert "Test Kill Quest" in player.completed_quests

    def test_quest_gives_reward_item(self, quest_system, player):
        player.enemies_killed = 5
        quest_system.check(player)
        assert "Iron Sword" in player.inventory

    def test_quest_gives_reward_gold(self, quest_system, player):
        player.enemies_killed = 5
        old_gold = player.gold
        quest_system.check(player)
        assert player.gold == old_gold + 100

    def test_quest_not_completed_below_target(self, quest_system, player):
        player.enemies_killed = 3
        quest_system.check(player)
        assert "Test Kill Quest" not in player.completed_quests

    def test_duplicate_completion_prevented(self, quest_system, player):
        player.enemies_killed = 5
        quest_system.check(player)
        quest_system.check(player)  # check again
        # Should only get reward once
        assert player.inventory.get("Iron Sword", 0) == 1

    def test_floor_quest_completes(self, quest_system, player):
        player.floor = 10
        quest_system.check(player)
        assert "Test Floor Quest" in player.completed_quests
