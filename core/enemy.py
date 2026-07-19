"""
core/enemy.py
-------------
Mendefinisikan enemy biasa, boss, dan boss final.

Perubahan dari versi sebelumnya:
  [NEW] Enemy.critical_chance / critical_multiplier / accuracy / dodge
        → stat combat yang sama dengan Player agar sistem bisa reuse
  [NEW] Enemy.status_effects
        → list effect aktif; dikelola oleh status_effects.py
  [NEW] Enemy.choose_action() — AI sederhana berbasis probabilitas
  [NEW] BossPhase dataclass   — deskripsi satu phase boss
  [NEW] MultiphaseBoss        — boss dengan N phase; mudah dikonfigurasi
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any


# ─────────────────────────────────────────────────────────────────────────────
# AI PROFILE SYSTEM
# ─────────────────────────────────────────────────────────────────────────────

class AIProfile(Enum):
    """
    Different AI behavior profiles for enemies.
    Each profile has distinct action preferences and strategies.
    """
    BALANCED = "balanced"    # Default behavior (current logic)
    AGGRESSIVE = "aggressive"  # High attack weight, low defense
    DEFENSIVE = "defensive"    # Prioritizes defending, uses spells when low
    CASTER = "caster"          # Prefers spells, moderate defense
    SUPPORT = "support"        # Uses buffs/debuffs, lower damage focus


@dataclass
class AIWeights:
    """Container for AI action weights."""
    attack: float = 50.0
    defend: float = 10.0
    spell: float = 0.0
    dodge: float = 0.0


# Default weight configurations for each AI profile
AI_PROFILE_WEIGHTS: Dict[AIProfile, Dict[str, AIWeights]] = {
    AIProfile.BALANCED: {
        "default": AIWeights(attack=50.0, defend=10.0, spell=25.0, dodge=15.0),
        "low_hp": AIWeights(attack=35.0, defend=40.0, spell=20.0, dodge=5.0),
    },
    AIProfile.AGGRESSIVE: {
        "default": AIWeights(attack=70.0, defend=5.0, spell=20.0, dodge=5.0),
        "low_hp": AIWeights(attack=50.0, defend=25.0, spell=15.0, dodge=10.0),
    },
    AIProfile.DEFENSIVE: {
        "default": AIWeights(attack=30.0, defend=35.0, spell=20.0, dodge=15.0),
        "low_hp": AIWeights(attack=20.0, defend=50.0, spell=25.0, dodge=5.0),
    },
    AIProfile.CASTER: {
        "default": AIWeights(attack=25.0, defend=15.0, spell=50.0, dodge=10.0),
        "low_hp": AIWeights(attack=20.0, defend=20.0, spell=45.0, dodge=15.0),
    },
    AIProfile.SUPPORT: {
        "default": AIWeights(attack=20.0, defend=25.0, spell=45.0, dodge=10.0),
        "low_hp": AIWeights(attack=15.0, defend=35.0, spell=40.0, dodge=10.0)
    }
}




# ─────────────────────────────────────────────────────────────────────────────
# ENEMY BASE
# ─────────────────────────────────────────────────────────────────────────────

class Enemy:
    """
    Enemy dasar.

    Stat combat (critical, accuracy, dodge) ikut skema yang sama dengan
    Player sehingga fungsi helper di combat.py bisa dipakai untuk keduanya.
    """

    bosses: dict = {}

    @classmethod
    def load_bosses(cls, bosses_data: dict) -> None:
        cls.bosses = bosses_data

    def __init__(
        self,
        name: str,
        hp: int,
        attack: int,
        *,
        critical_chance: int = 10,
        critical_multiplier: float = 1.5,
        accuracy: int = 3,
        dodge: int = 5,
        spells: Optional[list[str]] = None,
        ai_profile: AIProfile = AIProfile.BALANCED,
    ) -> None:
        self.name = name
        self.hp = hp
        self.max_hp = hp          # dipakai Burn (persen dari max_hp)
        self.attack = attack

        # ── Combat stats (NEW) ────────────────────────────────────────────────
        self.critical_chance = critical_chance
        self.critical_multiplier = critical_multiplier
        self.accuracy = accuracy
        self.dodge = dodge

        # ── Status effects (NEW) ──────────────────────────────────────────────
        self.status_effects: list = []

        # ── AI state ──────────────────────────────────────────────────────────
        # Spell pool yang bisa digunakan enemy (nama spell dari spells.json)
        self.spells: list[str] = spells or []
        # Cooldown dodge: enemy tidak bisa dodge setiap giliran
        self._dodge_cooldown: int = 0
        # AI behavior profile
        self.ai_profile = ai_profile

    # ── Convenience ──────────────────────────────────────────────────────────

    @property
    def is_alive(self) -> bool:
        return self.hp > 0

    @property
    def hp_ratio(self) -> float:
        """Rasio HP saat ini terhadap max_hp (0.0 – 1.0)."""
        return self.hp / self.max_hp if self.max_hp > 0 else 0.0

    # ── AI: choose_action ─────────────────────────────────────────────────────

    def choose_action(self, mana: int = 0) -> str:
        """
        AI berbasis profil dengan bobot aksi yang bervariasi.

        Logika:
          - Menggunakan profil AI untuk menentukan bobot aksi
          - HP rendah → beralih ke profil "low_hp"
          - Spell aktif bila ada dan mana > 0
          - Dodge dengan cooldown

        Returns salah satu dari: "attack", "defend", "spell", "dodge"
        """
        # Turunkan cooldown dodge
        if self._dodge_cooldown > 0:
            self._dodge_cooldown -= 1

        # Ambil profil AI yang sesuai
        profile_weights = AI_PROFILE_WEIGHTS.get(
            self.ai_profile, AIProfile.BALANCED
        )
        weight_key = "low_hp" if self.hp_ratio < 0.30 else "default"
        weights_data = profile_weights[weight_key]

        weights: dict[str, float] = {
            "attack": weights_data.attack,
            "defend": weights_data.defend,
            "spell": weights_data.spell if self.spells and mana > 0 else 0.0,
            "dodge": 0.0,  # Set to 0, will be adjusted below if applicable
        }

        # Adjust spell weight based on mana availability
        if self.spells and mana > 0:
            weights["spell"] = weights_data.spell
        else:
            weights["spell"] = 0.0

        # Aktifkan dodge jika cooldown selesai dan HP tidak kritis
        if self._dodge_cooldown == 0 and self.hp_ratio > 0.20:
            weights["dodge"] = weights_data.dodge

        # Normalisasi agar total ≥ 0 untuk semua pilihan
        actions = list(weights.keys())
        probabilities = [max(0.0, weights[a]) for a in actions]
        total = sum(probabilities)
        if total == 0:
            return "attack"

        chosen = random.choices(actions, weights=probabilities, k=1)[0]

        if chosen == "dodge":
            self._dodge_cooldown = 3   # tidak bisa dodge lagi selama 3 turn

        return chosen

    # ── Factory: random enemies ───────────────────────────────────────────────

    @staticmethod
    def random_enemy(floor: int) -> "Enemy":
        """Kembalikan enemy acak sesuai floor."""
        if floor <= 5:
            pool = [
                Enemy("Goblin",     15,  8, critical_chance=8, dodge=3),
                Enemy("Skeleton",   24, 10, critical_chance=10, accuracy=4),
                Enemy("Dark Wolf",  28, 12, dodge=12),
                Enemy("Bomber",     30, 20, critical_chance=20,
                      critical_multiplier=2.0),
            ]
        elif floor <= 15:
            pool = [
                Enemy("Venom Spider", 38, 14, dodge=8,
                      spells=["poison_bite"]),
                Enemy("Ghoul",        40, 15, critical_chance=15),
                Enemy("Bone Archer",  42, 16, accuracy=8),
                Enemy("Dark Shaman",  50, 18, critical_chance=12,
                      spells=["shadow_bolt"]),
            ]
        elif floor <= 25:
            pool = [
                Enemy("Stone Golem",   70, 18, dodge=3, accuracy=6),
                Enemy("Ogre",          82, 20, critical_chance=12,
                      critical_multiplier=2.0),
                Enemy("Necromancer",    86, 22, spells=[
                      "shadow_bolt", "icicle"]),
                Enemy("Giant",         90, 15, accuracy=10),
            ]
        else:
            pool = [
                Enemy("Doom Knight",   100, 25, critical_chance=18,
                      critical_multiplier=2.5, dodge=8),
                Enemy("Abyss Walker",  180, 28, dodge=15,
                      spells=["shadow_bolt", "arcane_burst"]),
            ]
        return random.choice(pool)

    # ── Factory: random boss ──────────────────────────────────────────────────

    @classmethod
    def random_boss(cls, player_level: int) -> "Boss | MultiphaseBoss":
        """Kembalikan Boss (atau MultiphaseBoss) sesuai level pemain."""
        if not cls.bosses:
            raise ValueError("Boss data belum dimuat.")

        selected = None
        for level_req, boss_data in sorted(
            cls.bosses.items(), key=lambda x: int(x[0])
        ):
            if player_level >= int(level_req):
                selected = boss_data

        if selected is None:
            selected = next(iter(cls.bosses.values()))

        # Level tinggi → MultiphaseBoss
        if player_level >= 10 and selected.get("phases"):
            return MultiphaseBoss.from_data(selected)

        return Boss(
            selected["name"],
            selected["hp"],
            selected["attack"],
            selected["exp_reward"],
            selected["gold_reward"],
        )


# ─────────────────────────────────────────────────────────────────────────────
# BOSS
# ─────────────────────────────────────────────────────────────────────────────

class Boss(Enemy):
    """Boss standar (single-phase)."""

    def __init__(
        self,
        name: str,
        hp: int,
        attack: int,
        exp_reward: int,
        gold_reward: int,
        *,
        critical_chance: int = 15,
        critical_multiplier: float = 2.0,
        accuracy: int = 5,
        dodge: int = 8,
        spells: Optional[list[str]] = None,
    ) -> None:
        super().__init__(
            name, hp, attack,
            critical_chance=critical_chance,
            critical_multiplier=critical_multiplier,
            accuracy=accuracy,
            dodge=dodge,
            spells=spells or [],
        )
        self.exp_reward = exp_reward
        self.gold_reward = gold_reward


# ─────────────────────────────────────────────────────────────────────────────
# BOSS PHASE SYSTEM (NEW)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class BossPhase:
    """
    Deskripsi satu phase boss.

    Mudah ditambah: cukup tambahkan BossPhase baru ke list phases.
    """
    phase_number: int
    hp: int
    attack: int
    critical_chance: int = 15
    critical_multiplier: float = 2.0
    accuracy: int = 5
    dodge: int = 8
    spells: list[str] = field(default_factory=list)
    transition_message: str = ""    # pesan saat memasuki phase ini


class MultiphaseBoss(Boss):
    """
    Boss dengan beberapa phase.

    Cara kerja:
      1. Boss dimulai dari phase[0].
      2. Saat HP ≤ 0, jika masih ada phase berikutnya:
           - HP diisi ulang ke nilai phase berikutnya
           - Stats di-update (attack, crit, dll.)
           - Pesan transisi ditampilkan
           - Pertarungan BERLANJUT
      3. Saat phase terakhir habis, boss mati seperti biasa.

    Untuk menambah phase, cukup tambahkan BossPhase ke list phases.
    Tidak ada perubahan kode Combat.
    """

    def __init__(
        self,
        name: str,
        phases: list[BossPhase],
        exp_reward: int,
        gold_reward: int,
    ) -> None:
        if not phases:
            raise ValueError("MultiphaseBoss harus punya minimal 1 phase.")

        self.phases = phases
        self._phase_index = 0

        first = phases[0]
        super().__init__(
            name,
            first.hp,
            first.attack,
            exp_reward,
            gold_reward,
            critical_chance=first.critical_chance,
            critical_multiplier=first.critical_multiplier,
            accuracy=first.accuracy,
            dodge=first.dodge,
            spells=list(first.spells),
        )
        self.max_hp = first.hp

    # ── Phase properties ──────────────────────────────────────────────────────

    @property
    def current_phase(self) -> BossPhase:
        return self.phases[self._phase_index]

    @property
    def phase_number(self) -> int:
        return self._phase_index + 1

    @property
    def total_phases(self) -> int:
        return len(self.phases)

    @property
    def has_next_phase(self) -> bool:
        return self._phase_index + 1 < len(self.phases)

    # ── Transition ────────────────────────────────────────────────────────────

    def try_advance_phase(self) -> bool:
        """
        Dicek oleh Combat saat hp ≤ 0.

        Returns True jika berhasil masuk phase berikutnya (hp diisi ulang).
        Returns False jika sudah phase terakhir (boss mati).
        """
        if not self.has_next_phase:
            return False

        self._phase_index += 1
        next_phase = self.phases[self._phase_index]

        # Update stats
        self.hp = next_phase.hp
        self.max_hp = next_phase.hp
        self.attack = next_phase.attack
        self.critical_chance = next_phase.critical_chance
        self.critical_multiplier = next_phase.critical_multiplier
        self.accuracy = next_phase.accuracy
        self.dodge = next_phase.dodge
        self.spells = list(next_phase.spells)

        # Bersihkan status effects (boss "transform" → kebal effect lama)
        self.status_effects = []

        # Tampilkan pesan transisi
        msg = next_phase.transition_message or (
            f"⚠️  {self.name} bertransformasi!\n"
            f"    ╔══════════════════════════╗\n"
            f"    ║   PHASE {self.phase_number} DIMULAI!        ║\n"
            f"    ╚══════════════════════════╝"
        )
        print(f"\n{msg}\n")
        print(
            f"  {self.name} HP: {self.hp} | ATK: {self.attack} | "
            f"CRIT: {self.critical_chance}%"
        )

        return True

    # ── Factory ───────────────────────────────────────────────────────────────

    @classmethod
    def from_data(cls, data: dict) -> "MultiphaseBoss":
        """
        Buat MultiphaseBoss dari dict (misalnya dari bosses.json dengan key 'phases').

        Contoh format bosses.json:
          {
            "name": "Ancient Dragon",
            "exp_reward": 350,
            "gold_reward": 400,
            "phases": [
              {"hp": 400, "attack": 45, "transition_message": "The dragon roars!"},
              {"hp": 600, "attack": 65, "critical_chance": 25, "spells": ["fireball"]}
            ]
          }
        """
        phases_data = data.get("phases", [])
        phases = [
            BossPhase(
                phase_number=i + 1,
                hp=p.get("hp", 200),
                attack=p.get("attack", 30),
                critical_chance=p.get("critical_chance", 15),
                critical_multiplier=p.get("critical_multiplier", 2.0),
                accuracy=p.get("accuracy", 5),
                dodge=p.get("dodge", 8),
                spells=p.get("spells", []),
                transition_message=p.get("transition_message", ""),
            )
            for i, p in enumerate(phases_data)
        ]

        # Fallback: jika tidak ada phases key, buat 2-phase dari stat dasar
        if not phases:
            phases = [
                BossPhase(
                    phase_number=1,
                    hp=data.get("hp", 200),
                    attack=data.get("attack", 30),
                ),
                BossPhase(
                    phase_number=2,
                    hp=int(data.get("hp", 200) * 0.6),
                    attack=int(data.get("attack", 30) * 1.4),
                    critical_chance=25,
                    transition_message=(
                        f"💀 {data.get('name', 'Boss')} bangkit kembali!\n"
                        f"   Kekuatan sejati terbuka — PHASE 2!"
                    ),
                ),
            ]

        return cls(
            name=data.get("name", "Unknown Boss"),
            phases=phases,
            exp_reward=data.get("exp_reward", 100),
            gold_reward=data.get("gold_reward", 100),
        )


# ─────────────────────────────────────────────────────────────────────────────
# SPECIAL BOSS
# ─────────────────────────────────────────────────────────────────────────────

class TheFirstHollow(MultiphaseBoss):
    """
    Boss final dengan 3 phase.
    Contoh penggunaan MultiphaseBoss yang dikonfigurasi via kode.
    """

    def __init__(self) -> None:
        phases = [
            BossPhase(
                phase_number=1,
                hp=500,
                attack=50,
                critical_chance=15,
                transition_message=(
                    "💀 The First Hollow tersenyum...\n"
                    "   「Kau cukup kuat untuk melihat wujud asliku.」\n"
                    "   ══════════ PHASE 2 ══════════"
                ),
            ),
            BossPhase(
                phase_number=2,
                hp=400,
                attack=70,
                critical_chance=25,
                critical_multiplier=2.5,
                spells=["shadow_bolt", "arcane_burst"],
                transition_message=(
                    "💀 The First Hollow MENGGELEGAR...\n"
                    "   「Ini... bukan batas kekuatanku!」\n"
                    "   ══════════ PHASE 3: TRUE FORM ══════════"
                ),
            ),
            BossPhase(
                phase_number=3,
                hp=300,
                attack=90,
                critical_chance=35,
                critical_multiplier=3.0,
                dodge=20,
                spells=["origin_flame", "requiem_of_light"],
            ),
        ]
        super().__init__(
            name="The First Hollow",
            phases=phases,
            exp_reward=1000,
            gold_reward=500,
        )
