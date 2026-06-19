class NPC:
    def __init__(self, name, quest, reward_item, reward_gold):
        self.name = name
        self.quest = quest
        self.reward_item = reward_item
        self.reward_gold = reward_gold
        self.completed = False

    def talk(self, player):
        if not self.completed:
            print(f"\n🧙 {self.name}: {self.quest}")
            choice = input("Terima quest ini? (y/n): ").lower()
            if choice == "y":
                print(f"{self.name}: Bagus! Kembali padaku setelah kamu mengalahkan 1 musuh.")
                player.quest.append("Quest: defeat enemy")
            else:
                print(f"{self.name}: Baiklah, hati-hati di jalan.")
        else:
            print(f"{self.name}: Terima kasih lagi, petualang.")

    def complete(self, player):
        if "Quest: defeated enemy" in player.quest:
            player.quest.remove("Quest: defeated enemy")
            player.quest.append(self.reward_item)
            player.gold += self.reward_gold
            self.completed = True
            print(f"\n{self.name}: Kamu luar biasa! Ini hadiahmu: {self.reward_item} (+{self.reward_gold} gold)")
        else:
            print(f"{self.name}: Kamu belum menyelesaikan tugasmu.")
