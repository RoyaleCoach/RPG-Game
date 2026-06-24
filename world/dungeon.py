import random
from core.enemy import Enemy


class Dungeon:

    def __init__(self):
        pass

    # -------------------------
    # MAIN EVENT ROUTER
    # -------------------------
    def random_event(self, player):

        event = random.choice([
            self.treasure_room,
            self.cursed_shrine,
            self.healing_fountain,
            self.ancient_statue,
            self.gambler,
            self.secret_passage,
            self.lost_adventurer
        ])

        event(player)

    # -------------------------
    # TREASURE ROOM
    # -------------------------
    def treasure_room(self, player):

        print("\n🎁 Treasure Room!")

        choice = input("[1] Open Chest\n[2] Leave\n> ")

        if choice != "1":
            return

        if random.randint(1, 100) <= 20:

            print("😈 It's a Mimic!")

            return Enemy("Mimic", 50, 15)

        gold = random.randint(20, 100)
        player.gold += gold

        print(f"You found {gold} gold!")

    # -------------------------
    # HEALING FOUNTAIN
    # -------------------------
    def healing_fountain(self, player):

        print("\n💧 Healing Fountain")

        choice = input("[1] Drink\n[2] Leave\n> ")

        if choice != "1":
            return

        if random.randint(1, 100) <= 15:

            damage = 15
            player.hp -= damage

            print(f"☠️ Poisoned! -{damage} HP")

        else:

            heal = random.randint(20, 50)
            player.hp += heal

            print(f"❤️ +{heal} HP")

    # -------------------------
    # CURSED SHRINE
    # -------------------------
    def cursed_shrine(self, player):

        print("\n☠️ Cursed Shrine")

        choice = input("[1] Pray\n[2] Leave\n> ")

        if choice != "1":
            return

        outcome = random.randint(1, 3)

        if outcome == 1:

            player.attack += 5
            player.hp -= 20
            print("+5 ATK, -20 HP")

        elif outcome == 2:

            player.gold += 100
            print("+100 Gold")

        else:

            player.level += 1
            print("📈 Level Up!")

    # -------------------------
    # ANCIENT STATUE
    # -------------------------
    def ancient_statue(self, player):

        print("\n🗿 Ancient Statue")

        if player.gold < 50:
            print("Need 50 gold.")
            return

        choice = input("[1] Offer 50 Gold\n[2] Leave\n> ")

        if choice != "1":
            return

        player.gold -= 50

        if random.randint(1, 2) == 1:
            player.attack += 2
            print("⚔️ ATK +2")
        else:
            player.defense += 2
            print("🛡️ DEF +2")

    # -------------------------
    # GAMBLER
    # -------------------------
    def gambler(self, player):

        print("\n🎲 Gambler")

        if player.gold < 50:
            print("Need 50 gold.")
            return

        choice = input("[1] Bet 50 Gold\n[2] Leave\n> ")

        if choice != "1":
            return

        player.gold -= 50

        if random.randint(1, 100) <= 50:
            player.gold += 100
            print("🎉 You won!")
        else:
            print("😭 You lost!")

    # -------------------------
    # SECRET PASSAGE
    # -------------------------
    def secret_passage(self, player):

        print("\n🚪 Secret Passage!")

        player.floor += 1

        print(f"📈 Floor {player.floor}")

    # -------------------------
    # LOST ADVENTURER
    # -------------------------
    def lost_adventurer(self, player):

        print("\n👤 Lost Adventurer")

        choice = input("[1] Help\n[2] Rob\n[3] Leave\n> ")

        if choice == "1":

            player.gold += 50
            print("+50 Gold")

        elif choice == "2":

            gold = random.randint(50, 150)
            player.gold += gold

            print(f"+{gold} Gold")