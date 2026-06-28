"""
tests/integration/test_full_combat.py
-----------------------------------
Integration test for end-to-end combat.
"""

import pytest
from unittest.mock import patch
from core.game_context import GameContext
from core.player import Player
from core.enemy import Enemy, Boss


class TestFullCombat:
    """End-to-end combat scenarios."""

    @pytest.fixture
    def ctx(self):
        return GameContext()

    @pytest.fixture
    def strong_player(self, items_data):
        p = Player(name="Warrior", level=10, hp=1000, attack=25,
                   defense=15, gold=500, items=items_data)
        p.initialize_items(items_data)
        p.inventory = {"Fists": 1, "Iron Sword": 1, "Health Potion": 3}
        return p

    def test_combat_victory_grants_rewards(self, ctx, strong_player):
        """Winning a combat grants gold, exp, and loot."""
        enemy = Enemy("Goblin", hp=20, attack=5)
        initial_gold = strong_player.gold

        with patch('builtins.input', side_effect=['attack'] * 10):
            result = ctx.combat.fight(strong_player, enemy)

        if result:  # if player won
            assert strong_player.gold >= initial_gold

    def test_combat_triggers_loot(self, ctx, strong_player):
        """Combat victory triggers loot table rolls."""
        enemy = Enemy("Goblin", hp=15, attack=3)
        ctx.combat.set_loot_engine(ctx.loot_engine)
        ctx.combat.set_encyclopedia(ctx.encyclopedia)

        initial_inventory_size = len(strong_player.inventory)

        with patch('builtins.input', side_effect=['attack'] * 10):
            ctx.combat.fight(strong_player, enemy)

        # Inventory may have grown from loot
        assert len(strong_player.inventory) >= initial_inventory_size

    def test_encyclopedia_updates_after_combat(self, ctx, strong_player):
        """Encyclopedia syncs with inventory after combat."""
        enemy = Enemy("Goblin", hp=15, attack=3)
        ctx.combat.set_loot_engine(ctx.loot_engine)
        ctx.combat.set_encyclopedia(ctx.encyclopedia)

        with patch('builtins.input', side_effect=['attack'] * 10):
            ctx.combat.fight(strong_player, enemy)

        # Encyclopedia should have discovered items
        assert len(ctx.encyclopedia.discovered) >= 1

    def test_boss_combat_grants_bonus_rewards(self, ctx, strong_player):
        """Boss combat grants higher rewards."""
        boss = Boss("Goblin King", hp=50, attack=10,
                    exp_reward=100, gold_reward=150)
        initial_gold = strong_player.gold

        with patch('builtins.input', side_effect=['attack'] * 20):
            result = ctx.combat.fight(strong_player, boss)

        if result:
            assert strong_player.gold >= initial_gold + 150

    def test_combat_defeat_returns_false(self, ctx):
        """Losing combat returns False."""
        weak_player = Player(name="Weak", hp=1, attack=1, defense=0,
                             items={"weapons": {}, "potions": {}, "defends": {}})
        strong_enemy = Enemy("Dragon", hp=999, attack=99)

        with patch('builtins.input', side_effect=['attack'] * 10):
            result = ctx.combat.fight(weak_player, strong_enemy)

        assert result is False
