import random
from enemy import Enemy
from puzzle import random_puzzle
from npc import NPC
from player import Player
from utils.text_effect import typewriter

MAP = [
    ["enemy", "merchant", "puzzle"],
    ["npc", "enemy", "nothing"],
    ["puzzle", "enemy", "exit"]
]

player = Player.load()
npc_mentor = NPC("Elder Rion", "Buktikan keberanianmu dengan mengalahkan satu musuh.", "Magic Staff", 50)

def explore(player):
    event = random.choice(["enemy", "puzzle", "merchant", "npc", "nothing"])

    if event == "enemy":
        enemy = Enemy.random_enemy()
        print(f"\n⚔️ Kamu bertemu {enemy.name}!")
        battle(player, enemy)

    elif event == "puzzle":
        success = random_puzzle()
        if success:
            Player.gain_exp(player, 20)
        elif not success:
            amount = 10
            Player.damage(player, amount)
            print(f"HP berkurang sebanyak -{amount}")

    elif event == "npc":
        if "Quest: defeated enemy" in player.quest:
            npc_mentor.complete(player)
        else:
            npc_mentor.talk(player)

    else:
        typewriter("\n🌿 Tidak ada yang terjadi di ruangan ini", dramatic=True)

def battle(player, enemy):
    while player.hp > 0 and enemy.hp > 0:
        print(f"\n{player.name} HP: {player.hp} | {enemy.name} HP: {enemy.hp}")
        action = input("Pilih aksi (serang / bertahan): ").lower()

        if action == "serang":
            dmg = random.randint(5, player.attack)
            enemy.hp -= dmg
            print(f"Kamu menyerang {enemy.name} dan memberi {dmg} damage!")
        elif action == "bertahan":
            print("Kamu bertahan dan mengurangi damage musuh.")
        else:
            print("Aksi tidak valid.")
            continue

        if enemy.hp > 0:
            amount = random.randint(3, enemy.attack)
            if action == "bertahan":
                amount //= 2
            Player.damage(player, amount)
            print(f"{enemy.name} menyerangmu! Kamu kehilangan {amount} HP.")
    if player.hp <= 0:
        print("💀 Kamu kalah...")
    else:
        reward = random.randint(10, 30)
        player.gold += reward
        print(f"🏆 Kamu menang dan mendapatkan {reward} gold!")
        player.quest.append("Quest: defeated enemy")
