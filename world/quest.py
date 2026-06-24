from core.quests import QUESTS


def show_quests(player):

    print("\n=== QUEST BOARD ===")

    for quest_name, data in QUESTS.items():

        status = "Completed" \
            if quest_name in player.completed_quests \
            else "Available"

        print(f"\n{quest_name}")
        print(f"Description : {data['description']}")
        print(f"Reward      : {data['reward']}")
        print(f"Gold        : {data['reward_gold']}")
        print(f"Status      : {status}")
        
def check_quests(player):

    for quest_name, data in QUESTS.items():

        if quest_name in player.completed_quests:
            continue

        completed = False

        if quest_name == "Assassin's Legacy":
            completed = player.enemies_killed >= 15

        elif quest_name == "Dragon Hunt":
            completed = player.floor >= 18

        elif quest_name == "Sword in the Stone":
            completed = player.level >= 20

        elif quest_name == "Alchemist's Secret":
            completed = player.puzzles_solved >= 10

        elif quest_name == "Guardian's Oath":
            completed = player.floor >= 22

        elif quest_name == "Trial of the Gods":
            completed = player.level >= 25

        if completed:

            reward = data["reward"]

            player.inventory[reward] = (
                player.inventory.get(reward, 0) + 1
            )

            player.gold += data["reward_gold"]

            player.completed_quests.append(
                quest_name
            )

            print(
                f"\n🏆 Quest Complete!"
            )

            print(
                f"{quest_name}"
            )

            print(
                f"Reward: {reward}"
            )

            print(
                f"Gold: +{data['reward_gold']}"
            )