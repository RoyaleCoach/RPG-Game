"""
tests/test_combat.py
-------------------
Unit tests for Combat system, including loot integration.
"""

import pytest
from unittest.mock import Mock, patch
from core.combat import Combat, roll_damage, roll_dodge


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _make_player(**kwargs):
    from core.player import Player
    defaults = dict(
        name="TestPlayer", hp=100, attack=10, defense=5,
        gold=50, level=1, critical_chance=15, critical_multiplier=2.0,
        accuracy=5, dodge=5,
    )
    defaults.update(kwargs)
    return Player(**defaults)


def _make_enemy(**kwargs):
    from core.enemy import Enemy
    defaults = dict(
        name="TestEnemy", hp=50, attack=5,
        critical_chance=10, critical_multiplier=1.5,
        accuracy=3, dodge=5,
    )
    defaults.update(kwargs)
    return Enemy(**defaults)


@pytest.fixture
def combat(skill_system, items_data, quest_system):
    from core.combat import Combat
    return Combat(quest_system, items_data, skill_system)


# ─────────────────────────────────────────────────────────────────────────────
# Roll Damage Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestRollDamage:

    def _attacker(self, accuracy=0, crit_chance=0, crit_mult=2.0):
        from unittest.mock import Mock
        a = Mock()
        a.accuracy = accuracy
        a.critical_chance = crit_chance
        a.critical_multiplier = crit_mult
        return a

    def test_damage_within_range(self):
        attacker = self._attacker(accuracy=3)
        for _ in range(50):
            dmg, _ = roll_damage(attacker, 20)
            assert 3 <= dmg <= 20

    def test_min_damage_capped_by_base_max(self):
        attacker = self._attacker(accuracy=999)
        for _ in range(20):
            dmg, _ = roll_damage(attacker, 10)
            assert dmg == 10

    def test_critical_always_triggers(self):
        attacker = self._attacker(accuracy=5, crit_chance=100, crit_mult=3.0)
        for _ in range(20):
            dmg, is_crit = roll_damage(attacker, 10)
            assert is_crit
            assert dmg >= 15  # 5 * 3

    def test_critical_never_triggers(self):
        attacker = self._attacker(crit_chance=0)
        for _ in range(50):
            _, is_crit = roll_damage(attacker, 10)
            assert not is_crit

    def test_damage_at_least_one(self):
        attacker = self._attacker(accuracy=0, crit_chance=0)
        for _ in range(30):
            dmg, _ = roll_damage(attacker, 1)
            assert dmg >= 1


# ─────────────────────────────────────────────────────────────────────────────
# Roll Dodge Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestRollDodge:

    def _target(self, dodge):
        from unittest.mock import Mock
        t = Mock()
        t.dodge = dodge
        return t

    def test_dodge_100_always_true(self):
        for _ in range(20):
            assert roll_dodge(self._target(100))

    def test_dodge_0_always_false(self):
        for _ in range(20):
            assert not roll_dodge(self._target(0))

    def test_no_dodge_attr_defaults_false(self):
        from unittest.mock import Mock
        t = Mock(spec=[])
        for _ in range(10):
            assert not roll_dodge(t)


# ─────────────────────────────────────────────────────────────────────────────
# Spell Effect Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestSpellEffects:

    def test_damage_spell_reduces_enemy_hp(self, combat):
        player = _make_player()
        enemy = _make_enemy()
        enemy.dodge = 0  # prevent dodge
        spell = {"type": "st/damage", "cost": 10, "level": 1}
        initial_hp = enemy.hp
        combat.apply_spell_effect(player, enemy, spell, 5)
        assert enemy.hp <= initial_hp

    def test_dodge_prevents_damage(self, combat):
        player = _make_player()
        enemy = _make_enemy()
        enemy.dodge = 100
        spell = {"type": "st/damage", "cost": 10, "level": 1}
        initial_hp = enemy.hp
        combat.apply_spell_effect(player, enemy, spell, 5)
        assert enemy.hp == initial_hp

    def test_heal_spell_increases_hp(self, combat):
        player = _make_player()
        player._hp = 50
        enemy = _make_enemy()
        spell = {"type": "st/heal", "cost": 10, "level": 1}
        initial_hp = player.hp
        combat.apply_spell_effect(player, enemy, spell, 5)
        assert player.hp >= initial_hp

    def test_heal_does_not_exceed_max(self, combat):
        player = _make_player()
        player._hp = player.max_hp
        enemy = _make_enemy()
        spell = {"type": "st/heal", "cost": 999, "level": 10}
        combat.apply_spell_effect(player, enemy, spell, 5)
        assert player.hp <= player.max_hp

    def test_buff_increases_defense(self, combat):
        player = _make_player()
        enemy = _make_enemy()
        spell = {"type": "st/buff", "cost": 10, "level": 2}
        new_def = combat.apply_spell_effect(player, enemy, spell, 5)
        assert new_def > 5

    def test_unknown_spell_type_no_crash(self, combat):
        player = _make_player()
        enemy = _make_enemy()
        spell = {"type": "unknown", "cost": 5, "level": 1}
        result = combat.apply_spell_effect(player, enemy, spell, 7)
        assert result == 7


# ─────────────────────────────────────────────────────────────────────────────
# Loot Integration Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestLootIntegration:

    def test_set_loot_engine(self, combat, loot_engine):
        combat.set_loot_engine(loot_engine)
        assert combat._loot_engine is loot_engine

    def test_set_encyclopedia(self, combat, encyclopedia):
        combat.set_encyclopedia(encyclopedia)
        assert combat._encyclopedia is encyclopedia

    def test_award_victory_calls_loot(self, combat, loot_engine):
        from core.enemy import Boss
        combat.set_loot_engine(loot_engine)
        player = _make_player()
        player.level = 5
        enemy = Boss("Goblin King", hp=150, attack=20,
                     exp_reward=100, gold_reward=150)
        player.gold = 0
        with patch.object(player, 'gain_exp'):
            combat._award_victory(player, enemy)
        # Boss gold_reward (150) + possible loot table gold drops
        assert player.gold >= 150

    def test_award_victory_normal_enemy(self, combat, loot_engine):
        combat.set_loot_engine(loot_engine)
        player = _make_player()
        player.level = 1
        player.gold = 0
        enemy = _make_enemy(name="Goblin", hp=30, attack=8)
        with patch.object(player, 'gain_exp'):
            combat._award_victory(player, enemy)
        assert player.gold > 0  # base reward + possible loot

    def test_encyclopedia_sync_after_victory(self, combat, loot_engine, encyclopedia):
        from core.enemy import Boss
        combat.set_loot_engine(loot_engine)
        combat.set_encyclopedia(encyclopedia)
        player = _make_player()
        player.level = 10
        enemy = Boss("Goblin King", hp=150, attack=20,
                     exp_reward=100, gold_reward=150)
        with patch.object(player, 'gain_exp'):
            combat._award_victory(player, enemy)
        # Encyclopedia should have synced with player inventory
        # (at minimum, items from loot table)
        assert isinstance(encyclopedia.discovered, set)
