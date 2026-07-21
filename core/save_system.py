# core/save_system.py
# This is the public entry point for the save system.
# It now contains the main SaveSystem logic (coordinator).

import os
import sys
import time
import json  # <<< ADDED IMPORT FOR JSON HANDLING
from typing import Any, Dict, Union, List, Tuple  # Added types for clarity

# Correctly import modules from the same package 'core.savesystem'
# These are now absolute imports since this file serves as the public entry point.
# <<< ADDED execute_query, execute_non_query
from core.savesystem.database import get_db_connection, execute_query, execute_non_query
from core.savesystem.schema import initialize_database
from core.savesystem.utils import normalize_slot_name, get_db_path

# Import repository classes
from core.savesystem.player_repository import PlayerRepository
from core.savesystem.inventory_repository import InventoryRepository
from core.savesystem.world_repository import WorldRepository
from core.savesystem.flags_repository import FlagsRepository
from core.savesystem.statistics_repository import StatisticsRepository
from core.savesystem.loadout_repository import LoadoutRepository
from core.savesystem.quest_repository import QuestRepository

# Import Player class for constructing from saved data
from core.player import Player

# Define the current save version related to the schema
# This should ideally align with the save_version in schema.py or be managed centrally
CURRENT_SAVE_VERSION = 4  # Matches schema.py default value for new saves


