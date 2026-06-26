from core.enemy import Enemy
from world.puzzle import random_puzzle
import random


class Explore:

    def __init__(self, combat, dungeon_system, quest_system):

        self.combat = combat
        self.dungeon_system = dungeon_system
        self.quest_system = quest_system

    # -------------------------
    # BOSS CHECK SYSTEM
    # -------------------------
    def check_dungeon_boss(self, player):

        if player.skip_next_boss_preparation:
            print("🛡️ Boss preparation was skipped by fate.")
            player.skip_next_boss_preparation = False
            return

        player.dungeon_runs += 1

        if player.dungeon_runs % 3 == 0:

            boss = Enemy.random_boss(player.level)

            print("\n👑 A Boss Appears!")
            print(f"{boss.name} blocks your path!")

            self.combat.fight(player, boss)

            if player.hp <= 0:
                return

    # -------------------------
    # MAIN EXPLORE LOOP
    # -------------------------
    def explore(self, player):

        while True:

            print("\n=== DUNGEON ===")
            print("[1] Fight Enemy")
            print("[2] Solve Puzzle")
            print("[3] Quest Board")
            print("[4] Random Event")
            print("[0] Return")

            choice = input("> ").strip()

            if choice == "0":
                break

            # -------------------------
            # FIGHT ENEMY
            # -------------------------
            elif choice == "1":

                if player.skip_next_battle:
                    print("🛡️ The next battle was skipped.")
                    player.skip_next_battle = False
                    continue

                self.check_dungeon_boss(player)

                enemy = Enemy.random_enemy(player.floor)

                print(f"\n⚔️ You encountered {enemy.name}!")

                self.combat.fight(player, enemy)

            # -------------------------
            # PUZZLE
            # -------------------------
            elif choice == "2":

                success = random_puzzle()

                if player.skip_next_trap:
                    print("🧩 The trap was skipped.")
                    player.skip_next_trap = False
                    success = True

                if success:

                    player.puzzles_solved += 1
                    player.gain_exp(20)
                    self.quest_system.check(player)

                else:

                    damage = random.randint(5, 15)
                    final_damage = player.damage(damage, 0)

                    print(f"HP -{final_damage}")

            # -------------------------
            # QUEST
            # -------------------------
            elif choice == "3":

                self.quest_system.show(player)

            # -------------------------
            # RANDOM EVENT
            # -------------------------
            elif choice == "4":

                self.dungeon_system.random_event(player)
                self.check_dungeon_boss(player)

            else:

                print("Invalid choice.")