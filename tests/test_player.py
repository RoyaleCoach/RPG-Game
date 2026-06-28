"""
tests/test_player.py
-------------------
Unit tests for Player class.
"""

import pytest
from core.player import Player


class TestPlayerInitialization:
    """Player initializes with correct defaults."""

    def test_default_name(self, player):
        assert player.name == "TestHero"

    def test_default_hp(self, player):
        assert player.hp == 100

    def test_default_level(self, player):
        assert player.level == 1

    def test_default_gold(self, player):
        assert player.gold == 50

    def test_default_weapon(self, player):
        assert player.weapon == "Fists"

    def test_default_armor_is_none(self, player):
        assert player.armor is None

    def test_default_inventory_has_fists(self, player):
        assert "Fists" in player.inventory

    def test_default_critical_chance(self, player):
        assert player.critical_chance == 15

    def test_default_critical_multiplier(self, player):
        assert player.critical_multiplier == 2.0

    def test_default_accuracy(self, player):
        assert player.accuracy == 5

    def test_default_dodge(self, player):
        assert player.dodge == 5

    def test_status_effects_empty(self, player):
        assert player.status_effects == []

    def test_custom_stats(self, items_data):
        p = Player(name="Custom", hp=200, attack=20, defense=10,
                   gold=100, level=5, items=items_data)
        assert p.level == 5
        assert p.max_hp == 500
        assert p.gold == 100


class TestPlayerLeveling:
    """Player levels up correctly."""

    def test_gain_exp_increases_exp(self, player):
        player.gain_exp(50)
        assert player.exp == 50

    def test_level_up_at_threshold(self, player):
        player.gain_exp(100)
        assert player.level == 2

    def test_level_up_increases_max_hp(self, player):
        old_max = player.max_hp
        player.gain_exp(100)
        assert player.max_hp > old_max

    def test_level_up_full_heal(self, player):
        player._hp = 50
        player.gain_exp(100)
        assert player.hp == player.max_hp

    def test_level_up_restores_mana(self, player):
        player._mana = 0
        player.gain_exp(100)
        assert player.mana == player.max_mana

    def test_level_up_grants_skill_point(self, player):
        old_sp = player.skill_points
        player.gain_exp(100)
        assert player.skill_points == old_sp + 1

    def test_multiple_level_ups(self, player):
        player.gain_exp(250)
        assert player.level == 3
        assert player.exp == 50

    def test_level_up_increases_base_attack(self, player):
        old_base = player._base_attack
        player.gain_exp(100)
        assert player._base_attack == old_base + 2

    def test_exp_carry_over(self, player):
        player.gain_exp(150)
        assert player.level == 2
        assert player.exp == 50


class TestPlayerStats:
    """Player stat calculations."""

    @pytest.mark.parametrize("level,expected_max_hp", [
        (1, 100), (2, 200), (5, 500), (10, 1000),
    ])
    def test_max_hp_by_level(self, level, expected_max_hp, items_data):
        p = Player(level=level, items=items_data)
        assert p.max_hp == expected_max_hp

    @pytest.mark.parametrize("level,expected_max_mana", [
        (1, 10), (2, 20), (5, 50), (10, 100),
    ])
    def test_max_mana_by_level(self, level, expected_max_mana, items_data):
        p = Player(level=level, items=items_data)
        assert p.max_mana == expected_max_mana

    def test_hp_clamped_to_max(self, player):
        player.hp = 9999
        assert player.hp == player.max_hp

    def test_hp_clamped_to_zero(self, player):
        player.hp = -50
        assert player.hp == 0

    def test_mana_clamped_to_max(self, player):
        player.mana = 9999
        assert player.mana == player.max_mana

    def test_mana_clamped_to_zero(self, player):
        player.mana = -10
        assert player.mana == 0

    def test_is_alive_when_hp_positive(self, player):
        assert player.is_alive is True

    def test_is_not_alive_when_hp_zero(self, player):
        player.hp = 0
        assert player.is_alive is False

    def test_exp_to_next_level(self, player):
        assert player.exp_to_next_level == 100

    def test_exp_to_next_level_partial(self, player):
        player.exp = 60
        assert player.exp_to_next_level == 40


