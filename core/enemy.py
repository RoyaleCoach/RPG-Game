import random


class Enemy:

    def __init__(self, name, hp, attack):
        self.name = name
        self.hp = hp
        self.attack = attack

    @staticmethod
    def random_enemy(floor):

        if floor <= 5:
            enemies = [
                Enemy("Goblin", 30, 8),
                Enemy("Skeleton", 40, 10),
                Enemy("Dark Wolf", 50, 12),
                Enemy("Bomber", 20, 20)
            ]

        elif floor <= 15:
            enemies = [
                Enemy("Venom Spider", 45, 14),
                Enemy("Ghoul", 60, 15),
                Enemy("Bone Archer", 55, 16),
                Enemy("Dark Shaman", 70, 18)
            ]

        elif floor <= 25:
            enemies = [
                Enemy("Stone Golem", 120, 18),
                Enemy("Ogre", 140, 20),
                Enemy("Necromancer", 90, 22),
                Enemy("Giant", 100, 15)
            ]

        else:
            enemies = [
                Enemy("Doom Knight", 160, 25),
                Enemy("Abyss Walker", 180, 28)
            ]

        return random.choice(enemies)

    @staticmethod
    def random_boss(player_level):

        selected = BOSSES[1]

        for level_req, boss_data in BOSSES.items():

            if player_level >= level_req:
                selected = boss_data

        return Boss(
            selected["name"],
            selected["hp"],
            selected["attack"],
            selected["exp_reward"],
            selected["gold_reward"]
        )


class Boss(Enemy):

    def __init__(
        self,
        name,
        hp,
        attack,
        exp_reward,
        gold_reward
    ):
        super().__init__(
            name,
            hp,
            attack
        )

        self.exp_reward = exp_reward
        self.gold_reward = gold_reward


BOSSES = {
    1: {
        "name": "Goblin King",
        "hp": 150,
        "attack": 20,
        "exp_reward": 100,
        "gold_reward": 150
    },

    5: {
        "name": "Skeleton Lord",
        "hp": 250,
        "attack": 30,
        "exp_reward": 200,
        "gold_reward": 250
    },

    10: {
        "name": "Ancient Dragon",
        "hp": 400,
        "attack": 45,
        "exp_reward": 350,
        "gold_reward": 400
    },

    15: {
        "name": "Demon Overlord",
        "hp": 600,
        "attack": 60,
        "exp_reward": 500,
        "gold_reward": 600
    },

    20: {
        "name": "Forgotten God",
        "hp": 900,
        "attack": 80,
        "exp_reward": 1000,
        "gold_reward": 1000
    }
}