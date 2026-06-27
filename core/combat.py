"""
core/combat.py
--------------
Sistem pertarungan turn-based.

Perubahan dari versi sebelumnya:
  [NEW] roll_damage()     — menghitung damage dengan accuracy & critical hit
  [NEW] roll_dodge()      — cek peluang dodge
  [NEW] Giliran player    — pakai roll_damage / roll_dodge
  [NEW] Giliran enemy     — AI choose_action(), roll_damage, roll_dodge player
  [NEW] Status effects    — tick awal setiap giliran (Burn, Poison, dll.)
  [NEW] MultiphaseBoss    — cek try_advance_phase() saat HP boss ≤ 0
  [NEW] Enemy spell cast  — enemy bisa cast spell dari spell pool-nya
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from core.enemy import Boss, MultiphaseBoss
from core.status_effects import (
    apply_status_effects,
    apply_effect_to,
    get_spell_effect,
)

if TYPE_CHECKING:
    from core.player import Player
    from core.enemy import Enemy
    from core.skill import Skill


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def roll_damage(attacker, base_max: int) -> tuple[int, bool]:
    """
    Hitung damage satu serangan.

    Menerapkan:
      1. Accuracy   → menaikkan minimum damage
      2. Critical   → jika terjadi, kalikan damage

    Args:
        attacker : entity yang menyerang (Player atau Enemy)
        base_max : batas atas damage sebelum crit (biasanya attacker.attack)

    Returns:
        (damage, is_critical)
    """
    accuracy = getattr(attacker, "accuracy", 0)
    # min_damage naik seiring accuracy, tidak melebihi base_max
    min_damage = min(max(1, accuracy), base_max)
    damage = random.randint(min_damage, max(min_damage, base_max))

    # Critical hit check
    crit_chance = getattr(attacker, "critical_chance", 0)
    is_crit = random.randint(1, 100) <= crit_chance
    if is_crit:
        multiplier = getattr(attacker, "critical_multiplier", 2.0)
        damage = int(damage * multiplier)

    return damage, is_crit


def roll_dodge(target) -> bool:
    """
    Kembalikan True jika target berhasil dodge serangan.

    dodge = 20 → 20% peluang dodge.
    """
    dodge_chance = getattr(target, "dodge", 0)
    return random.randint(1, 100) <= dodge_chance


# ─────────────────────────────────────────────────────────────────────────────
# COMBAT CLASS
# ─────────────────────────────────────────────────────────────────────────────

class Combat:

    def __init__(self, quest_system, items: dict, skill_system: "Skill | None" = None):
        self.quest_system = quest_system
        self.potions = items.get("potions", {})
        self.skill_system = skill_system

    # ─────────────────────────────────────────────────────────────────────────
    # MAIN BATTLE LOOP
    # ─────────────────────────────────────────────────────────────────────────

    def fight(self, player: "Player", enemy: "Enemy") -> bool:
        """
        Jalankan pertarungan hingga salah satu pihak mati.

        Returns True jika player menang, False jika kalah.
        """
        # Defense saat ini (bisa berubah oleh defend/spell buff)
        battle_defense = player.defense

        while player.hp > 0 and enemy.hp > 0:

            # ── Tampilkan status ──────────────────────────────────────────────
            phase_info = ""
            if isinstance(enemy, MultiphaseBoss):
                phase_info = f" [Phase {enemy.phase_number}/{enemy.total_phases}]"

            print(
                f"\n{player.name} HP: {player.hp}/{player.max_hp} "
                f"| Mana: {player.mana}/{player.max_mana} "
                f"| DEF: {battle_defense} | "
                f"{enemy.name}{phase_info} HP: {enemy.hp}/{enemy.max_hp}"
            )

            # ── Tampilkan status effects aktif ────────────────────────────────
            self._display_active_effects(player, enemy)

            # ── Tick status effects PLAYER (awal giliran player) ──────────────
            player_can_act = apply_status_effects(player)
            if not player.is_alive:
                break

            # ── Input player ──────────────────────────────────────────────────
            if not player_can_act:
                # Ter-stun/freeze — skip giliran
                print(f"⚡ {player.name} tidak bisa bergerak!")
            else:
                action = (
                    input("Choose action (attack / defend / heal / spell): ")
                    .lower()
                    .strip()
                )
                battle_defense = self._player_turn(
                    player, enemy, action, battle_defense
                )

            if not enemy.is_alive:
                # Cek multiphase sebelum menganggap boss mati
                if isinstance(enemy, MultiphaseBoss):
                    if enemy.try_advance_phase():
                        # Boss masuk phase berikutnya — lanjutkan
                        continue
                break

            # ── Tick status effects ENEMY (awal giliran enemy) ────────────────
            enemy_can_act = apply_status_effects(enemy)
            if not enemy.is_alive:
                if isinstance(enemy, MultiphaseBoss) and enemy.try_advance_phase():
                    continue
                break

            # ── Giliran enemy ─────────────────────────────────────────────────
            if enemy_can_act:
                battle_defense = self._enemy_turn(
                    player, enemy, action if player_can_act else "none",
                    battle_defense
                )
            else:
                print(f"⚡ {enemy.name} tidak bisa bergerak!")

        # ── Hasil pertarungan ─────────────────────────────────────────────────
        # Bersihkan status effects setelah battle
        player.status_effects = []
        enemy.status_effects = []

        if not player.is_alive:
            print("\n💀 Defeat.")
            return False

        self._award_victory(player, enemy)
        self.quest_system.check(player)
        return True

    # ─────────────────────────────────────────────────────────────────────────
    # PLAYER TURN
    # ─────────────────────────────────────────────────────────────────────────

    def _player_turn(
        self,
        player: "Player",
        enemy: "Enemy",
        action: str,
        battle_defense: int,
    ) -> int:
        """Proses aksi player. Returns battle_defense (bisa berubah)."""

        if action in ("attack", "a"):
            self._player_attack(player, enemy)

        elif action in ("defend", "d"):
            print("🛡️ Kau bersiap menangkis.")

        elif action in ("heal", "h"):
            self._player_heal(player)

        elif action == "spell":
            battle_defense = self._player_spell(
                player, enemy, battle_defense
            )

        else:
            print("❌ Aksi tidak valid.")

        return battle_defense

    def _player_attack(self, player: "Player", enemy: "Enemy") -> None:
        """Serangan fisik player ke enemy (dengan accuracy & crit)."""
        damage, is_crit = roll_damage(player, player.attack)

        if is_crit:
            print(f"💥 Critical Hit! ", end="")

        enemy.hp = max(0, enemy.hp - damage)
        print(f"Kau menyerang dan mengenai {damage} damage pada {enemy.name}!")

    def _player_heal(self, player: "Player") -> None:
        """Menu heal dengan potion."""
        print("\n=== POTIONS ===")
        available = [i for i in player.inventory if i in self.potions]

        if not available:
            print("Tidak ada potion tersedia.")
            return

        for item in available:
            print(f"- {item} (Heal: {self.potions[item]['effect']} HP)")

        potion_name = input("\nMasukkan nama potion: ").strip()
        player.equip_potion(potion_name)

    def _player_spell(
        self,
        player: "Player",
        enemy: "Enemy",
        battle_defense: int,
    ) -> int:
        """Cast spell player. Returns (mungkin updated) battle_defense."""
        if self.skill_system is None:
            print("Sihir tidak tersedia.")
            return battle_defense

        available_spells = self.skill_system.get_available_spells(player)
        if not available_spells:
            print("Kau belum mengetahui mantra apapun.")
            return battle_defense

        print("\n=== SPELLS ===")
        for name, data in available_spells.items():
            print(
                f"- {name} "
                f"(Cost: {data.get('cost', 0)} Mana, "
                f"Type: {data.get('type')})"
            )

        spell_name = input("\nMasukkan nama spell: ").strip()
        spell = self.skill_system.get_spell(spell_name)

        if spell is None or spell_name not in player.learned_spells:
            print("⚠️ Spell tidak valid.")
            return battle_defense

        cost = spell.get("cost", 0)
        if player.mana < cost:
            print("⚠️ Mana tidak cukup.")
            return battle_defense

        player.mana -= cost
        description = spell.get(
            "description",
            f"{player.name} menggunakan {spell_name}!"
        )
        print(description.replace("[caster]", player.name))

        # Terapkan efek spell (damage/heal/buff)
        battle_defense = self.apply_spell_effect(
            player, enemy, spell, battle_defense
        )

        # Terapkan status effect jika spell punya (mis. Fireball → Burn)
        status_effect = get_spell_effect(spell_name)
        if status_effect:
            apply_effect_to(enemy, status_effect)

        return battle_defense

    # ─────────────────────────────────────────────────────────────────────────
    # ENEMY TURN (dengan AI)
    # ─────────────────────────────────────────────────────────────────────────

    def _enemy_turn(
        self,
        player: "Player",
        enemy: "Enemy",
        player_last_action: str,
        battle_defense: int,
    ) -> int:
        """
        Giliran enemy dengan AI sederhana.
        Returns (mungkin updated) battle_defense.
        """
        # Enemy punya mana? (opsional — Enemy sederhana tidak punya mana)
        enemy_mana = getattr(enemy, "mana", 10 if enemy.spells else 0)
        action = enemy.choose_action(mana=enemy_mana)

        if action == "defend":
            print(f"\n🛡️ {enemy.name} bersiap menangkis.")
            # Enemy defend: damage ke player dikurangi pada serangan berikutnya
            # (disimulasikan dengan tidak menyerang giliran ini)
            return battle_defense

        if action == "dodge":
            # Enemy siap dodge — tandai agar bisa dipakai saat player hit
            # (pada implementasi ini dodge enemy dicek di _resolve_enemy_attack)
            print(f"\n💨 {enemy.name} melompat menghindar dan tidak menyerang!")
            return battle_defense

        if action == "spell" and enemy.spells:
            return self._enemy_cast_spell(player, enemy, battle_defense)

        # Default: attack
        return self._enemy_attack(player, enemy, player_last_action, battle_defense)

    def _enemy_attack(
        self,
        player: "Player",
        enemy: "Enemy",
        player_last_action: str,
        battle_defense: int,
    ) -> int:
        """Serangan fisik enemy ke player."""
        damage, is_crit = roll_damage(enemy, enemy.attack)

        # Defend player → kurangi damage 50%
        if player_last_action in ("defend", "d"):
            damage //= 2

        # Cek dodge player
        if roll_dodge(player):
            print(
                f"\n🌀 Dodge! {player.name} menghindari serangan {enemy.name}!")
            return battle_defense

        if is_crit:
            print(f"\n💥 Critical Hit dari {enemy.name}! ", end="")

        final_damage = player.damage(damage, battle_defense)

        # Setiap serangan sedikit mengikis defense battle (armor aus)
        battle_defense = max(
            0,
            battle_defense - max(1, damage // 4)
        )

        print(f"{enemy.name} menyerang dan mengenai {final_damage} damage.")
        return battle_defense

    def _enemy_cast_spell(
        self,
        player: "Player",
        enemy: "Enemy",
        battle_defense: int,
    ) -> int:
        """Enemy memilih dan menggunakan spell secara acak."""
        spell_name = random.choice(enemy.spells)

        if self.skill_system:
            spell = self.skill_system.get_spell(spell_name)
        else:
            spell = None

        if spell is None:
            # Spell tidak ada di database → fallback ke attack
            return self._enemy_attack(player, enemy, "", battle_defense)

        description = spell.get(
            "description",
            f"{enemy.name} menggunakan {spell_name}!"
        )
        print(f"\n{description.replace('[caster]', enemy.name)}")

        # Damage/heal/buff ke PLAYER (target dibalik)
        # Enemy spell selalu menyerang player; heal/buff pada diri sendiri
        spell_type = spell.get("type", "st/damage")
        if "damage" in spell_type:
            damage, is_crit = roll_damage(
                enemy, enemy.attack + spell.get("level", 1) * 3)
            if is_crit:
                print(f"💥 Critical! ", end="")
            if roll_dodge(player):
                print(f"🌀 {player.name} menghindari {spell_name}!")
            else:
                player.damage(damage, battle_defense)
                print(f"{enemy.name} mengenai {damage} damage pada {player.name}!")

                # Status effect dari spell enemy
                status_effect = get_spell_effect(spell_name)
                if status_effect:
                    apply_effect_to(player, status_effect)

        elif "heal" in spell_type:
            heal = spell.get("cost", 5) + 10
            enemy.hp = min(enemy.max_hp, enemy.hp + heal)
            print(f"{enemy.name} memulihkan {heal} HP!")

        elif "buff" in spell_type:
            boost = spell.get("level", 1) * 2
            enemy.attack += boost
            print(f"{enemy.name} menguat! ATK +{boost}!")

        return battle_defense

    # ─────────────────────────────────────────────────────────────────────────
    # SPELL EFFECTS (player spells)
    # ─────────────────────────────────────────────────────────────────────────

    def apply_spell_effect(
        self,
        player: "Player",
        enemy: "Enemy",
        spell: dict,
        battle_defense: int,
    ) -> int:
        """
        Terapkan efek langsung spell (damage/heal/buff).
        Status effect ditangani terpisah oleh status_effects.py.
        """
        spell_type = spell.get("type", "st/damage")

        if "damage" in spell_type:
            damage, is_crit = roll_damage(
                player,
                player.attack + spell.get("level", 1) * 2
            )
            if is_crit:
                print(f"💥 Critical! ", end="")

            # Cek dodge enemy
            if roll_dodge(enemy):
                print(f"🌀 {enemy.name} menghindari spell!")
            else:
                enemy.hp = max(0, enemy.hp - damage)
                print(f"{enemy.name} terkena {damage} damage!")

        elif "heal" in spell_type:
            heal_amount = random.randint(
                spell.get("cost", 5),
                spell.get("cost", 5) + player.level * 2
            )
            player.hp += heal_amount
            print(f"Kau memulihkan {heal_amount} HP!")

        elif "buff" in spell_type:
            boost = spell.get("level", 1) * 2
            battle_defense += boost
            print(f"Defense meningkat sebesar {boost} untuk giliran ini!")

        else:
            print("Spell tidak memberikan efek.")

        return battle_defense

    # ─────────────────────────────────────────────────────────────────────────
    # VICTORY
    # ─────────────────────────────────────────────────────────────────────────

    def _award_victory(self, player: "Player", enemy: "Enemy") -> None:
        """Berikan reward setelah menang."""
        if isinstance(enemy, Boss):
            player.gold += enemy.gold_reward
            player.gain_exp(enemy.exp_reward)
            print("\n👑 Boss Dikalahkan!")
            print(f"+{enemy.gold_reward} Gold")
            print(f"+{enemy.exp_reward} EXP")
        else:
            reward = random.randint(10, 30)
            player.gold += reward
            player.enemies_killed += 1

            if player.enemies_killed % 3 == 0:
                player.floor += 1
                print(f"📈 Mencapai Floor {player.floor}!")

            player.gain_exp(10)
            print("\n🏆 Kemenangan!")
            print(f"+{reward} Gold")

    # ─────────────────────────────────────────────────────────────────────────
    # UTILITY
    # ─────────────────────────────────────────────────────────────────────────

    def _display_active_effects(self, player: "Player", enemy: "Enemy") -> None:
        """Tampilkan status effects aktif untuk kedua pihak (jika ada)."""
        if player.status_effects:
            fx = ", ".join(repr(e) for e in player.status_effects)
            print(f"  [STATUS] {player.name}: {fx}")
        if enemy.status_effects:
            fx = ", ".join(repr(e) for e in enemy.status_effects)
            print(f"  [STATUS] {enemy.name}: {fx}")
