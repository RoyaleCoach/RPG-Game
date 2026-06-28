"""
core/saveload.py
----------------
SQLite persistence layer untuk save/load game.

Keputusan desain
~~~~~~~~~~~~~~~~
* Public API identik dengan versi JSON sebelumnya:
    save(filename)  → bool
    load(filename)  → Player | None
    save_exists(filename) → bool

  Satu-satunya perubahan yang terlihat dari luar: "filename" sekarang
  adalah nama *slot* (string bebas), bukan path file .json.
  Semua slot tersimpan dalam satu database ``game.db``.

* Player.to_dict() / Player.from_dict() TIDAK diubah.
  Layer SQLite cukup mengurai dict yang dikembalikan to_dict() ke baris-baris
  tabel, dan merakit ulang dict yang sama saat load sebelum diserahkan ke
  from_dict(). Tidak ada duplikasi logika serialisasi.

* Multi-slot gratis: setiap slot adalah satu baris di tabel ``saves``,
  semua tabel anak mengacu ke ``save_id`` via foreign key + CASCADE DELETE.

* Migrasi otomatis: jika ditemukan save.json lama di direktori save,
  isinya diimpor ke SQLite dan file asli diubah namanya jadi .bak.

Schema
~~~~~~
  saves               – metadata slot (nama, versi, timestamp)
  player_core         – stat utama player
  player_combat       – crit / accuracy / dodge
  player_world        – floor, boss, dungeon
  player_flags        – skip_next_* flags
  player_statistics   – enemies_killed, puzzles_solved
  player_loadout      – weapon, armor yang dipakai
  inventory_items     – (item_name, quantity) per slot  [one-to-many]
  learned_spells      – satu baris per spell            [one-to-many]
  unlocked_skills     – satu baris per skill            [one-to-many]
  quests_active       – satu baris per quest aktif      [one-to-many]
  quests_completed    – satu baris per quest selesai    [one-to-many]
  quest_meta          – story_progress per slot
"""

from __future__ import annotations

import json
import os
import sqlite3
import sys
import time
from contextlib import contextmanager
from typing import Any, Generator

from core.player import Player


# ── Path resolution ───────────────────────────────────────────────────────────

def _resolve_base_dir() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


BASE_DIR = _resolve_base_dir()
SAVE_DIR = os.path.join(BASE_DIR, "save")
DB_PATH = os.path.join(SAVE_DIR, "game.db")
SAVE_VERSION = 3

# ── DDL: semua CREATE TABLE dalam satu tempat ─────────────────────────────────

