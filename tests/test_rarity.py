"""
tests/test_rarity.py
-------------------
Unit tests for the rarity system.
"""

import pytest
from core.rarity import (
    RARITIES, get_rarity, get_rarity_label,
    get_stat_multiplier, get_sell_multiplier, all_rarities,
)


class TestRarityData:
    """Rarity definitions."""

    def test_six_rarities_exist(self):
        assert len(RARITIES) == 6

    def test_all_rarities_present(self):
        expected = {"Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic"}
        assert set(RARITIES.keys()) == expected

    def test_common_has_correct_multipliers(self):
        r = RARITIES["Common"]
        assert r["stat_multiplier"] == 1.0
        assert r["sell_multiplier"] == 1.0

    def test_legendary_has_highest_multipliers(self):
        r = RARITIES["Legendary"]
        assert r["stat_multiplier"] == 1.75
        assert r["sell_multiplier"] == 3.0

    def test_stat_multipliers_increase_with_rarity(self):
        rarities = all_rarities()
        mults = [RARITIES[r]["stat_multiplier"] for r in rarities]
        assert mults == sorted(mults)

    def test_sell_multipliers_increase_with_rarity(self):
        rarities = all_rarities()
        mults = [RARITIES[r]["sell_multiplier"] for r in rarities]
        assert mults == sorted(mults)


class TestRarityFunctions:
    """Rarity helper functions."""

    def test_get_rarity_common(self):
        r = get_rarity("Common")
        assert r["label"] == "[Common]"

    def test_get_rarity_legendary(self):
        r = get_rarity("Legendary")
        assert r["label"] == "[Legendary]"

    def test_get_rarity_unknown_defaults_to_common(self):
        r = get_rarity("NonExistent")
        assert r["label"] == "[Common]"

    def test_get_rarity_label(self):
        assert get_rarity_label("Rare") == "[Rare]"

    def test_get_rarity_label_unknown(self):
        assert get_rarity_label("Unknown") == "[Common]"

    @pytest.mark.parametrize("rarity,expected", [
        ("Common", 1.0), ("Uncommon", 1.1), ("Rare", 1.25),
        ("Epic", 1.5), ("Legendary", 1.75),
    ])
    def test_get_stat_multiplier(self, rarity, expected):
        assert get_stat_multiplier(rarity) == expected

    @pytest.mark.parametrize("rarity,expected", [
        ("Common", 1.0), ("Uncommon", 1.25), ("Rare", 1.5),
        ("Epic", 2.0), ("Legendary", 3.0),
    ])
    def test_get_sell_multiplier(self, rarity, expected):
        assert get_sell_multiplier(rarity) == expected

    def test_all_rarities_sorted(self):
        rarities = all_rarities()
        assert rarities == ["Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic"]

    def test_all_rarities_returns_list(self):
        assert isinstance(all_rarities(), list)
