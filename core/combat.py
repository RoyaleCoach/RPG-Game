import random

from core.enemy import Boss


class Combat:

    def __init__(self, quest_system, items, skill_system=None):

        self.quest_system = quest_system
        self.potions = items.get(
            "potions",
            {}
        )
        self.skill_system = skill_system

    # -------------------------
    # MAIN BATTLE SYSTEM
    # -------------------------
    def fight(self, player, enemy):

        battle_defense = player.defense

        while player.hp > 0 and enemy.hp > 0:

            print(
                f"\n{player.name} HP: {player.hp}/{player.max_hp} "
                f"| Mana: {player.mana}/{player.max_mana} "
                f"| DEF: {battle_defense} | "
                f"{enemy.name} HP: {enemy.hp}"
            )

            action = (
                input(
                    "Choose action (attack / defend / heal / spell): "
                )
                .lower()
                .strip()
            )

            # -------------------------
            # PLAYER TURN
            # -------------------------
            if action in ["attack", "a"]:

                damage = random.randint(
                    1,
                    player.attack
                )

                enemy.hp = max(
                    0,
                    enemy.hp - damage
                )

                print(
                    f"You dealt {damage} damage!"
                )

            elif action in ["defend", "d"]:

                print(
                    "You brace yourself."
                )

            elif action in ["heal", "h"]:

                print("\n=== POTIONS ===")

                available_potions = [
                    item
                    for item in player.inventory
                    if item in self.potions
                ]

                if not available_potions:
                    print("No potions available.")
                    continue

                for item in available_potions:

                    print(
                        f"- {item} "
                        f"(Heal: {self.potions[item]['effect']} HP)"
                    )

                potion_name = input(
                    "\nEnter potion name: "
                ).strip()

                player.equip_potion(
                    potion_name
                )

            elif action == "spell":

                if self.skill_system is None:
                    print("Magic is unavailable.")
                    continue

                available_spells = self.skill_system.get_available_spells(
                    player
                )

                if not available_spells:
                    print("You do not know any spells.")
                    continue

                print("\n=== SPELLS ===")

                for name, data in available_spells.items():
                    print(
                        f"- {name} (Cost: {data.get('cost', 0)} Mana, "
                        f"Type: {data.get('type')})"
                    )

                spell_name = input(
                    "\nEnter spell name: "
                ).strip()

                spell = self.skill_system.get_spell(
                    spell_name
                )

                if spell is None or spell_name not in player.learned_spells:
                    print("⚠️ Invalid spell.")
                    continue

                cost = spell.get("cost", 0)
                if player.mana < cost:
                    print("⚠️ Not enough mana.")
                    continue

                player.mana -= cost
                description = spell.get(
                    "description",
                    f"{player.name} casts {spell_name}!"
                )

                print(
                    description.replace(
                        "[caster]",
                        player.name
                    )
                )

                battle_defense = self.apply_spell_effect(
                    player,
                    enemy,
                    spell,
                    battle_defense
                )

            else:

                print(
                    "Invalid action."
                )
                continue

            # -------------------------
            # ENEMY TURN
            # -------------------------
            if enemy.hp > 0:

                incoming_damage = random.randint(
                    3,
                    enemy.attack
                )

                if action == "defend":
                    incoming_damage //= 2

                final_damage = player.damage(
                    incoming_damage,
                    battle_defense
                )

                battle_defense -= max(
                    1,
                    incoming_damage // 4
                )

                battle_defense = max(
                    0,
                    battle_defense
                )

                print(
                    f"{enemy.name} dealt "
                    f"{final_damage} damage."
                )

        # -------------------------
        # RESULT
        # -------------------------
        if not player.is_alive:

            print("\n💀 Defeat.")
            return False

        if isinstance(enemy, Boss):

            player.gold += enemy.gold_reward
            player.gain_exp(
                enemy.exp_reward
            )

            print(
                "\n👑 Boss Defeated!"
            )
            print(
                f"+{enemy.gold_reward} Gold"
            )
            print(
                f"+{enemy.exp_reward} EXP"
            )

        else:

            reward = random.randint(
                10,
                30
            )

            player.gold += reward
            player.enemies_killed += 1

            if player.enemies_killed % 3 == 0:

                player.floor += 1
                print(
                    f"📈 Reached Floor "
                    f"{player.floor}!"
                )

            player.gain_exp(10)
            print("\n🏆 Victory!")
            print(f"+{reward} Gold")

        # -------------------------
        # QUEST CHECK
        self.quest_system.check(
            player
        )

        return True

    def apply_spell_effect(self, player, enemy, spell, battle_defense):

        spell_type = spell.get("type", "st/damage")

        if "damage" in spell_type:
            damage = random.randint(
                max(1, spell.get("cost", 5)),
                player.attack + spell.get("level", 1) * 2
            )
            enemy.hp = max(
                0,
                enemy.hp - damage
            )
            print(
                f"{enemy.name} takes {damage} damage!"
            )

        elif "heal" in spell_type:
            heal_amount = random.randint(
                spell.get("cost", 5),
                spell.get("cost", 5) + player.level * 2
            )
            player.hp += heal_amount
            print(
                f"You healed {heal_amount} HP!"
            )

        elif "buff" in spell_type:
            boost = spell.get("level", 1) * 2
            battle_defense += boost
            print(
                f"Your defense increases by {boost} this turn!"
            )

        else:
            print(
                "The spell fizzles without effect."
            )

        return battle_defense
