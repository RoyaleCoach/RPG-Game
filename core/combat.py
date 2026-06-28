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
  [NEW] Defense as shield — DEF berfungsi sebagai second health bar; damage
                            enemy dikurangi ke DEF dulu, sisanya ke HP.
                            Aksi defend player dihapus.
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
        self._loot_engine = None
        self._encyclopedia = None

    def set_loot_engine(self, loot_engine) -> None:
        """Attach a LootEngine for combat rewards."""
        self._loot_engine = loot_engine

    def set_encyclopedia(self, encyclopedia) -> None:
        """Attach an ItemEncyclopedia for auto-discovery."""
        self._encyclopedia = encyclopedia

    # ─────────────────────────────────────────────────────────────────────────
    # MAIN BATTLE LOOP
    # ─────────────────────────────────────────────────────────────────────────

    def fight(self, player: "Player", enemy: "Enemy") -> bool:
        """
        Jalankan pertarungan hingga salah satu pihak mati.

        Returns True jika player menang, False jika kalah.
        """
        # Defense berfungsi sebagai second health bar — menyerap damage enemy
        # sebelum HP berkurang. Diisi ulang dari player.defense setiap battle.
        current_defense = player.defense

        while player.hp > 0 and enemy.hp > 0:

            # ── Tampilkan status ──────────────────────────────────────────────
            phase_info = ""
            if isinstance(enemy, MultiphaseBoss):
                phase_info = f" [Phase {enemy.phase_number}/{enemy.total_phases}]"

            shield_bar = f"🛡️ {current_defense}/{player.defense}" if current_defense > 0 else "🛡️ HABIS"
            print(
                f"\n{player.name} HP: {player.hp}/{player.max_hp} "
                f"| {shield_bar} "
                f"| Mana: {player.mana}/{player.max_mana} | "
                f"{enemy.name}{phase_info} HP: {enemy.hp}/{enemy.max_hp}"
            )

            # ── Tampilkan status effects aktif ────────────────────────────────
            self._display_active_effects(player, enemy)

            # ── Tick status effects PLAYER (awal giliran player) ──────────────
            player_can_act = apply_status_effects(player)
            if not player.is_alive:
                break

            # ── Input player ──────────────────────────────────────────────────
            player_is_dodging = False
            if not player_can_act:
                # Ter-stun/freeze — skip giliran
                print(f"⚡ {player.name} tidak bisa bergerak!")
            else:
                action = (
                    input("Choose action (attack / heal / spell / dodge): ")
                    .lower()
                    .strip()
                )
                current_defense, player_is_dodging = self._player_turn(
                    player, enemy, action, current_defense
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
                current_defense = self._enemy_turn(
                    player, enemy, action if player_can_act else "none",
                    current_defense, player_is_dodging
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
        current_defense: int,
    ) -> tuple[int, bool]:
        """Proses aksi player. Returns (current_defense, player_is_dodging)."""
        player_is_dodging = False

        if action in ("attack", "a"):
            self._player_attack(player, enemy)

        elif action in ("heal", "h"):
            self._player_heal(player)

        elif action == "spell":
            current_defense = self._player_spell(
                player, enemy, current_defense
            )

        elif action in ("dodge", "dg"):
            player_is_dodging = True
            print(f"💨 {player.name} bersiap menghindar dari serangan berikutnya!")

        else:
            print("❌ Aksi tidak valid.")

        return current_defense, player_is_dodging

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
        current_defense: int,
    ) -> int:
        """Cast spell player. Returns (mungkin updated) current_defense."""
        if self.skill_system is None:
            print("Sihir tidak tersedia.")
            return current_defense

        available_spells = self.skill_system.get_available_spells(player)
        if not available_spells:
            print("Kau belum mengetahui mantra apapun.")
            return current_defense

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
            return current_defense

        cost = spell.get("cost", 0)
        if player.mana < cost:
            print("⚠️ Mana tidak cukup.")
            return current_defense

        player.mana -= cost
        description = spell.get(
            "description",
            f"{player.name} menggunakan {spell_name}!"
        )
        print(description.replace("[caster]", player.name))

        # Terapkan efek spell (damage/heal/buff)
        current_defense = self.apply_spell_effect(
            player, enemy, spell, current_defense
        )

        # Terapkan status effect jika spell punya (mis. Fireball → Burn)
        status_effect = get_spell_effect(spell_name)
        if status_effect:
            apply_effect_to(enemy, status_effect)

        return current_defense

    # ─────────────────────────────────────────────────────────────────────────
    # ENEMY TURN (dengan AI)
    # ─────────────────────────────────────────────────────────────────────────

    def _enemy_turn(
        self,
        player: "Player",
        enemy: "Enemy",
        player_last_action: str,
        current_defense: int,
        player_is_dodging: bool = False,
    ) -> int:
        """
        Giliran enemy dengan AI sederhana.
        Returns (mungkin updated) current_defense.
        """
        # Enemy punya mana? (opsional — Enemy sederhana tidak punya mana)
        enemy_mana = getattr(enemy, "mana", 10 if enemy.spells else 0)
        action = enemy.choose_action(mana=enemy_mana)

        if action == "defend":
            print(f"\n🛡️ {enemy.name} bersiap menangkis.")
            return current_defense

        if action == "dodge":
            print(f"\n💨 {enemy.name} melompat menghindar dan tidak menyerang!")
            return current_defense

        if action == "spell" and enemy.spells:
            return self._enemy_cast_spell(player, enemy, current_defense, player_is_dodging)

        # Default: attack
        return self._enemy_attack(player, enemy, current_defense, player_is_dodging)

    def _enemy_attack(
        self,
        player: "Player",
        enemy: "Enemy",
        current_defense: int,
        player_is_dodging: bool = False,
    ) -> int:
        """
        Serangan fisik enemy ke player.
        Damage diserap oleh current_defense (second health bar) terlebih dahulu;
        sisanya baru mengurangi HP player.
        """
        damage, is_crit = roll_damage(enemy, enemy.attack)

        # Cek dodge player
        if player_is_dodging:
            dodge_bonus = getattr(player, "dodge", 0) + \
                30  # +30% bonus saat aktif dodge
            dodged = random.randint(1, 100) <= min(dodge_bonus, 95)  # cap 95%
        else:
            dodged = roll_dodge(player)

        if dodged:
            dodge_msg = (
                f"\n🌀 Dodge! {player.name} dengan sigap mengelak dari serangan {enemy.name}!"
                if player_is_dodging
                else f"\n🌀 Dodge! {player.name} menghindari serangan {enemy.name}!"
            )
            print(dodge_msg)
            return current_defense

        if is_crit:
            print(f"\n💥 Critical Hit dari {enemy.name}! ", end="")

        # Serap damage ke defense terlebih dahulu
        if current_defense >= damage:
            current_defense -= damage
            print(
                f"{enemy.name} menyerang {damage} damage → "
                f"diserap oleh armor. (DEF tersisa: {current_defense})"
            )
        elif current_defense > 0:
            leftover = damage - current_defense
            print(
                f"{enemy.name} menyerang {damage} damage → "
                f"{current_defense} diserap armor, {leftover} menembus ke HP!"
            )
            current_defense = 0
            player.hp = max(0, player.hp - leftover)
            if not player.is_alive:
                print("💀 Game Over!")
        else:
            # Defense sudah habis — damage langsung ke HP
            player.hp = max(0, player.hp - damage)
            print(
                f"{enemy.name} menyerang dan mengenai {damage} damage langsung ke HP!")
            if not player.is_alive:
                print("💀 Game Over!")

        return current_defense

    def _enemy_cast_spell(
        self,
        player: "Player",
        enemy: "Enemy",
        current_defense: int,
        player_is_dodging: bool = False,
    ) -> int:
        """Enemy memilih dan menggunakan spell secara acak."""
        spell_name = random.choice(enemy.spells)

        if self.skill_system:
            spell = self.skill_system.get_spell(spell_name)
        else:
            spell = None

        if spell is None:
            # Spell tidak ada di database → fallback ke attack
            return self._enemy_attack(player, enemy, current_defense, player_is_dodging)

        description = spell.get(
            "description",
            f"{enemy.name} menggunakan {spell_name}!"
        )
        print(f"\n{description.replace('[caster]', enemy.name)}")

        spell_type = spell.get("type", "st/damage")
        if "damage" in spell_type:
            damage, is_crit = roll_damage(
                enemy, enemy.attack + spell.get("level", 1) * 3)
            if is_crit:
                print(f"💥 Critical! ", end="")

            # Cek dodge player (dengan bonus jika sedang aktif dodge)
            if player_is_dodging:
                dodge_bonus = getattr(player, "dodge", 0) + 30
                dodged = random.randint(1, 100) <= min(dodge_bonus, 95)
            else:
                dodged = roll_dodge(player)

            if dodged:
                dodge_msg = (
                    f"🌀 {player.name} dengan sigap mengelak dari {spell_name}!"
                    if player_is_dodging
                    else f"🌀 {player.name} menghindari {spell_name}!"
                )
                print(dodge_msg)
            else:
                # Spell damage juga diserap defense terlebih dahulu
                if current_defense >= damage:
                    current_defense -= damage
                    print(
                        f"{spell_name} mengenai {damage} damage → "
                        f"diserap armor. (DEF tersisa: {current_defense})"
                    )
                elif current_defense > 0:
                    leftover = damage - current_defense
                    print(
                        f"{spell_name} mengenai {damage} damage → "
                        f"{current_defense} diserap armor, {leftover} menembus ke HP!"
                    )
                    current_defense = 0
                    player.hp = max(0, player.hp - leftover)
                    if not player.is_alive:
                        print("💀 Game Over!")
                else:
                    player.hp = max(0, player.hp - damage)
                    print(f"{enemy.name} mengenai {damage} damage langsung ke HP!")
                    if not player.is_alive:
                        print("💀 Game Over!")

                # Status effect dari spell enemy (hanya terkena jika tidak dodge)
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

        return current_defense

    # ─────────────────────────────────────────────────────────────────────────
    # SPELL EFFECTS (player spells)
    # ─────────────────────────────────────────────────────────────────────────

    def apply_spell_effect(
        self,
        player: "Player",
        enemy: "Enemy",
        spell: dict,
        current_defense: int,
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
            current_defense += boost
            print(
                f"🛡️ Armor menguat! DEF +{boost} (sekarang: {current_defense})!")

        else:
            print("Spell tidak memberikan efek.")

        return current_defense

    # ─────────────────────────────────────────────────────────────────────────
    # VICTORY
    # ─────────────────────────────────────────────────────────────────────────

    def _award_victory(self, player: "Player", enemy: "Enemy") -> None:
        """Berikan reward setelah menang."""
        # Loot system integration
        loot_engine = getattr(self, "_loot_engine", None)
        drops = []

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

        # Roll loot table drops (after base rewards)
        if loot_engine is not None:
            drops = loot_engine.roll_for_enemy(enemy, player)
            if drops:
                from core.loot import LootEngine
                LootEngine.display_drops(drops)

        # Sync encyclopedia with new items
        encyclopedia = getattr(self, "_encyclopedia", None)
        if encyclopedia is not None:
            encyclopedia.sync_with_player(player.inventory)

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
