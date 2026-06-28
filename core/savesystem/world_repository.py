# world_repository.py

from typing import Any, Dict

class WorldRepository:
    """
    Handles all database operations related to player's world progression.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        from core.savesystem.database import execute_query, execute_non_query
        self.execute_query = execute_query
        self.execute_non_query = execute_non_query

    def save_world_data(self, save_id: int, world_data: Dict[str, Any]) -> None:
        """
        Saves player's world progression data for a given save ID.
        Uses INSERT OR REPLACE for atomic upsert.
        """
        self.execute_non_query(self.db_path, """
            INSERT OR REPLACE INTO player_world
                (save_id, floor, boss_progress, dungeon_runs, last_event)
            VALUES (?, ?, ?, ?, ?)
        """, (
            save_id,
            world_data.get("floor", 1),
            world_data.get("boss_progress", 0),
            world_data.get("dungeon_runs", 0),
            world_data.get("last_event"),
        ))

    def load_world_data(self, save_id: int) -> Dict[str, Any]:
        """
        Loads player's world progression data for a given save ID.
        Returns a dictionary containing world data.
        """
        row = self.execute_query(
            self.db_path, "SELECT * FROM player_world WHERE save_id = ?", (save_id,)
        )

        if not row:
            raise ValueError(f"World data not found for save_id: {save_id}")
        
        world_data = row[0] # Assuming exactly one row will be returned
        return {
            "floor": world_data["floor"],
            "boss_progress": world_data["boss_progress"],
            "dungeon_runs": world_data["dungeon_runs"],
            "last_event": world_data["last_event"],
        }

    # Optional: Add methods for save_flags, load_flags if you want to separate flags
    # or if flags become more complex. For now, let's assume player_repository handles them.
