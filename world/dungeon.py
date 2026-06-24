import random

from core.enemy import Enemy


def random_event(player):

    event = random.choice([
        treasure_room,
        cursed_shrine,
        healing_fountain,
        ancient_statue,
        gambler,
        secret_passage,
        lost_adventurer
    ])

    event(player)


def treasure_room(player):

    print("\n🎁 Treasure Room!")

    choice = input(
        "[1] Open Chest\n"
        "[2] Leave\n> "
    )

    if choice != "1":
        return

    if random.randint(1, 100) <= 20:

        print("😈 It's a Mimic!")

        enemy = Enemy(
            "Mimic",
            50,
            15
        )

        return enemy

    gold = random.randint(20, 100)

    player.gold += gold

    print(
        f"You found {gold} gold!"
    )


def healing_fountain(player):

    print("\n💧 Healing Fountain")

    choice = input(
        "[1] Drink\n"
        "[2] Leave\n> "
    )

    if choice != "1":
        return

    if random.randint(1, 100) <= 15:

        damage = 15

        player.hp -= damage

        print(
            f"☠️ Poisoned! "
            f"-{damage} HP"
        )

    else:

        heal = random.randint(20, 50)

        player.hp += heal

        print(
            f"❤️ +{heal} HP"
        )


def cursed_shrine(player):

    print("\n☠️ Cursed Shrine")

    choice = input(
        "[1] Pray\n"
        "[2] Leave\n> "
    )

    if choice != "1":
        return

    outcome = random.randint(1, 3)

    if outcome == 1:

        player.attack += 5
        player.hp -= 20

        print(
            "+5 ATK, -20 HP"
        )

    elif outcome == 2:

        player.gold += 100

        print(
            "+100 Gold"
        )

    else:

        player.level += 1

        print(
            "📈 Level Up!"
        )


def ancient_statue(player):

    print("\n🗿 Ancient Statue")

    if player.gold < 50:

        print(
            "Need 50 gold."
        )

        return

    choice = input(
        "[1] Offer 50 Gold\n"
        "[2] Leave\n> "
    )

    if choice != "1":
        return

    player.gold -= 50

    if random.randint(1, 2) == 1:

        player.attack += 2

        print(
            "⚔️ ATK +2"
        )

    else:

        player.defense += 2

        print(
            "🛡️ DEF +2"
        )


def gambler(player):

    print("\n🎲 Gambler")

    if player.gold < 50:

        print(
            "Need 50 gold."
        )

        return

    choice = input(
        "[1] Bet 50 Gold\n"
        "[2] Leave\n> "
    )

    if choice != "1":
        return

    player.gold -= 50

    if random.randint(1, 100) <= 50:

        player.gold += 100

        print(
            "🎉 You won!"
        )

    else:

        print(
            "😭 You lost!"
        )


def secret_passage(player):

    print(
        "\n🚪 Secret Passage!"
    )

    player.floor += 1

    print(
        f"📈 Floor {player.floor}"
    )


def lost_adventurer(player):

    print(
        "\n👤 Lost Adventurer"
    )

    choice = input(
        "[1] Help\n"
        "[2] Rob\n"
        "[3] Leave\n> "
    )

    if choice == "1":

        player.gold += 50

        print(
            "+50 Gold"
        )

    elif choice == "2":

        gold = random.randint(
            50,
            150
        )

        player.gold += gold

        print(
            f"+{gold} Gold"
        )