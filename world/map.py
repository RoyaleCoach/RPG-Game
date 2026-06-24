import random

from core.enemy import Enemy
from world.puzzle import random_puzzle
from world.quest import (
    show_quests,
    check_quests
)

def explore(player):

    while True:

        print("\n=== DUNGEON ===")
        print("[1] Fight Enemy")
        print("[2] Solve Puzzle")
        print("[3] Quest Board")
        print("[0] Return")

        choice = input("> ").strip()

        if choice == "0":
            break

        elif choice == "1":

            enemy = Enemy.random_enemy(player.floor)

            print(
                f"\n⚔️ You encountered {enemy.name}!"
            )

            battle(player, enemy)

        elif choice == "2":

            success = random_puzzle()

            if success:

                player.puzzles_solved += 1

                player.gain_exp(20)

                check_quests(player)

            else:

                damage = 10

                player.damage(damage)

                print(f"HP -{damage}")

        elif choice == "3":

            show_quests(player)

        else:

            print("Invalid choice.")


def battle(player, enemy):

    while player.hp > 0 and enemy.hp > 0:

        print(
            f"\n{player.name} HP: {player.hp} | "
            f"{enemy.name} HP: {enemy.hp}"
        )

        action = input(
            "Choose action (attack / defend): "
        ).lower()

        if action == "attack":

            damage = random.randint(
                max(1, player.attack // 2),
                player.attack
            )

            enemy.hp -= damage

            print(
                f"You dealt {damage} damage!"
            )

        elif action == "defend":

            print(
                "You brace yourself."
            )

        else:

            print("Invalid action.")
            continue

        if enemy.hp > 0:

            damage = random.randint(
                3,
                enemy.attack
            )

            if action == "defend":
                damage //= 2

            player.damage(damage)

            print(
                f"{enemy.name} dealt "
                f"{damage} damage."
            )

    if player.hp <= 0:

        print("\n💀 Defeat.")

    else:

        reward = random.randint(10, 30)

        player.gold += reward

        player.enemies_killed += 1

        player.gain_exp(10)

        print(
            f"\n🏆 Victory!"
        )

        print(
            f"+{reward} Gold"
        )

        check_quests(player)