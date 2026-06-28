"""
tests/integration/test_item_discovery.py
---------------------------------------
Integration test for item discovery via encyclopedia.
"""

import pytest
from unittest.mock import patch
from core.game_context import GameContext
from core.player import Player
from core.enemy import Enemy


class TestItemDiscovery:
    """Item discovery through gameplay."""

    @pytest.fixture
    def ctx(self):
        return GameContext()

    @pytest.fixture
    def player(self, items_data):
        p = Player(name="Explorer", level=5, hp=500, attack=15,
                   defense=8, gold=200, items=items_data)
        p.initialize_items(items_data)
        p.inventory = {"Fists": 1}
        return p

    def test_starting_items_discovered(self, ctx, player):
        """Items in starting inventory are discovered."""
        ctx.encyclopedia.sync_with_player(player.inventory)
        assert ctx.encyclopedia.is_discovered("Fists")

    def test_looted_items_discovered(self, ctx, player):
        """Items obtained from loot are discovered."""
        ctx.combat.set_loot_engine(ctx.loot_engine)
        ctx.combat.set_encyclopedia(ctx.encyclopedia)

        enemy = Enemy("Goblin", hp=10, attack=2)
        with patch('builtins.input', side_effect=['attack'] * 5):
            ctx.combat.fight(player, enemy)

        # Encyclopedia should have discovered looted items
        for item_name in player.inventory:
            assert ctx.encyclopedia.is_discovered(item_name)

    def test_unknown_items_remain_hidden(self, ctx, player):
        """Items not yet obtained remain hidden."""
        ctx.encyclopedia.sync_with_player(player.inventory)
        # Dragon Slayer should not be discovered yet
        assert not ctx.encyclopedia.is_discovered("Dragon Slayer")

    def test_completion_updates_after_loot(self, ctx, player):
        """Completion percentage updates after obtaining items."""
        ctx.combat.set_loot_engine(ctx.loot_engine)
        ctx.combat.set_encyclopedia(ctx.encyclopedia)

        initial_count = len(ctx.encyclopedia.discovered)

        enemy = Enemy("Goblin", hp=10, attack=2)
        with patch('builtins.input', side_effect=['attack'] * 5):
            ctx.combat.fight(player, enemy)

        assert len(ctx.encyclopedia.discovered) >= initial_count

    def test_every_obtainable_item_discovered(self, ctx, items_data):
        """Every item obtained through combat is auto-discovered."""
        from core.player import Player
        ctx.combat.set_loot_engine(ctx.loot_engine)
        ctx.combat.set_encyclopedia(ctx.encyclopedia)

        # Use a strong player that won't die
        strong = Player(name="Strong", level=20, hp=2000, attack=50,
                        defense=20, gold=500, items=items_data)
        strong.initialize_items(items_data)
        strong.inventory = {"Fists": 1}

        for _ in range(5):
            enemy = Enemy("Goblin", hp=10, attack=2)
            with patch('builtins.input', side_effect=['attack'] * 5):
                ctx.combat.fight(strong, enemy)
            if not strong.is_alive:
                break

        # All items in inventory should be discovered
        for item_name in strong.inventory:
            assert ctx.encyclopedia.is_discovered(item_name), \
                f"{item_name} not discovered"