class SaveSystem:
    """
    The main SaveSystem class (coordinator).
    This class orchestrates calls to repositories and the database module.
    It was moved from core/savesystem/save_system.py to here.
    """

    def __init__(self, game_instance: Any) -> None:
        """
        Initializes the SaveSystem, setting up connection and repositories.
        :param game_instance: The main game object, used to access player data.
        """
        self.game = game_instance
        self.db_path = get_db_path()

        # Assign database query functions to the instance
        self.execute_query = execute_query  # <<< ADDED THIS LINE
        self.execute_non_query = execute_non_query  # <<< ADDED THIS LINE

        # Initialize the database schema if it doesn't exist
        try:
            initialize_database(self.db_path)
        except Exception as e:
            print(
                f"FATAL: Could not initialize database at {self.db_path}: {e}")
            # Depending on game behavior, you might want to halt execution or proceed without saving.
            # For now, we'll let it continue, but save operations might fail.

        # Initialize repositories
        self.player_repo = PlayerRepository(self.db_path)
        self.inventory_repo = InventoryRepository(self.db_path)
        self.world_repo = WorldRepository(self.db_path)
        self.flags_repo = FlagsRepository(self.db_path)
        self.stats_repo = StatisticsRepository(self.db_path)
        self.loadout_repo = LoadoutRepository(self.db_path)
        self.quest_repo = QuestRepository(self.db_path)

        # Check for legacy JSON migration on startup
        self._run_legacy_migration()

    def _run_legacy_migration(self) -> None:
        """
        Checks for legacy JSON save files and attempts to migrate them.
        This logic is moved from the original SaveSystem and adapted.
        """
        # Import utilities specific to savesystem
        # Using absolute import path as this is now the main entry point
        from core.savesystem.utils import normalize_slot_name, convert_legacy_player_data

        # Assumes save.json is in the same directory as game.db
        json_path = os.path.join(os.path.dirname(self.db_path), "save.json")

        if not os.path.isfile(json_path):
            return

        print(
            f"🔄 Found legacy JSON save file at {json_path}. Attempting migration...")
        try:
            with open(json_path, "r", encoding="utf-8") as fh:
                legacy_raw_data = json.load(fh)

            # Convert legacy data to the sectioned format
            sectioned_data = convert_legacy_player_data(legacy_raw_data)

            # Use slot_name 'default' for migrated JSONs
            slot_name = "default"

            # Get save_id for the slot, or create one if it doesn't exist
            save_id = self._get_or_create_save_id(slot_name)

            # Save the converted data using the repositories
            self._save_all_data(save_id, sectioned_data)

            # Rename the JSON file to prevent re-migration
            bak_path = json_path + ".bak"
            os.rename(json_path, bak_path)
            print(f"✅ Migration successful. Legacy file renamed to {bak_path}")

        except Exception as e:
            print(
                f"⚠️  Migration failed for {json_path}. Error: {e}. Original file not modified.")

    def _get_or_create_save_id(self, slot_name: str) -> int:
        """
        Finds existing save_id for a slot name, or creates a new entry in 'saves' table.
        Returns the save_id.
        """
        normalized_slot = normalize_slot_name(slot_name)
        with get_db_connection(self.db_path) as conn:
            # Check if slot exists
            cursor = conn.execute(
                "SELECT id FROM saves WHERE slot_name = ?", (normalized_slot,))
            row = cursor.fetchone()

            if row:
                save_id = row["id"]
            else:
                # Insert new save entry and get its ID
                timestamp = time.time()
                conn.execute(
                    "INSERT INTO saves (slot_name, save_version, timestamp) VALUES (?, ?, ?)",
                    (normalized_slot, CURRENT_SAVE_VERSION, timestamp)
                )
                save_id = conn.execute(
                    "SELECT last_insert_rowid()").fetchone()[0]

            # Update timestamp to reflect the migration/save time
            conn.execute(
                "UPDATE saves SET timestamp = ?, save_version = ? WHERE id = ?",
                (time.time(), CURRENT_SAVE_VERSION, save_id)
            )
        return save_id

    def _save_all_data(self, save_id: int, full_data: Dict[str, Any]) -> None:
        """
        Helper to save all parts of the game data using the appropriate repositories.
        """
        self.player_repo.save_player_data(save_id, full_data)
        self.stats_repo.save_statistics(
            save_id, full_data.get("statistics", {}))
        self.world_repo.save_world_data(save_id, full_data.get("world", {}))
        self.flags_repo.save_flags(save_id, full_data.get("flags", {}))
        self.loadout_repo.save_loadout(save_id, full_data.get("loadout", {}))
        self.inventory_repo.save_inventory(save_id, full_data.get(
            # Inventory is part of loadout data
            "loadout", {}).get("inventory", {}))
        self.quest_repo.save_quest_meta(save_id, full_data.get(
            "quests", {}).get("story_progress", 0))
        self.quest_repo.save_active_quests(
            save_id, full_data.get("quests", {}).get("quest", []))
        self.quest_repo.save_completed_quests(
            save_id, full_data.get("quests", {}).get("completed_quests", []))

    # --- Public API Methods ---

    def save(self, slot_name: str = "default") -> bool:
        """
        Save the current game state to the specified slot.
        Returns True if successful, False otherwise.
        """
        normalized_slot = normalize_slot_name(slot_name)

        if not hasattr(self.game, 'player') or self.game.player is None:
            print("SAVE ERROR: Player object not found or is None. Cannot save.")
            return False

        player_payload = self.game.player.to_dict()

        try:
            save_id = self._get_or_create_save_id(slot_name)
            self._save_all_data(save_id, player_payload)
            print(f"💾 Game saved successfully → slot '{normalized_slot}'")
            return True

        except Exception as e:
            print(
                f"SAVE ERROR: Failed to save game to slot '{normalized_slot}': {e}")
            return False

    def load(self, slot_name: str = "default") -> Any | None:
        """
        Load game state from the specified slot.
        Returns the Player object if successful, None otherwise.
        """
        normalized_slot = normalize_slot_name(slot_name)

        try:
            # This method calls self.execute_query
            save_id = self._get_save_id(slot_name)
            if save_id is None:
                print(f"LOAD ERROR: Slot '{normalized_slot}' not found.")
                return None

            player_data = self.player_repo.load_player_data(save_id)
            stats_data = self.stats_repo.load_statistics(save_id)
            world_data = self.world_repo.load_world_data(save_id)
            flags_data = self.flags_repo.load_flags(save_id)
            loadout_data = self.loadout_repo.load_loadout(save_id)
            inventory_data = self.inventory_repo.load_inventory(save_id)
            story_progress = self.quest_repo.load_quest_meta(save_id)
            active_quests = self.quest_repo.load_active_quests(save_id)
            completed_quests = self.quest_repo.load_completed_quests(save_id)

            full_loaded_data = {
                **player_data,
                "statistics": stats_data,
                "world": world_data,
                "flags": flags_data,
                "loadout": {
                    **loadout_data,
                    "inventory": inventory_data
                },
                "quests": {
                    "story_progress": story_progress,
                    "quest": active_quests,
                    "completed_quests": completed_quests,
                }
            }

            # Reconstruct a Player instance from the saved payload
            player_instance = Player.from_dict(full_loaded_data)
            # Re-apply passive skill effects from unlocked skills
            if hasattr(self.game, 'ctx') and hasattr(self.game.ctx, 'skill_tree'):
                skill_tree = self.game.ctx.skill_tree
                for skill_id in player_instance.unlocked_skills:
                    node = skill_tree.get_node(skill_id)
                    if node and node.skill_type == 'passive':
                        skill_tree._apply_passive_effects(player_instance, node)
            else:
                print("WARNING: Skill tree context not available during load. Passive effects may not be re-applied.")

            # Sync encyclopedia with new items
            if hasattr(self.game, 'ctx') and hasattr(self.game.ctx, 'data'):
                player_instance.initialize_items(self.game.ctx.data.items)
            print(f"Successfully loaded game from slot '{normalized_slot}'")
            return player_instance

        except ValueError as ve:
            print(f"LOAD ERROR: {ve}")
            return None
        except Exception as e:
            print(
                f"LOAD ERROR: An unexpected error occurred while loading slot '{normalized_slot}': {e}")
            import traceback  # Import traceback for detailed error logging
            traceback.print_exc(file=sys.stderr)  # Print full traceback
            return None

    def save_exists(self, slot_name: str = "default") -> bool:
        """
        Checks if a save slot exists.
        """
        normalized_slot = normalize_slot_name(slot_name)
        try:
            save_id = self._get_save_id(slot_name)
            return save_id is not None
        except Exception as e:
            print(
                f"SAVE EXISTS ERROR: Could not check for slot '{normalized_slot}': {e}")
            return False

    def delete_save(self, slot_name: str = "default") -> bool:
        """
        Deletes a save slot entirely from the database.
        Returns True if successful, False otherwise.
        """
        normalized_slot = normalize_slot_name(slot_name)
        try:
            save_id = self._get_save_id(slot_name)
            if save_id is None:
                print(
                    f"DELETE SAVE ERROR: Slot '{normalized_slot}' not found.")
                return False

            with get_db_connection(self.db_path) as conn:
                conn.execute("DELETE FROM saves WHERE id = ?", (save_id,))

            print(f"🗑️ Deleted save slot '{normalized_slot}'")
            return True

        except Exception as e:
            print(
                f"DELETE SAVE ERROR: Failed to delete slot '{normalized_slot}': {e}")
            return False

    def _get_save_id(self, slot_name: str) -> int | None:
        """
        Helper method to get the save_id for a given slot name.
        Returns the save_id or None if the slot does not exist.
        This method now uses `self.execute_query` which is assigned from database module.
        """
        normalized_slot = normalize_slot_name(slot_name)
        try:
            # This call was failing because SaveSystem instance did not have execute_query
            # It has been fixed by assigning it in __init__
            rows = self.execute_query(
                self.db_path, "SELECT id FROM saves WHERE slot_name = ?", (
                    normalized_slot,)
            )
            if rows:
                return rows[0]["id"]
            return None
        except Exception as e:
            print(
                f"Error retrieving save_id for slot '{normalized_slot}': {e}")
            return None
