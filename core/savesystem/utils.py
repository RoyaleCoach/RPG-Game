# utils.py

import json
import os
import sys
import time
from typing import Any, Dict

# --- Constants ---
# Base directory resolution, crucial for finding save files compatibly
# whether the script is run directly or as a frozen executable.
def _resolve_base_dir() -> str:
    # Check if running in a frozen context (e.g., PyInstaller executable)
    if getattr(sys, "frozen", False):
        # In a frozen app, sys.executable points to the executable.
        # sys._MEIPASS is the temporary directory where the app is extracted.
        # The save directory should ideally be outside the temp extraction folder for persistence.
        # A common approach is to place it in the user's application data folder.
        # For simplicity in this refactoring, we'll try to keep it relative to script location,
        # but a more robust solution would use user's AppData.
        # Let's assume `sys._MEIPASS` (if available) or the directory of the executable is a safe bet for the base.
        # If sys._MEIPASS is available, it usually means it's a bundled app.
        # The executable path is more reliable.
        return os.path.dirname(sys.executable)
        
    # When running as a normal script, use the directory of this file.
    # __file__ is the path to the current script.
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

BASE_DIR = _resolve_base_dir()
SAVE_DIR = os.path.join(BASE_DIR, "save")
SAVE_VERSION = 3 # Current schema version

# --- Path Management ---
def get_save_dir() -> str:
    """Ensures the save directory exists and returns its path."""
    os.makedirs(SAVE_DIR, exist_ok=True)
    return SAVE_DIR

def get_db_path() -> str:
    """Returns the full path to the game database."""
    return os.path.join(get_save_dir(), "game.db")

# --- Slot Name Resolution ---
def normalize_slot_name(slot_name: str) -> str:
    """
    Normalizes a slot name, removing common file extensions like .json
    to ensure compatibility with older save systems or user input.
    """
    return slot_name.removesuffix(".json")

# --- Data Conversion Helpers ---

def dict_to_json_string(data: Dict[str, Any]) -> str:
    """Converts a dictionary to a JSON string, ensuring proper encoding."""
    # ensure_ascii=False is important for non-English characters if any.
    return json.dumps(data, ensure_ascii=False)

def json_string_to_dict(json_string: str) -> Dict[str, Any]:
    """Converts a JSON string back to a dictionary."""
    # Handles potential errors during JSON parsing gracefully.
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON string: {e}")
        # Depending on game logic, you might return an empty dict, None, or raise a specific error.
        return {} # Returning empty dict as a safe default

# --- Legacy Data Handling ---

def convert_legacy_player_data(legacy_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Converts older, flat player data format (possibly from JSON saves)
    into the newer sectioned format expected by the current SaveSystem.
    """
    # This structure should mirror the expected sections for the multi-table save
    sectioned_data = {
        "player": {},
        "world": {},
        "loadout": {},
        "quests": {},
        "statistics": {},
        "flags": {},
    }

    # Map flat keys to their sectioned counterparts.
    # 'player' section for core player stats
    sectioned_data["player"] = {
        "name":                 legacy_data.get("name", "Adventurer"),
        "level":                legacy_data.get("level", 1),
        "exp":                  legacy_data.get("exp", 0),
        "hp":                   legacy_data.get("hp", 100),
        "mana":                 legacy_data.get("mana"), # Can be None
        "base_attack":          legacy_data.get("attack", legacy_data.get("base_attack", 10)),
        "base_defense":         legacy_data.get("defense", legacy_data.get("base_defense", 5)),
        "gold":                 legacy_data.get("gold", 50),
        "luck":                 legacy_data.get("luck", 0),
        "reputation":           legacy_data.get("reputation", 0),
        "skill_points":         legacy_data.get("skill_points", 0),
        "critical_chance":      legacy_data.get("critical_chance", 15),
        "critical_multiplier":  legacy_data.get("critical_multiplier", 2.0),
        "accuracy":             legacy_data.get("accuracy", 5),
        "dodge":                legacy_data.get("dodge", 5),
    }

    # 'world' section
    sectioned_data["world"] = {
        "floor":                legacy_data.get("floor", legacy_data.get("current_floor", 1)),
        "boss_progress":        legacy_data.get("boss_progress", 0),
        "dungeon_runs":         legacy_data.get("dungeon_runs", 0),
        "last_event":           legacy_data.get("last_event"),
    }

    # 'loadout' section - includes inventory, spells, skills
    sectioned_data["loadout"] = {
        "weapon":               legacy_data.get("weapon", "Fists"),
        "armor":                legacy_data.get("armor"), # Can be None
        "inventory":            legacy_data.get("inventory", {"Fists": 1}), # Default inventory if not present
        "learned_spells":       legacy_data.get("learned_spells", []),
        "unlocked_skills":      legacy_data.get("unlocked_skills", []),
    }

    # 'quests' section
    sectioned_data["quests"] = {
        "story_progress":       legacy_data.get("story_progress", 0),
        "quest":                legacy_data.get("quest", []), # Active quests
        "completed_quests":     legacy_data.get("completed_quests", []),
    }

    # 'statistics' section
    sectioned_data["statistics"] = {
        "enemies_killed":       legacy_data.get("enemies_killed", 0),
        "puzzles_solved":       legacy_data.get("puzzles_solved", 0),
    }

    # 'flags' section
    sectioned_data["flags"] = {
        "skip_next_battle":             legacy_data.get("skip_next_battle", False),
        "skip_next_trap":               legacy_data.get("skip_next_trap", False),
        "skip_next_boss_preparation":   legacy_data.get("skip_next_boss_preparation", False),
    }

    return sectioned_data

