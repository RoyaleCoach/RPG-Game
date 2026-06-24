from core.quests import QUESTS


def get_progress(player, quest_type):

    if quest_type == "kills":
        return player.enemies_killed

    elif quest_type == "floor":
        return player.floor

    elif quest_type == "level":
        return player.level

    elif quest_type == "puzzle":
        return player.puzzles_solved

    return 0


def show_quests(player):

    print("\n=== QUEST BOARD ===")

    for quest_name, data in QUESTS.items():

        status = (
            "Completed"
            if quest_name in player.completed_quests
            else "Available"
        )

        current = get_progress(
            player,
            data["type"]
        )

        progress = (
            f"{min(current, data['target'])}"
            f"/{data['target']}"
        )

        print(f"\n{quest_name}")
        print(f"Description : {data['description']}")
        print(f"Reward      : {data['reward']}")
        print(f"Gold        : {data['reward_gold']}")
        print(f"Status      : {status}")
        print(f"Progress    : {progress}")


def check_quests(player):

    for quest_name, data in QUESTS.items():

        if quest_name in player.completed_quests:
            continue

        current = get_progress(
            player,
            data["type"]
        )

        completed = current >= data["target"]

        if completed:

            reward = data["reward"]

            player.inventory[reward] = (
                player.inventory.get(reward, 0) + 1
            )

            player.gold += data["reward_gold"]

            player.completed_quests.append(
                quest_name
            )

            print("\n🏆 Quest Complete!")
            print(quest_name)
            print(f"Reward: {reward}")
            print(f"Gold: +{data['reward_gold']}")