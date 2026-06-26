"""
Unit tests for Inventory system.
"""

import unittest
from core.inventory import Inventory
from core.player import Player


class TestInventory(unittest.TestCase):
    """Tests for Inventory functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.items = {
            "weapons": {
                "Iron Sword": {
                    "attack": 5,
                    "rarity": "common"
                },
                "Steel Sword": {
                    "attack": 10,
                    "rarity": "uncommon"
                }
            },
            "defends": {
                "Iron Armor": {
                    "defense": 3,
                    "rarity": "common"
                }
            },
            "potions": {
                "health_potion": {
                    "effect": 50,
                    "rarity": "common"
                }
            }
        }

        self.inventory = Inventory(self.items)

        self.player = Player(
            name="TestPlayer",
            hp=100,
            attack=10,
            defense=5,
            level=1,
            items=self.items
        )

    def test_inventory_initialization(self):
        """Test inventory initialization."""
        self.assertIn("weapons", self.items)
        self.assertIn("defends", self.items)
        self.assertIn("potions", self.items)

    def test_player_inventory(self):
        """Test player inventory."""
        self.assertIsNotNone(self.player.inventory)
        self.assertIn("Fists", self.player.inventory)

    def test_player_weapons(self):
        """Test player weapon data."""
        self.assertIsNotNone(self.player.weapons)
        self.assertIn("Iron Sword", self.player.weapons)

    def test_player_potions(self):
        """Test player potion data."""
        self.assertIsNotNone(self.player.potions)
        self.assertIn("health_potion", self.player.potions)

    def test_player_armor(self):
        """Test player armor data."""
        self.assertIsNotNone(self.player.defends)
        self.assertIn("Iron Armor", self.player.defends)

    def test_add_to_inventory(self):
        """Test adding items to inventory."""
        self.player.inventory["health_potion"] = self.player.inventory.get(
            "health_potion", 0) + 1
        self.assertGreater(self.player.inventory.get("health_potion", 0), 0)

    def test_weapon_attack_bonus(self):
        """Test weapon attack bonus."""
        self.player.weapon = "Iron Sword"
        expected_attack = self.player._base_attack + \
            self.items["weapons"]["Iron Sword"]["attack"]
        self.assertEqual(self.player.attack, expected_attack)

    def test_armor_defense_bonus(self):
        """Test armor defense bonus."""
        self.player.armor = "Iron Armor"
        expected_defense = self.player._base_defense + \
            self.items["defends"]["Iron Armor"]["defense"]
        self.assertEqual(self.player.defense, expected_defense)


if __name__ == "__main__":
    unittest.main()
