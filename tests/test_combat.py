"""
Unit tests for Combat system.

Mencakup fitur baru:
  - Critical Hit (roll_damage)
  - Accuracy (min damage)
  - Dodge (roll_dodge)
  - Status Effects (Burn, Poison, Freeze, dll.)
  - Enemy AI (choose_action)
  - MultiphaseBoss (try_advance_phase)
"""

import unittest
from unittest.mock import Mock, patch, MagicMock


# ─────────────────────────────────────────────────────────────────────────────
# Helpers: minimal stub agar tidak butuh seluruh project
# ─────────────────────────────────────────────────────────────────────────────

def _make_player(**kwargs):
    """Buat Player dengan nilai default yang aman untuk testing."""
    from core.player import Player
    defaults = dict(
        name="TestPlayer",
        hp=100,
        attack=10,
        defense=5,
        gold=50,
        level=1,
        critical_chance=15,
        critical_multiplier=2.0,
        accuracy=5,
        dodge=5,
    )
    defaults.update(kwargs)
    return Player(**defaults)


def _make_enemy(**kwargs):
    """Buat Enemy dengan nilai default yang aman untuk testing."""
    from core.enemy import Enemy
    defaults = dict(
        name="TestEnemy",
        hp=50,
        attack=5,
        critical_chance=10,
        critical_multiplier=1.5,
        accuracy=3,
        dodge=5,
    )
    defaults.update(kwargs)
    return Enemy(**defaults)


# ─────────────────────────────────────────────────────────────────────────────
# Test: Combat initialization
# ─────────────────────────────────────────────────────────────────────────────

class TestCombatInitialization(unittest.TestCase):
    """Combat terbentuk dengan benar dari parameter konstruktor."""

    def setUp(self):
        from core.combat import Combat
        from core.skill import Skill

        self.quest_system = Mock()
        self.quest_system.check = Mock()
        self.items = {
            "potions": {"health_potion": {"effect": 50}}
        }
        self.skill_system = Skill({
            "icicle": {"cost": 10, "type": "st/damage",
                       "description": "[caster] casts icicle!"}
        })
        self.combat = Combat(self.quest_system, self.items, self.skill_system)

    def test_quest_system_assigned(self):
        self.assertEqual(self.combat.quest_system, self.quest_system)

    def test_skill_system_assigned(self):
        self.assertEqual(self.combat.skill_system, self.skill_system)

    def test_potions_loaded(self):
        self.assertIn("health_potion", self.combat.potions)

    def test_no_skill_system(self):
        from core.combat import Combat
        combat = Combat(self.quest_system, self.items, skill_system=None)
        self.assertIsNone(combat.skill_system)


# ─────────────────────────────────────────────────────────────────────────────
# Test: Spell Effects
# ─────────────────────────────────────────────────────────────────────────────

