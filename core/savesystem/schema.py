# schema.py

# SQL DDL statements for creating tables and indexes.
# This module is responsible for database initialization and schema definition.

_DDL = """
-- Enable foreign-key enforcement (SQLite does not enable it by default)
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS saves (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    slot_name       TEXT    NOT NULL UNIQUE,
    save_version    INTEGER NOT NULL DEFAULT 2,
    timestamp       REAL    NOT NULL
);

-- Player core stats
CREATE TABLE IF NOT EXISTS player_core (
    save_id         INTEGER PRIMARY KEY REFERENCES saves(id) ON DELETE CASCADE,
    name            TEXT    NOT NULL,
    level           INTEGER NOT NULL DEFAULT 1,
    exp             INTEGER NOT NULL DEFAULT 0,
    hp              INTEGER NOT NULL DEFAULT 100,
    mana            INTEGER,
    base_attack     INTEGER NOT NULL DEFAULT 10,
    base_defense    INTEGER NOT NULL DEFAULT 5,
    gold            INTEGER NOT NULL DEFAULT 50,
    luck            INTEGER NOT NULL DEFAULT 0,
    reputation      INTEGER NOT NULL DEFAULT 0,
    skill_points    INTEGER NOT NULL DEFAULT 0
);

-- Player combat stats
CREATE TABLE IF NOT EXISTS player_combat (
    save_id             INTEGER PRIMARY KEY REFERENCES saves(id) ON DELETE CASCADE,
    critical_chance     INTEGER NOT NULL DEFAULT 15,
    critical_multiplier REAL    NOT NULL DEFAULT 2.0,
    accuracy            INTEGER NOT NULL DEFAULT 5,
    dodge               INTEGER NOT NULL DEFAULT 5
);

-- World progression
CREATE TABLE IF NOT EXISTS player_world (
    save_id         INTEGER PRIMARY KEY REFERENCES saves(id) ON DELETE CASCADE,
    floor           INTEGER NOT NULL DEFAULT 1,
    boss_progress   INTEGER NOT NULL DEFAULT 0,
    dungeon_runs    INTEGER NOT NULL DEFAULT 0,
    last_event      TEXT
);

-- Boolean flags (stored as 0/1)
CREATE TABLE IF NOT EXISTS player_flags (
    save_id                     INTEGER PRIMARY KEY REFERENCES saves(id) ON DELETE CASCADE,
    skip_next_battle            INTEGER NOT NULL DEFAULT 0,
    skip_next_trap              INTEGER NOT NULL DEFAULT 0,
    skip_next_boss_preparation  INTEGER NOT NULL DEFAULT 0
);

-- Game statistics
CREATE TABLE IF NOT EXISTS player_statistics (
    save_id         INTEGER PRIMARY KEY REFERENCES saves(id) ON DELETE CASCADE,
    enemies_killed  INTEGER NOT NULL DEFAULT 0,
    puzzles_solved  INTEGER NOT NULL DEFAULT 0
);

-- Equipped items
CREATE TABLE IF NOT EXISTS player_loadout (
    save_id         INTEGER PRIMARY KEY REFERENCES saves(id) ON DELETE CASCADE,
    weapon          TEXT    NOT NULL DEFAULT 'Fists',
    armor           TEXT                                    -- NULL = no armor equipped
);

-- Inventory items: multiple items per slot [one-to-many]
CREATE TABLE IF NOT EXISTS inventory_items (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    save_id         INTEGER NOT NULL REFERENCES saves(id) ON DELETE CASCADE,
    item_name       TEXT    NOT NULL,
    quantity        INTEGER NOT NULL DEFAULT 1,
    UNIQUE(save_id, item_name)
);

-- Learned spells [one-to-many]
CREATE TABLE IF NOT EXISTS learned_spells (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    save_id         INTEGER NOT NULL REFERENCES saves(id) ON DELETE CASCADE,
    spell_name      TEXT    NOT NULL,
    UNIQUE(save_id, spell_name)
);

-- Unlocked skills [one-to-many]
CREATE TABLE IF NOT EXISTS unlocked_skills (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    save_id         INTEGER NOT NULL REFERENCES saves(id) ON DELETE CASCADE,
    skill_name      TEXT    NOT NULL,
    UNIQUE(save_id, skill_name)
);

-- Quest metadata (e.g., story progress)
CREATE TABLE IF NOT EXISTS quest_meta (
    save_id         INTEGER PRIMARY KEY REFERENCES saves(id) ON DELETE CASCADE,
    story_progress  INTEGER NOT NULL DEFAULT 0
);

-- Active quests (stored as JSON string per row)
CREATE TABLE IF NOT EXISTS quests_active (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    save_id         INTEGER NOT NULL REFERENCES saves(id) ON DELETE CASCADE,
    quest_data      TEXT    NOT NULL  -- JSON string representing a single active quest
);

-- Completed quests (stored as JSON string per row)
CREATE TABLE IF NOT EXISTS quests_completed (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    save_id         INTEGER NOT NULL REFERENCES saves(id) ON DELETE CASCADE,
    quest_data      TEXT    NOT NULL  -- JSON string representing a single completed quest
);
"""

def initialize_database(db_path: str) -> None:
    """
    Creates all necessary tables if they do not already exist.
    """
    try:
        from core.savesystem.database import execute_script
        execute_script(db_path, _DDL)
    except Exception as e:
        print(f"Error initializing database schema: {e}")
        raise
