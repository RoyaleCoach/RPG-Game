# player_repository.py

from typing import Any, Dict

# Assume database functions are imported and available
# from core.savesystem.database import execute_query, execute_non_query
# Assume DB_PATH is globally accessible or passed somehow

class PlayerRepository:
    """
    Handles all database operations related to player core and combat statistics.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        # Import database functions here to avoid circular dependencies if database.py imports this.
        # A better approach might be dependency injection or passing the db_path directly.
        from core.savesystem.database import execute_query, execute_non_query
        self.execute_query = execute_query
        self.execute_non_query = execute_non_query

    def save_player_data(self, save_id: int, player_data: Dict[str, Any]) -> None:
        """
        Saves player core and combat statistics for a given save ID.
        This method will upsert the data (update if exists, insert if not).
        """
        # Player Core Data
        player_core_data = player_data.get("player", {})
        self.execute_non_query(self.db_path, """
            INSERT OR REPLACE INTO player_core
                (save_id, name, level, exp, hp, mana, base_attack, base_defense, gold, luck, reputation, skill_points)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            save_id,
            player_core_data.get("name", "Adventurer"),
            player_core_data.get("level", 1),
            player_core_data.get("exp", 0),
            player_core_data.get("hp", 100),
            player_core_data.get("mana"),
            player_core_data.get("base_attack", 10),
            player_core_data.get("base_defense", 5),
            player_core_data.get("gold", 50),
            player_core_data.get("luck", 0),
            player_core_data.get("reputation", 0),
            player_core_data.get("skill_points", 0),
        ))

        # Player Combat Data
        player_combat_data = player_data.get("player", {}) # Combat stats are part of 'player' in the current structure
        self.execute_non_query(self.db_path, """
            INSERT OR REPLACE INTO player_combat
                (save_id, critical_chance, critical_multiplier, accuracy, dodge)
            VALUES (?, ?, ?, ?, ?)
        """, (
            save_id,
            player_combat_data.get("critical_chance", 15),
            player_combat_data.get("critical_multiplier", 2.0),
            player_combat_data.get("accuracy", 5),
            player_combat_data.get("dodge", 5),
        ))

        # Note: Other player-related data like world, flags, statistics, loadout
        # would be handled by their respective repositories.

    def load_player_data(self, save_id: int) -> Dict[str, Any]:
        """
        Loads and reconstructs player core and combat statistics for a given save ID.
        Returns a dictionary containing the player data.
        """
        player_core_row = self.execute_query(
            self.db_path, "SELECT * FROM player_core WHERE save_id = ?", (save_id,)
        )
        player_combat_row = self.execute_query(
            self.db_path, "SELECT * FROM player_combat WHERE save_id = ?", (save_id,)
        )

        if not player_core_row:
            # This should ideally not happen if save_id is valid, but defensive coding is good.
            raise ValueError(f"Player core data not found for save_id: {save_id}")
        
        # ``sqlite3.Row`` does not implement ``dict.get``. Use direct indexing.
        # ``mana`` may be NULL in the database, which yields ``None`` – acceptable for the game logic.
        # ``pco`` may be ``None`` if player_combat row doesn't exist; provide defaults.
        pc = player_core_row[0]
        pco = player_combat_row[0] if player_combat_row else None

        player_data = {
            "player": {
                "name": pc["name"],
                "level": pc["level"],
                "exp": pc["exp"],
                "hp": pc["hp"],
                "mana": pc["mana"],
                "base_attack": pc["base_attack"],
                "base_defense": pc["base_defense"],
                "gold": pc["gold"],
                "luck": pc["luck"],
                "reputation": pc["reputation"],
                "skill_points": pc["skill_points"],
                "critical_chance": pco["critical_chance"] if pco else 15,
                "critical_multiplier": pco["critical_multiplier"] if pco else 2.0,
                "accuracy": pco["accuracy"] if pco else 5,
                "dodge": pco["dodge"] if pco else 5,
            }
        }
        return player_data

    # Add delete_player_data if needed for specific save slot cleanup by this repo
    # def delete_player_data(self, save_id: int) -> None:
    #     """ Deletes player data for a given save ID. """
    #     self.execute_non_query(self.db_path, "DELETE FROM player_core WHERE save_id = ?", (save_id,))
    #     self.execute_non_query(self.db_path, "DELETE FROM player_combat WHERE save_id = ?", (save_id,))