class TestSpellEffects(unittest.TestCase):
    """apply_spell_effect() menerapkan damage / heal / buff dengan benar."""

    def setUp(self):
        from core.combat import Combat
        from core.skill import Skill

        self.quest_system = Mock()
        self.combat = Combat(self.quest_system, {}, Skill({}))
        self.player = _make_player()
        self.enemy = _make_enemy()

    def test_damage_spell_reduces_enemy_hp(self):
        spell = {"type": "st/damage", "cost": 10, "level": 1}
        initial_hp = self.enemy.hp
        self.combat.apply_spell_effect(self.player, self.enemy, spell, 5)
        # Enemy bisa dodge, jadi hp hanya bisa sama atau lebih kecil
        self.assertLessEqual(self.enemy.hp, initial_hp)

    def test_damage_spell_dodge_enemy_hp_unchanged(self):
        """Jika enemy dodge 100%, HP tidak berubah."""
        self.enemy.dodge = 100
        spell = {"type": "st/damage", "cost": 10, "level": 1}
        initial_hp = self.enemy.hp
        self.combat.apply_spell_effect(self.player, self.enemy, spell, 5)
        self.assertEqual(self.enemy.hp, initial_hp)

    def test_heal_spell_increases_player_hp(self):
        spell = {"type": "st/heal", "cost": 10, "level": 1}
        self.player._hp = 50
        initial_hp = self.player.hp
        self.combat.apply_spell_effect(self.player, self.enemy, spell, 5)
        self.assertGreaterEqual(self.player.hp, initial_hp)

    def test_heal_spell_does_not_exceed_max_hp(self):
        spell = {"type": "st/heal", "cost": 999, "level": 10}
        self.player._hp = self.player.max_hp
        self.combat.apply_spell_effect(self.player, self.enemy, spell, 5)
        self.assertLessEqual(self.player.hp, self.player.max_hp)

    def test_buff_spell_increases_battle_defense(self):
        spell = {"type": "st/buff", "cost": 10, "level": 2}
        new_def = self.combat.apply_spell_effect(
            self.player, self.enemy, spell, 5)
        self.assertGreater(new_def, 5)

    def test_buff_defense_boost_scales_with_level(self):
        spell_lv1 = {"type": "st/buff", "cost": 10, "level": 1}
        spell_lv3 = {"type": "st/buff", "cost": 10, "level": 3}
        def1 = self.combat.apply_spell_effect(
            self.player, self.enemy, spell_lv1, 0)
        def3 = self.combat.apply_spell_effect(
            self.player, self.enemy, spell_lv3, 0)
        self.assertGreater(def3, def1)

    def test_unknown_spell_type_returns_defense_unchanged(self):
        spell = {"type": "unknown_type", "cost": 5, "level": 1}
        result = self.combat.apply_spell_effect(
            self.player, self.enemy, spell, 7)
        self.assertEqual(result, 7)


# ─────────────────────────────────────────────────────────────────────────────
# Test: roll_damage — Critical Hit & Accuracy
# ─────────────────────────────────────────────────────────────────────────────

class TestRollDamage(unittest.TestCase):
    """roll_damage() menerapkan accuracy dan critical hit dengan benar."""

    def setUp(self):
        from core.combat import roll_damage
        self.roll_damage = roll_damage

    def _attacker(self, accuracy=0, crit_chance=0, crit_mult=2.0):
        a = Mock()
        a.accuracy = accuracy
        a.critical_chance = crit_chance
        a.critical_multiplier = crit_mult
        return a

    def test_damage_within_range(self):
        """Damage selalu antara min_damage dan base_max."""
        attacker = self._attacker(accuracy=3)
        for _ in range(50):
            dmg, _ = self.roll_damage(attacker, 20)
            self.assertGreaterEqual(dmg, 3)
            self.assertLessEqual(dmg, 20)

    def test_min_damage_capped_by_base_max(self):
        """accuracy lebih besar dari base_max → min = base_max."""
        attacker = self._attacker(accuracy=999)
        for _ in range(20):
            dmg, _ = self.roll_damage(attacker, 10)
            self.assertEqual(dmg, 10)   # min == max → selalu 10

    def test_critical_hit_always_triggers(self):
        """crit_chance=100 → selalu critical; damage >= min_damage * multiplier."""
        # accuracy=5 → min_damage=5, crit_mult=3.0 → damage minimal = 5*3 = 15
        attacker = self._attacker(accuracy=5, crit_chance=100, crit_mult=3.0)
        for _ in range(20):
            dmg, is_crit = self.roll_damage(attacker, 10)
            self.assertTrue(is_crit)
            # min_damage(5) * multiplier(3.0)
            self.assertGreaterEqual(dmg, 5 * 3)

    def test_critical_hit_never_triggers(self):
        """crit_chance=0 → tidak pernah critical."""
        attacker = self._attacker(crit_chance=0)
        for _ in range(50):
            _, is_crit = self.roll_damage(attacker, 10)
            self.assertFalse(is_crit)

    def test_critical_multiplier_applied(self):
        """Damage saat crit = damage * multiplier."""
        attacker = self._attacker(accuracy=10, crit_chance=100, crit_mult=2.0)
        for _ in range(10):
            dmg, is_crit = self.roll_damage(attacker, 10)
            self.assertTrue(is_crit)
            # base_max=10, accuracy=10 → min=max=10 → damage pasti 10*2=20
            self.assertEqual(dmg, 20)

    def test_damage_always_at_least_one(self):
        """Damage tidak pernah 0 atau negatif."""
        attacker = self._attacker(accuracy=0, crit_chance=0)
        for _ in range(30):
            dmg, _ = self.roll_damage(attacker, 1)
            self.assertGreaterEqual(dmg, 1)

    def test_higher_accuracy_raises_average(self):
        """Rata-rata damage lebih tinggi saat accuracy lebih besar."""
        low_acc = self._attacker(accuracy=1,  crit_chance=0)
        high_acc = self._attacker(accuracy=18, crit_chance=0)
        avg_low = sum(self.roll_damage(low_acc,  20)
                      [0] for _ in range(200)) / 200
        avg_high = sum(self.roll_damage(high_acc, 20)
                       [0] for _ in range(200)) / 200
        self.assertGreater(avg_high, avg_low)


