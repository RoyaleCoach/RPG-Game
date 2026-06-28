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
        """
        # Save equipped weapon and armor
        self.execute_non_query(self.db_path, """
            INSERT OR REPLACE INTO player_loadout
                (save_id, weapon, armor)
            VALUES (?, ?, ?)
        """, (
            save_id,
            loadout_data.get("weapon", "Fists"),
            loadout_data.get("armor"), # Can be None
        ))

        # Save learned spells
        learned_spells = loadout_data.get("learned_spells", [])
        # Clear existing spells before inserting new ones
        self.execute_non_query(self.db_path, "DELETE FROM learned_spells WHERE save_id = ?", (save_id,))
        if learned_spells:
            insert_spells_query = "INSERT INTO learned_spells (save_id, spell_name) VALUES (?, ?)"
            spell_params = [(save_id, spell) for spell in learned_spells]
            # Assuming execute_non_query can handle list of tuples for batch insert, otherwise use explicit executemany
            self.execute_non_query(self.db_path, insert_spells_query, spell_params) # Placeholder for potential executemany

        # Save unlocked skills
        unlocked_skills = loadout_data.get("unlocked_skills", [])
        # Clear existing skills before inserting new ones
        self.execute_non_query(self.db_path, "DELETE FROM unlocked_skills WHERE save_id = ?", (save_id,))
        if unlocked_skills:
            insert_skills_query = "INSERT INTO unlocked_skills (save_id, skill_name) VALUES (?, ?)"
            skill_params = [(save_id, skill) for skill in unlocked_skills]
            # Assuming execute_non_query can handle list of tuples for batch insert
            self.execute_non_query(self.db_path, insert_skills_query, skill_params) # Placeholder for potential executemany

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
