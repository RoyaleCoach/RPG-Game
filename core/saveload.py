"""
core/saveload.py
----------------
Responsible for **only** three things:

1. Writing a Python dict to a JSON file on disk.
2. Reading a JSON file from disk and returning a Python dict.
3. Telling callers whether a save file exists.

It knows *nothing* about Player fields, world state, or gameplay.
All serialization logic lives in ``Player.to_dict()`` / ``Player.from_dict()``.
"""

from __future__ import annotations

import json
import os
import sys
import time
from typing import Any

from core.player import Player


# ── Path resolution ───────────────────────────────────────────────────────────

def _resolve_base_dir() -> str:
    """Return the project root, whether running from source or a frozen exe."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


BASE_DIR = _resolve_base_dir()
SAVE_DIR = os.path.join(BASE_DIR, "save")


# ── SaveSystem ────────────────────────────────────────────────────────────────

class SaveSystem:
    """
    Thin persistence layer: reads and writes save files.

    Responsibilities
    ~~~~~~~~~~~~~~~~
    * Resolve the file path for a given save-slot name.
    * Wrap the player payload with metadata (timestamp) before writing.
    * Strip the metadata wrapper and delegate reconstruction to ``Player``.
    * Report I/O errors without crashing the caller.

    Non-responsibilities (intentionally excluded)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    * Knowing what fields Player contains.
    * Duplicating world-state values that Player already owns.
    * Any gameplay logic.
    """

    CURRENT_SAVE_VERSION = 2  # bump when the save format changes

    def __init__(self, game: Any) -> None:
        self.game = game

    # ── Public interface ──────────────────────────────────────────────────────

    def save(self, filename: str = "save.json") -> bool:
        """
        Serialize the current player and write it to *filename*.

        Returns ``True`` on success, ``False`` on any I/O or serialization error.
        The caller may show its own message; this method prints a confirmation
        or error so the user always gets feedback.
        """
        os.makedirs(SAVE_DIR, exist_ok=True)
        path = self._save_path(filename)

        payload = self._build_payload(self.game.player)

        try:
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(payload, fh, indent=4, ensure_ascii=False)
            print(f"💾 Game saved: {path}")
            return True
        except (OSError, TypeError) as exc:
            print(f"SAVE ERROR: {exc}")
            return False

    def load(self, filename: str = "save.json") -> Player | None:
        """
        Load a save file and return a fully constructed ``Player``.

        Returns ``None`` if the file is missing, corrupt, or structurally
        invalid.  Callers should treat ``None`` as "no save available" and
        fall back to creating a new player.

        Note: the returned player has no item catalog attached.
        The caller must call ``player.initialize_items(game_data.items)``
        before the player is used in gameplay.
        """
        path = self._save_path(filename)

        try:
            with open(path, "r", encoding="utf-8") as fh:
                raw = json.load(fh)
        except FileNotFoundError:
            print(f"LOAD ERROR: save file not found at {path}")
            return None
        except json.JSONDecodeError as exc:
            print(f"LOAD ERROR: save file is corrupt — {exc}")
            return None

        player = self._reconstruct_player(raw)
        if player is not None:
            print(f"📂 Save loaded: {path}")
        return player

    def save_exists(self, filename: str = "save.json") -> bool:
        """Return True if the given save file exists on disk."""
        return os.path.isfile(self._save_path(filename))

    # ── Private helpers ───────────────────────────────────────────────────────

    def _save_path(self, filename: str) -> str:
        """Resolve the full path for *filename* inside the save directory."""
        return os.path.join(SAVE_DIR, filename)

    def _build_payload(self, player: Player) -> dict[str, Any]:
        """
        Wrap the player's save data with top-level metadata.

        The ``player_data`` key contains exactly what ``Player.to_dict()``
        returns — SaveSystem never inspects or copies individual fields.
        """
        return {
            "save_version": self.CURRENT_SAVE_VERSION,
            "timestamp": time.time(),
            "player_data": player.to_dict(),
        }

    def _reconstruct_player(self, raw: dict[str, Any]) -> Player | None:
        """
        Extract player data from the save payload and delegate to Player.

        Handles two envelope shapes:
          * New format  (v2+): ``raw["player_data"]`` holds the sectioned dict.
          * Legacy format (v1): ``raw["player"]`` was the flat player dict and
            ``raw["world"]`` held duplicate floor/boss/run counters.

        In the legacy case we merge the two sub-dicts before handing off to
        ``Player.from_dict()``, which recognises the flat structure and applies
        its own legacy path.
        """
        try:
            if "player_data" in raw:
                # New format — delegate entirely to Player
                return Player.from_dict(raw["player_data"])

            # Legacy format — merge player + world into a flat dict
            legacy_player = dict(raw.get("player", {}))
            legacy_world = raw.get("world", {})

            # World section may have held the authoritative floor/boss values;
            # prefer world if present (matches original SaveSystem behaviour).
            legacy_player.setdefault("floor", legacy_world.get("current_floor", 1))
            legacy_player.setdefault("boss_progress", legacy_world.get("boss_progress", 0))
            legacy_player.setdefault("dungeon_runs", legacy_world.get("dungeon_runs", 0))

            return Player.from_dict(legacy_player)

        except (KeyError, TypeError, ValueError) as exc:
            print(f"LOAD ERROR: could not reconstruct player — {exc}")
            return None