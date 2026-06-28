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
        This implementation clears existing inventory for the save_id and re-inserts.
        Ensures efficient bulk insertion using database.py's executemany capability.
        """
        # First, delete existing inventory items for this save_id.
        self.execute_non_query(self.db_path, "DELETE FROM inventory_items WHERE save_id = ?", (save_id,))
        
        # Prepare data for bulk insertion if inventory_data is not empty.
        if inventory_data: 
            insert_query = """
                INSERT INTO inventory_items (save_id, item_name, quantity)
                VALUES (?, ?, ?)
            """
            # Prepare data as a list of tuples for executemany.
            items_to_insert: List[Tuple[int, str, int]] = [
                (save_id, item_name, quantity)
                for item_name, quantity in inventory_data.items()
            ]
            
            if items_to_insert:
                # Call execute_non_query with the list of tuples; database.py should handle executemany.
                self.execute_non_query(self.db_path, insert_query, items_to_insert)

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