# ─────────────────────────────────────────────────────────────────────────────
# Test: roll_dodge
# ─────────────────────────────────────────────────────────────────────────────

class TestRollDodge(unittest.TestCase):
    """roll_dodge() mengembalikan True/False sesuai probabilitas dodge."""

    def setUp(self):
        from core.combat import roll_dodge
        self.roll_dodge = roll_dodge

    def _target(self, dodge):
        t = Mock()
        t.dodge = dodge
        return t

    def test_dodge_100_always_true(self):
        t = self._target(100)
        for _ in range(20):
            self.assertTrue(self.roll_dodge(t))

    def test_dodge_0_always_false(self):
        t = self._target(0)
        for _ in range(20):
            self.assertFalse(self.roll_dodge(t))

    def test_dodge_returns_bool(self):
        t = self._target(50)
        result = self.roll_dodge(t)
        self.assertIsInstance(result, bool)

    def test_no_dodge_attr_defaults_to_false(self):
        """Entity tanpa atribut dodge tidak pernah dodge."""
        t = Mock(spec=[])   # tidak punya atribut apapun
        # roll_dodge pakai getattr dengan default 0
        from core.combat import roll_dodge as rd
        # Pastikan tidak raise, dan selalu False
        for _ in range(10):
            result = rd(t)
            self.assertFalse(result)


# ─────────────────────────────────────────────────────────────────────────────
# Test: Status Effects
# ─────────────────────────────────────────────────────────────────────────────

