"""
tests/test_inventory.py
----------------------
Unit tests for Inventory.
"""

import pytest
from unittest.mock import patch
from core.inventory import Inventory
from core.player import Player


class TestInventoryItems:
    """Inventory item management."""

    def test_weapons_loaded(self, inventory, items_data):
        assert len(inventory.weapons) > 0
        assert "Iron Sword" in inventory.weapons

    def test_potions_loaded(self, inventory, items_data):
        assert len(inventory.potions) > 0
        assert "Health Potion" in inventory.potions

    def test_defends_loaded(self, inventory, items_data):
        assert len(inventory.defends) > 0
        assert "Leather Armour" in inventory.defends

    def test_weapon_has_rarity(self, inventory):
        assert "rarity" in inventory.weapons["Iron Sword"]

    def test_potion_has_rarity(self, inventory):
        assert "rarity" in inventory.potions["Health Potion"]

    def test_armor_has_rarity(self, inventory):
        assert "rarity" in inventory.defends["Leather Armour"]


class TestInventoryAddRemove:
    """Adding and removing items from player inventory."""

    def test_add_item(self, player):
        player.inventory["Iron Sword"] = 1
        assert player.inventory["Iron Sword"] == 1

    def test_stack_items(self, player):
        player.inventory["Health Potion"] = 1
        player.inventory["Health Potion"] += 1
        assert player.inventory["Health Potion"] == 2

    def test_remove_item(self, player):
        player.inventory["Iron Sword"] = 1
        del player.inventory["Iron Sword"]
        assert "Iron Sword" not in player.inventory


class TestInventoryEquip:
    """Equipping items."""

    def test_equip_weapon(self, player, items_data):
        player.inventory["Iron Sword"] = 1
        player.level = 5
        player.equip_weapon("Iron Sword")
        assert player.weapon == "Iron Sword"

    def test_equip_armor(self, player, items_data):
        player.inventory["Leather Armour"] = 1
        player.level = 2  # Leather Armour requires level 2
        player.equip_defense("Leather Armour")
        assert player.armor == "Leather Armour"

    def test_equip_unknown_weapon(self, player):
        player.equip_weapon("Unknown Weapon")
        assert player.weapon == "Fists"

    def test_equip_weapon_not_in_inventory(self, player):
        player.equip_weapon("Dragon Slayer")
        assert player.weapon == "Fists"


class TestInventoryRarityDisplay:
    """Rarity labels in inventory display."""

    def test_weapon_rarity_label(self, inventory):
        from core.rarity import get_rarity_label
        sword = inventory.weapons["Iron Sword"]
        label = get_rarity_label(sword["rarity"])
        assert label == "[Uncommon]"

    def test_common_rarity_label(self, inventory):
        from core.rarity import get_rarity_label
        fists = inventory.weapons["Fists"]
        label = get_rarity_label(fists["rarity"])
        assert label == "[Common]"

    def test_legendary_rarity_label(self, inventory):
        from core.rarity import get_rarity_label
        ds = inventory.weapons["Dragon Slayer"]
        label = get_rarity_label(ds["rarity"])
        assert label == "[Legendary]"


class TestInventoryDisplay:
    """Inventory display doesn't crash."""

    def test_open_displays_without_error(self, inventory, player, capsys):
        # Mock input to exit immediately
        with patch('builtins.input', return_value='0'):
            inventory.open(player)
        captured = capsys.readouterr()
        assert "INVENTORY" in captured.out
