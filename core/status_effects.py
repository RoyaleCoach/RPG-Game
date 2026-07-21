"""
core/status_effects.py
-----------------------
Sistem Status Effect yang reusable dan mudah diperluas.

Setiap StatusEffect adalah objek mandiri dengan:
  - tick()      → dipanggil setiap awal giliran pemilik
  - on_apply()  → dipanggil saat pertama kali dikenakan
  - on_expire() → dipanggil saat durasi habis

Untuk menambah effect baru, cukup buat subclass dari StatusEffect.
Tidak perlu mengubah kode lain.

Integrasi:
  - Player dan Enemy sama-sama memiliki status_effects: list[StatusEffect]
  - Combat.fight() memanggil apply_status_effects() setiap awal giliran
"""

from __future__ import annotations

from typing import Any

# Tipe alias runtime — pakai Any agar tidak ada circular import.
# Semua entity (Player, Enemy) yang punya atribut .name, .hp, .max_hp
# bisa dipakai sebagai target status effect.
EntityType = Any


# ─────────────────────────────────────────────────────────────────────────────
# BASE CLASS
# ─────────────────────────────────────────────────────────────────────────────

class StatusEffect:
    """
    Base class untuk semua status effect.

    Subclass wajib mendefinisikan ``name`` dan mengoverride metode
    yang relevan. Defaults sudah aman (tidak melakukan apa-apa).
    """

    name: str = "Unknown"

    def __init__(self, duration: int) -> None:
        self.duration = duration       # Sisa giliran effect aktif
        self.is_expired = False        # Flag agar Combat tahu effect sudah habis

    # ── Hook methods ──────────────────────────────────────────────────────────

    def on_apply(self, target: EntityType) -> None:
        """Dipanggil sekali saat effect pertama kali dikenakan."""
        print(f"⚡ {target.name} terkena {self.name}! ({self.duration} giliran)")

    def tick(self, target: EntityType) -> None:
        """
        Dipanggil setiap awal giliran pemilik.
        Kurangi durasi, terapkan damage/buff, cek expiry.
        """
        if self.is_expired:
            return

        self._apply_effect(target)

        self.duration -= 1
        if self.duration <= 0:
            self.expire(target)

    def _apply_effect(self, target: EntityType) -> None:
        """Override di subclass — efek per giliran."""
        pass

    def on_expire(self, target: EntityType) -> None:
        """Dipanggil saat durasi habis."""
        print(f"✅ {self.name} pada {target.name} telah berakhir.")

    def expire(self, target: EntityType) -> None:
        """Tandai expired dan panggil on_expire."""
        self.is_expired = True
        self.on_expire(target)

    def __repr__(self) -> str:
        return f"{self.name}({self.duration}t)"


# ─────────────────────────────────────────────────────────────────────────────
# BUILT-IN EFFECTS
# ─────────────────────────────────────────────────────────────────────────────

class Burn(StatusEffect):
    """
    Terbakar — dikenakan oleh Fireball.

    Setiap giliran mengurangi HP sebesar PERCENT dari max_hp,
    atau FIXED_DAMAGE jika target tidak punya atribut max_hp.
    """

    name = "Burn"
    PERCENT = 0.05       # 5% dari max_hp
    FIXED_DAMAGE = 8     # fallback jika max_hp tidak ada

    def __init__(self, duration: int = 3) -> None:
        super().__init__(duration)

    def on_apply(self, target: EntityType) -> None:
        print(f"🔥 {target.name} terbakar! ({self.duration} giliran)")

    def _apply_effect(self, target: EntityType) -> None:
        max_hp = getattr(target, "max_hp", None)
        damage = int(max_hp * self.PERCENT) if max_hp else self.FIXED_DAMAGE
        damage = max(1, damage)
        target.hp = max(0, target.hp - damage)
        print(f"🔥 Burn mengenai {target.name} sebesar {damage} damage!")

    def on_expire(self, target: EntityType) -> None:
        print(f"💨 Api pada {target.name} padam.")


class Poison(StatusEffect):
    """
    Racun — damage lebih rendah dari Burn tapi durasinya lebih panjang.
    Damage tetap (flat), bukan persentase.
    """

    name = "Poison"

    def __init__(self, duration: int = 5, damage_per_tick: int = 5) -> None:
        super().__init__(duration)
        self.damage_per_tick = damage_per_tick

    def on_apply(self, target: EntityType) -> None:
        print(f"☠️ {target.name} diracun! ({self.duration} giliran)")

    def _apply_effect(self, target: EntityType) -> None:
        target.hp = max(0, target.hp - self.damage_per_tick)
        print(
            f"☠️ Poison mengenai {target.name} sebesar {self.damage_per_tick} damage!")

    def on_expire(self, target: EntityType) -> None:
        print(f"💚 Racun pada {target.name} menghilang.")


class Bleed(StatusEffect):
    """
    Perdarahan — damage meningkat setiap giliran (stacking).
    """

    name = "Bleed"

    def __init__(self, duration: int = 4, base_damage: int = 4) -> None:
        super().__init__(duration)
        self.base_damage = base_damage
        self._tick_count = 0

    def on_apply(self, target: EntityType) -> None:
        print(f"🩸 {target.name} mulai berdarah! ({self.duration} giliran)")

    def _apply_effect(self, target: EntityType) -> None:
        self._tick_count += 1
        damage = self.base_damage + self._tick_count
        target.hp = max(0, target.hp - damage)
        print(f"🩸 Bleed mengenai {target.name} sebesar {damage} damage!")

    def on_expire(self, target: EntityType) -> None:
        print(f"🩹 Perdarahan pada {target.name} berhenti.")


