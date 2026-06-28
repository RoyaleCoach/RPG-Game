"""
tests/test_enemy.py
------------------
Unit tests for Enemy, Boss, and MultiphaseBoss.
"""

import pytest
from core.enemy import Enemy, Boss, MultiphaseBoss, BossPhase, TheFirstHollow


class TestEnemyCreation:
    """Enemy initializes correctly."""

    def test_basic_enemy(self, basic_enemy):
        assert basic_enemy.name == "Goblin"
        assert basic_enemy.hp == 30
        assert basic_enemy.attack == 8

    def test_enemy_is_alive(self, basic_enemy):
        assert basic_enemy.is_alive is True

    def test_enemy_not_alive_at_zero_hp(self, basic_enemy):
        basic_enemy.hp = 0
        assert basic_enemy.is_alive is False

    def test_enemy_max_hp_set(self, basic_enemy):
        assert basic_enemy.max_hp == 30

    def test_enemy_hp_ratio(self, basic_enemy):
        basic_enemy.hp = 15
        assert basic_enemy.hp_ratio == 0.5

    def test_enemy_default_combat_stats(self, basic_enemy):
        # basic_enemy fixture: Enemy("Goblin", hp=30, attack=8) with defaults
        assert basic_enemy.critical_chance == 10  # default in Enemy.__init__
        assert basic_enemy.dodge == 5  # default in Enemy.__init__

    def test_enemy_spells_empty_by_default(self, basic_enemy):
        assert basic_enemy.spells == []


class TestEnemyAI:
    """Enemy AI decision making."""

    def test_choose_action_returns_valid(self, basic_enemy):
        valid = {"attack", "defend", "spell", "dodge"}
        for _ in range(50):
            action = basic_enemy.choose_action(mana=0)
            assert action in valid

    def test_low_hp_increases_defend(self, basic_enemy):
        basic_enemy.hp = 5  # < 30% of 30
        actions = [basic_enemy.choose_action(mana=0) for _ in range(200)]
        defend_count = actions.count("defend")
        assert defend_count > 20  # should be significantly more than baseline

    def test_spell_available_with_mana(self):
        enemy = Enemy("Mage", hp=50, attack=10, spells=["fireball"])
        enemy.max_hp = 50
        actions = [enemy.choose_action(mana=30) for _ in range(200)]
        assert "spell" in actions

    def test_no_spell_without_mana(self):
        enemy = Enemy("Mage", hp=50, attack=10, spells=["fireball"])
        enemy.max_hp = 50
        actions = [enemy.choose_action(mana=0) for _ in range(100)]
        assert "spell" not in actions

    def test_dodge_cooldown(self, basic_enemy):
        basic_enemy.dodge = 100
        basic_enemy._dodge_cooldown = 0
        basic_enemy.hp = basic_enemy.max_hp
        # Force several turns to find a dodge
        found = False
        for _ in range(200):
            action = basic_enemy.choose_action(mana=0)
            if action == "dodge":
                found = True
                break
        if found:
            assert basic_enemy._dodge_cooldown > 0


class TestEnemyFactory:
    """Enemy.random_enemy() factory."""

    def test_floor_1_pool(self):
        enemy = Enemy.random_enemy(1)
        names = {"Goblin", "Skeleton", "Dark Wolf", "Bomber"}
        assert enemy.name in names

    def test_floor_10_pool(self):
        enemy = Enemy.random_enemy(10)
        names = {"Venom Spider", "Ghoul", "Bone Archer", "Dark Shaman"}
        assert enemy.name in names

    def test_floor_20_pool(self):
        enemy = Enemy.random_enemy(20)
        names = {"Stone Golem", "Ogre", "Necromancer", "Giant"}
        assert enemy.name in names

    def test_floor_30_pool(self):
        enemy = Enemy.random_enemy(30)
        names = {"Doom Knight", "Abyss Walker"}
        assert enemy.name in names


class TestBoss:
    """Boss enemy."""

    def test_boss_creation(self, boss_enemy):
        assert boss_enemy.name == "Goblin King"
        assert boss_enemy.hp == 150
        assert boss_enemy.exp_reward == 100
        assert boss_enemy.gold_reward == 150

    def test_boss_is_enemy(self, boss_enemy):
        assert isinstance(boss_enemy, Enemy)


class TestMultiphaseBoss:
    """Multiphase boss behavior."""

    def _make_boss(self):
        phases = [
            BossPhase(phase_number=1, hp=300, attack=30),
            BossPhase(phase_number=2, hp=200, attack=50,
                      transition_message="Phase 2!"),
            BossPhase(phase_number=3, hp=100, attack=70),
        ]
        return MultiphaseBoss("TestBoss", phases, exp_reward=500, gold_reward=300)

    def test_initial_phase(self):
        boss = self._make_boss()
        assert boss.phase_number == 1
        assert boss.hp == 300

    def test_advance_phase(self):
        boss = self._make_boss()
        boss.hp = 0
        result = boss.try_advance_phase()
        assert result is True
        assert boss.phase_number == 2
        assert boss.hp == 200

    def test_advance_to_final_phase(self):
        boss = self._make_boss()
        boss.hp = 0
        boss.try_advance_phase()
        boss.hp = 0
        boss.try_advance_phase()
        assert boss.phase_number == 3
        assert boss.hp == 100

    def test_no_advance_after_final(self):
        boss = self._make_boss()
        boss.try_advance_phase()
        boss.try_advance_phase()
        result = boss.try_advance_phase()
        assert result is False

    def test_has_next_phase(self):
        boss = self._make_boss()
        assert boss.has_next_phase is True
        boss.try_advance_phase()
        boss.try_advance_phase()
        assert boss.has_next_phase is False

    def test_total_phases(self):
        boss = self._make_boss()
        assert boss.total_phases == 3

    def test_status_effects_cleared_on_advance(self):
        from core.status_effects import Burn
        boss = self._make_boss()
        boss.status_effects.append(Burn())
        boss.hp = 0
        boss.try_advance_phase()
        assert len(boss.status_effects) == 0

    def test_from_data_fallback(self):
        data = {"name": "SimpleBoss", "hp": 400, "attack": 40,
                "exp_reward": 200, "gold_reward": 100}
        boss = MultiphaseBoss.from_data(data)
        assert boss.total_phases == 2

    def test_from_data_with_phases(self):
        data = {
            "name": "MultiBoss",
            "exp_reward": 500, "gold_reward": 300,
            "phases": [
                {"hp": 300, "attack": 30},
                {"hp": 200, "attack": 50},
            ],
        }
        boss = MultiphaseBoss.from_data(data)
        assert boss.total_phases == 2
        assert boss.hp == 300


class TestTheFirstHollow:
    """Final boss."""

    def test_three_phases(self):
        boss = TheFirstHollow()
        assert boss.total_phases == 3

    def test_exp_reward(self):
        boss = TheFirstHollow()
        assert boss.exp_reward == 1000

    def test_gold_reward(self):
        boss = TheFirstHollow()
        assert boss.gold_reward == 500
