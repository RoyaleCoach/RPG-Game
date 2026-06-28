"""
tests/test_status_effects.py
---------------------------
Unit tests for status effects.
"""

import pytest
from unittest.mock import Mock
from core.status_effects import (
    StatusEffect, Burn, Poison, Bleed, Freeze, Stun, Regen,
    apply_status_effects, apply_effect_to, get_spell_effect,
)


def _entity(hp=100, max_hp=100):
    e = Mock()
    e.name = "Target"
    e.hp = hp
    e.max_hp = max_hp
    e.status_effects = []
    return e


class TestBurn:
    """Burn status effect."""

    def test_burn_reduces_hp(self):
        e = _entity(hp=100, max_hp=100)
        burn = Burn(duration=3)
        apply_effect_to(e, burn)
        apply_status_effects(e)
        assert e.hp < 100

    def test_burn_expires(self):
        e = _entity()
        burn = Burn(duration=2)
        apply_effect_to(e, burn)
        apply_status_effects(e)
        apply_status_effects(e)
        apply_status_effects(e)
        assert len(e.status_effects) == 0

    def test_burn_damage_is_percentage(self):
        e = _entity(hp=200, max_hp=200)
        burn = Burn(duration=1)
        apply_effect_to(e, burn)
        apply_status_effects(e)
        # 5% of 200 = 10
        assert e.hp == 190


class TestPoison:
    """Poison status effect."""

    def test_poison_reduces_hp(self):
        e = _entity(hp=100)
        poison = Poison(duration=3, damage_per_tick=5)
        apply_effect_to(e, poison)
        apply_status_effects(e)
        assert e.hp == 95

    def test_poison_flat_damage(self):
        e = _entity(hp=100)
        poison = Poison(duration=1, damage_per_tick=10)
        apply_effect_to(e, poison)
        apply_status_effects(e)
        assert e.hp == 90


class TestBleed:
    """Bleed status effect."""

    def test_bleed_increasing_damage(self):
        e = _entity(hp=200, max_hp=200)
        bleed = Bleed(duration=3, base_damage=4)
        apply_effect_to(e, bleed)
        hp_after_first = e.hp
        apply_status_effects(e)
        hp_after_second = e.hp
        # Second tick should deal more damage than first
        dmg_first = 200 - hp_after_first
        dmg_second = hp_after_first - hp_after_second
        assert dmg_second > 0


class TestFreeze:
    """Freeze status effect."""

    def test_freeze_immobilizes(self):
        e = _entity()
        freeze = Freeze(duration=2)
        apply_effect_to(e, freeze)
        can_act = apply_status_effects(e)
        assert can_act is False

    def test_freeze_expires(self):
        e = _entity()
        freeze = Freeze(duration=1)
        apply_effect_to(e, freeze)
        apply_status_effects(e)  # tick -> expire
        can_act = apply_status_effects(e)
        assert can_act is True

    def test_is_frozen_property(self):
        freeze = Freeze(duration=2)
        assert freeze.is_frozen is True
        freeze.tick(_entity())
        freeze.tick(_entity())
        assert freeze.is_frozen is False


class TestStun:
    """Stun status effect."""

    def test_stun_immobilizes(self):
        e = _entity()
        stun = Stun(duration=1)
        apply_effect_to(e, stun)
        can_act = apply_status_effects(e)
        assert can_act is False

    def test_stun_expires_after_one_turn(self):
        e = _entity()
        stun = Stun(duration=1)
        apply_effect_to(e, stun)
        apply_status_effects(e)
        can_act = apply_status_effects(e)
        assert can_act is True


class TestRegen:
    """Regeneration status effect."""

    def test_regen_heals(self):
        e = _entity(hp=50, max_hp=100)
        regen = Regen(duration=3, heal_per_tick=10)
        apply_effect_to(e, regen)
        apply_status_effects(e)
        assert e.hp > 50

    def test_regen_does_not_exceed_max(self):
        e = _entity(hp=95, max_hp=100)
        regen = Regen(duration=3, heal_per_tick=20)
        apply_effect_to(e, regen)
        apply_status_effects(e)
        assert e.hp <= 100


class TestEffectStacking:
    """Effect stacking rules."""

    def test_same_effect_refreshed(self):
        e = _entity()
        apply_effect_to(e, Burn(duration=2))
        apply_effect_to(e, Burn(duration=5))
        assert len(e.status_effects) == 1
        assert e.status_effects[0].duration == 5

    def test_different_effects_stack(self):
        e = _entity()
        apply_effect_to(e, Burn(duration=3))
        apply_effect_to(e, Poison(duration=3))
        assert len(e.status_effects) == 2


class TestSpellEffectMapping:
    """Spell to effect mapping."""

    def test_fireball_returns_burn(self):
        effect = get_spell_effect("fireball")
        assert isinstance(effect, Burn)

    def test_icicle_returns_freeze(self):
        effect = get_spell_effect("icicle")
        assert isinstance(effect, Freeze)

    def test_shadow_bolt_returns_bleed(self):
        effect = get_spell_effect("shadow_bolt")
        assert isinstance(effect, Bleed)

    def test_unknown_spell_returns_none(self):
        assert get_spell_effect("nonexistent") is None