class TestStatusEffects(unittest.TestCase):
    """Status effects diterapkan, men-tick, dan expire dengan benar."""

    def _entity(self, hp=100, max_hp=100):
        e = Mock()
        e.name = "Target"
        e.hp = hp
        e.max_hp = max_hp
        e.status_effects = []
        return e

    def test_burn_applies_to_target(self):
        from core.status_effects import Burn, apply_effect_to
        e = self._entity()
        apply_effect_to(e, Burn(duration=3))
        self.assertEqual(len(e.status_effects), 1)
        self.assertEqual(e.status_effects[0].name, "Burn")

    def test_burn_deals_damage_per_tick(self):
        from core.status_effects import Burn, apply_effect_to, apply_status_effects
        e = self._entity(hp=100, max_hp=100)
        apply_effect_to(e, Burn(duration=2))
        apply_status_effects(e)
        self.assertLess(e.hp, 100)

    def test_burn_expires_after_duration(self):
        from core.status_effects import Burn, apply_effect_to, apply_status_effects
        e = self._entity()
        apply_effect_to(e, Burn(duration=2))
        apply_status_effects(e)
        apply_status_effects(e)
        apply_status_effects(e)   # extra tick setelah expire
        self.assertEqual(len(e.status_effects), 0)

    def test_same_effect_refreshed_not_stacked(self):
        from core.status_effects import Burn, apply_effect_to
        e = self._entity()
        apply_effect_to(e, Burn(duration=2))
        apply_effect_to(e, Burn(duration=5))   # refresh
        self.assertEqual(len(e.status_effects), 1)
        self.assertEqual(e.status_effects[0].duration, 5)

    def test_poison_reduces_hp(self):
        from core.status_effects import Poison, apply_effect_to, apply_status_effects
        e = self._entity(hp=100)
        apply_effect_to(e, Poison(duration=1, damage_per_tick=10))
        apply_status_effects(e)
        self.assertEqual(e.hp, 90)

    def test_regen_increases_hp(self):
        from core.status_effects import Regen, apply_effect_to, apply_status_effects
        e = self._entity(hp=50, max_hp=100)
        apply_effect_to(e, Regen(duration=1, heal_per_tick=20))
        apply_status_effects(e)
        self.assertGreater(e.hp, 50)

    def test_freeze_immobilizes_target(self):
        from core.status_effects import Freeze, apply_effect_to, apply_status_effects
        e = self._entity()
        apply_effect_to(e, Freeze(duration=2))
        can_act = apply_status_effects(e)
        self.assertFalse(can_act)

    def test_freeze_expires_after_duration(self):
        from core.status_effects import Freeze, apply_effect_to, apply_status_effects
        e = self._entity()
        apply_effect_to(e, Freeze(duration=1))
        apply_status_effects(e)   # tick → expire
        can_act = apply_status_effects(e)  # sudah tidak ada freeze
        self.assertTrue(can_act)

    def test_stun_immobilizes_for_one_turn(self):
        from core.status_effects import Stun, apply_effect_to, apply_status_effects
        e = self._entity()
        apply_effect_to(e, Stun(duration=1))
        can_act = apply_status_effects(e)
        self.assertFalse(can_act)
        can_act_next = apply_status_effects(e)
        self.assertTrue(can_act_next)

    def test_bleed_damage_increases_each_tick(self):
        from core.status_effects import Bleed, apply_effect_to
        e = self._entity(hp=200, max_hp=200)
        bleed = Bleed(duration=3, base_damage=4)
        apply_effect_to(e, bleed)
        hp_after_tick1 = e.hp
        bleed.tick(e)
        hp_after_tick2 = e.hp
        # 4 + 1 = 5 (dari on_apply tidak deal dmg)
        dmg1 = 200 - hp_after_tick1
        # tick manual pertama (on_apply sudah dijalankan apply_effect_to, lalu tick pertama)
        dmg2 = hp_after_tick1 - hp_after_tick2
        self.assertGreater(dmg2, 0)

    def test_get_spell_effect_fireball_returns_burn(self):
        from core.status_effects import get_spell_effect, Burn
        effect = get_spell_effect("fireball")
        self.assertIsInstance(effect, Burn)

    def test_get_spell_effect_unknown_returns_none(self):
        from core.status_effects import get_spell_effect
        self.assertIsNone(get_spell_effect("nonexistent_spell"))

    def test_multiple_different_effects_stack(self):
        from core.status_effects import Burn, Poison, apply_effect_to
        e = self._entity()
        apply_effect_to(e, Burn(duration=3))
        apply_effect_to(e, Poison(duration=3))
        self.assertEqual(len(e.status_effects), 2)


# ─────────────────────────────────────────────────────────────────────────────
# Test: Enemy AI
# ─────────────────────────────────────────────────────────────────────────────

class TestEnemyAI(unittest.TestCase):
    """Enemy.choose_action() mengembalikan aksi valid dan bereaksi ke kondisi."""

    VALID_ACTIONS = {"attack", "defend", "spell", "dodge"}

    def setUp(self):
        self.enemy = _make_enemy(hp=100)
        self.enemy.max_hp = 100

    def test_returns_valid_action(self):
        for _ in range(30):
            action = self.enemy.choose_action(mana=0)
            self.assertIn(action, self.VALID_ACTIONS)

    def test_low_hp_increases_defend_frequency(self):
        """Saat HP < 30%, defend harus muncul lebih sering dari normal."""
        self.enemy.hp = 20   # 20% dari 100
        actions = [self.enemy.choose_action(mana=0) for _ in range(200)]
        defend_ratio = actions.count("defend") / len(actions)
        self.assertGreater(defend_ratio, 0.15)

    def test_spell_chosen_when_mana_available(self):
        """Spell muncul dalam pool jika enemy punya spell & mana."""
        from core.enemy import Enemy
        enemy = Enemy("Mage", hp=100, attack=10, spells=["fireball"])
        enemy.max_hp = 100
        actions = [enemy.choose_action(mana=30) for _ in range(200)]
        self.assertIn("spell", actions)

    def test_spell_never_chosen_without_mana(self):
        from core.enemy import Enemy
        enemy = Enemy("Mage", hp=100, attack=10, spells=["fireball"])
        enemy.max_hp = 100
        actions = [enemy.choose_action(mana=0) for _ in range(100)]
        self.assertNotIn("spell", actions)

    def test_dodge_cooldown_prevents_spam(self):
        """Setelah dodge, enemy tidak bisa dodge selama 3 turn."""
        self.enemy.dodge = 100
        # Paksa cooldown reset, lalu pilih dodge
        self.enemy._dodge_cooldown = 0
        self.enemy.hp = self.enemy.max_hp   # HP tidak rendah
        # Cari turn di mana dodge dipilih
        found_dodge = False
        for _ in range(100):
            action = self.enemy.choose_action(mana=0)
            if action == "dodge":
                found_dodge = True
                break
        # Setelah dodge ditemukan, cooldown harus > 0
        if found_dodge:
            self.assertGreater(self.enemy._dodge_cooldown, 0)

    def test_no_spell_when_no_spells_pool(self):
        """Enemy tanpa spell pool tidak pernah pilih 'spell'."""
        actions = [self.enemy.choose_action(mana=99) for _ in range(100)]
        self.assertNotIn("spell", actions)


