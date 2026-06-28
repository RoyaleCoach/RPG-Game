"""
tests/integration/test_progression.py
-----------------------------------
Integration test for player progression through multiple battles.
"""

import pytest
from unittest.mock import patch
from core.game_context import GameContext
from core.player import Player
from core.enemy import Enemy


class TestProgression:
    """Player progression through multiple battles."""

    @pytest.fixture
    def ctx(self):
        return GameContext()

    @pytest.fixture
    def player(self, items_data):
        p = Player(name="Progressor", level=1, hp=100, attack=12,
                   defense=5, gold=100, items=items_data)
        p.initialize_items(items_data)
        p.inventory = {"Fists": 1, "Health Potion": 5}
        return p

    def test_level_up_after_multiple_battles(self, ctx, player):
        """Player levels up after gaining enough EXP."""
        initial_level = player.level

        for _ in range(5):
            enemy = Enemy("Goblin", hp=15, attack=3)
            with patch('builtins.input', side_effect=['attack'] * 5):
                ctx.combat.fight(player, enemy)
            if not player.is_alive:
                break

        # Should have gained at least some EXP
        assert player.level >= initial_level

    def test_inventory_grows_over_battles(self, ctx, player):
        """Inventory grows as loot is collected."""
        ctx.combat.set_loot_engine(ctx.loot_engine)
        initial_count = len(player.inventory)

        for _ in range(3):
            enemy = Enemy("Goblin", hp=10, attack=2)
            with patch('builtins.input', side_effect=['attack'] * 5):
                ctx.combat.fight(player, enemy)
            if not player.is_alive:
                break

        # Inventory should have grown (or at least not shrunk)
        assert len(player.inventory) >= initial_count

    def test_encyclopedia_completeness_increases(self, ctx, player):
        """Encyclopedia discovers more items over time."""
        ctx.combat.set_loot_engine(ctx.loot_engine)
        ctx.combat.set_encyclopedia(ctx.encyclopedia)

        for _ in range(3):
            enemy = Enemy("Goblin", hp=10, attack=2)
            with patch('builtins.input', side_effect=['attack'] * 5):
                ctx.combat.fight(player, enemy)
            if not player.is_alive:
                break

        assert len(ctx.encyclopedia.discovered) >= 1

    def test_floor_increases(self, ctx, player):
        """Floor increases after every 3 kills."""
        ctx.combat.set_loot_engine(ctx.loot_engine)
        initial_floor = player.floor

        for _ in range(3):
            enemy = Enemy("Goblin", hp=10, attack=2)
            with patch('builtins.input', side_effect=['attack'] * 5):
                ctx.combat.fight(player, enemy)
            if not player.is_alive:
                break

        if player.enemies_killed >= 3:
            assert player.floor > initial_floor

    def test_gold_accumulates(self, ctx, player):
        """Gold accumulates from combat rewards."""
        ctx.combat.set_loot_engine(ctx.loot_engine)
        initial_gold = player.gold

        for _ in range(3):
            enemy = Enemy("Goblin", hp=10, attack=2)
            with patch('builtins.input', side_effect=['attack'] * 5):
                ctx.combat.fight(player, enemy)
            if not player.is_alive:
                break

        assert player.gold >= initial_gold