_DDL = """
-- Aktifkan foreign-key enforcement (SQLite tidak aktifkan secara default)
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS saves (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    slot_name       TEXT    NOT NULL UNIQUE,
    save_version    INTEGER NOT NULL DEFAULT 2,
    timestamp       REAL    NOT NULL
);

-- Satu baris per slot: stat utama player
CREATE TABLE IF NOT EXISTS player_core (
    save_id         INTEGER PRIMARY KEY REFERENCES saves(id) ON DELETE CASCADE,
    name            TEXT    NOT NULL,
    level           INTEGER NOT NULL DEFAULT 1,
    exp             INTEGER NOT NULL DEFAULT 0,
    hp              INTEGER NOT NULL DEFAULT 100,
    mana            INTEGER,
    base_attack     INTEGER NOT NULL DEFAULT 10,
    base_defense    INTEGER NOT NULL DEFAULT 5,
    gold            INTEGER NOT NULL DEFAULT 50,
    luck            INTEGER NOT NULL DEFAULT 0,
    reputation      INTEGER NOT NULL DEFAULT 0,
    skill_points    INTEGER NOT NULL DEFAULT 0
);

-- Combat stats terpisah agar mudah di-extend nanti
CREATE TABLE IF NOT EXISTS player_combat (
    save_id             INTEGER PRIMARY KEY REFERENCES saves(id) ON DELETE CASCADE,
    critical_chance     INTEGER NOT NULL DEFAULT 15,
    critical_multiplier REAL    NOT NULL DEFAULT 2.0,
    accuracy            INTEGER NOT NULL DEFAULT 5,
    dodge               INTEGER NOT NULL DEFAULT 5
);

-- Progres dunia
CREATE TABLE IF NOT EXISTS player_world (
    save_id         INTEGER PRIMARY KEY REFERENCES saves(id) ON DELETE CASCADE,
    floor           INTEGER NOT NULL DEFAULT 1,
    boss_progress   INTEGER NOT NULL DEFAULT 0,
    dungeon_runs    INTEGER NOT NULL DEFAULT 0,
    last_event      TEXT
);

-- Boolean flags (disimpan sebagai 0/1)
CREATE TABLE IF NOT EXISTS player_flags (
    save_id                     INTEGER PRIMARY KEY REFERENCES saves(id) ON DELETE CASCADE,
    skip_next_battle            INTEGER NOT NULL DEFAULT 0,
    skip_next_trap              INTEGER NOT NULL DEFAULT 0,
    skip_next_boss_preparation  INTEGER NOT NULL DEFAULT 0
);

-- Statistik permainan
CREATE TABLE IF NOT EXISTS player_statistics (
    save_id         INTEGER PRIMARY KEY REFERENCES saves(id) ON DELETE CASCADE,
    enemies_killed  INTEGER NOT NULL DEFAULT 0,
    puzzles_solved  INTEGER NOT NULL DEFAULT 0
);

-- Equipment yang sedang dipakai
CREATE TABLE IF NOT EXISTS player_loadout (
    save_id         INTEGER PRIMARY KEY REFERENCES saves(id) ON DELETE CASCADE,
    weapon          TEXT    NOT NULL DEFAULT 'Fists',
    armor           TEXT                                    -- NULL = tidak pakai armor
);

-- Inventory: banyak item per slot  [one-to-many]
CREATE TABLE IF NOT EXISTS inventory_items (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    save_id         INTEGER NOT NULL REFERENCES saves(id) ON DELETE CASCADE,
    item_name       TEXT    NOT NULL,
    quantity        INTEGER NOT NULL DEFAULT 1,
    UNIQUE(save_id, item_name)
);

-- Spell yang sudah dipelajari  [one-to-many]
CREATE TABLE IF NOT EXISTS learned_spells (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    save_id         INTEGER NOT NULL REFERENCES saves(id) ON DELETE CASCADE,
    spell_name      TEXT    NOT NULL,
    UNIQUE(save_id, spell_name)
);

-- Skill yang sudah di-unlock  [one-to-many]
CREATE TABLE IF NOT EXISTS unlocked_skills (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    save_id         INTEGER NOT NULL REFERENCES saves(id) ON DELETE CASCADE,
    skill_name      TEXT    NOT NULL,
    UNIQUE(save_id, skill_name)
);

-- Story progress (beda tabel agar tidak campur aduk dengan quest rows)
CREATE TABLE IF NOT EXISTS quest_meta (
    save_id         INTEGER PRIMARY KEY REFERENCES saves(id) ON DELETE CASCADE,
    story_progress  INTEGER NOT NULL DEFAULT 0
);

-- Quest aktif (list of string/dict — simpan sebagai JSON text per row)
CREATE TABLE IF NOT EXISTS quests_active (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    save_id         INTEGER NOT NULL REFERENCES saves(id) ON DELETE CASCADE,
    quest_data      TEXT    NOT NULL  -- JSON string satu quest
);

-- Quest yang sudah selesai
CREATE TABLE IF NOT EXISTS quests_completed (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    save_id         INTEGER NOT NULL REFERENCES saves(id) ON DELETE CASCADE,
    quest_data      TEXT    NOT NULL
);
"""


# ── SaveSystem ────────────────────────────────────────────────────────────────

