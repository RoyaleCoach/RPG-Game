"""
Unit tests for Combat system.
"""

import unittest
from unittest.mock import Mock, patch
from core.combat import Combat
from core.player import Player
from core.enemy import Enemy
from core.skill import Skill


class TestCombat(unittest.TestCase):
    """Tests for Combat functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.quest_system = Mock()
        self.quest_system.check = Mock()

        self.items = {
            "potions": {
                "health_potion": {"effect": 50}
            }
        }

        self.spells = {
            "icicle": {
                "cost": 10,
                "type": "st/damage",
                "description": "[caster] casts icicle!"
            }
        }

        self.skill_system = Skill(self.spells)

        self.combat = Combat(
            self.quest_system,
            self.items,
            self.skill_system
        )

        self.player = Player(
            name="TestPlayer",
            hp=100,
            attack=10,
            defense=5,
            gold=50,
            level=1
        )

        self.enemy = Enemy(
            name="TestEnemy",
            hp=50,
            attack=5
        )

    def test_combat_initialization(self):
        """Test combat system initialization."""
        self.assertEqual(self.combat.quest_system, self.quest_system)
        self.assertEqual(self.combat.skill_system, self.skill_system)
        self.assertIn("potions", self.items)

    def test_spell_effect_damage(self):
        """Test spell damage effect."""
        spell = {"type": "st/damage", "cost": 10, "level": 1}
        initial_hp = self.enemy.hp

        battle_def = self.combat.apply_spell_effect(
            self.player,
            self.enemy,
            spell,
            5
        )

        self.assertLess(self.enemy.hp, initial_hp)

    def test_spell_effect_heal(self):
        """Test spell healing effect."""
        spell = {"type": "heal", "cost": 10, "level": 1}
        self.player.hp = 50
        initial_hp = self.player.hp

        self.combat.apply_spell_effect(
            self.player,
            self.enemy,
            spell,
            5
        )

        self.assertGreater(self.player.hp, initial_hp)

    def test_spell_effect_buff(self):
        """Test spell buff effect."""
        spell = {"type": "buff", "cost": 10, "level": 2}
        initial_def = 5

        new_def = self.combat.apply_spell_effect(
            self.player,
            self.enemy,
            spell,
            initial_def
        )

        self.assertGreater(new_def, initial_def)

    def test_potion_availability(self):
        """Test potion lookup."""
        self.assertIn("health_potion", self.items["potions"])


if __name__ == "__main__":
    unittest.main()