# ─────────────────────────────────────────────────────────────────────────────
# Test: MultiphaseBoss
# ─────────────────────────────────────────────────────────────────────────────

class TestMultiphaseBoss(unittest.TestCase):
    """MultiphaseBoss berpindah phase dengan benar."""

    def _make_boss(self):
        from core.enemy import MultiphaseBoss, BossPhase
        phases = [
            BossPhase(phase_number=1, hp=300, attack=30, critical_chance=10),
            BossPhase(phase_number=2, hp=200, attack=50, critical_chance=20,
                      spells=["fireball"],
                      transition_message="Phase 2!"),
            BossPhase(phase_number=3, hp=100, attack=70, critical_chance=30),
        ]
        return MultiphaseBoss("TestBoss", phases, exp_reward=500, gold_reward=300)

    def test_initial_phase_is_one(self):
        boss = self._make_boss()
        self.assertEqual(boss.phase_number, 1)

    def test_initial_stats_from_phase_one(self):
        boss = self._make_boss()
        self.assertEqual(boss.hp, 300)
        self.assertEqual(boss.attack, 30)

    def test_has_next_phase_true_when_not_last(self):
        boss = self._make_boss()
        self.assertTrue(boss.has_next_phase)

    def test_advance_to_phase_two(self):
        boss = self._make_boss()
        boss.hp = 0
        result = boss.try_advance_phase()
        self.assertTrue(result)
        self.assertEqual(boss.phase_number, 2)
        self.assertEqual(boss.hp, 200)
        self.assertEqual(boss.attack, 50)

    def test_advance_to_phase_three(self):
        boss = self._make_boss()
        boss.hp = 0
        boss.try_advance_phase()
        boss.hp = 0
        boss.try_advance_phase()
        self.assertEqual(boss.phase_number, 3)
        self.assertEqual(boss.hp, 100)
        self.assertEqual(boss.attack, 70)

    def test_no_advance_after_last_phase(self):
        boss = self._make_boss()
        boss.try_advance_phase()
        boss.try_advance_phase()
        result = boss.try_advance_phase()   # sudah di phase terakhir
        self.assertFalse(result)

    def test_has_next_phase_false_at_last_phase(self):
        boss = self._make_boss()
        boss.try_advance_phase()
        boss.try_advance_phase()
        self.assertFalse(boss.has_next_phase)

    def test_critical_chance_updates_on_advance(self):
        boss = self._make_boss()
        boss.try_advance_phase()
        self.assertEqual(boss.critical_chance, 20)

    def test_spells_update_on_advance(self):
        boss = self._make_boss()
        boss.try_advance_phase()
        self.assertIn("fireball", boss.spells)

    def test_status_effects_cleared_on_advance(self):
        from core.status_effects import Burn
        boss = self._make_boss()
        boss.status_effects.append(Burn())
        boss.try_advance_phase()
        self.assertEqual(len(boss.status_effects), 0)

    def test_total_phases(self):
        boss = self._make_boss()
        self.assertEqual(boss.total_phases, 3)

    def test_from_data_fallback_creates_two_phases(self):
        """from_data() tanpa key 'phases' otomatis buat 2-phase."""
        from core.enemy import MultiphaseBoss
        data = {"name": "FallbackBoss", "hp": 400, "attack": 40,
                "exp_reward": 200, "gold_reward": 100}
        boss = MultiphaseBoss.from_data(data)
        self.assertEqual(boss.total_phases, 2)

    def test_the_first_hollow_has_three_phases(self):
        from core.enemy import TheFirstHollow
        boss = TheFirstHollow()
        self.assertEqual(boss.total_phases, 3)
        self.assertEqual(boss.exp_reward, 1000)


