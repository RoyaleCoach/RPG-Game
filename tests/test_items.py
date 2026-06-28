"""
tests/test_items.py
------------------
Validation tests for game items data.
"""

import pytest


class TestWeaponsValidation:
    """Validate all weapons in items.json."""

    @pytest.fixture
    def weapons(self, items_data):
        return items_data.get("weapons", {})

    def test_at_least_one_weapon(self, weapons):
        assert len(weapons) > 0

    def test_all_have_attack(self, weapons):
        for name, data in weapons.items():
            assert isinstance(data["attack"], (int, float)), \
                f"{name}: attack must be numeric"

    def test_attack_non_negative(self, weapons):
        for name, data in weapons.items():
            assert data["attack"] >= 0, f"{name}: negative attack"

    def test_rarity_present(self, weapons):
        for name, data in weapons.items():
            assert "rarity" in data, f"{name}: missing rarity"

    def test_level_required_present(self, weapons):
        for name, data in weapons.items():
            assert "level_required" in data, f"{name}: missing level_required"

    def test_price_or_limited(self, weapons):
        """Items should either have a price or be limited/quest items."""
        for name, data in weapons.items():
            has_price = data.get("price") is not None
            is_limited = data.get("limited", False)
            assert has_price or is_limited, \
                f"{name}: needs price or limited flag"


class TestPotionsValidation:
    """Validate all potions in items.json."""

    @pytest.fixture
    def potions(self, items_data):
        return items_data.get("potions", {})

    def test_at_least_one_potion(self, potions):
        assert len(potions) > 0

    def test_all_have_effect(self, potions):
        for name, data in potions.items():
            assert "effect" in data, f"{name}: missing effect"

    def test_effect_positive(self, potions):
        for name, data in potions.items():
            assert data["effect"] > 0, f"{name}: non-positive effect"

    def test_rarity_present(self, potions):
        for name, data in potions.items():
            assert "rarity" in data, f"{name}: missing rarity"


class TestArmorValidation:
    """Validate all armor in items.json."""

    @pytest.fixture
    def armors(self, items_data):
        return items_data.get("defends", {})

    def test_at_least_one_armor(self, armors):
        assert len(armors) > 0

    def test_all_have_defense(self, armors):
        for name, data in armors.items():
            assert "defense" in data, f"{name}: missing defense"

    def test_defense_positive(self, armors):
        for name, data in armors.items():
            assert data["defense"] > 0, f"{name}: non-positive defense"

    def test_rarity_present(self, armors):
        for name, data in armors.items():
            assert "rarity" in data, f"{name}: missing rarity"


class TestConsistentRarityNaming:
    """Rarity names should be consistent across categories."""

    def test_rarity_capitalization(self, items_data):
        for category in items_data.values():
            for name, data in category.items():
                rarity = data.get("rarity", "")
                assert rarity[0].isupper(), \
                    f"{name}: rarity '{rarity}' not capitalized"
