# flags_repository.py

from typing import Any, Dict

class FlagsRepository:
    """
    Handles all database operations related to player flags.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        from core.savesystem.database import execute_query, execute_non_query
        self.execute_query = execute_query
        self.execute_non_query = execute_non_query

    def save_flags(self, save_id: int, flags_data: Dict[str, bool]) -> None:
        """
        Saves player flags for a given save ID.
        Flags are stored as integers (0 or 1).
        """
        self.execute_non_query(self.db_path, """
            INSERT OR REPLACE INTO player_flags
                (save_id, skip_next_battle, skip_next_trap, skip_next_boss_preparation)
            VALUES (?, ?, ?, ?)
        """, (
            save_id,
            int(flags_data.get("skip_next_battle", False)),
            int(flags_data.get("skip_next_trap", False)),
            int(flags_data.get("skip_next_boss_preparation", False)),
        ))

    def load_flags(self, save_id: int) -> Dict[str, bool]:
        """
        Loads player flags for a given save ID.
        Returns a dictionary with flag names and their boolean values.
        """
        row = self.execute_query(
            self.db_path, "SELECT * FROM player_flags WHERE save_id = ?", (save_id,)
        )

        if not row:
            raise ValueError(f"Flags data not found for save_id: {save_id}")
        
        flags = row[0]
        return {
            "skip_next_battle": bool(flags["skip_next_battle"]),
            "skip_next_trap": bool(flags["skip_next_trap"]),
            "skip_next_boss_preparation": bool(flags["skip_next_boss_preparation"]),
        }
