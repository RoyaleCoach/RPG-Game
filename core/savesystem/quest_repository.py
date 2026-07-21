# quest_repository.py

import json
from typing import Any, List, Tuple

class QuestRepository:
    """
    Handles all database operations related to player quests.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        from core.savesystem.database import execute_query, execute_non_query
        from core.savesystem.utils import dict_to_json_string, json_string_to_dict
        self.execute_query = execute_query
        self.execute_non_query = execute_non_query
        self.dict_to_json_string = dict_to_json_string
        self.json_string_to_dict = json_string_to_dict

    def save_quest_meta(self, save_id: int, story_progress: int) -> None:
        """
        Saves the quest story progress for a given save ID.
        """
        params_tuple = (save_id, story_progress)
        self.execute_non_query(self.db_path, """
            INSERT OR REPLACE INTO quest_meta
                (save_id, story_progress)
            VALUES (?, ?)
        """, params_tuple)

    def load_quest_meta(self, save_id: int) -> int:
        """
        Loads the quest story progress for a given save ID.
        """
        rows = self.execute_query(
            self.db_path, "SELECT story_progress FROM quest_meta WHERE save_id = ?", (save_id,)
        )
        if not rows: # Check for empty list of rows
            return 0 
        return rows[0]["story_progress"] # rows[0] is safe if query returns items

    def save_active_quests(self, save_id: int, active_quests: List[Any]) -> None:
        """
        Saves the list of active quests for a given save ID.
        Clears existing active quests and inserts the new ones in a single transaction.
        """
        from core.savesystem.database import get_db_connection
        with get_db_connection(self.db_path) as conn:
            conn.execute("DELETE FROM quests_active WHERE save_id = ?", (save_id,))
            if not active_quests:
                return
            quests_to_insert: List[Tuple[int, str]] = [
                (save_id, self.dict_to_json_string(quest)) for quest in active_quests
            ]
            conn.executemany(
                "INSERT INTO quests_active (save_id, quest_data) VALUES (?, ?)",
                quests_to_insert,
            )

    def load_active_quests(self, save_id: int) -> List[Any]:
        """
        Loads active quests for a given save ID.
        Returns a list of quest dictionaries.
        """
        rows = self.execute_query(
            self.db_path, "SELECT quest_data FROM quests_active WHERE save_id = ?", (save_id,)
        )
        
        active_quests = []
        for row in rows:
            try:
                quest_data = self.json_string_to_dict(row["quest_data"])
                active_quests.append(quest_data)
            except Exception as e:
                print(f"Error decoding quest data for save_id {save_id}: {e}")
                continue
        return active_quests

    def save_completed_quests(self, save_id: int, completed_quests: List[Any]) -> None:
        """
        Saves the list of completed quests for a given save ID.
        Clears existing completed quests and inserts the new ones in a single transaction.
        """
        from core.savesystem.database import get_db_connection
        with get_db_connection(self.db_path) as conn:
            conn.execute("DELETE FROM quests_completed WHERE save_id = ?", (save_id,))
            if not completed_quests:
                return
            quests_to_insert = [(save_id, self.dict_to_json_string(quest)) for quest in completed_quests]
            conn.executemany(
                "INSERT INTO quests_completed (save_id, quest_data) VALUES (?, ?)",
                quests_to_insert,
            )


    def load_completed_quests(self, save_id: int) -> List[Any]:
        """
        Loads completed quests for a given save ID.
        Returns a list of quest dictionaries.
        """
        rows = self.execute_query(
            self.db_path, "SELECT quest_data FROM quests_completed WHERE save_id = ?", (save_id,)
        )
        
        completed_quests = []
        for row in rows:
            try:
                quest_data = self.json_string_to_dict(row["quest_data"])
                completed_quests.append(quest_data)
            except Exception as e:
                print(f"Error decoding completed quest data for save_id {save_id}: {e}")
                continue
        return completed_quests
