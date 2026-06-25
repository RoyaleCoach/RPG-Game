import random

from core.enemy import Boss


class Combat:

    def __init__(self, quest_system, items):

        self.quest_system = quest_system
        self.potions = items.get(
            "potions",
            {}
        )

    # -------------------------
    # MAIN BATTLE SYSTEM
    # -------------------------
    def fight(self, player, enemy):

        battle_defense = player.defense

        while player.hp > 0 and enemy.hp > 0:

            print(
                f"\n{player.name} HP: {player.hp} DEF: {battle_defense} | "
                f"{enemy.name} HP: {enemy.hp}"
            )

            action = (
                input(
                    "Choose action (attack / defend / heal): "
                )
                .lower()
                .strip()
            )

            # -------------------------
            # PLAYER TURN
            # -------------------------
            if action == "attack":

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

            elif action == "defend":

                print(
                    "You brace yourself."
                )
                
            elif action == "heal":
                print("\n=== POTIONS ===")

                available_potions = [
                    item
                    for item in player.inventory
                    if item in self.potions
                ]

                
                if not available_potions:

                    print("Tidak ada potion.")
                    continue

                for item in available_potions:

                    print(
                        f"- {item} "
                        f"(Heal: {self.potions[item]['effect']} HP)"
                    )
                    
                potion_name = input(
                    "\nMasukkan nama potion: "
                ).strip()

                player.equip_potion(
                    potion_name
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

            return

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
        # -------------------------
        self.quest_system.check(
            player
        )