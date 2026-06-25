"""
Unit tests for Player class.
"""

import unittest
from core.player import Player


class TestPlayer(unittest.TestCase):
    """Tests for Player functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.player = Player(
            name="TestPlayer",
            hp=100,
            attack=10,
            defense=5,
            gold=50,
            level=1
        )

    def test_player_initialization(self):
        """Test player initialization."""
        self.assertEqual(self.player.name, "TestPlayer")
        self.assertEqual(self.player.hp, 100)
        self.assertEqual(self.player.attack, 10)
        self.assertEqual(self.player.defense, 5)
        self.assertEqual(self.player.gold, 50)

    def test_player_is_alive(self):
        """Test player alive status."""
        self.assertTrue(self.player.is_alive)
        self.player.hp = 0
        self.assertFalse(self.player.is_alive)

    def test_player_gain_exp(self):
        """Test experience gain and leveling."""
        initial_level = self.player.level
        self.player.gain_exp(100)
        self.assertEqual(self.player.level, initial_level + 1)

    def test_player_max_hp(self):
        """Test max HP calculation."""
        expected_max_hp = self.player.level * 100
        self.assertEqual(self.player.max_hp, expected_max_hp)

    def test_player_max_mana(self):
        """Test max mana calculation."""
        expected_max_mana = self.player.level * 10
        self.assertEqual(self.player.max_mana, expected_max_mana)

    def test_player_mana_property(self):
        """Test mana property clamping."""
        self.player.mana = 50
        self.assertEqual(self.player.mana, 50)
        
        # Test upper bound
        self.player.mana = 10000
        self.assertEqual(self.player.mana, self.player.max_mana)
        
        # Test lower bound
        self.player.mana = -10
        self.assertEqual(self.player.mana, 0)

    def test_player_learned_spells(self):
        """Test spell tracking."""
        self.assertEqual(len(self.player.learned_spells), 0)
        self.player.learned_spells.append("icicle")
        self.assertIn("icicle", self.player.learned_spells)

    def test_player_to_dict(self):
        """Test player serialization."""
        self.player.learned_spells = ["icicle"]
        player_dict = self.player.to_dict()
        
        self.assertIn("name", player_dict)
        self.assertIn("hp", player_dict)
        self.assertIn("mana", player_dict)
        self.assertIn("learned_spells", player_dict)
        self.assertEqual(player_dict["name"], "TestPlayer")
        self.assertEqual(player_dict["learned_spells"], ["icicle"])


if __name__ == "__main__":
    unittest.main()