class TestPlayerEquipment:
    """Player equipment handling."""

    def test_equip_weapon_increases_attack(self, player, items_data):
        player.inventory["Iron Sword"] = 1
        player.level = 5  # meet level requirement
        player.equip_weapon("Iron Sword")
        assert player.weapon == "Iron Sword"
        assert player.attack == player._base_attack + 6

    def test_equip_armor_increases_defense(self, player, items_data):
        player.inventory["Leather Armour"] = 1
        player.level = 2  # Leather Armour requires level 2
        player.equip_defense("Leather Armour")
        assert player.armor == "Leather Armour"
        assert player.defense == player._base_defense + 10

    def test_equip_weapon_not_in_inventory(self, player):
        player.equip_weapon("Dragon Slayer")
        assert player.weapon == "Fists"  # unchanged

    def test_equip_weapon_level_too_low(self, player, items_data):
        player.inventory["Dragon Slayer"] = 1
        player.equip_weapon("Dragon Slayer")
        assert player.weapon == "Fists"  # unchanged

    def test_equip_potion_heals(self, player, items_data):
        player.inventory["Health Potion"] = 1
        player._hp = 50
        player.equip_potion("Health Potion")
        assert player.hp == 90

    def test_equip_potion_consumes_item(self, player, items_data):
        player.inventory["Health Potion"] = 1
        player.equip_potion("Health Potion")
        assert "Health Potion" not in player.inventory

    def test_equip_potion_stacks_consumed(self, player, items_data):
        player.inventory["Health Potion"] = 3
        player.equip_potion("Health Potion")
        assert player.inventory["Health Potion"] == 2

    def test_case_insensitive_equip(self, player, items_data):
        player.inventory["Iron Sword"] = 1
        player.level = 5
        player.equip_weapon("iron sword")
        assert player.weapon == "Iron Sword"


class TestPlayerSerialization:
    """Player to_dict / from_dict round-trip."""

    def test_to_dict_has_player_section(self, player):
        d = player.to_dict()
        assert "player" in d

    def test_to_dict_has_loadout_section(self, player):
        d = player.to_dict()
        assert "loadout" in d

    def test_to_dict_has_world_section(self, player):
        d = player.to_dict()
        assert "world" in d

    def test_round_trip_preserves_name(self, player):
        d = player.to_dict()
        restored = Player.from_dict(d)
        assert restored.name == player.name

    def test_round_trip_preserves_level(self, player):
        d = player.to_dict()
        restored = Player.from_dict(d)
        assert restored.level == player.level

    def test_round_trip_preserves_gold(self, player):
        d = player.to_dict()
        restored = Player.from_dict(d)
        assert restored.gold == player.gold

    def test_round_trip_preserves_combat_stats(self, player):
        d = player.to_dict()
        restored = Player.from_dict(d)
        assert restored.critical_chance == player.critical_chance
        assert restored.accuracy == player.accuracy
        assert restored.dodge == player.dodge

    def test_round_trip_preserves_inventory(self, player):
        player.inventory["Iron Sword"] = 2
        d = player.to_dict()
        restored = Player.from_dict(d)
        assert restored.inventory["Iron Sword"] == 2

    def test_legacy_flat_dict_compat(self, items_data):
        legacy = {
            "name": "OldHero", "level": 3, "exp": 50,
            "hp": 250, "attack": 14, "defense": 7,
            "gold": 200, "luck": 2, "reputation": 0,
            "skill_points": 2, "floor": 5,
        }
        p = Player.from_dict(legacy)
        assert p.name == "OldHero"
        assert p.level == 3
        assert p.critical_chance == 15  # default
        assert p.accuracy == 5  # default

    def test_legacy_dict_preserves_items(self, items_data):
        legacy = {"name": "Hero", "inventory": {"Iron Sword": 1}}
        p = Player.from_dict(legacy)
        assert "Iron Sword" in p.inventory
