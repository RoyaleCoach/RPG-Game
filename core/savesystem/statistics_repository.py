# statistics_repository.py

from typing import Any, Dict

class StatisticsRepository:
    """
    Handles all database operations related to player statistics.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        from core.savesystem.database import execute_query, execute_non_query
        self.execute_query = execute_query
        self.execute_non_query = execute_non_query

    def save_statistics(self, save_id: int, stats_data: Dict[str, Any]) -> None:
        """
        Saves player statistics for a given save ID.
        Uses INSERT OR REPLACE for upsert.
        """
        self.execute_non_query(self.db_path, """
            INSERT OR REPLACE INTO player_statistics
                (save_id, enemies_killed, puzzles_solved)
            VALUES (?, ?, ?)
        """, (
            save_id,
            stats_data.get("enemies_killed", 0),
            stats_data.get("puzzles_solved", 0),
        ))

    def load_statistics(self, save_id: int) -> Dict[str, Any]:
        """
        Loads player statistics for a given save ID.
        Returns a dictionary containing statistics data.
        """
        row = self.execute_query(
            self.db_path, "SELECT * FROM player_statistics WHERE save_id = ?", (save_id,)
        )

        if not row:
            raise ValueError(f"Statistics data not found for save_id: {save_id}")
        
        stats = row[0]
        return {
            "enemies_killed": stats["enemies_killed"],
            "puzzles_solved": stats["puzzles_solved"],
        }
