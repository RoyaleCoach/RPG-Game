class QuestSystem:

    def __init__(self, quests):

        self.quests = quests

    # -------------------------
    # PROGRESS TRACKER
    # -------------------------
    def get_progress(
        self,
        player,
        quest_type
    ):

        progress_map = {
            "kills": player.enemies_killed,
            "floor": player.floor,
            "level": player.level,
            "puzzle": player.puzzles_solved
        }

        return progress_map.get(
            quest_type,
            0
        )

    # -------------------------
    # SHOW QUEST BOARD
    # -------------------------
    def show(self, player):

        print("\n=== QUEST BOARD ===")

        for quest_name, data in self.quests.items():

            completed = (
                quest_name
                in player.completed_quests
            )

            status = (
                "Completed"
                if completed
                else "Available"
            )

            current = self.get_progress(
                player,
                data["type"]
            )

            progress = (
                f"{min(current, data['target'])}"
                f"/{data['target']}"
            )

            print(f"\n{quest_name}")
            print(
                f"Description : "
                f"{data['description']}"
            )

            print(
                f"Reward      : "
                f"{data['reward']}"
            )

            print(
                f"Gold        : "
                f"{data['reward_gold']}"
            )

            print(
                f"Status      : "
                f"{status}"
            )

            print(
                f"Progress    : "
                f"{progress}"
            )

    # -------------------------
    # CHECK QUEST COMPLETION
    # -------------------------
    def check(self, player):

        for quest_name, data in self.quests.items():

            if (
                quest_name
                in player.completed_quests
            ):
                continue

            current = self.get_progress(
                player,
                data["type"]
            )

            if current < data["target"]:
                continue

            reward = data["reward"]

            player.inventory[reward] = (
                player.inventory.get(
                    reward,
                    0
                ) + 1
            )

            player.gold += (
                data["reward_gold"]
            )

            player.completed_quests.append(
                quest_name
            )

            print(
                "\n🏆 Quest Complete!"
            )

            print(
                quest_name
            )

            print(
                f"Reward: {reward}"
            )

            print(
                f"Gold: +{data['reward_gold']}"
            )