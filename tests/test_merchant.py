"""
tests/test_merchant.py
---------------------
Unit tests for the Merchant system.
"""

import pytest
from unittest.mock import patch
from world.merchant import Merchant
from core.player import Player


@pytest.fixture
def merchant(items_data):
    return Merchant(items_data)


@pytest.fixture
def player(items_data):
    p = Player(name="Buyer", gold=500, items=items_data)
    p.initialize_items(items_data)
    return p


class TestMerchantInit:
    """Merchant initialization."""

    def test_items_loaded(self, merchant):
        assert len(merchant.items) > 0

    def test_limited_items_excluded(self, merchant):
        """Limited/quest items should not appear in shop."""
        # Guardian Plate is limited=True
        assert "Guardian Plate" not in merchant.items

    def test_items_have_prices(self, merchant):
        for item, price in merchant.items.items():
            assert isinstance(price, int)
            assert price >= 0


class TestMerchantTrade:
    """Buying items."""

    def test_buy_item_deducts_gold(self, merchant, player):
        # Find an affordable item
        affordable = {k: v for k, v in merchant.items.items() if v <= player.gold}
        if not affordable:
            pytest.skip("No affordable items")

        item_name = list(affordable.keys())[0]
        price = affordable[item_name]
        old_gold = player.gold

        with patch('builtins.input', side_effect=[item_name, '0']):
            merchant.trade(player)

        assert player.gold == old_gold - price
        assert item_name in player.inventory

    def test_buy_item_insufficient_gold(self, merchant, player):
        player.gold = 0
        old_inventory = dict(player.inventory)

        with patch('builtins.input', side_effect=['0']):
            merchant.trade(player)

        assert player.inventory == old_inventory

    def test_exit_without_buying(self, merchant, player):
        old_gold = player.gold
        with patch('builtins.input', return_value='0'):
            merchant.trade(player)
        assert player.gold == old_gold
