# inventory_repository.py

from typing import Any, Dict, List, Tuple # Added Tuple for type hinting

class InventoryRepository:
    """
    Handles all database operations related to player inventory.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        # Import necessary database functions
        from core.savesystem.database import execute_query, execute_non_query
        self.execute_query = execute_query
        self.execute_non_query = execute_non_query

    def save_inventory(self, save_id: int, inventory_data: Dict[str, int]) -> None:
        """
        Saves the player's inventory for a given save ID.
        Deletes existing inventory and re-inserts in a single transaction
        to prevent data loss on crash.
        """
        from core.savesystem.database import get_db_connection
        with get_db_connection(self.db_path) as conn:
            conn.execute("DELETE FROM inventory_items WHERE save_id = ?", (save_id,))
            if inventory_data:
                insert_query = """
                    INSERT INTO inventory_items (save_id, item_name, quantity)
                    VALUES (?, ?, ?)
                """
                items_to_insert: List[Tuple[int, str, int]] = [
                    (save_id, item_name, quantity)
                    for item_name, quantity in inventory_data.items()
                ]
                if items_to_insert:
                    conn.executemany(insert_query, items_to_insert)

    def load_inventory(self, save_id: int) -> Dict[str, int]:
        """
        Loads the player's inventory for a given save ID.
        Returns a dictionary where keys are item names and values are quantities.
        """
        rows = self.execute_query(
            self.db_path,
            "SELECT item_name, quantity FROM inventory_items WHERE save_id = ?",
            (save_id,)
        )
        
        inventory = {row["item_name"]: row["quantity"] for row in rows}
        return inventory
