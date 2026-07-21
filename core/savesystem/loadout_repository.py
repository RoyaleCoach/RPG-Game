# loadout_repository.py

from typing import Any, Dict, List

class LoadoutRepository:
    """
    Handles database operations for player's equipped items (weapon, armor)
    and skill/spell loadouts.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        from core.savesystem.database import execute_query, execute_non_query
        self.execute_query = execute_query
        self.execute_non_query = execute_non_query

    def save_loadout(self, save_id: int, loadout_data: Dict[str, Any]) -> None:
        """
        Saves weapon, armor, learned spells, and unlocked skills for a given save ID.
        All writes happen in a single transaction to prevent data loss on crash.
        """
        from core.savesystem.database import get_db_connection
        with get_db_connection(self.db_path) as conn:
            # Save equipped weapon and armor
            conn.execute("""
                INSERT OR REPLACE INTO player_loadout
                    (save_id, weapon, armor)
                VALUES (?, ?, ?)
            """, (
                save_id,
                loadout_data.get("weapon", "Fists"),
                loadout_data.get("armor"),
            ))

            # Save learned spells
            learned_spells = loadout_data.get("learned_spells", [])
            conn.execute("DELETE FROM learned_spells WHERE save_id = ?", (save_id,))
            if learned_spells:
                conn.executemany(
                    "INSERT INTO learned_spells (save_id, spell_name) VALUES (?, ?)",
                    [(save_id, spell) for spell in learned_spells],
                )

            # Save unlocked skills
            unlocked_skills = loadout_data.get("unlocked_skills", [])
            conn.execute("DELETE FROM unlocked_skills WHERE save_id = ?", (save_id,))
            if unlocked_skills:
                conn.executemany(
                    "INSERT INTO unlocked_skills (save_id, skill_name) VALUES (?, ?)",
                    [(save_id, skill) for skill in unlocked_skills],
                )

    def load_loadout(self, save_id: int) -> Dict[str, Any]:
        """
        Loads equipped items, learned spells, and unlocked skills for a given save ID.
        Returns a dictionary containing loadout data.
        """
        # Load equipment
        loadout_row = self.execute_query(
            self.db_path, "SELECT weapon, armor FROM player_loadout WHERE save_id = ?", (save_id,)
        )
        
        weapon = "Fists" # Default
        armor = None
        if loadout_row:
            weapon = loadout_row[0]["weapon"]
            armor = loadout_row[0]["armor"]

        # Load learned spells
        spells_rows = self.execute_query(
            self.db_path, "SELECT spell_name FROM learned_spells WHERE save_id = ?", (save_id,)
        )
        learned_spells = [row["spell_name"] for row in spells_rows]

        # Load unlocked skills
        skills_rows = self.execute_query(
            self.db_path, "SELECT skill_name FROM unlocked_skills WHERE save_id = ?", (save_id,)
        )
        unlocked_skills = [row["skill_name"] for row in skills_rows]

        return {
            "weapon": weapon,
            "armor": armor,
            "learned_spells": learned_spells,
            "unlocked_skills": unlocked_skills,
        }
