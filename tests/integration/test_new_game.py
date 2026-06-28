"""
tests/integration/test_new_game.py
--------------------------------
Integration test for new game creation.
"""

import pytest
from core.game_context import GameContext
from core.player import Player


class TestNewGame:
    """New game initialization."""

    def test_game_context_creates(self):
        ctx = GameContext()
        assert ctx is not None

    def test_player_creation(self, items_data):
        p = Player(name="NewHero", items=items_data, skill_points=1)
        p.initialize_items(items_data)
        assert p.name == "NewHero"
        assert p.level == 1

    def test_starting_inventory(self, items_data):
        p = Player(name="Hero", items=items_data)
        p.initialize_items(items_data)
        assert "Fists" in p.inventory

    def test_encyclopedia_sync_on_new_game(self, items_data):
        from core.encyclopedia import ItemEncyclopedia
        p = Player(name="Hero", items=items_data)
        p.initialize_items(items_data)
        enc = ItemEncyclopedia(items_data)
        enc.sync_with_player(p.inventory)
        assert enc.is_discovered("Fists")

    def test_loot_engine_available(self):
        ctx = GameContext()
        assert ctx.loot_engine is not None

    def test_encyclopedia_available(self):
        ctx = GameContext()
        assert ctx.encyclopedia is not None

    def test_combat_has_loot_engine(self):
        ctx = GameContext()
        assert ctx.combat._loot_engine is not None

    def test_combat_has_encyclopedia(self):
        ctx = GameContext()
        assert ctx.combat._encyclopedia is not None