class Freeze(StatusEffect):
    """
    Beku — target di-skip (tidak bisa bertindak) selama durasi.
    Membutuhkan dukungan dari Combat untuk men-skip giliran.
    """

    name = "Freeze"

    def __init__(self, duration: int = 2) -> None:
        super().__init__(duration)

    def on_apply(self, target: EntityType) -> None:
        print(f"❄️ {target.name} membeku! ({self.duration} giliran)")

    def _apply_effect(self, target: EntityType) -> None:
        # Combat loop prints the skip message; this is a no-op to avoid duplicates.
        pass

    def on_expire(self, target: EntityType) -> None:
        print(f"🌡️ {target.name} bebas dari pembekuan.")

    @property
    def is_frozen(self) -> bool:
        return not self.is_expired and self.duration > 0


class Stun(StatusEffect):
    """
    Terpana — mirip Freeze tapi biasanya durasi 1 giliran.
    """

    name = "Stun"

    def __init__(self, duration: int = 1) -> None:
        super().__init__(duration)

    def on_apply(self, target: EntityType) -> None:
        print(f"⚡ {target.name} terpana! ({self.duration} giliran)")

    def _apply_effect(self, target: EntityType) -> None:
        # Combat loop prints the skip message; this is a no-op to avoid duplicates.
        pass

    def on_expire(self, target: EntityType) -> None:
        print(f"✅ {target.name} kembali sadar.")


class Regen(StatusEffect):
    """
    Regenerasi — memulihkan HP setiap giliran.
    """

    name = "Regen"

    def __init__(self, duration: int = 5, heal_per_tick: int = 10) -> None:
        super().__init__(duration)
        self.heal_per_tick = heal_per_tick

    def on_apply(self, target: EntityType) -> None:
        print(f"💚 {target.name} mendapatkan Regen! ({self.duration} giliran)")

    def _apply_effect(self, target: EntityType) -> None:
        old_hp = target.hp
        max_hp = getattr(target, "max_hp", target.hp + self.heal_per_tick)
        target.hp = min(max_hp, target.hp + self.heal_per_tick)
        actual = target.hp - old_hp
        if actual > 0:
            print(f"💚 Regen memulihkan {actual} HP untuk {target.name}!")

    def on_expire(self, target: EntityType) -> None:
        print(f"Regen pada {target.name} berakhir.")


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def apply_status_effects(entity: EntityType) -> bool:
    """
    Proses semua status effect aktif pada entity.

    Dipanggil di awal setiap giliran entity (player atau enemy).
    Returns True jika entity masih bisa bertindak (tidak ter-stun/freeze).
    """
    if not hasattr(entity, "status_effects"):
        return True

    # Cek apakah ter-stun/freeze SEBELUM tick (agar 1 turn penuh ter-skip)
    is_immobilized = any(
        isinstance(eff, (Stun, Freeze)) and not eff.is_expired
        for eff in entity.status_effects
    )

    # Jalankan semua effect
    for effect in list(entity.status_effects):
        if not effect.is_expired:
            effect.tick(entity)

    # Bersihkan effect yang sudah expired
    entity.status_effects = [
        eff for eff in entity.status_effects if not eff.is_expired
    ]

    return not is_immobilized


def apply_effect_to(target: EntityType, effect: StatusEffect) -> None:
    """
    Kenakan effect ke target.

    Jika effect dengan nama sama sudah ada, refresh durasi (tidak stack).
    """
    if not hasattr(target, "status_effects"):
        target.status_effects = []

    # Refresh jika sudah ada
    for existing in target.status_effects:
        if existing.name == effect.name:
            existing.duration = max(existing.duration, effect.duration)
            existing.is_expired = False
            print(f"🔄 {effect.name} pada {target.name} diperbarui.")
            return

    effect.on_apply(target)
    target.status_effects.append(effect)


# ─────────────────────────────────────────────────────────────────────────────
# SPELL → EFFECT MAPPING
# Tambahkan mapping di sini jika spell baru punya effect
# ─────────────────────────────────────────────────────────────────────────────

SPELL_EFFECTS: dict[str, type[StatusEffect]] = {
    "fireball":      Burn,
    "flame_burst":   Burn,
    "inferno":       Burn,
    "origin_flame":  Burn,
    "shadow_bolt":   Bleed,
    "icicle":        Freeze,
    "frost_lance":   Freeze,
    "absolute_zero": Freeze,
    "arcane_burst":  Stun,
    "requiem_of_light": Burn,
}


def get_spell_effect(spell_name: str) -> StatusEffect | None:
    """
    Kembalikan instance StatusEffect untuk spell_name, atau None.
    Tambahkan entry ke SPELL_EFFECTS untuk extend sistem ini.
    """
    effect_cls = SPELL_EFFECTS.get(spell_name)
    return effect_cls() if effect_cls else None