class SaveSystem:
    """
    SQLite persistence layer.

    Public API (identik dengan versi JSON):
        save(slot)        → bool
        load(slot)        → Player | None
        save_exists(slot) → bool

    Parameter ``filename`` pada versi lama sekarang menjadi ``slot_name``.
    Untuk backward-compat, parameter masih bisa dipanggil dengan nama
    ``filename`` (alias diterima).
    """

    CURRENT_SAVE_VERSION = 2

    def __init__(self, game: Any) -> None:
        self.game = game
        os.makedirs(SAVE_DIR, exist_ok=True)
        self._init_db()
        self._maybe_migrate_json()

    # ── Public interface ──────────────────────────────────────────────────────

    def save(self, filename: str = "default") -> bool:
        """
        Simpan state player saat ini ke slot *filename*.
        Returns True jika berhasil.
        """
        slot = self._slot_name(filename)
        payload = self.game.player.to_dict()

        try:
            with self._db() as conn:
                save_id = self._upsert_slot(conn, slot)
                self._write_all_tables(conn, save_id, payload)
            print(f"💾 Game saved → slot '{slot}' ({DB_PATH})")
            return True
        except sqlite3.Error as exc:
            print(f"SAVE ERROR: {exc}")
            return False

    def load(self, filename: str = "default") -> Player | None:
        """
        Load player dari slot *filename*.
        Returns None jika slot tidak ditemukan atau data rusak.
        """
        slot = self._slot_name(filename)

        try:
            with self._db() as conn:
                save_id = self._find_slot(conn, slot)
                if save_id is None:
                    print(f"LOAD ERROR: slot '{slot}' tidak ditemukan.")
                    return None
                payload = self._read_all_tables(conn, save_id)

            player = Player.from_dict(payload)
            print(f"📂 Save loaded ← slot '{slot}'")
            return player

        except (sqlite3.Error, KeyError, TypeError, ValueError) as exc:
            print(f"LOAD ERROR: {exc}")
            return None

    def save_exists(self, filename: str = "default") -> bool:
        """True jika slot *filename* ada di database."""
        slot = self._slot_name(filename)
        try:
            with self._db() as conn:
                return self._find_slot(conn, slot) is not None
        except sqlite3.Error:
            return False

    # ── DB init ───────────────────────────────────────────────────────────────

    def _init_db(self) -> None:
        """Buat semua tabel jika belum ada."""
        with self._db() as conn:
            conn.executescript(_DDL)

    # ── Context manager ───────────────────────────────────────────────────────

    @contextmanager
    def _db(self) -> Generator[sqlite3.Connection, None, None]:
        """
        Buka koneksi SQLite, aktifkan foreign keys, yield, lalu commit/rollback.
        Menggunakan row_factory agar hasil query bisa diakses via nama kolom.
        """
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ── Slot helpers ──────────────────────────────────────────────────────────

    @staticmethod
    def _slot_name(filename: str) -> str:
        """
        Normalise slot name: hapus ekstensi .json jika ada
        (agar pemanggil lama ``save("save.json")`` tetap berjalan).
        """
        return filename.removesuffix(".json")

    def _upsert_slot(self, conn: sqlite3.Connection, slot: str) -> int:
        """
        Insert slot baru atau update timestamp jika sudah ada.
        Returns save_id.
        """
        conn.execute(
            """
            INSERT INTO saves (slot_name, save_version, timestamp)
            VALUES (?, ?, ?)
            ON CONFLICT(slot_name) DO UPDATE SET
                save_version = excluded.save_version,
                timestamp    = excluded.timestamp
            """,
            (slot, self.CURRENT_SAVE_VERSION, time.time()),
        )
        row = conn.execute(
            "SELECT id FROM saves WHERE slot_name = ?", (slot,)
        ).fetchone()
        return row["id"]

    @staticmethod
    def _find_slot(conn: sqlite3.Connection, slot: str) -> int | None:
        """Returns save_id untuk slot ini, atau None jika tidak ada."""
        row = conn.execute(
            "SELECT id FROM saves WHERE slot_name = ?", (slot,)
        ).fetchone()
        return row["id"] if row else None

    # ── Write helpers ─────────────────────────────────────────────────────────

    def _write_all_tables(
        self, conn: sqlite3.Connection, save_id: int, payload: dict
    ) -> None:
        """
        Tulis seluruh payload (hasil to_dict()) ke tabel-tabel SQLite.
        Urutan: hapus data lama untuk save_id ini (kecuali saves),
        lalu insert ulang — sederhana dan idempoten.
        """
        self._clear_save_data(conn, save_id)

        p = payload.get("player", {})
        w = payload.get("world", {})
        lo = payload.get("loadout", {})
        q = payload.get("quests", {})
        s = payload.get("statistics", {})
        f = payload.get("flags", {})

        # ── player_core ───────────────────────────────────────────────────────
        conn.execute(
            """
            INSERT INTO player_core
                (save_id, name, level, exp, hp, mana,
                 base_attack, base_defense, gold, luck, reputation, skill_points)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                save_id,
                p.get("name", "Adventurer"),
                p.get("level", 1),
                p.get("exp", 0),
                p.get("hp", 100),
                p.get("mana"),
                p.get("base_attack", 10),
                p.get("base_defense", 5),
                p.get("gold", 50),
                p.get("luck", 0),
                p.get("reputation", 0),
                p.get("skill_points", 0),
            ),
        )

        # ── player_combat ─────────────────────────────────────────────────────
        conn.execute(
            """
            INSERT INTO player_combat
                (save_id, critical_chance, critical_multiplier, accuracy, dodge)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                save_id,
                p.get("critical_chance", 15),
                p.get("critical_multiplier", 2.0),
                p.get("accuracy", 5),
                p.get("dodge", 5),
            ),
        )

        # ── player_world ──────────────────────────────────────────────────────
        conn.execute(
            """
            INSERT INTO player_world (save_id, floor, boss_progress, dungeon_runs, last_event)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                save_id,
                w.get("floor", 1),
                w.get("boss_progress", 0),
                w.get("dungeon_runs", 0),
                w.get("last_event"),
            ),
        )

        # ── player_flags ──────────────────────────────────────────────────────
        conn.execute(
            """
            INSERT INTO player_flags
                (save_id, skip_next_battle, skip_next_trap, skip_next_boss_preparation)
            VALUES (?, ?, ?, ?)
            """,
            (
                save_id,
                int(f.get("skip_next_battle", False)),
                int(f.get("skip_next_trap", False)),
                int(f.get("skip_next_boss_preparation", False)),
            ),
        )

        # ── player_statistics ─────────────────────────────────────────────────
        conn.execute(
            """
            INSERT INTO player_statistics (save_id, enemies_killed, puzzles_solved)
            VALUES (?, ?, ?)
            """,
            (
                save_id,
                s.get("enemies_killed", 0),
                s.get("puzzles_solved", 0),
            ),
        )

        # ── player_loadout ────────────────────────────────────────────────────
        conn.execute(
            """
            INSERT INTO player_loadout (save_id, weapon, armor)
            VALUES (?, ?, ?)
            """,
            (
                save_id,
                lo.get("weapon", "Fists"),
                lo.get("armor"),
            ),
        )

        # ── inventory_items (many rows) ───────────────────────────────────────
        inventory: dict = lo.get("inventory", {})
        conn.executemany(
            "INSERT INTO inventory_items (save_id, item_name, quantity) VALUES (?, ?, ?)",
            [(save_id, name, qty) for name, qty in inventory.items()],
        )

        # ── learned_spells (many rows) ────────────────────────────────────────
        conn.executemany(
            "INSERT INTO learned_spells (save_id, spell_name) VALUES (?, ?)",
            [(save_id, sp) for sp in lo.get("learned_spells", [])],
        )

        # ── unlocked_skills (many rows) ───────────────────────────────────────
        conn.executemany(
            "INSERT INTO unlocked_skills (save_id, skill_name) VALUES (?, ?)",
            [(save_id, sk) for sk in lo.get("unlocked_skills", [])],
        )

        # ── quest_meta ────────────────────────────────────────────────────────
        conn.execute(
            "INSERT INTO quest_meta (save_id, story_progress) VALUES (?, ?)",
            (save_id, q.get("story_progress", 0)),
        )

        # ── quests_active (many rows, setiap quest = 1 row JSON) ──────────────
        conn.executemany(
            "INSERT INTO quests_active (save_id, quest_data) VALUES (?, ?)",
            [(save_id, json.dumps(entry, ensure_ascii=False))
             for entry in q.get("quest", [])],
        )

        # ── quests_completed (many rows) ──────────────────────────────────────
        conn.executemany(
            "INSERT INTO quests_completed (save_id, quest_data) VALUES (?, ?)",
            [(save_id, json.dumps(entry, ensure_ascii=False))
             for entry in q.get("completed_quests", [])],
        )

    @staticmethod
    def _clear_save_data(conn: sqlite3.Connection, save_id: int) -> None:
        """
        Hapus semua baris anak untuk save_id ini.
        Tabel 'saves' TIDAK dihapus — kita hanya update timestamp-nya.
        Foreign key CASCADE DELETE tidak dipakai di sini agar lebih eksplisit
        dan tidak menghapus baris saves itu sendiri.
        """
        child_tables = [
            "player_core", "player_combat", "player_world",
            "player_flags", "player_statistics", "player_loadout",
            "inventory_items", "learned_spells", "unlocked_skills",
            "quest_meta", "quests_active", "quests_completed",
        ]
        for table in child_tables:
            conn.execute(f"DELETE FROM {table} WHERE save_id = ?", (save_id,))

    # ── Read helpers ──────────────────────────────────────────────────────────

    def _read_all_tables(
        self, conn: sqlite3.Connection, save_id: int
    ) -> dict[str, Any]:
        """
        Baca semua tabel untuk save_id dan susun kembali menjadi dict
        yang identik dengan format Player.to_dict() — siap diserahkan ke
        Player.from_dict().
        """
        pc = self._fetchone(conn, "player_core",       save_id)
        pco = self._fetchone(conn, "player_combat",     save_id)
        pw = self._fetchone(conn, "player_world",      save_id)
        pf = self._fetchone(conn, "player_flags",      save_id)
        ps = self._fetchone(conn, "player_statistics", save_id)
        pl = self._fetchone(conn, "player_loadout",    save_id)
        qm = self._fetchone(conn, "quest_meta",        save_id)

        inventory = {
            row["item_name"]: row["quantity"]
            for row in conn.execute(
                "SELECT item_name, quantity FROM inventory_items WHERE save_id = ?",
                (save_id,),
            )
        }
        spells = [
            row["spell_name"]
            for row in conn.execute(
                "SELECT spell_name FROM learned_spells WHERE save_id = ?",
                (save_id,),
            )
        ]
        skills = [
            row["skill_name"]
            for row in conn.execute(
                "SELECT skill_name FROM unlocked_skills WHERE save_id = ?",
                (save_id,),
            )
        ]
        active_quests = [
            json.loads(row["quest_data"])
            for row in conn.execute(
                "SELECT quest_data FROM quests_active WHERE save_id = ?",
                (save_id,),
            )
        ]
        completed_quests = [
            json.loads(row["quest_data"])
            for row in conn.execute(
                "SELECT quest_data FROM quests_completed WHERE save_id = ?",
                (save_id,),
            )
        ]

        # Rakit ulang dict yang identik dengan Player.to_dict()
        return {
            "player": {
                "name":                 pc["name"],
                "level":                pc["level"],
                "exp":                  pc["exp"],
                "hp":                   pc["hp"],
                "mana":                 pc["mana"],
                "base_attack":          pc["base_attack"],
                "base_defense":         pc["base_defense"],
                "gold":                 pc["gold"],
                "luck":                 pc["luck"],
                "reputation":           pc["reputation"],
                "skill_points":         pc["skill_points"],
                "critical_chance":      pco["critical_chance"],
                "critical_multiplier":  pco["critical_multiplier"],
                "accuracy":             pco["accuracy"],
                "dodge":                pco["dodge"],
            },
            "world": {
                "floor":                pw["floor"],
                "boss_progress":        pw["boss_progress"],
                "dungeon_runs":         pw["dungeon_runs"],
                "last_event":           pw["last_event"],
            },
            "loadout": {
                "weapon":               pl["weapon"],
                "armor":                pl["armor"],
                "inventory":            inventory,
                "learned_spells":       spells,
                "unlocked_skills":      skills,
            },
            "quests": {
                "story_progress":       qm["story_progress"],
                "quest":                active_quests,
                "completed_quests":     completed_quests,
            },
            "statistics": {
                "enemies_killed":       ps["enemies_killed"],
                "puzzles_solved":       ps["puzzles_solved"],
            },
            "flags": {
                "skip_next_battle":             bool(pf["skip_next_battle"]),
                "skip_next_trap":               bool(pf["skip_next_trap"]),
                "skip_next_boss_preparation":   bool(pf["skip_next_boss_preparation"]),
            },
        }

    @staticmethod
    def _fetchone(
        conn: sqlite3.Connection, table: str, save_id: int
    ) -> sqlite3.Row:
        """
        Ambil satu baris dari *table* untuk save_id.
        Raise ValueError jika baris tidak ditemukan (data tidak konsisten).
        """
        row = conn.execute(
            f"SELECT * FROM {table} WHERE save_id = ?", (save_id,)
        ).fetchone()
        if row is None:
            raise ValueError(
                f"Tabel '{table}' tidak punya baris untuk save_id={save_id}")
        return row

    # ── Migration: JSON → SQLite ──────────────────────────────────────────────

    def _maybe_migrate_json(self) -> None:
        """
        Jika ditemukan save.json lama di direktori save, impor ke SQLite
        lalu ubah namanya jadi save.json.bak agar tidak diimpor ulang.
        """
        json_path = os.path.join(SAVE_DIR, "save.json")
        if not os.path.isfile(json_path):
            return

        print("🔄 Ditemukan save lama (JSON). Migrasi ke SQLite…")
        try:
            with open(json_path, "r", encoding="utf-8") as fh:
                raw = json.load(fh)

            # Ekstrak player_data (format v2) atau format lama
            if "player_data" in raw:
                player_data = raw["player_data"]
            elif "player" in raw:
                # v1 legacy: merge player + world
                player_data = dict(raw.get("player", {}))
                world = raw.get("world", {})
                player_data.setdefault(
                    "floor",         world.get("current_floor", 1))
                player_data.setdefault(
                    "boss_progress", world.get("boss_progress", 0))
                player_data.setdefault(
                    "dungeon_runs",  world.get("dungeon_runs", 0))
                # Ubah ke sectioned format agar _write_all_tables bisa membacanya
                player_data = self._flat_to_sectioned(player_data)
            else:
                raise ValueError("Format JSON tidak dikenali.")

            with self._db() as conn:
                save_id = self._upsert_slot(conn, "default")
                self._write_all_tables(conn, save_id, player_data)

            bak_path = json_path + ".bak"
            os.rename(json_path, bak_path)
            print(f"✅ Migrasi selesai. File lama → {bak_path}")

        except Exception as exc:
            print(f"⚠️  Migrasi gagal (save JSON tidak diubah): {exc}")

    @staticmethod
    def _flat_to_sectioned(flat: dict) -> dict:
        """Konversi flat legacy dict ke format sectioned Player.to_dict()."""
        return {
            "player": {
                "name":                 flat.get("name", "Adventurer"),
                "level":                flat.get("level", 1),
                "exp":                  flat.get("exp", 0),
                "hp":                   flat.get("hp", 100),
                "mana":                 flat.get("mana"),
                "base_attack":          flat.get("attack", flat.get("base_attack", 10)),
                "base_defense":         flat.get("defense", flat.get("base_defense", 5)),
                "gold":                 flat.get("gold", 50),
                "luck":                 flat.get("luck", 0),
                "reputation":           flat.get("reputation", 0),
                "skill_points":         flat.get("skill_points", 0),
                "critical_chance":      flat.get("critical_chance", 15),
                "critical_multiplier":  flat.get("critical_multiplier", 2.0),
                "accuracy":             flat.get("accuracy", 5),
                "dodge":                flat.get("dodge", 5),
            },
            "world": {
                "floor":                flat.get("floor", 1),
                "boss_progress":        flat.get("boss_progress", 0),
                "dungeon_runs":         flat.get("dungeon_runs", 0),
                "last_event":           flat.get("last_event"),
            },
            "loadout": {
                "weapon":               flat.get("weapon", "Fists"),
                "armor":                flat.get("armor"),
                "inventory":            flat.get("inventory", {"Fists": 1}),
                "learned_spells":       flat.get("learned_spells", []),
                "unlocked_skills":      flat.get("unlocked_skills", []),
            },
            "quests": {
                "story_progress":       flat.get("story_progress", 0),
                "quest":                flat.get("quest", []),
                "completed_quests":     flat.get("completed_quests", []),
            },
            "statistics": {
                "enemies_killed":       flat.get("enemies_killed", 0),
                "puzzles_solved":       flat.get("puzzles_solved", 0),
            },
            "flags": {
                "skip_next_battle":             flat.get("skip_next_battle", False),
                "skip_next_trap":               flat.get("skip_next_trap", False),
                "skip_next_boss_preparation":   flat.get("skip_next_boss_preparation", False),
            },
        }