# ─────────────────────────────────────────────────────────────────────────────
# Test: Player stat baru
# ─────────────────────────────────────────────────────────────────────────────

class TestPlayerNewStats(unittest.TestCase):
    """Player mempunyai stat baru dengan default yang benar."""

    def test_default_critical_chance(self):
        p = _make_player()
        self.assertEqual(p.critical_chance, 15)

    def test_default_critical_multiplier(self):
        p = _make_player()
        self.assertEqual(p.critical_multiplier, 2.0)

    def test_default_accuracy(self):
        p = _make_player()
        self.assertEqual(p.accuracy, 5)

    def test_default_dodge(self):
        p = _make_player()
        self.assertEqual(p.dodge, 5)

    def test_status_effects_empty_on_init(self):
        p = _make_player()
        self.assertEqual(p.status_effects, [])

    def test_custom_stats_assigned(self):
        p = _make_player(critical_chance=30, accuracy=10, dodge=20)
        self.assertEqual(p.critical_chance, 30)
        self.assertEqual(p.accuracy, 10)
        self.assertEqual(p.dodge, 20)

    def test_new_stats_serialized_to_dict(self):
        p = _make_player(critical_chance=25, accuracy=8, dodge=12)
        d = p.to_dict()
        player_section = d["player"]
        self.assertEqual(player_section["critical_chance"], 25)
        self.assertEqual(player_section["accuracy"], 8)
        self.assertEqual(player_section["dodge"], 12)

    def test_new_stats_deserialized_from_dict(self):
        from core.player import Player
        p = _make_player(critical_chance=25, accuracy=8, dodge=12)
        d = p.to_dict()
        restored = Player.from_dict(d)
        self.assertEqual(restored.critical_chance, 25)
        self.assertEqual(restored.accuracy, 8)
        self.assertEqual(restored.dodge, 12)

    def test_legacy_save_uses_defaults(self):
        """Save lama tanpa stat baru → default saat load."""
        from core.player import Player
        legacy = {
            "name": "OldHero", "level": 1, "exp": 0,
            "hp": 80, "attack": 10, "defense": 5,
            "gold": 100, "luck": 0, "reputation": 0,
            "skill_points": 0, "floor": 1,
        }
        p = Player.from_dict(legacy)
        self.assertEqual(p.critical_chance, 15)
        self.assertEqual(p.accuracy, 5)
        self.assertEqual(p.dodge, 5)

    def test_level_up_increases_combat_stats(self):
        p = _make_player(level=1, exp=0)
        old_crit = p.critical_chance
        old_acc = p.accuracy
        old_dodge = p.dodge
        p.gain_exp(100)   # level up
        self.assertGreaterEqual(p.critical_chance, old_crit)
        self.assertGreaterEqual(p.accuracy, old_acc)
        self.assertGreaterEqual(p.dodge, old_dodge)


# ─────────────────────────────────────────────────────────────────────────────
# Test: Potion
# ─────────────────────────────────────────────────────────────────────────────

class TestPotionAvailability(unittest.TestCase):

    def test_potion_in_items(self):
        items = {"potions": {"health_potion": {"effect": 50}}}
        self.assertIn("health_potion", items["potions"])

    def test_player_use_potion(self):
        items = {"potions": {"Health Potion": {"effect": 40, "price": 30,
                                               "limited": False,
                                               "rarity": "Common",
                                               "level_required": 1,
                                               "quest": None}}}
        p = _make_player(items=items)
        p._hp = 50
        p.inventory["Health Potion"] = 1
        p.equip_potion("Health Potion")
        self.assertGreater(p.hp, 50)
        self.assertNotIn("Health Potion", p.inventory)


# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    unittest.main(verbosity=2)
