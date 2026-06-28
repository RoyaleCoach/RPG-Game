"""
tests/test_skills.py
-------------------
Unit tests for the Skill system.
"""

import pytest
from core.skill import Skill
from core.player import Player


@pytest.fixture
def spells():
    return {
        "fireball": {"type": "aoe/damage", "level": 3, "cost": 20, "obtain": "boss"},
        "icicle": {"type": "st/damage", "level": 2, "cost": 10, "obtain": "merchant"},
        "minor_healing": {"type": "st/heal", "level": 2, "cost": 10, "obtain": "merchant"},
        "stone_skin": {"type": "st/buff", "level": 4, "cost": 15, "obtain": "dungeon"},
    }


@pytest.fixture
def skill(spells):
    return Skill(spells)


@pytest.fixture
def player(spells):
    from core.player import Player
    p = Player(name="Mage", items={"weapons": {}, "potions": {}, "defends": {}})
    return p


class TestSkillInit:
    """Skill system initialization."""

    def test_spells_loaded(self, skill, spells):
        assert len(skill.spells) == len(spells)

    def test_empty_spells(self):
        s = Skill({})
        assert s.spells == {}

    def test_default_none_spells(self):
        s = Skill()
        assert s.spells == {}


class TestSkillLookup:
    """Spell lookup functions."""

    def test_get_existing_spell(self, skill):
        spell = skill.get_spell("icicle")
        assert spell is not None
        assert spell["cost"] == 10

    def test_get_nonexistent_spell(self, skill):
        assert skill.get_spell("nonexistent") is None

    def test_get_spells_by_obtain(self, skill):
        dungeon_spells = skill.get_spells_by_obtain("dungeon")
        assert "stone_skin" in dungeon_spells

    def test_get_available_spells(self, skill, player):
        player.learned_spells = ["icicle", "fireball"]
        available = skill.get_available_spells(player)
        assert "icicle" in available
        assert "fireball" in available

    def test_get_available_spells_empty(self, skill, player):
        assert skill.get_available_spells(player) == {}


class TestSkillLearn:
    """Learning spells."""

    def test_learn_new_spell(self, skill, player):
        assert skill.learn_spell(player, "icicle") is True
        assert "icicle" in player.learned_spells

    def test_learn_duplicate_spell(self, skill, player):
        skill.learn_spell(player, "icicle")
        assert skill.learn_spell(player, "icicle") is False

    def test_learn_unknown_spell(self, skill, player):
        assert skill.learn_spell(player, "unknown") is False
        assert "unknown" not in player.learned_spells

    def test_learn_random_spell(self, skill, player):
        import random
        random.seed(42)
        spell = skill.learn_random_spell(player, "merchant")
        assert spell is not None
        assert spell in player.learned_spells

    def test_learn_random_no_available(self, skill, player):
        player.learned_spells = list(skill.spells.keys())
        spell = skill.learn_random_spell(player, "merchant")
        assert spell is None
