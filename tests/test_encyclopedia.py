"""
tests/test_encyclopedia.py
-------------------------
Unit tests for the Item Encyclopedia.
"""

import pytest
from core.encyclopedia import ItemEncyclopedia


class TestEncyclopediaDiscovery:
    """Item discovery tracking."""

    def test_discover_new_item(self, encyclopedia):
        assert encyclopedia.discover("Iron Sword") is True

    def test_discover_duplicate_returns_false(self, encyclopedia):
        encyclopedia.discover("Iron Sword")
        assert encyclopedia.discover("Iron Sword") is False

    def test_discover_unknown_item_returns_false(self, encyclopedia):
        assert encyclopedia.discover("Nonexistent Item") is False

    def test_is_discovered(self, encyclopedia):
        assert encyclopedia.is_discovered("Iron Sword") is False
        encyclopedia.discover("Iron Sword")
        assert encyclopedia.is_discovered("Iron Sword") is True

    def test_sync_with_player(self, encyclopedia):
        encyclopedia.sync_with_player({"Iron Sword": 1, "Health Potion": 2})
        assert encyclopedia.is_discovered("Iron Sword")
        assert encyclopedia.is_discovered("Health Potion")

    def test_sync_ignores_unknown_items(self, encyclopedia):
        encyclopedia.sync_with_player({"Unknown Item": 1})
        assert len(encyclopedia.discovered) == 0


class TestEncyclopediaData:
    """Encyclopedia data integrity."""

    def test_all_items_loaded(self, encyclopedia):
        assert len(encyclopedia._all_items) > 0

    def test_items_have_rarity(self, encyclopedia):
        for item_name, item_data in encyclopedia._all_items.items():
            assert "rarity" in item_data

    def test_items_have_type(self, encyclopedia):
        for item_name, item_data in encyclopedia._all_items.items():
            assert "type" in item_data

    def test_items_have_description(self, encyclopedia):
        for item_name, item_data in encyclopedia._all_items.items():
            assert "description" in item_data

    def test_weapons_are_equipment_type(self, encyclopedia):
        for item_name, item_data in encyclopedia._all_items.items():
            if item_data["category"] == "weapons":
                assert item_data["type"] == "equipment"

    def test_potions_are_consumable_type(self, encyclopedia):
        for item_name, item_data in encyclopedia._all_items.items():
            if item_data["category"] == "potions":
                assert item_data["type"] == "consumable"


class TestEncyclopediaFiltering:
    """Filtering and display."""

    def test_show_by_rarity(self, encyclopedia, capsys):
        encyclopedia.discover("Iron Sword")
        encyclopedia.show_by_rarity("Uncommon")
        captured = capsys.readouterr()
        assert "Iron Sword" in captured.out

    def test_show_by_type(self, encyclopedia, capsys):
        encyclopedia.discover("Iron Sword")
        encyclopedia.show_by_type("equipment")
        captured = capsys.readouterr()
        assert "Iron Sword" in captured.out

    def test_show_by_type_no_match(self, encyclopedia, capsys):
        encyclopedia.show_by_type("material")
        captured = capsys.readouterr()
        # Should show "No materials found" or similar
        assert "material" in captured.out.lower() or "???" in captured.out

    def test_show_full_encyclopedia(self, encyclopedia, capsys):
        encyclopedia.discover("Iron Sword")
        encyclopedia.show()
        captured = capsys.readouterr()
        assert "ITEM ENCYCLOPEDIA" in captured.out
        assert "Iron Sword" in captured.out
        assert "Completion" in captured.out

    def test_hidden_items_show_as_unknown(self, encyclopedia, capsys):
        encyclopedia.show()
        captured = capsys.readouterr()
        assert "???" in captured.out


class TestEncyclopediaCompletion:
    """Completion percentage."""

    def test_completion_starts_at_zero(self, encyclopedia):
        d = encyclopedia.to_dict()
        assert len(d["discovered"]) == 0

    def test_completion_increases(self, encyclopedia):
        encyclopedia.discover("Iron Sword")
        encyclopedia.discover("Health Potion")
        d = encyclopedia.to_dict()
        assert len(d["discovered"]) == 2

    def test_completion_percentage_displayed(self, encyclopedia, capsys):
        encyclopedia.discover("Iron Sword")
        encyclopedia.show()
        captured = capsys.readouterr()
        assert "%" in captured.out


class TestEncyclopediaPersistence:
    """Serialization round-trip."""

    def test_to_dict(self, encyclopedia):
        encyclopedia.discover("Iron Sword")
        d = encyclopedia.to_dict()
        assert "discovered" in d
        assert "Iron Sword" in d["discovered"]

    def test_from_dict(self, encyclopedia):
        data = {"discovered": ["Iron Sword", "Health Potion"]}
        encyclopedia.from_dict(data)
        assert encyclopedia.is_discovered("Iron Sword")
        assert encyclopedia.is_discovered("Health Potion")

    def test_round_trip(self, encyclopedia):
        encyclopedia.discover("Iron Sword")
        encyclopedia.discover("Dragon Slayer")
        d = encyclopedia.to_dict()
        enc2 = ItemEncyclopedia(encyclopedia.catalog)
        enc2.from_dict(d)
        assert enc2.is_discovered("Iron Sword")
        assert enc2.is_discovered("Dragon Slayer")
        assert not enc2.is_discovered("Health Potion")
