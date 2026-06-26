"""
game_menu.py
------------
Self-contained menu configuration.

MenuEntry    – pairs a key, a display label, and the callable to invoke.
MenuRegistry – ordered collection of entries; renders itself and dispatches
               actions, so Game._game_loop contains zero menu logic.

Adding a new menu item (e.g. "Crafting") is a single MenuEntry line.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


# ── Menu entry ────────────────────────────────────────────────────────────────

@dataclass
class MenuEntry:
    """One item in the main menu."""

    key: str          # What the player types, e.g. "1"
    label: str        # Display text, e.g. "Main Story"
    action: Callable  # Zero-argument callable invoked on selection


# ── Menu registry ─────────────────────────────────────────────────────────────

class MenuRegistry:
    """
    Ordered collection of MenuEntry objects.

    Responsibilities
    ----------------
    * Render the menu to stdout.
    * Dispatch the correct action for a given key.
    * Report whether a key is the exit key (so the loop can break).

    The registry does not know about Game or GameContext — it is a pure
    presentation / dispatch layer.
    """

    EXIT_KEY = "0"

    def __init__(self, entries: list[MenuEntry]) -> None:
        # Preserve insertion order; dict keyed by entry.key for O(1) lookup.
        self._entries: dict[str, MenuEntry] = {e.key: e for e in entries}

    # ── Public API ────────────────────────────────────────────────────────────

    def show(self) -> str:
        """Print the menu and return the player's raw input."""
        print("\n=== MENU ===")
        for entry in self._entries.values():
            print(f"[{entry.key}] {entry.label}")
        return input("> ").strip()

    def dispatch(self, key: str) -> bool:
        """
        Invoke the action bound to *key*.

        Returns
        -------
        True  – action was found and called.
        False – key is unknown (caller should print an error).
        """
        entry = self._entries.get(key)
        if entry is None:
            return False
        entry.action()
        return True

    def is_exit(self, key: str) -> bool:
        return key == self.EXIT_KEY
