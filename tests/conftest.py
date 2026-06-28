"""
tests/conftest.py
----------------
Shared pytest fixtures for the entire test suite.
"""

import json
import sys
import os
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pytest


# ─────────────────────────────────────────────────────────────────────────────
# JSON Data Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def data_dir():
    """Path to the data directory."""
    return PROJECT_ROOT / "data"


@pytest.fixture(scope="session")
def items_data(data_dir):
    """Load items.json."""
    with open(data_dir / "items.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def quests_data(data_dir):
    """Load quests.json."""
    with open(data_dir / "quests.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def bosses_data(data_dir):
    """Load bosses.json."""
    with open(data_dir / "bosses.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def spells_data(data_dir):
    """Load spells.json."""
    with open(data_dir / "spells.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def loot_tables_data(data_dir):
    """Load loot_tables.json."""
    with open(data_dir / "loot_tables.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def skill_tree_data(data_dir):
    """Load skill_tree.json."""
    with open(data_dir / "skill_tree.json", encoding="utf-8") as f:
        return json.load(f)


# ─────────────────────────────────────────────────────────────────────────────
# Player Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def player(items_data):
    """Create a default player for testing."""
    from core.player import Player
    p = Player(name="TestHero", items=items_data)
    p.initialize_items(items_data)
    return p


@pytest.fixture
def high_level_player(items_data):
    """Create a high-level player."""
    from core.player import Player
    p = Player(
        name="Veteran",
        level=10,
        exp=0,
        hp=1000,
        attack=20,
        defense=15,
        gold=500,
        items=items_data,
    )
    p.initialize_items(items_data)
    return p


# ─────────────────────────────────────────────────────────────────────────────
# Enemy Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def basic_enemy():
    """Create a basic enemy."""
    from core.enemy import Enemy
    return Enemy(name="Goblin", hp=30, attack=8)


@pytest.fixture
def boss_enemy():
    """Create a boss enemy."""
    from core.enemy import Boss
    return Boss(name="Goblin King", hp=150, attack=20,
                exp_reward=100, gold_reward=150)


# ─────────────────────────────────────────────────────────────────────────────
# System Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def inventory(items_data):
    """Create an Inventory instance."""
    from core.inventory import Inventory
    return Inventory(items_data)


@pytest.fixture
def skill_system(spells_data):
    """Create a Skill system."""
    from core.skill import Skill
    return Skill(spells_data)


@pytest.fixture
def quest_system(quests_data):
    """Create a QuestSystem."""
    from world.quest import QuestSystem
    return QuestSystem(quests_data)


@pytest.fixture
def loot_engine(items_data, loot_tables_data):
    """Create a LootEngine."""
    from core.loot import LootEngine
    return LootEngine(loot_tables_data, items_data)


@pytest.fixture
def encyclopedia(items_data):
    """Create an ItemEncyclopedia."""
    from core.encyclopedia import ItemEncyclopedia
    return ItemEncyclopedia(items_data)


# ─────────────────────────────────────────────────────────────────────────────
# Database / Save Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def tmp_db_path(tmp_path):
    """Provide a temporary database path."""
    return str(tmp_path / "test_game.db")


@pytest.fixture
def savesystem(tmp_db_path):
    """Create a SaveSystem with a temporary database."""
    from core.save_system import SaveSystem
    # Create a minimal mock game object
    class MockGame:
        player = None
    game = MockGame()
    return SaveSystem(game)


# ─────────────────────────────────────────────────────────────────────────────
# Combat Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def combat(skill_system, items_data, quest_system):
    """Create a Combat instance."""
    from core.combat import Combat
    c = Combat(quest_system, items_data, skill_system)
    return c
